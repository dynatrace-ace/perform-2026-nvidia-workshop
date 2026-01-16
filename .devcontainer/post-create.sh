HOST_BASE_URL=http://98.88.29.112:3800
echo "Getting the workshop environment settings..."

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

# Verify that environment variables were retrieved successfully
if [ -z "$DT_BASE_URL" ] || [ "$DT_BASE_URL" = "null" ]; then
  echo "Error: Failed to retrieve DT_BASE_URL. Please check your WORKSHOP_PASSWORD and try again."
  exit 1
fi

echo "Saving environment settings..."
echo "export DT_BASE_URL=\"$DT_BASE_URL\"" >> ~/.bashrc
echo "export DT_API_TOKEN=\"$DT_API_TOKEN\"" >> ~/.bashrc
echo "export NVIDIA_API_KEY=\"$NVIDIA_API_KEY\"" >> ~/.bashrc
echo "export TAVILY_API_KEY=\"$TAVILY_API_KEY\"" >> ~/.bashrc
echo "export OTEL_OTLP_ENDPOINT=\"$OTEL_OTLP_ENDPOINT\"" >> ~/.bashrc

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
export UV_HTTP_TIMEOUT=300
if ! uv pip install -r requirements.txt; then
  echo "Error: Failed to install Python dependencies. Please check requirements.txt and try again."
  exit 1
fi

echo "Launching Streamlit application..."
streamlit run app.py

echo "Codespace setup complete."
echo "Dynatrace API URL is: $DT_BASE_URL"
