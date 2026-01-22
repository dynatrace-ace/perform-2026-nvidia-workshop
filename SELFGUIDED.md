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

    Once set, you can review your API usage with this command.
    
    ```bash
    curl --request GET \
        --url https://api.tavily.com/usage  \
        --header "Authorization: Bearer $TAVILY_API_KEY" | jq .
    ```

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

## 🚀 Run the Application locally using Python

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
    
    # update the configuration files
    python update_config.py --config-type=build

    # Start app which will open the web UI in a local browser
    streamlit run app.py
    ```

## 📚 Setup Details

See the [RESOURCES.md](RESOURCES.md) guide for details.

## 📚 Reference

- [Dynatrace AI and LLM Observability](https://www.dynatrace.com/solutions/ai-observability/)
- [NVIDIA NeMo Agent Toolkit](https://docs.nvidia.com/nemo/agent-toolkit/)
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
- [NeMo Guardrails Documentation](https://docs.nvidia.com/nemo/guardrails/latest/index.html)
- [NVIDIA NIM](https://www.nvidia.com/en-us/ai/)
- [NVIDIA AI Endpoints](https://build.nvidia.com)