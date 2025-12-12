---
title: "Troubleshooting Guide"
status: draft
last_updated: 2025-12-12
tags: [troubleshooting, guide]
---

# Troubleshooting Guide

## Frontend Not Loading

### Issue: UI is not loading / Frontend not starting

**Symptoms**:
- Backend is running but frontend doesn't start
- Port 3000 is free but no frontend process
- Browser shows "Connection refused" on localhost:3000

**Root Causes & Solutions**:

#### 1. Makefile Runs Servers Sequentially
The `make dev` command runs `dev-backend` first, which blocks, so `dev-frontend` never executes.

**Solution**: Use the helper script instead:
```bash
./start_dev.sh
```

Or start servers separately in different terminals:
```bash
# Terminal 1
export DEMO_MODE=true
cd backend && python server.py

# Terminal 2
cd frontend && npm run dev
```

#### 2. Missing Frontend Dependencies
**Error**: `Cannot find package 'picomatch'` or similar module errors

**Solution**:
```bash
cd frontend
npm install
```

#### 3. Port Already in Use
**Error**: `Port 3000 is already in use` or `Port 8000 is already in use`

**Solution**:
```bash
# Kill processes on ports
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Or use make command
make stop-servers
```

#### 4. Frontend Process Crashed
**Check logs**:
```bash
tail -f /tmp/frontend.log
# Or if running manually, check terminal output
```

**Common causes**:
- Missing dependencies (run `npm install`)
- Syntax errors in code
- Port conflicts

---

## Backend Not Starting

### Issue: Backend fails to start

**Symptoms**:
- `make dev-backend` fails immediately
- Port 8000 error: "address already in use"
- Import errors

**Solutions**:

#### 1. Port Already in Use
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

#### 2. Missing Python Dependencies
```bash
cd backend
uv pip install -r requirements.txt
# Or
make install-backend
```

#### 3. Wrong Python Version
```bash
# Check Python version
python --version  # Should be 3.11.14

# Update Makefile if needed
# Edit Makefile and change PYTHON variable
```

#### 4. DEMO_MODE Not Set
Backend may try to access real AgentQMS tools if DEMO_MODE is not set.

```bash
export DEMO_MODE=true
make dev-backend
```

---

## Both Servers Running But UI Not Loading

### Issue: Servers are running but browser shows errors

**Check**:

1. **Backend Health**:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
   Should return JSON with status "online"

2. **Frontend Response**:
   ```bash
   curl http://localhost:3000
   ```
   Should return HTML

3. **Browser Console** (F12):
   - Check for CORS errors
   - Check for network errors
   - Check for JavaScript errors

4. **CORS Configuration**:
   - Verify `backend/server.py` has CORS middleware
   - Check `frontend/vite.config.ts` proxy configuration

---

## Process Debugging

### Check What's Running

```bash
# Check all processes
ps aux | grep -E "(npm|node|python)" | grep -v grep

# Check specific ports
lsof -ti:3000  # Frontend port
lsof -ti:8000  # Backend port

# Check server status
make status
```

### View Logs

```bash
# Backend logs
tail -f /tmp/backend.log
# Or if running manually, check terminal

# Frontend logs
tail -f /tmp/frontend.log
# Or if running manually, check terminal
```

### Stop All Servers

```bash
# Use make command
make stop-servers

# Or manually
pkill -f "python server.py"
pkill -f "npm run dev"

# Or kill by port
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

---

## Common Error Messages

### "Cannot find package 'picomatch'"
**Fix**: `cd frontend && npm install`

### "Port 3000 is already in use"
**Fix**: `lsof -ti:3000 | xargs kill -9`

### "Port 8000 is already in use"
**Fix**: `lsof -ti:8000 | xargs kill -9`

### "Module not found" (Python)
**Fix**: `cd backend && uv pip install -r requirements.txt`

### "AgentQMS path not found"
**Fix**: Set `export DEMO_MODE=true` to use demo mode

### "CORS error" in browser
**Fix**: 
- Check `backend/server.py` CORS configuration
- Verify frontend proxy in `frontend/vite.config.ts`
- Check that backend is running on port 8000

---

## Quick Diagnostic Commands

```bash
# Full system check
./test_local_setup.sh

# Check ports
netstat -tuln | grep -E ":3000|:8000"
# Or
ss -tuln | grep -E ":3000|:8000"

# Test backend
curl http://localhost:8000/api/v1/health

# Test frontend
curl http://localhost:3000

# Check processes
pgrep -f "npm run dev"
pgrep -f "python server.py"

# View logs
tail -20 /tmp/backend.log
tail -20 /tmp/frontend.log
```

---

## Still Having Issues?

1. **Check the logs**: Always check `/tmp/backend.log` and `/tmp/frontend.log`
2. **Verify environment**: Run `./test_local_setup.sh`
3. **Start fresh**: 
   ```bash
   make stop-servers
   ./start_dev.sh
   ```
4. **Check documentation**: See `docs/guides/local-testing-guide.md` for detailed steps
