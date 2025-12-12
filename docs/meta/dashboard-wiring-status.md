---
title: "Dashboard Wiring Status"
status: active
last_updated: 2025-12-12
tags: [integration, dashboard, wiring, status]
---

# Dashboard Wiring Status

## Current State

### Fixed Issues
- ✅ **Tracking import error**: Fixed Python path resolution in `tracking.py` and `server.py`
- ✅ **Backend paths**: All routes now use correct project root (`../..` from backend/routes)
- ✅ **Tool execution**: Enhanced with fallback to direct script execution if make/uv unavailable
- ✅ **Metrics endpoints**: Added `/api/v1/stats` and `/api/v1/compliance/metrics` for real data

### Wired Components
- ✅ **Strategy Dashboard**: Now fetches real compliance metrics from `/api/v1/compliance/metrics`
- ✅ **Context Explorer**: Loads real artifacts and displays in matrix view
- ✅ **System Stats**: Dashboard home fetches from `/api/v1/stats` endpoint

### Known Issues

#### 1. Artifacts API Returns Empty
**Symptom**: Librarian shows "No artifacts found" (0 of 0 artifacts)

**Root Cause**: Backend `DEMO_MODE` environment variable must be set **before** server starts. The `ARTIFACTS_ROOT` is determined at module import time.

**Solution**: 
```bash
# Set DEMO_MODE before starting backend
export DEMO_MODE=true
./start_dev.sh

# Or restart backend with DEMO_MODE set
make stop-servers
export DEMO_MODE=true
make dev-backend
```

**Verification**:
```bash
curl http://localhost:8000/api/v1/artifacts
# Should return JSON with items array containing 18 artifacts
```

#### 2. Tracking Database Error
**Symptom**: "No module named 'AgentQMS'" error in tracking status

**Status**: Fixed - improved error handling shows helpful message when AgentQMS not available

**When DEMO_MODE=true**: Uses stub (works)
**When DEMO_MODE=false**: Requires AgentQMS in path (may need additional setup)

#### 3. Static Statistics
**Symptom**: Dashboard metrics don't reflect changes

**Status**: Partially fixed - `/api/v1/stats` endpoint calculates real metrics from artifacts
**Remaining**: Strategy Dashboard status cards (Indexing Status, Containerization, Traceability) still use hardcoded text

## Testing Checklist

### Backend Endpoints
- [ ] `/api/v1/artifacts` returns 18 artifacts when DEMO_MODE=true
- [ ] `/api/v1/stats` returns real counts from artifacts
- [ ] `/api/v1/compliance/metrics` returns calculated percentages
- [ ] `/api/v1/tracking/status` works in demo mode (stub)
- [ ] `/api/v1/tools/exec` executes boundary check successfully

### Frontend Components
- [ ] Librarian page shows 18 artifacts
- [ ] Strategy Dashboard shows real metrics in chart
- [ ] Context Explorer shows artifacts in matrix view
- [ ] Dashboard Home shows real document counts

## Next Steps

1. **Set DEMO_MODE at startup**: Ensure environment variable is set before backend starts
2. **Test real execution**: Run with `DEMO_MODE=false` to test AgentQMS integration
3. **Wire status cards**: Update Strategy Dashboard status cards to use real data
4. **Add relationships**: Extract artifact relationships for Context Explorer graph view

## Files Modified

- `backend/routes/artifacts.py` - Enhanced error handling, fallback search
- `backend/routes/compliance.py` - Added `/metrics` endpoint
- `backend/routes/system.py` - Added `/stats` endpoint
- `backend/routes/tracking.py` - Fixed import path, better error messages
- `backend/server.py` - Fixed workspace root path
- `frontend/components/StrategyDashboard.tsx` - Wired to real metrics
- `frontend/components/ContextExplorer.tsx` - Wired to real artifacts
- `frontend/services/registry.ts` - Updated to fetch real stats
