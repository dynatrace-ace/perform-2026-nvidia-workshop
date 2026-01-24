# environment variables used:
# - OTEL_OTLP_ENDPOINT: OpenTelemetry OTLP exporter endpoint (default: http://localhost:4317)

import asyncio
import contextlib
import io
import logging
import warnings
import os
import sys
import time
from pathlib import Path

# Suppress Pydantic warnings BEFORE importing libraries that use Pydantic
warnings.filterwarnings("ignore", message=".*validate_default.*", module="pydantic")

# for streamlit app
import streamlit as st

# for NVIDIA Guardrails
from nemoguardrails import RailsConfig, LLMRails

# for OpenTelemetry setup
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor,ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# for OpenTelemetry and Dynatrace Traceloop
from opentelemetry import trace
from traceloop.sdk import Traceloop

# ------------------------------------------------------------------------------
# constants
# ------------------------------------------------------------------------------
# name used in tracing
SERVICE_NAME = "nvidia-example" + ("-" + os.getenv("GITHUB_USER", "") if os.getenv("GITHUB_USER", "") else "")
# used in UI selectbox
OPTION_WITH_GUARDRAILS = "With NeMo Guardrails"
OPTION_WITHOUT_GUARDRAILS = "Without NeMo Guardrails"

# ------------------------------------------------------------------------------
# traceloop-sdk setup for intrumentation and Dynatrace OTLP ingestion
# ------------------------------------------------------------------------------

# disable SDK collects anonymous telemetry data
os.environ['TRACELOOP_TELEMETRY'] = "false"
# set metrics preference to delta since this is what Dynatrace API expects
os.environ['OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE'] = "delta"

@st.cache_resource(show_spinner="Initializing Traceloop SDK...")
def initialize_traceloop():
    """Initialize Traceloop once (cached to prevent re-initialization on every Streamlit rerun)."""

    print("✓ Initializing Traceloop SDK...")
    Traceloop.init(
        app_name=SERVICE_NAME,
        api_endpoint=os.environ.get('OTEL_OTLP_ENDPOINT', 'http://localhost:4318'),
        disable_batch=True,
        should_enrich_metrics=True,
    )
    print("✓ Traceloop SDK initialized with: "+ os.environ.get('OTEL_OTLP_ENDPOINT', 'http://localhost:4318'))
    
# ------------------------------------------------------------------------------
# Suppress verbose NAT agent logging and warnings
# ------------------------------------------------------------------------------
@st.cache_resource(show_spinner="Configuring logging...")
def configure_logging():
    """Configure logging levels once (cached to prevent re-execution on every Streamlit rerun)."""
    print("✓ Configuring logging levels...")
    logging.getLogger("nat.agent").setLevel(logging.CRITICAL)
    logging.getLogger("nat").setLevel(logging.CRITICAL)
    logging.getLogger("langchain_community").setLevel(logging.ERROR)
    logging.getLogger("nemoguardrails.actions.action_dispatcher").setLevel(logging.ERROR)
    warnings.filterwarnings("ignore")
    return True

# ------------------------------------------------------------------------------
# Config file validation
# ------------------------------------------------------------------------------
@st.cache_resource(show_spinner="Config file validation...")
def ensure_config_files_exist():
    """Verify required config files exist before app starts."""
    print("✓ Ensuring required config files exist...")

    # Construct config file paths
    guardrails_config_path = Path("guardrails_config/config.yml")
    nat_config_path = Path("src/nat_simple_web_query/configs/config.yml")
    
    # Ensure both config files exist
    missing_files = []
    for config_path in [guardrails_config_path, nat_config_path]:
        if not config_path.exists():
            missing_files.append(str(config_path))
    
    if missing_files:
        print(f"❌ Error: The following config files were not found:")
        for file in missing_files:
            print(f"   - {file}")
        print(f"   Please run 'python update_config.py <config_type>' to generate config files.")
        os._exit(1)  # Force immediate exit without cleanup
    
    print("✓ All required config files found")

