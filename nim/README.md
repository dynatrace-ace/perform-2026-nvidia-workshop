# Overview

This guide shows how to start the NIM services used by the sample app.  This guide only to be followed when running local NIM services and not `build.nvidia.com` APIs.

Provided scripts, assuming using bash scripts and Docker.

# Prerequisites - Environment Variables file

1. If not done already, Clone this repo

1. Make an environment file using the provided template

    ```bash
    cd nim
    cp .env-nim-template .env
    ```

# Prerequisites - NVIDIA

1. If not done already, get a NVIDIA API Key (get from [build.nvidia.com](https://build.nvidia.com))

1. adjust `.env` with your NVIDIA API Key as `NVIDIA_API_KEY`

# Start the containers

Run this shell script to start the containers using Docker. Optionally specify a container name to start a specific container:

**Option 1 - Start all containers:**

```bash
./start-nim.sh
```

**Option 2 - Start a specific container:**

For example just `nim-llama-70b`

```bash
./start-nim.sh nim-topic-control    # Start only the topic control container
```

# Stop the containers

Run this shell script to stop the containers using Docker. Optionally specify a container name to stop a specific container:

**Option 1 - Stop all containers:**

```bash
./stop-nim.sh
```

**Option 2 - Stop a specific container:**

For example just `nim-llama-70b`

```bash
./stop-nim.sh nim-llama-70b        # Stop only the LLaMA 70B container
```
