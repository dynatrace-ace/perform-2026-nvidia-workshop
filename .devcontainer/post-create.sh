HOST_BASE_URL=http://98.88.29.112:3800

export DT_BASE_URL=$(curl -s -X POST $HOST_BASE_URL/dynatrace-url \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"$WORKSHOP_PASSWORD\"}" | jq -r '.dynatrace_url')

export DYNATRACE_API_TOKEN=$(curl -s -X POST $HOST_BASE_URL/dynatrace-token \
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

echo "Codespace setup complete."
echo "Dynatrace API URL is: $DT_BASE_URL"
