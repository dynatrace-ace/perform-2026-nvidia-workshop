# 🌟 NVIDIA Guardrails and Dynatrace Insights 🌟

This repository demonstrates how to build a secure, enterprise-grade AI agent is incapsulated within a simply Python application built using [streamlit](https://www.streamlit.io) and all of the observability telemetry of traces, logs, and metrics are collected using [OpenTelmemety collector](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/collector) for analysis within [Dynatrace](https://www.dynatrace.com).

NVIDIA [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) combined with the [NVIDIA NeMo Agent Toolkit](https://docs.nvidia.com/nemo/agent-toolkit/) will:
- **Validate input and output** for safety and appropriateness
- **Stay focused on topic** with content relevance checking

## 🚀 Quick Start

### Prerequisites

- Python 3.11, 3.12, or 3.13
- NVIDIA API Key (get from [build.nvidia.com](https://build.nvidia.com))
- Dynatrace tenant and API Key (get from [Dynatrace signup page](https://www.dynatrace.com/signup/))
- Docker or Podman for containerized deployment

### Installation

1. **Clone the repository:**

    ```bash
    git clone <your-repo-url>
    
    cd nat-simple-web-query-guardrail-demo
    ```

2. **Create Environment Variables file**

    Make an environment file using the provided template

    ```bash
    cp .env-app-template .env
    ```
3. **Set Tavily API Key**

    If not done already, get a Tavily API KEY API Key (get from [tavily.com](https://www.tavily.com)) and adjust `.env` with your Tavily API Key for `TAVILY_API_KEY`

4. **Set NVIDIA API Key**

    If not done already, get a NVIDIA API Key (get from [build.nvidia.com](https://build.nvidia.com)) and adjust `.env` with your NVIDIA API Key for `NVIDIA_API_KEY`

5. **Create Dynatrace API Key**

    Make a Dynatrace API Token with the required scopes for the OTLP API:
    
    * `openTelemetryTrace.ingest`
    * `metrics.ingest`
    * `logs.ingest`
        
    Adjust `.env` with your Dynatrace environment `DT_BASE_URL` and `DT_API_TOKEN`

6. **Start NIM containers locally**

    If running with NIM containers locally, then follow the [Setup guide](nim/README.md) 

7. **Start OpenTelemetry Collector locally**

    Use an OpenTelemetry Collector configured to send observability data to Dynatrace. For this, follow the [Setup guide](otel/README.md)

### Run the Application locally using Python

1. **Create virtual environment**

    ```
    uv venv --python 3.13 .venv
    source .venv/bin/activate
    ```

2. **Install dependencies**

    ```bash
    # Using uv (recommended)
    uv pip install -r requirements.txt
    ```

3. **Start sample App**

    This will start a web app on port `8501` for example `http://localhost:8501`
    
    ```bash
    # Set environment variables in `.env` and then source the file
    source .env
    
    # Start app which will open the web UI in a local browser
    streamlit run app.py
    ```

## 📁 Repository Structure

```
nat-simple-web-query-guardrail-demo/
├── README.md                      # This file
├── app.py                         # sample web app
├── .env-app-template              # template for your .env file used by app.py
├── pyproject.toml                 # Python package configuration
├── Dockerfile                     # Production container image
├── DOCKER.md                      # Guide for building sample app as container
├── .streamlit                     # folder used by streamlit web framework
│   └── config.toml                # streamlit config file
│
├── src/nat_simple_web_query/
│   ├── __init__.py
│   ├── register.py                # NAT component registration
│   ├── guarded_workflow.py        # Guardrails wrapper class
│   └── configs/
│       ├── config.yml             # Main workflow configuration
│       └── config-guarded.yml     # Guarded workflow config
│
├── guardrails_config/
│   ├── config.yml                 # Guardrails main config
│   ├── prompts.yml                # Validation prompts
│   └── actions.py                 # Custom validation functions
│
├── nim/
│   ├── README.md                  # setup guide
│   ├── .env-nim-template          # template for your .env file used by docker run command
│   └── start-nim.sh               # script to start NIM containers
│   └── stop-nim.sh                # script to stop NIM containers
│
└── otel/
    ├── README.md                  # setup guide
    ├── .env-otel-template         # template for your .env file used by docker run command
    ├── config-dcgm-nim.yaml       # otel config file for otlp receiver, dcgm and nim
    ├── config-dcgm.yaml           # otel config file for otlp receiver and dcgm
    ├── config.yaml                # otel config file for just otlp receiver
    ├── start-otel.sh              # script to start OTel collector
    └── stop-otel.sh               # script to stop OTel collector
```

## 🔧 Configuration

See ```src/nat_simple_web_query/configs/config.yml``` for workflow configuration and ```guardrails_config/``` for guardrails settings.

### NAT Workflow Configuration
- **File:** `src/nat_simple_web_query/configs/config.yml`
- **Purpose:** Defines the ReAct agent, tools, LLMs, and embedders
- **Key Settings:**
  - `verbose: false` - Reduces log noise
  - `parse_agent_response_max_retries: 1` - Fails fast on safety refusals

### Guardrails Configuration

#### Main Config (`guardrails_config/config.yml`)
- **Models:** NVIDIA NeMoGuard for content safety
- **Input Flows:**
  - `check jailbreak` - Custom pattern-based jailbreak detection
  - `check input topic` - Ensures queries are on topic
  - `content safety check input` - NVIDIA content moderation
- **Output Flows:**
  - `content safety check output` - Validates response safety
  - `check output relevance` - Ensures on-topic responses

#### Custom Actions (`guardrails_config/actions.py`)
- `check_jailbreak()` - Detects 12+ jailbreak patterns
- `check_input_topic()` - Topic validation with keyword matching
- `check_output_relevance()` - Ensures ocused responses
- `check_blocked_terms()` - Term-based filtering
- `check_input_length()` - Length validation (2000 char limit)

#### Colang Flows (`guardrails_config/flows.co`)
- Defines control flow logic for each guardrail
- Specifies refusal messages for different violation types
- Implements `stop` directives to halt processing

#### Prompts (`guardrails_config/prompts.yml`)
- Content safety validation templates
- Self-check prompts for input/output validation
- Output parsers and token limits


## 📚 Resources

- [Dynatrace AI and LLM Observability](https://www.dynatrace.com/solutions/ai-observability/)
- [NVIDIA NeMo Agent Toolkit](https://docs.nvidia.com/nemo/agent-toolkit/)
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
- [NeMo Guardrails Documentation](https://docs.nvidia.com/nemo/guardrails/latest/index.html)
- [NVIDIA NIM](https://www.nvidia.com/en-us/ai/)
- [NVIDIA AI Endpoints](https://build.nvidia.com)

---

**Built with ❤️ using NVIDIA NeMo Agent Toolkit and Dynatrace**