# ------------------------------------------------------------------------------
# guardrail functions
# ------------------------------------------------------------------------------
@st.cache_resource(show_spinner="Configuring guardrails...")
def initialize_guardrails():
    """Initialize guardrails configuration once (cached to prevent re-initialization on every Streamlit rerun)."""
    print("✓ Initializing guardrails configuration...")
    try:
        # Load guardrails configuration
        guardrails_path = Path(__file__).parent / "guardrails_config"
        
        if not guardrails_path.exists():
            print(f"⚠️ Guardrails config not found at: {guardrails_path}")
            return None
        
        rails_config = RailsConfig.from_path(str(guardrails_path))
        rails = LLMRails(rails_config)
        
        # Register custom guardrails actions
        import sys
        sys.path.insert(0, str(guardrails_path))
        
        try:
            from actions import (
                check_jailbreak, 
                check_blocked_terms, 
                check_input_topic, 
                check_input_length,
                check_output_relevance,
                check_politics
            )
            
            rails.register_action(check_jailbreak, "check_jailbreak")
            rails.register_action(check_input_topic, "check_input_topic")
            rails.register_action(check_output_relevance, "check_output_relevance")
            rails.register_action(check_blocked_terms, "check_blocked_terms")
            rails.register_action(check_input_length, "check_input_length")
            rails.register_action(check_politics, "check_politics")
            
            print("✓ Guardrails initialized successfully")
            return rails
        except ImportError as e:
            print(f"⚠️ Could not load custom actions: {e}")
            return rails
            
    except Exception as e:
        print(f"❌ Error initializing guardrails: {e}")
        return None

async def check_input_guardrails(rails, user_input):
    """Apply input guardrails and return (is_safe, message)."""
    try:
        start_time = time.time()
        input_result = await rails.generate_async(
            messages=[{"role": "user", "content": user_input}]
        )
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱️  Input guardrail execution time: {duration:.2f} seconds")
        
        # Check if input was blocked
        # Handle GenerationResponse objects (from NeMo Guardrails)
        if hasattr(input_result, 'response') and isinstance(input_result.response, list):
            # Extract content from GenerationResponse
            if input_result.response:
                content = input_result.response[-1].get('content', '')
                if any(phrase in content.lower() for phrase in ["i'm sorry", "i can't", "i cannot", "please ask", "i can only"]):
                    return False, content
        elif isinstance(input_result, dict):
            content = input_result.get('content', '')
            # Consistent phrase checking across both branches
            if any(phrase in content.lower() for phrase in ["i'm sorry", "i can't", "i cannot", "please ask", "i can only"]):
                return False, content
        elif hasattr(input_result, 'is_stop') and input_result.is_stop:
            return False, input_result.return_value
        
        return True, "Input passed guardrails"
    except Exception as e:
        return False, f"Error checking input: {str(e)}"

async def check_output_guardrails(rails, user_input, workflow_result):
    """Apply output guardrails and return (is_safe, message)."""
    try:
        start_time = time.time()
        output_result = await rails.generate_async(
            messages=[
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": workflow_result}
            ]
        )
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱️  Output guardrail execution time: {duration:.2f} seconds")
        
        # Check if output was blocked
        # Handle GenerationResponse objects (from NeMo Guardrails)
        if hasattr(output_result, 'response') and isinstance(output_result.response, list):
            # Extract content from GenerationResponse
            if output_result.response:
                content = output_result.response[-1].get('content', '')
                if any(phrase in content.lower() for phrase in ["i can only", "please ask questions", "i'm sorry", "i cannot"]):
                    return False, content
        elif isinstance(output_result, dict):
            content = output_result.get('content', '')
            # Fixed: Added "i cannot" to match GenerationResponse branch for consistency
            if any(phrase in content.lower() for phrase in ["i can only", "please ask questions", "i'm sorry", "i cannot"]):
                return False, content
        elif hasattr(output_result, 'is_stop') and output_result.is_stop:
            return False, output_result.return_value
        
        return True, "Output passed guardrails"
    except Exception as e:
        return False, f"Error checking output: {str(e)}"
    
