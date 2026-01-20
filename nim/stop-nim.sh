#!/bin/bash

# Script to stop and remove Docker containers
# Usage: ./stop-containers.sh [container_name]
# If no container name is provided, stops and removes all specified containers

# Define the container names
CONTAINERS=("nim-topic-control" "nim-content-safety" "nim-llama-70b" "nim-embedqa")

# Function to stop and remove a container
stop_and_remove_container() {
    local container_name=$1
    
    # Check if container exists and is running
    if docker ps -q -f name="^${container_name}$" | grep -q .; then
        echo "⏹️  Stopping container: ${container_name}"
        docker stop "${container_name}"
    else
        echo "ℹ️  Container ${container_name} is not running"
    fi
    
    # Check if container exists (stopped or running) and remove it
    if docker ps -aq -f name="^${container_name}$" | grep -q .; then
        echo "🗑️  Removing container: ${container_name}"
        docker rm "${container_name}"
    else
        echo "ℹ️  Container ${container_name} does not exist"
    fi
    
    echo ""
}

# Main logic
if [ $# -eq 0 ]; then
    # No arguments provided - stop and remove all containers
    echo "🔄 Stopping and removing all containers..."
    echo ""
    for container in "${CONTAINERS[@]}"; do
        stop_and_remove_container "$container"
    done
    echo "✅ All containers processed"
else
    # Argument provided - stop and remove specific container
    container_name=$1
    echo "🔄 Stopping and removing container: ${container_name}"
    echo ""
    stop_and_remove_container "$container_name"
    echo "✅ Container ${container_name} processed"
fi
echo ""
echo "✅ Showing list of containers"
echo ""
docker ps