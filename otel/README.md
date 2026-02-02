# Overview

This guide shows how to configure an OpenTelemetry Collector to export traces, metrics and logs to Dynatrace.

The `config.yaml` is configured to as a OTLP receiver only and Docker or Podman is used to start the [Dynatrace distribution of the OpenTelemetry Collector OpenTelemetry Collector](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/collector) with a specified configuration file.

## Prerequisites

### Dynatrace

This is required for all configuration options.

1. If not done already, then make a Dynatrace API Token with the required scopes for the OTLP API:

    * `openTelemetryTrace.ingest`
    * `metrics.ingest`
    * `logs.ingest`

1. If not done already, Clone this repo

1. Make an environment file using the provided environment variable template:

    ```bash
    cd otel
    cp .env-otel-template .env
    ```
    
1. adjust `.env` with your Dynatrace environment `DT_BASE_URL` and `DT_API_TOKEN`

## Start and stop Otel Collector container

Provided scripts, assume using Docker.

### Start the Otel Collector

Run this shell script to start the container using Docker command.  Adjust as required to podman.

```bash
source .env
./start-otel.sh
```

### Stop the Otel Collector

Run this shell script to stop the container user Docker

```bash
./stop-otel.sh
```

# Other use cases

There are two other configuration files provided for various ways to run the Otel Collector:
* Config Option 1 - OTLP receiver plus Prometheus metric scraping from a locally run DCGM exporter. Uses `config-dcgm.yaml`
* Config Option 2 - OTLP receiver plus Prometheus metric scraping from a locally run DCGM exporter and locally run NIM Services. Uses `config-dcgm-nim.yaml`

## Prerequisites

### Prerequisites metric scraping for the DCGM exporter

Used in Config Option 1 and 2.

1. Get the DCGM HOST IP and PORT

    This example is for Kubernetes `DCGM_HOST` = 10.104.213.9 and `DCGM_PORT` = 9400

    ```bash
    kubectl -n nvidia-gpu-operator get svc --selector=app=nvidia-dcgm-exporter
    NAME                   TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
    nvidia-dcgm-exporter   ClusterIP   10.104.213.9   <none>        9400/TCP   23d
    ```

1. Update `.env` with your `DCGM_HOST` IP and `DCGM_PORT` 

### Prerequisites metric scraping for NIM services

Used in Config Option 2. 

This setup assumes there are three NIM services to scrap metrics from.  The `NIM_HOST` is the host that the Otel Collector container is running on and needs to be provided.

1. Get the host IP where containers are run.  This example is from unix:

     ```bash
    hostname -I | awk '{print $1}'
    ```

1. Update `.env` with your `NIM_HOST` 

## Start and stop Otel Collector container

Provided scripts, assume using Docker. Adjust as required to podman.

### Start Config Option 1 - metric scraping for the DCGM

```bash
source .env
./start-otel.sh config-dcgm.yaml
```

### Start Config Option 2 - metric scraping for the DCGM and NIM services

```bash
source .env
./start-otel.sh config-dcgm-nim.yaml
```

### Stop the Otel Collector

Run this shell script to stop the container user Docker

```bash
./stop-otel.sh
```
