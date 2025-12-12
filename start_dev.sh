#!/bin/bash
# Helper script to start both frontend and backend servers
# Usage: ./start_dev.sh

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting AgentQMS Dashboard Development Servers...${NC}"
echo ""

# Check if DEMO_MODE is set
if [ "$DEMO_MODE" != "true" ]; then
    echo -e "${YELLOW}⚠ DEMO_MODE is not set. Setting it to true for local testing...${NC}"
    export DEMO_MODE=true
fi

# Stop any existing servers
echo -e "${BLUE}Cleaning up existing processes...${NC}"
pkill -f "python server.py" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
sleep 1

# Clear ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 1

# Start backend in background
echo -e "${BLUE}Starting backend server on port 8000...${NC}"
cd backend
# Use Python from Makefile or default to python3
PYTHON=${PYTHON:-/home/vscode/.pyenv/versions/3.11.14/bin/python}
if [ ! -f "$PYTHON" ]; then
    PYTHON=python3
fi
$PYTHON server.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${YELLOW}Backend failed to start. Check logs:${NC}"
    tail -20 /tmp/backend.log
    exit 1
fi

# Test backend health
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${YELLOW}⚠ Backend started but not responding yet...${NC}"
fi

# Start frontend in background
echo -e "${BLUE}Starting frontend server on port 3000...${NC}"
cd frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${YELLOW}Frontend failed to start. Check logs:${NC}"
    tail -20 /tmp/frontend.log
    exit 1
fi

# Test frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${YELLOW}⚠ Frontend started but not responding yet...${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Both servers are running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Process IDs:"
echo "  Backend PID:  $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo ""
echo "View logs:"
echo "  Backend:  tail -f /tmp/backend.log"
echo "  Frontend: tail -f /tmp/frontend.log"
echo ""
echo "Stop servers:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  Or: make stop-servers"
echo ""

# Keep script running and show logs
echo -e "${BLUE}Press Ctrl+C to stop both servers...${NC}"
echo ""

# Trap Ctrl+C to cleanup
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Wait for processes
wait
