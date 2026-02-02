<img alt="Workshop" src="static/nvidia-workshop-header.png">

This repository demonstrates how to build a secure, enterprise-grade AI agent is incapsulated within a simply Python application built using [streamlit](https://www.streamlit.io), [NVIDIA NeMo Agent Toolkit](https://docs.nvidia.com/nemo/agent-toolkit/) and NVIDIA [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails). All of the observability telemetry of traces, logs, and metrics are collected using the [Dynatrace distribution of the OpenTelemetry Collector](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/collector) for analysis within [Dynatrace](https://www.dynatrace.com).

This repo and related guides assume Mac OS/Linux, but you can adapt as required for Windows.

## Setup

This diagram below depicts the setup consisting of:
* Sample Python app - Used to generate prompts and send telemetry data to and OpenTelemetry Collector
* OpenTelemetry Collector - Configured to send telemetry data to Dynatrace OTLP APIs
* NVIDIA Build - free to use LLM models accessed via APIs and a Build API key
* Tavily - Uses as Agentic tool to search the internet and accessed via APIs and a Build API key
* Dynatrace - View and analyze OpenTelemetry metrics

<img alt="Selfguided setup" src="static/selfguided-setup.png" width="75%">

## 🚀 Quick Start

### Prerequisites

1. Local software
    - Python 3.11, 3.12, or 3.13 
    - Python package and project manager, [uv](https://docs.astral.sh/uv/getting-started/installation/)
    - Docker or Podman for containerized deployment of a OpenTelemetry Collector
1. NVIDIA Build Account on [build.nvidia.com](https://build.nvidia.com)
1. Tavily Developer Account on [tavily.com](https://www.tavily.com)
1. Dynatrace Tenant. For a Trial, visit [Dynatrace signup page](https://www.dynatrace.com/signup/)

### Installation

1. **Clone the repository:**

    ```bash
    git clone git@github.com:dynatrace-ace/perform-2026-nvidia-workshop.git
    
    cd perform-2026-nvidia-workshop
    ```

2. **Create Environment Variables file**

    Make an environment file using the provided environment variable template:

    ```bash
    cp .env-app-template .env
    ```
3. **Set Tavily API Key**

    - Create a Tavily API KEY API Key on [tavily.com](https://www.tavily.com)
    - Adjust `.env` with your Tavily API Key for `TAVILY_API_KEY`
    - Once set, you can review your API usage with this command.
        ```bash
        curl --request GET \
            --url https://api.tavily.com/usage  \
            --header "Authorization: Bearer $TAVILY_API_KEY" | jq .
        ```

4. **Set NVIDIA API Key**

    - Create a NVIDIA API Key on [build.nvidia.com](https://build.nvidia.com)
    - Adjust `.env` with your NVIDIA API Key for `NVIDIA_API_KEY`

5. **Create Dynatrace API Key**

    - Make a Dynatrace API Token with the required scopes for the OTLP API:
        * `openTelemetryTrace.ingest`
        * `metrics.ingest`
        * `logs.ingest`
    - Adjust `.env` with your Dynatrace environment `DT_BASE_URL` and `DT_API_TOKEN`

6. Start an OpenTelemetry Collector configured to send observability data to Dynatrace. For this, follow the [OTLP receiver only setup guide](otel/README.md)

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

3. **Update the NVIDIA configuration files**
    
    This script will create the `guardrails_config/config.yml` and `src/configs/config.yml` files from the provided template for NVIDIA build API usage required for NVIDIA NAT and Guardrail usage.

    ```bash
    source .env
    python update_config.py build
    ```

4. **Start sample App**

    This will start a web app on port `8501` for example `http://localhost:8501`

    ```bash
    streamlit run app.py
    ```

5. **Open App**

    Start app which will open the web UI in a local browser at `http://localhost:5801`


## 📚 Setup Details

See the [RESOURCES.md](RESOURCES.md) guide for details.

## 📚 Reference

- [Dynatrace AI and LLM Observability](https://www.dynatrace.com/solutions/ai-observability/)
- [NVIDIA NeMo Agent Toolkit](https://docs.nvidia.com/nemo/agent-toolkit/)
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
- [NeMo Guardrails Documentation](https://docs.nvidia.com/nemo/guardrails/latest/index.html)
- [NVIDIA NIM](https://www.nvidia.com/en-us/ai/)
- [NVIDIA AI Endpoints](https://build.nvidia.com)

