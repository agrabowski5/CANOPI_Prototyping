#!/bin/bash

# CANOPI API Fix Verification Script
# This script verifies that the API path fixes are working correctly

set -e

echo "=================================="
echo "CANOPI API Fix Verification"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo "1. Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not running${NC}"
    echo "   Please start the backend with: cd backend && uvicorn app.main:app --reload"
    exit 1
fi

echo ""

# Test API endpoints
echo "2. Testing API endpoints..."

# Test projects endpoint
echo -n "   Testing /api/v1/projects/... "
response=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:8000/api/v1/projects/)
if [ "$response" == "200" ]; then
    echo -e "${GREEN}✓ 200 OK${NC}"
else
    echo -e "${RED}✗ $response${NC}"
fi

# Test grid topology endpoint
echo -n "   Testing /api/v1/grid/topology... "
response=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:8000/api/v1/grid/topology)
if [ "$response" == "200" ]; then
    echo -e "${GREEN}✓ 200 OK${NC}"
else
    echo -e "${RED}✗ $response${NC}"
fi

# Test transmission lines endpoint
echo -n "   Testing /api/v1/transmission/lines/geojson... "
response=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:8000/api/v1/transmission/lines/geojson?limit=1")
if [ "$response" == "200" ]; then
    echo -e "${GREEN}✓ 200 OK${NC}"
else
    echo -e "${RED}✗ $response${NC}"
fi

# Test optimization endpoint
echo -n "   Testing /api/v1/optimization/jobs... "
response=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:8000/api/v1/optimization/jobs)
if [ "$response" == "200" ]; then
    echo -e "${GREEN}✓ 200 OK${NC}"
else
    echo -e "${RED}✗ $response${NC}"
fi

echo ""

# Verify old paths return 404 (as expected)
echo "3. Verifying legacy paths are not accessible..."

echo -n "   Testing /v1/projects/ (should be 404)... "
response=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:8000/v1/projects/)
if [ "$response" == "404" ]; then
    echo -e "${GREEN}✓ 404 (correct)${NC}"
else
    echo -e "${YELLOW}⚠ $response (unexpected)${NC}"
fi

echo ""

# Check frontend tests
echo "4. Running frontend API path tests..."
cd frontend
if npm test -- api-paths.test.ts --watchAll=false --silent 2>&1 | grep -q "PASS"; then
    echo -e "${GREEN}✓ Frontend tests passed${NC}"
else
    echo -e "${YELLOW}⚠ Frontend tests need attention${NC}"
fi
cd ..

echo ""

# Summary
echo "=================================="
echo "Verification Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Start the frontend: cd frontend && npm start"
echo "2. Open http://localhost:3000"
echo "3. Check browser console - should see no 404 errors"
echo "4. Test creating projects, viewing grid, and running optimization"
echo ""
