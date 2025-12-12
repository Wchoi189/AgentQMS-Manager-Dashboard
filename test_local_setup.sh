#!/bin/bash
# Quick test script to verify local setup is working

set -e

echo "=========================================="
echo "AgentQMS Dashboard - Local Setup Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check demo data exists
echo "Test 1: Checking demo data..."
if [ -d "demo_data/artifacts" ] && [ "$(find demo_data/artifacts -name '*.md' | wc -l)" -ge 5 ]; then
    echo -e "${GREEN}✓ Demo artifacts found${NC}"
else
    echo -e "${RED}✗ Demo artifacts missing. Run: ./create_demo_data_simple.sh${NC}"
    exit 1
fi

# Test 2: Check demo scripts exist
echo "Test 2: Checking demo scripts..."
if [ -f "demo_scripts/validate_stub.py" ] && \
   [ -f "demo_scripts/compliance_stub.py" ] && \
   [ -f "demo_scripts/tracking_stub.py" ]; then
    echo -e "${GREEN}✓ Demo scripts found${NC}"
else
    echo -e "${RED}✗ Demo scripts missing. Run: ./create_demo_data_simple.sh${NC}"
    exit 1
fi

# Test 3: Test demo scripts are executable
echo "Test 3: Testing demo scripts..."
if python3 demo_scripts/validate_stub.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Demo scripts are executable${NC}"
else
    echo -e "${RED}✗ Demo scripts failed to execute${NC}"
    exit 1
fi

# Test 4: Check DEMO_MODE environment variable
echo "Test 4: Checking DEMO_MODE..."
if [ "$DEMO_MODE" = "true" ]; then
    echo -e "${GREEN}✓ DEMO_MODE is set to true${NC}"
else
    echo -e "${YELLOW}⚠ DEMO_MODE is not set. Set it with: export DEMO_MODE=true${NC}"
fi

# Test 5: Check Python dependencies
echo "Test 5: Checking Python dependencies..."
if python3 -c "import fastapi, uvicorn, frontmatter" 2>/dev/null; then
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ Some Python dependencies missing. Run: make install-backend${NC}"
fi

# Test 6: Check Node.js dependencies
echo "Test 6: Checking Node.js dependencies..."
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ Frontend dependencies missing. Run: make install-frontend${NC}"
fi

# Test 7: Check backend routes have DEMO_MODE support
echo "Test 7: Checking backend DEMO_MODE support..."
if grep -q "DEMO_MODE" backend/routes/artifacts.py && \
   grep -q "DEMO_MODE" backend/routes/tools.py && \
   grep -q "DEMO_MODE" backend/routes/tracking.py; then
    echo -e "${GREEN}✓ Backend routes have DEMO_MODE support${NC}"
else
    echo -e "${RED}✗ Backend routes missing DEMO_MODE support${NC}"
    exit 1
fi

# Test 8: Check ports are available
echo "Test 8: Checking ports availability..."
if ! lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Port 8000 is available${NC}"
else
    echo -e "${YELLOW}⚠ Port 8000 is in use. Stop existing server with: make stop-backend${NC}"
fi

if ! lsof -ti:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Port 3000 is available${NC}"
else
    echo -e "${YELLOW}⚠ Port 3000 is in use. Stop existing server with: make stop-frontend${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Setup verification complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Set DEMO_MODE: export DEMO_MODE=true"
echo "  2. Start servers: make dev"
echo "  3. Open browser: http://localhost:3000"
echo ""
echo "For detailed testing, see: LOCAL_TESTING_GUIDE.md"
