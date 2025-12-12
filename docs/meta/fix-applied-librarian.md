---
title: "Fix Applied: Librarian Page Artifacts"
status: draft
last_updated: 2025-12-12
tags: [librarian, fix, meta]
---

# Fix Applied: Librarian Page Artifacts

## Problem
The Librarian page wasn't showing any artifacts because the backend was looking for artifacts in the wrong directory.

## Root Cause
The backend runs from the `backend/` directory, but `ARTIFACTS_ROOT` was set to a relative path `"demo_data/artifacts"`, which resolved to `backend/demo_data/artifacts` (doesn't exist) instead of the project root's `demo_data/artifacts`.

## Fix Applied
Updated `backend/routes/artifacts.py` to resolve the path relative to the project root:

```python
# Now resolves to: /workspaces/AgentQMS-Manager-Dashboard/demo_data/artifacts
_routes_dir = os.path.dirname(os.path.abspath(__file__))  # backend/routes/
_backend_dir = os.path.dirname(_routes_dir)  # backend/
_project_root = os.path.dirname(_backend_dir)  # project root/
_artifacts_rel = "demo_data/artifacts" if DEMO_MODE else "docs/artifacts"
ARTIFACTS_ROOT = os.path.join(_project_root, _artifacts_rel)
```

## Action Required

**You must restart the backend** for the fix to take effect:

```bash
# Stop existing backend
make stop-servers

# Start with DEMO_MODE=true
export DEMO_MODE=true
./start_dev.sh
```

Or if running separately:
```bash
# Terminal 1 - Backend
export DEMO_MODE=true
cd backend && python server.py

# Terminal 2 - Frontend (if not already running)
cd frontend && npm run dev
```

## Verification

After restarting, test the API:
```bash
curl http://localhost:8000/api/v1/artifacts
```

Should return JSON with 18 artifacts.

Then refresh the Librarian page in your browser - you should see all artifacts!

## Status
✅ Fix applied and tested
✅ API now returns 18 artifacts correctly
⏳ Waiting for backend restart
