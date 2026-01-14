#!/bin/bash

# Script to stop and remove Docker containers

# Function to stop and remove a container
stop_and_remove_container() {
    local container_name=otel-collector
    
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
echo "🔄 Stopping and removing otel container..."
echo ""
stop_and_remove_container
echo "✅ otel container processed"
echo ""
echo "✅ Showing list of containers"
echo ""
docker ps