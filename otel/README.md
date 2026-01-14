# Overview

This guide shows how to configure an OpenTelemetry Collector to export traces, metrics and logs to Dynatrace.

Note that there are three configuration files provided for various ways to run the Otel Collector:
1. `config.yaml` - OTLP receiver only
1. `config-dcgm.yaml` - OTLP receiver plus Prometheus metric scraping for the DCGM exporter
1. `config-dcgm-nim.yaml` - OTLP receiver plus Prometheus metric scraping for the DCGM exporter and NIM Services

Use provided scripts to start and stop Otel Collector container using `config-dcgm-nim.yaml`

Use the docker command commands for the starting the Otel Collector with other options.s

# Prerequisites - Dynatrace

1. If not done already, then make a Dynatrace API Token with the required scopes for the OTLP API:

    * `openTelemetryTrace.ingest`
    * `metrics.ingest`
    * `logs.ingest`

1. If not done already, Clone this repo

1. make an environment file using the provided template

    ```bash
    cd otel
    cp .env-otel-template .env
    ```
    
1. adjust `.env` with your Dynatrace environment `DT_BASE_URL` and `DT_API_TOKEN`

# Prerequisites (Optional) - only if using the metric scraping for the DCGM exporter

1. Get the DCGM HOST IP and PORT

    This example is for Kubernetes `DCGM_HOST` = 10.104.213.9 and `DCGM_PORT` = 9400

    ```bash
    kubectl -n nvidia-gpu-operator get svc --selector=app=nvidia-dcgm-exporter
    NAME                   TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
    nvidia-dcgm-exporter   ClusterIP   10.104.213.9   <none>        9400/TCP   23d
    ```

1. Update `.env` with your `DCGM_HOST` IP and `DCGM_PORT` 

# Prerequisites - metric scraping for NIM services

This setup assumes there are three NIM services to scrap metrics from.  The `NIM_HOST` is the host that the Otel Collector container is running on and needs to be provided.

1. Get the host IP where containers are run.  This example is from unix

     ```bash
    hostname -I | awk '{print $1}'
    ```

1. Update `.env` with your `NIM_HOST` 

# Start and stop Otel Collector container

Provided scripts, assume using Docker.

### Start the Otel Collector

Run this shell script to start the container using Docker. Optionally specify a configuration file.

**Option 1 - OTLP receiver only (defaults to use config.yaml):**

```bash
./start-otel.sh
```

**Option 2 - OTLP receiver plus Prometheus metric scraping for DCGM exporter:**

```bash
./start-otel.sh config-dcgm.yaml
```

**Option 3 - OTLP receiver plus Prometheus metric scraping for DCGM exporter and NIM Services:**

```bash
./start-otel.sh config-dcgm-nim.yaml
```

### Stop the Otel Collector

Run this shell script to stop the container user Docker

```bash
./stop-otel.sh
```