# ------------------------------------------------------------------------------
# NAT functions
# ------------------------------------------------------------------------------
async def run_nat_workflow(user_input, nat_config_path):
    """Execute the NAT workflow."""
    from nat.runtime.loader import load_workflow
    
    stderr_capture = io.StringIO()
    
    try:
        with contextlib.redirect_stderr(stderr_capture):
            async with load_workflow(nat_config_path) as workflow:
                start_time = time.time()
                async with workflow.run(user_input) as runner:
                    workflow_result = await runner.result(to_type=str)
                end_time = time.time()
                duration = end_time - start_time
                print(f"⏱️  NAT workflow execution time: {duration:.2f} seconds")
        return True, str(workflow_result)
    except Exception as e:
        error_msg = str(e)
        if "list index out of range" in error_msg or "Failed to parse" in error_msg:
            return False, "Request was refused by the AI model for safety reasons"
        #if "match any of the expected tags" in error_msg:
        #    return False, "Request was refused by the AI model for safety reasons"
        return False, f"Error: {error_msg}"

# ------------------------------------------------------------------------------
# Main functions
# ------------------------------------------------------------------------------
async def process_query(user_input, user_option_guardrail, rails, nat_config_path, status_text=None):
    """Main processing function that coordinates all steps."""
    print("Processing", user_option_guardrail, "query:", user_input)
    results = {
        "input_safe": False,
        "input_message": "",
        "workflow_success": False,
        "workflow_result": "",
        "output_safe": False,
        "output_message": "",
        "final_result": ""
    }
    
    if user_option_guardrail == OPTION_WITH_GUARDRAILS:
        # Step 1: Input guardrails
        status_text.text("⚡ Running input guardrails...")
        results["input_safe"], results["input_message"] = await check_input_guardrails(rails, user_input)
        if not results["input_safe"]:
            return results
    else:
        results["input_safe"] = True
    
    # Step 2: Run NAT workflow
    status_text.text("⚡ Running NAT workflow...")
    results["workflow_success"], results["workflow_result"] = await run_nat_workflow(user_input, nat_config_path)
    if not results["workflow_success"]:
        return results
    
    # Check for safety refusal in NAT workflow result
    if "Invalid Format" in results["workflow_result"] and (
        "can't" in results["workflow_result"].lower() or 
        "illegal" in results["workflow_result"].lower()
    ):
        results["workflow_success"] = False
        results["workflow_result"] = "(NAT workflow) Request was refused by the AI model for safety reasons. Details: " + results["workflow_result"]
        return results
    
    # Step 3: Output guardrails
    if user_option_guardrail == OPTION_WITH_GUARDRAILS:
        status_text.text("⚡ Running Output guardrails...")
        results["output_safe"], results["output_message"] = await check_output_guardrails(
            rails, user_input, results["workflow_result"]
        )
        if results["output_safe"]:
            results["final_result"] = results["workflow_result"]
    else:
        # Output guardrails disabled - set as safe and use workflow result
        results["output_safe"] = True
        results["final_result"] = results["workflow_result"]
    
    return results

# ------------------------------------------------------------------------------
# streamlit Setup
# ------------------------------------------------------------------------------

