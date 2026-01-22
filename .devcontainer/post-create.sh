HOST_BASE_URL=http://107.21.127.218:3800

echo "Getting the workshop environment settings..."

# Verify that environment variables were retrieved successfully
if [ -z "$WORKSHOP_PASSWORD" ] || [ "$WORKSHOP_PASSWORD" = "null" ]; then
  echo "Error: WORKSHOP_PASSWORD is not set or is null. Please check your WORKSHOP_PASSWORD and try again."
  exit 1
fi

export DT_BASE_URL=$(curl -s -X POST $HOST_BASE_URL/dynatrace-url \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"$WORKSHOP_PASSWORD\"}" | jq -r '.dynatrace_url')

export DT_API_TOKEN=$(curl -s -X POST $HOST_BASE_URL/dynatrace-token \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"$WORKSHOP_PASSWORD\"}" | jq -r '.dynatrace_api_token')

export NVIDIA_API_KEY=$(curl -s -X POST $HOST_BASE_URL/nvidia-key \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"$WORKSHOP_PASSWORD\"}" | jq -r '.nvidia_api_key')

export TAVILY_API_KEY=$(curl -s -X POST $HOST_BASE_URL/tavily-key \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"$WORKSHOP_PASSWORD\"}" | jq -r '.tavily_api_key')

export OTEL_OTLP_ENDPOINT=$(curl -s -X POST $HOST_BASE_URL/otel-endpoint \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"$WORKSHOP_PASSWORD\"}" | jq -r '.otel_otlp_endpoint')

export NVIDIA_MODEL_ENDPOINT_8001=$(curl -s -X POST $HOST_BASE_URL/nvidia-model-endpoint-8001 \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"$WORKSHOP_PASSWORD\"}" | jq -r '.nvidia_model_endpoint_8001')

export NVIDIA_MODEL_ENDPOINT_8002=$(curl -s -X POST $HOST_BASE_URL/nvidia-model-endpoint-8002 \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"$WORKSHOP_PASSWORD\"}" | jq -r '.nvidia_model_endpoint_8002')

export NVIDIA_MODEL_ENDPOINT_8003=$(curl -s -X POST $HOST_BASE_URL/nvidia-model-endpoint-8003 \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"$WORKSHOP_PASSWORD\"}" | jq -r '.nvidia_model_endpoint_8003')

export NVIDIA_MODEL_ENDPOINT_8004=$(curl -s -X POST $HOST_BASE_URL/nvidia-model-endpoint-8004 \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"$WORKSHOP_PASSWORD\"}" | jq -r '.nvidia_model_endpoint_8004')

echo "DT_BASE_URL=$DT_BASE_URL"
echo "NVIDIA_MODEL_ENDPOINT_8001=$NVIDIA_MODEL_ENDPOINT_8001"

# Verify that environment variables were retrieved successfully
if [ -z "$DT_BASE_URL" ] || [ "$DT_BASE_URL" = "null" ]; then
  echo "Error: Failed to retrieve DT_BASE_URL. Please check your WORKSHOP_PASSWORD and try again."
  exit 1
fi
if [ -z "$NVIDIA_MODEL_ENDPOINT_8001" ] || [ "$NVIDIA_MODEL_ENDPOINT_8001" = "null" ]; then
  echo "Error: Failed to retrieve NVIDIA_MODEL_ENDPOINT_8001. Please check your WORKSHOP_PASSWORD and try again."
  exit 1
fi

echo "Saving environment settings..."
echo "export DT_BASE_URL=\"$DT_BASE_URL\"" >> ~/.bashrc
echo "export DT_API_TOKEN=\"$DT_API_TOKEN\"" >> ~/.bashrc
echo "export NVIDIA_API_KEY=\"$NVIDIA_API_KEY\"" >> ~/.bashrc
echo "export TAVILY_API_KEY=\"$TAVILY_API_KEY\"" >> ~/.bashrc
echo "export OTEL_OTLP_ENDPOINT=\"$OTEL_OTLP_ENDPOINT\"" >> ~/.bashrc
echo "export NVIDIA_MODEL_ENDPOINT_8001=\"$NVIDIA_MODEL_ENDPOINT_8001\"" >> ~/.bashrc
echo "export NVIDIA_MODEL_ENDPOINT_8002=\"$NVIDIA_MODEL_ENDPOINT_8002\"" >> ~/.bashrc
echo "export NVIDIA_MODEL_ENDPOINT_8003=\"$NVIDIA_MODEL_ENDPOINT_8003\"" >> ~/.bashrc
echo "export NVIDIA_MODEL_ENDPOINT_8004=\"$NVIDIA_MODEL_ENDPOINT_8004\"" >> ~/.bashrc

echo "Starting up Otel Collector..."
cd /workspaces/perform-2026-nvidia-workshop/otel
./start-otel.sh
cd /workspaces/perform-2026-nvidia-workshop

echo "Setting up Python environment..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "Creating and activating Python virtual environment..."
uv venv --python 3.13 .venv
source .venv/bin/activate

echo "Installing Python dependencies..."
# Increase UV HTTP timeout to handle slower connections
export UV_HTTP_TIMEOUT=300
# Suppress UV hardlink warning for cross-filesystem operations
export UV_LINK_MODE=copy
if ! uv pip install -r requirements.txt; then
  echo "Error: Failed to install Python dependencies. Please check requirements.txt and try again."
  exit 1
fi

echo "Codespace setup complete."
echo "Dynatrace API URL is: $DT_BASE_URL"

echo "Launching Streamlit application..."
streamlit run app.py
