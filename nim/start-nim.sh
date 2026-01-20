#!/bin/bash

# Script to start Docker containers
# Usage: ./start-containers.sh [container_name]
# nim-llama-70b, nim-content-safety, nim-topic-control, nim-embedqa
# If no container name is provided, starts all specified containers

source .env

# Configuration
NGC_API_KEY=${NGC_API_KEY:-""}
LOCAL_NIM_CACHE=${LOCAL_NIM_CACHE:-"$HOME/.cache/nim"}

# Define the container names
CONTAINERS=("nim-topic-control" "nim-content-safety" "nim-llama-70b" "nim-embedqa")

# Function to start a container
start_container() {
    local container_name=$1
    
    # Check if container exists and is running
    if docker ps -q -f name="^${container_name}$" | grep -q .; then
        echo "✅ Container ${container_name} is already running"
        echo ""
        return
    fi
    
    # Check if container exists but is stopped
    if docker ps -aq -f name="^${container_name}$" | grep -q .; then
        echo "▶️  Starting existing container: ${container_name}"
        docker start "${container_name}"
        echo ""
        return
    fi
    
    # Container doesn't exist, create and start it
    echo "🆕 Creating and starting new container: ${container_name}"
    
    case "${container_name}" in
        "nim-llama-70b")
            echo "   Image: meta/llama-3.1-70b-instruct"
            docker run -d --name nim-llama-70b \
                --gpus '"device=0"' \
                --shm-size=16GB \
                -e NGC_API_KEY \
                -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
                -u $(id -u) \
                -p 8001:8000 \
                nvcr.io/nim/meta/llama-3.1-70b-instruct:latest
            ;;
        "nim-content-safety")
            echo "   Image: nvidia/llama-3.1-nemoguard-8b-content-safety"
            docker run -d --name nim-content-safety \
                --gpus '"device=1"' \
                --shm-size=16GB \
                -e NGC_API_KEY \
                -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
                -u $(id -u) \
                -p 8002:8000 \
                nvcr.io/nim/nvidia/llama-3.1-nemoguard-8b-content-safety:latest
            ;;
        "nim-topic-control")
            echo "   Image: nvidia/llama-3.1-nemoguard-8b-topic-control"
            docker run -d --name nim-topic-control \
                --gpus '"device=2"' \
                --shm-size=16GB \
                -e NGC_API_KEY \
                -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
                -u $(id -u) \
                -p 8003:8000 \
                nvcr.io/nim/nvidia/llama-3.1-nemoguard-8b-topic-control:latest
            ;;
        "nim-embedqa")
            echo "   Image: nvidia/nv-embedqa-e5-v5"
            docker run -d --name nim-embedqa \
                --gpus '"device=4"' \
                --shm-size=16GB \
                -e NGC_API_KEY \
                -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
                -u $(id -u) \
                -p 8004:8000 \
                nvcr.io/nim/nvidia/nv-embedqa-e5-v5:latest
            ;;
        *)
            echo "❌ Unknown container: ${container_name}"
            echo ""
            return 1
            ;;
    esac
    
    echo ""
}

# Main script logic
if [ $# -eq 0 ]; then
    # No arguments provided - start all containers
    echo "🔄 Starting all containers..."
    echo ""
    for container in "${CONTAINERS[@]}"; do
        start_container "$container"
    done
    echo "✅ All containers processed"
else
    # Argument provided - start specific container
    container_name=$1
    echo "🔄 Starting container: ${container_name}"
    echo ""
    start_container "$container_name"
    echo "✅ Container ${container_name} processed"
fi
echo ""
echo "🔄 Waiting 30 seconds for containers to start..."
sleep 30
if [ $# -eq 0 ] || [ "$1" = "nim-topic-control" ]; then
    echo "▶️  Initializing nemoguard-8b-topic-control..."
    curl -X 'POST'   'http://0.0.0.0:8003/v1/chat/completions'   -H 'accept: application/json'   -H 'Content-Type: application/json'   -d '{
        "model": "nvidia/llama-3.1-nemoguard-8b-topic-control",
        "messages": [
        {
            "role":"user",
            "content":"Hello! How are you?"
        },
        {
            "role":"assistant",
            "content":"Hi! I am quite well, how can I help you today?"
        },
        {
            "role":"user",
            "content":"Can you write me a song?"
        }
        ],
        "top_p": 1,
        "n": 1,
        "max_tokens": 15,
        "stream": true,
        "frequency_penalty": 1.0,
        "stop": ["hello"]
    }'
fi
if [ $# -eq 0 ] || [ "$1" = "nim-topic-control" ]; then
    echo "▶️  Initializing nv-embedqa-e5-v5..."
    curl -X 'POST' 'http://0.0.0.0:8004/v1/embeddings' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
        "input": ["Hello world"],
        "model": "nvidia/nv-embedqa-e5-v5",
        "input_type": "query"
    }'
fi
echo ""
echo "✅ Showing list of containers"
echo ""
docker ps