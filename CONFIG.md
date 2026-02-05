## 📚 Reference

- [Dynatrace AI and LLM Observability](https://www.dynatrace.com/solutions/ai-observability/)
- [NVIDIA NeMo Agent Toolkit](https://docs.nvidia.com/nemo/agent-toolkit/)
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
- [NeMo Guardrails Documentation](https://docs.nvidia.com/nemo/guardrails/latest/index.html)
- [NVIDIA NIM](https://www.nvidia.com/en-us/ai/)
- [NVIDIA AI Endpoints](https://build.nvidia.com)

## 📁 Repository Structure

```
/
├── README.md
├── update_config.py               # copies the correct config.yml files for nat and guardrails
├── app.py                         # sample web app
├── .env-app-template              # template for your .env file used by app.py
├── .streamlit                     # folder used by streamlit web framework
│   └── config.toml                # streamlit config file
│
├── nat_config/
│   ├── __init__.py
│   ├── register.py                # NAT component registration
│   ├── guarded_workflow.py        # Guardrails wrapper class
│   └── configs/
│       └── config.yml.build       # Reference config.yml to use the build APIs
│       ├── config.yml.brev        # Reference config.yml to use local model accessable via public endpoints
│       └── config.yml.local       # Reference config.yml to use the local use of Docker NIMs
|
├── guardrails_config/
│   ├── config.yml.build           # Reference config.yml to use the build APIs
│   ├── config.yml.brev            # Reference config.yml to use local model accessable via public endpoints
│   ├── config.yml.local           # Reference config.yml to use the local use of Docker NIMs
│   ├── prompts.yml                # Validation prompts
│   └── actions.py                 # Custom validation functions
│
├── otel/
│   ├── README.md                  # setup guide for starting up an Otel Collector
│   ├── .env-otel-template         # template for your .env file used by docker run command
│   ├── config.yaml                # otel config file for just otlp receiver. Used for NVIDIA build APIs use case
│   ├── config-dcgm-nim.yaml       # otel config file for otlp receiver, dcgm and nim
│   ├── config-dcgm.yaml           # otel config file for otlp receiver and dcgm
│   ├── start-otel.sh              # script to start OTel collector
│   └── stop-otel.sh               # script to stop OTel collector
│
├── nim/                           # Only for when running NIMs locally with Docker
│   ├── README.md                  # setup guide 
│   ├── .env-nim-template          # template for your .env file used by docker run command
│   ├── start-nim.sh               # script to start NIM containers
│   └── stop-nim.sh                # script to stop NIM containers
│
└── .devcontainer/                 # Only for workshop when dev containers where used
```

## 🔧 NVIDIA Configuration

### NAT Workflow Configuration (`src/nat_simple_web_query/configs`)

- **Purpose:** Defines the ReAct agent, tools, LLMs, and embedders
- **Key Settings:**
  - `workflow` - over all workflow definition
    - `parse_agent_response_max_retries` - Fails fast on safety refusals
    - `verbose: false` - Reduces log noise
  - `functions` - tools to use in the workflow
  - `llms` and `embedders` - models to use in the workflow
  - `telemetry` - Where to send OpenTelemetry traces

### Guardrails Configuration

#### Main Config (`guardrails_config/config.yml`)
- **Models:** NVIDIA NeMoGuard for content safety
- **instructions:** Additional prompt context
- **Input Flows:** Input guard rail checks
- **Output Flows:** Output guard rail checks

#### Custom Actions (`guardrails_config/actions.py`)
Defines logic for each guardrail action
- `check_jailbreak()` - Detects 12+ jailbreak patterns
- `check_blocked_terms()` - Term-based filtering
- `check_input_length()` - Length validation (2000 char limit)
- `check_politics` - Check if user input contains political content
- `check_input_topic()` - Topic validation with keyword matching
- `check_output_relevance()` - Ensures focused responses

#### Colang Flows (`guardrails_config/flows.co`)
- Defines control flow logic for each guardrail
- Specifies refusal messages for different violation types
- Implements `stop` directives to halt processing

#### Prompts (`guardrails_config/prompts.yml`)
- Content safety validation templates
- Self-check prompts for input/output validation
- Output parsers and token limits
