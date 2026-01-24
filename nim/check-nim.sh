#!/bin/bash

echo "Checking 8001..."
curl http://localhost:8001/v1/health/ready
echo ""
echo "Checking 8002..."
curl http://localhost:8002/v1/health/ready
echo ""
echo "Checking 8003..."
curl http://localhost:8003/v1/health/ready
echo ""
echo "Checking 8004..."
curl http://localhost:8004/v1/health/ready
echo ""
echo ""
echo """✅ Health checks complete."