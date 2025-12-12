---
title: "Local Testing Guide for AgentQMS Dashboard"
status: draft
last_updated: 2025-12-12
tags: [testing, local, guide]
---

# Local Testing Guide for AgentQMS Dashboard

**Purpose**: Comprehensive guide to test the app locally before deploying to the cloud. This guide helps you find and fix bugs in a controlled environment.

---

## Quick Start (3 Steps)

```bash
# 1. Create demo data
./create_demo_data_simple.sh

# 2. Set demo mode
export DEMO_MODE=true

# 3. Start servers
make dev
```

**Access**: http://localhost:3000

---

## Prerequisites

### Required Software
- **Python 3.11.14** (check with `python --version`)
- **Node.js 18+** (check with `node --version`)
- **npm** (comes with Node.js)
- **uv** (Python package manager) - install with: `pip install uv`

### Verify Installation
```bash
# Check Python
python --version  # Should show 3.11.14

# Check Node.js
node --version    # Should show 18.x or higher

# Check npm
npm --version     # Should show 9.x or higher

# Check uv
uv --version      # Should show 0.x or higher
```

---

## Step-by-Step Setup

### Step 1: Install Dependencies

```bash
# Install all dependencies (frontend + backend)
make install

# Or install separately:
make install-frontend  # Installs npm packages
make install-backend    # Installs Python packages with uv
```

**Expected Output**:
```
✓ Frontend dependencies installed
✓ Backend dependencies installed
```

**Troubleshooting**:
- If `make install` fails, check that you're in the project root directory
- If Python version is wrong, update the `PYTHON` variable in `Makefile`
- If `uv` is not found, install it: `pip install uv`

---

### Step 2: Create Demo Data

```bash
# Run the demo data creation script
./create_demo_data_simple.sh
```

**What This Does**:
- Creates `demo_data/artifacts/` directory structure
- Generates 5 sample artifacts (implementation plan, assessment, bug report, audit, design)
- Creates 3 demo stub scripts (`validate_stub.py`, `compliance_stub.py`, `tracking_stub.py`)
- Makes stub scripts executable

**Expected Output**:
```
✅ Created 5 sample artifacts in demo_data/artifacts/
✅ Created 3 demo stubs in demo_scripts/
```

**Verify Demo Data**:
```bash
# Check artifacts exist
ls -la demo_data/artifacts/*/

# Check stubs exist
ls -la demo_scripts/*.py
```

**Troubleshooting**:
- If script fails, make it executable: `chmod +x create_demo_data_simple.sh`
- If directories don't exist, create them manually:
  ```bash
  mkdir -p demo_data/artifacts/{implementation_plans,assessments,audits,bug_reports,design_documents}
  mkdir -p demo_scripts
  ```

---

### Step 3: Configure Environment

```bash
# Set demo mode (required for local testing)
export DEMO_MODE=true

# Optional: Set Gemini API key (for AI features)
export GEMINI_API_KEY=your_api_key_here

# Optional: Set backend port (default: 8000)
export PORT=8000

# Optional: Set frontend URL for CORS (default: http://localhost:3000)
export FRONTEND_URL=http://localhost:3000
```

**Make Environment Persistent**:
```bash
# Add to ~/.bashrc or ~/.zshrc for permanent setup
echo 'export DEMO_MODE=true' >> ~/.bashrc
echo 'export GEMINI_API_KEY=your_api_key_here' >> ~/.bashrc
source ~/.bashrc
```

**Or create `.env` file** (if your setup supports it):
```bash
cat > .env << EOF
DEMO_MODE=true
GEMINI_API_KEY=your_api_key_here
PORT=8000
FRONTEND_URL=http://localhost:3000
EOF
```

---

### Step 4: Start Development Servers

#### Option A: Use Helper Script (Recommended)
```bash
# Use the helper script (handles everything automatically)
./start_dev.sh
```

This script:
- Stops any existing servers
- Starts backend on port 8000
- Starts frontend on port 3000
- Shows process IDs and log locations
- Handles cleanup on Ctrl+C

#### Option B: Start Both Servers with Make
```bash
make dev
```

**Note**: The Makefile runs servers in background. Use `make logs-backend` and `make logs-frontend` to view logs.

#### Option C: Start Servers Separately (Best for Debugging)

**Terminal 1 - Backend**:
```bash
export DEMO_MODE=true
cd backend
python server.py
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

**Troubleshooting**:
- **Port 3000 already in use**: Stop other processes: `lsof -ti:3000 | xargs kill -9`
- **Port 8000 already in use**: Stop other processes: `lsof -ti:8000 | xargs kill -9`
- **Backend fails to start**: Check Python version and dependencies
- **Frontend fails to start**: 
  - Check Node.js version: `node --version`
  - Reinstall dependencies: `cd frontend && npm install`
  - Check for missing packages: `npm list`
- **"Cannot find package 'picomatch'"**: Run `cd frontend && npm install` to fix dependencies

---

## Testing Checklist

### ✅ Basic Functionality Tests

#### 1. Health Check
```bash
# Test backend health endpoint
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status":"online","version":"0.1.0",...}
```

#### 2. List Artifacts
```bash
# Test artifact listing
curl http://localhost:8000/api/v1/artifacts

