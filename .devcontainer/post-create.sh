HOST_BASE_URL=http://98.88.29.112:3800

# Get the workshop password from the secrets server
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

# copy variables to .bashrc
echo "export DT_BASE_URL=\"$DT_BASE_URL\"" >> ~/.bashrc
echo "export DT_API_TOKEN=\"$DT_API_TOKEN\"" >> ~/.bashrc
echo "export NVIDIA_API_KEY=\"$NVIDIA_API_KEY\"" >> ~/.bashrc
echo "export TAVILY_API_KEY=\"$TAVILY_API_KEY\"" >> ~/.bashrc
echo "export OTEL_OTLP_ENDPOINT=\"$OTEL_OTLP_ENDPOINT\"" >> ~/.bashrc

# start up Otel Collector
. "./otel/start-otel.sh"

echo "Codespace setup complete."
echo "Dynatrace API URL is: $DT_BASE_URL"