def main():
    """Main Streamlit application."""
    # Verify config files exist first (will exit if missing)
    ensure_config_files_exist()
    
    # Initialize components will caching to prevent re-initialization on every rerun
    initialize_traceloop()
    configure_logging()
    rails = initialize_guardrails() 

    # Page configuration (must be first Streamlit command)
    st.set_page_config(
        page_title="NVIDIA Agent Toolkit with Guardrails with Dynatrace Observability",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #76B900;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.4rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        .status-box {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .success-box {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
        }
        .warning-box {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
        }
        .error-box {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
        }
        .info-box {
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">Operationalizing AI at Scale</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">NVIDIA NeMo Agent Toolkit, NeMo Guardrails and Dynatrace Insights</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center;"><img src="app/static/dt-nvidia.png" alt="Dynatrace and NVIDIA" width="300" style="margin: auto; display: block;"></div>', unsafe_allow_html=True)

    # Main content area
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # Initialize session state
        if 'history' not in st.session_state:
            st.session_state.history = []

        # Show Service name
        st.markdown(f'<hr><p><div style="text-align: left; font-style: italic;">Service Name: {SERVICE_NAME}</div></p>', unsafe_allow_html=True)

        # Query input
        user_input = st.text_area(
            "💬 Ask your question",
            placeholder="Enter your question here...",
            height=100,
            help="Type your question and press Submit"
        )
            
        user_option_guardrail = st.selectbox(
            label="Select an option",
            options=[OPTION_WITHOUT_GUARDRAILS, OPTION_WITH_GUARDRAILS],
            index=0,
            help="Choose an option to run with or without NeMo guardrails")
                
        col_submit, col_clear = st.columns([1, 1])
        
        with col_submit:
            submit_button = st.button("🚀 Submit Query", type="primary", use_container_width=True)
        
        with col_clear:
            clear_button = st.button("🗑️ Clear History", use_container_width=True)
        
        if clear_button:
            st.session_state.history = []
            st.rerun()
        
        # Process query
        nat_config_path = str(Path(__file__).parent / "src" / "nat_simple_web_query" / "configs" / "config.yml")
        if submit_button and user_input.strip():
            if not rails:
                st.error("❌ Cannot process query: Guardrails not initialized")
            elif not Path(nat_config_path).exists():
                st.error(f"❌ Config file not found: {nat_config_path}")
            else:
                with st.spinner("🔄 Processing your query..."):
                    with trace.get_tracer(SERVICE_NAME).start_as_current_span(name="prompt", kind=trace.SpanKind.SERVER) as span:
                        # Create progress indicators
                        progress_bar = st.progress(50)
                        status_text = st.empty()
                        
                        # Step 1: Input guardrails
                        if user_option_guardrail == OPTION_WITH_GUARDRAILS:
                            status_text.text("⚡ Checking Input guardrails...")
                        else:
                            status_text.text("⚡ Skipping guardrails...")
                        
                        # Run async processing
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        results = loop.run_until_complete(process_query(user_input, user_option_guardrail, rails, Path(nat_config_path), status_text=status_text))
                        loop.close()
                        
                        # Update progress
                        progress_bar.progress(100)
                        status_text.empty()
                        progress_bar.empty()
                        
                        # Display results
                        st.divider()
                        
                        # Input check result
                        if not results["input_safe"]:
                            st.error(f"🚫 Input Blocked: {results['input_message']}")
                        else:
                            if user_option_guardrail == OPTION_WITH_GUARDRAILS:
                                st.success("✅ Input passed safety checks")
                            
                            # Workflow result
                            if not results["workflow_success"]:
                                st.error(f"⚠️ NAT Workflow Error: {results['workflow_result']}")
                            else:
                                st.success("✅ NAT Workflow completed successfully")
                                
                                if user_option_guardrail == OPTION_WITH_GUARDRAILS:
                                    # Output check result
                                    if not results["output_safe"]:
                                        st.warning(f"⚠️ Output Blocked: {results['output_message']}")
                                    else:
                                        st.success("✅ Output passed safety checks")
                                
                                # Only display and store final result if output guardrails passed or are disabled
                                if results["final_result"]:  # final_result is only set if guardrails passed or are disabled
                                    # Final result
                                    st.markdown("### 📝 Response:")
                                    st.markdown(f'<div class="status-box success-box">{results["final_result"]}</div>', 
                                            unsafe_allow_html=True)
                                    
                                    # Add to history
                                    st.session_state.history.append({
                                        "question": user_input,
                                        "answer": results["final_result"]
                                    })
        
        # Display conversation history
        if st.session_state.history:
            st.divider()
            st.header("📜 Conversation History")
            
            for idx, item in enumerate(reversed(st.session_state.history)):
                with st.expander(f"Q{len(st.session_state.history) - idx}: {item['question'][:80]}...", expanded=(idx == 0)):
                    st.markdown("**Question:**")
                    st.info(item['question'])
                    st.markdown("**Answer:**")
                    st.success(item['answer'])

# ------------------------------------------------------------------------------
# App entry point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()