# Expected: JSON with 5 demo artifacts
```

#### 3. Frontend Access
- Open http://localhost:3000 in browser
- Should see dashboard home page
- No console errors in browser DevTools (F12)

#### 4. Navigation
- Click through all 7 pages:
  1. Dashboard Home
  2. Artifact Generator
  3. Framework Auditor
  4. Integration Hub
  5. Strategy Dashboard
  6. Context Explorer
  7. Librarian
- All pages should load without errors

---

### ✅ Feature-Specific Tests

#### Artifact Generator (Page 2)
1. **Open Artifact Generator page**
2. **Select artifact type**: Implementation Plan
3. **Enter title**: "Test Feature"
4. **Click "Generate with AI"** (requires GEMINI_API_KEY)
   - Should show loading state
   - Should generate artifact with frontmatter
   - Should display generated content
5. **Without API key**: Should show error message gracefully

**Test Cases**:
- ✅ Generate implementation plan
- ✅ Generate assessment
- ✅ Generate bug report
- ✅ Generate audit
- ✅ Generate design document
- ✅ Error handling when API key is missing

#### Framework Auditor (Page 3)
1. **Open Framework Auditor page**
2. **Click "Quick Validation"**
   - Should call `/api/v1/tools/exec` with `tool_id: "validate"`
   - Should display validation report from stub
   - Should show "PASS" status for demo artifacts
3. **Click "Compliance Check"**
   - Should call `/api/v1/compliance/validate`
   - Should show compliance report

**Test Cases**:
- ✅ Validation tool execution
- ✅ Compliance check execution
- ✅ Error handling for failed tool execution
- ✅ Display of validation results

#### Integration Hub (Page 4)
1. **Open Integration Hub page**
2. **Check tracking status**
   - Should call `/api/v1/tracking/status`
   - Should display tracking database status from stub
   - Should show active plans, experiments, etc.

**Test Cases**:
- ✅ Tracking status display
- ✅ Real-time status updates (if implemented)
- ✅ Error handling for tracking failures

#### Context Explorer (Page 5)
1. **Open Context Explorer page**
2. **Browse artifacts**
   - Should list all 5 demo artifacts
   - Should show artifact metadata (title, type, status, tags)
3. **View artifact details**
   - Click on an artifact
   - Should show full content with frontmatter
   - Should display relationships (if implemented)

**Test Cases**:
- ✅ Artifact listing
- ✅ Artifact detail view
- ✅ Filter by type
- ✅ Filter by status
- ✅ Search functionality

#### Librarian (Page 6)
1. **Open Librarian page**
2. **Browse by type**
   - Should show artifacts grouped by type
   - Should allow filtering
3. **Search artifacts**
   - Should search by title, content, tags
   - Should highlight search results

**Test Cases**:
- ✅ Browse by type
- ✅ Search functionality
- ✅ Filter by status
- ✅ Preview artifact content

---

### ✅ API Endpoint Tests

#### Test All Endpoints
```bash
# Health check
curl http://localhost:8000/api/v1/health

# List artifacts
curl http://localhost:8000/api/v1/artifacts

# Get specific artifact
curl http://localhost:8000/api/v1/artifacts/2025-12-01_1000_plan-ocr-feature

# Execute validation tool
curl -X POST http://localhost:8000/api/v1/tools/exec \
  -H "Content-Type: application/json" \
  -d '{"tool_id": "validate", "args": {}}'

# Get tracking status
curl http://localhost:8000/api/v1/tracking/status

# Compliance check
curl http://localhost:8000/api/v1/compliance/validate?target=all
```

**Expected Results**:
- All endpoints return 200 OK (except 404 for non-existent artifacts)
- JSON responses are valid
- No server errors in backend logs

---

### ✅ Error Handling Tests

#### Test Error Scenarios
1. **Invalid artifact ID**
   ```bash
   curl http://localhost:8000/api/v1/artifacts/invalid-id
   # Expected: 404 Not Found
   ```

2. **Invalid tool ID**
   ```bash
   curl -X POST http://localhost:8000/api/v1/tools/exec \
     -H "Content-Type: application/json" \
     -d '{"tool_id": "invalid", "args": {}}'
   # Expected: {"success": false, "error": "Unknown tool: invalid"}
   ```

3. **Missing API key for AI features**
   - Try to generate artifact without GEMINI_API_KEY
   - Should show user-friendly error message

4. **Network errors**
   - Stop backend server
   - Frontend should handle connection errors gracefully
   - Should show error message to user

---

### ✅ Browser Console Tests

1. **Open browser DevTools** (F12)
2. **Check Console tab**
   - Should have no red errors
   - Warnings are acceptable (e.g., React dev warnings)
3. **Check Network tab**
   - All API requests should return 200 OK
   - No failed requests
   - Check response times (should be < 1 second for demo mode)

---

## Common Issues & Solutions

### Issue 1: "Module not found" errors

**Symptoms**: Backend fails to start with import errors

**Solution**:
```bash
# Reinstall backend dependencies
cd backend
uv pip install -r requirements.txt

