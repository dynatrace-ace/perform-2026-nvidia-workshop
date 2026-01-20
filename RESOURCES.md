## 📁 Repository Structure

```
/
├── README.md                      # This file
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
│       ├── config.yml             # Main workflow configuration - same as config.yml.build
│       └── config.yml.build       # Reference config.yml to use the build APIs
│       └── config.yml.local       # Reference config.yml to use the local use of Docker NIMs
|
├── guardrails_config/
│   ├── config.yml                 # Guardrails main config
│   ├── config.yml.build           # Reference config.yml to use the build APIs
│   ├── config.yml.local           # Reference config.yml to use the local use of Docker NIMs
│   ├── prompts.yml                # Validation prompts
│   └── actions.py                 # Custom validation functions
│
├── nim/
│   ├── README.md                  # setup guide for starting NIMs locally with Docker
│   ├── .env-nim-template          # template for your .env file used by docker run command
│   └── start-nim.sh               # script to start NIM containers
│   └── stop-nim.sh                # script to stop NIM containers
│
└── otel/
    ├── README.md                  # setup guide for starting up an Otel Collector
    ├── .env-otel-template         # template for your .env file used by docker run command
    ├── config-dcgm-nim.yaml       # otel config file for otlp receiver, dcgm and nim
    ├── config-dcgm.yaml           # otel config file for otlp receiver and dcgm
    ├── config.yaml                # otel config file for just otlp receiver
    ├── start-otel.sh              # script to start OTel collector
    └── stop-otel.sh               # script to stop OTel collector
```

## 🔧 Configuration

See ```nat_config/configs/config.yml``` for NAT workflow configuration and ```guardrails_config/``` for guardrails settings.

### NAT Workflow Configuration
- **File:** `nat_config/configs/config.yml`
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