# Or use make
make install-backend
```

---

### Issue 2: "Port already in use"

**Symptoms**: Server fails to start, port conflict error

**Solution**:
```bash
# Find process using port 3000
lsof -ti:3000

# Kill process
lsof -ti:3000 | xargs kill -9

# Or use make command
make stop-servers
```

---

### Issue 3: "DEMO_MODE not working"

**Symptoms**: Backend still tries to access real AgentQMS tools

**Solution**:
```bash
# Verify environment variable is set
echo $DEMO_MODE  # Should output "true"

# If not set, export it
export DEMO_MODE=true

# Restart backend server
make restart-backend
```

---

### Issue 4: "Demo artifacts not showing"

**Symptoms**: Artifact list is empty or shows wrong artifacts

**Solution**:
```bash
# Verify demo data exists
ls -la demo_data/artifacts/*/

# Verify DEMO_MODE is set
echo $DEMO_MODE

# Check backend logs for errors
make logs-backend

# Restart backend
make restart-backend
```

---

### Issue 5: "CORS errors in browser"

**Symptoms**: Browser console shows CORS errors

**Solution**:
- Check `backend/server.py` has CORS middleware configured
- Verify frontend is accessing backend on correct port (8000)
- Check `frontend/vite.config.ts` proxy configuration

---

### Issue 6: "Frontend not connecting to backend"

**Symptoms**: API calls fail, network errors

**Solution**:
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/health

# Check frontend proxy config
cat frontend/vite.config.ts

# Restart both servers
make restart-servers
```

---

## Debugging Tips

### 1. Check Server Status
```bash
make status
```

Shows:
- Which servers are running
- Port information
- Database status

### 2. View Logs
```bash
# Backend logs
make logs-backend

# Frontend logs (in terminal where you ran `make dev-frontend`)
```

### 3. Test Backend Directly
```bash
# Start backend in verbose mode
cd backend
python server.py

# Test endpoints manually
curl http://localhost:8000/api/v1/health
```

### 4. Test Frontend Build
```bash
# Build frontend
make build

# Check for build errors
# Output should be in frontend/dist/
```

### 5. Check Environment Variables
```bash
# Print all environment variables
env | grep -E "DEMO_MODE|GEMINI|PORT|FRONTEND"

# Or check in Python
cd backend
python -c "import os; print('DEMO_MODE:', os.getenv('DEMO_MODE'))"
```

---

## Performance Testing

### Test Response Times
```bash
# Time API responses
time curl http://localhost:8000/api/v1/artifacts

# Expected: < 100ms for demo mode
```

### Test Frontend Load Time
- Open browser DevTools → Network tab
- Reload page (Ctrl+R / Cmd+R)
- Check "Load" time (should be < 2 seconds)

### Test Large Artifact Lists
- Create 20+ demo artifacts (modify script)
- Test pagination/limiting
- Check response times

---

## Security Testing

### Test Input Validation
```bash
# Test path traversal protection
curl "http://localhost:8000/api/v1/compliance/validate?target=../../../etc/passwd"
# Should return 400 Bad Request

# Test SQL injection (if applicable)
# Test XSS in artifact content
```

### Test CORS Configuration
- Verify CORS headers in responses
- Test from different origins (should fail if not allowed)

---

## Pre-Deployment Checklist

Before deploying to cloud, verify:

- [ ] All tests pass locally
- [ ] No console errors in browser
- [ ] All API endpoints work correctly
- [ ] Demo mode works as expected
- [ ] Error handling is graceful
- [ ] Performance is acceptable (< 1s response times)
- [ ] Environment variables are documented
- [ ] Dependencies are up to date
- [ ] Build succeeds without errors
- [ ] No sensitive data in code (API keys, etc.)

---

## Next Steps After Local Testing

1. **Fix any bugs found** during local testing
2. **Document issues** in a bug tracker or notes
3. **Test in production-like environment** (Docker)
4. **Deploy to staging** (if available)
5. **Deploy to production** (cloud)

---

## Additional Resources

- **Full Deployment Guide**: [Demo Deployment Guide](../deployment/demo-deployment-guide.md)
- **Quick Start**: [Demo Quick Start](../deployment/demo-quickstart.md)
- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **Makefile Commands**: Run `make help` for all available commands

---

## Getting Help

If you encounter issues not covered here:

1. Check backend logs: `make logs-backend`
2. Check browser console for frontend errors
3. Verify environment variables are set correctly
4. Check that demo data exists: `ls -la demo_data/artifacts/`
5. Review the deployment guides for additional context

---

**Happy Testing! 🚀**
