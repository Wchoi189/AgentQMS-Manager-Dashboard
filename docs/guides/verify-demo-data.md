---
title: "Verifying Demo Data in Librarian Page"
status: draft
last_updated: 2025-12-12
tags: [demo, verification, librarian]
---

# Verifying Demo Data in Librarian Page

## Quick Answer: **YES**, demo data will populate the Librarian page, BUT you need to:

1. ✅ **Set DEMO_MODE=true** before starting the backend
2. ✅ **Restart the backend** if it's already running
3. ✅ **Refresh the Librarian page** in your browser

---

## How It Works

### Backend Configuration
The backend reads artifacts from different directories based on `DEMO_MODE`:

```python
# In backend/routes/artifacts.py
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
ARTIFACTS_ROOT = "demo_data/artifacts" if DEMO_MODE else "docs/artifacts"
```

- **When DEMO_MODE=true**: Reads from `demo_data/artifacts/`
- **When DEMO_MODE=false or not set**: Reads from `docs/artifacts/`

### Frontend Flow
1. Librarian page calls `bridgeService.listArtifacts()`
2. This hits `/api/v1/artifacts` endpoint
3. Backend reads from `ARTIFACTS_ROOT` directory
4. Returns list of artifacts with metadata
5. Librarian displays them with filters and search

---

## Verification Steps

### Step 1: Check Demo Data Exists
```bash
# Count artifacts
find demo_data/artifacts -name "*.md" | wc -l
# Should show: 18 (or more)

# List by type
ls demo_data/artifacts/implementation_plans/
ls demo_data/artifacts/assessments/
ls demo_data/artifacts/bug_reports/
```

### Step 2: Ensure DEMO_MODE is Set
```bash
# Check current value
echo $DEMO_MODE

# Set it if not set
export DEMO_MODE=true
```

### Step 3: Restart Backend with DEMO_MODE
```bash
# Stop existing backend
make stop-servers
# Or: pkill -f "python server.py"

# Start with DEMO_MODE
export DEMO_MODE=true
./start_dev.sh

# Or start separately:
export DEMO_MODE=true
cd backend && python server.py
```

### Step 4: Test API Endpoint
```bash
# Test the API directly
curl http://localhost:8000/api/v1/artifacts

# Should return JSON with items array containing artifacts
# Example:
# {
#   "items": [
#     {
#       "id": "2025-12-01_1000_plan-ocr-feature",
#       "title": "Implementation Plan: OCR Feature Enhancement",
#       "type": "implementation_plan",
#       "status": "active",
#       ...
#     },
#     ...
#   ],
#   "total": 18
# }
```

### Step 5: Check Librarian Page
1. Open http://localhost:3000
2. Navigate to "Librarian" page
3. You should see all 18 artifacts listed
4. Test filters:
   - Filter by type (Implementation Plans, Assessments, etc.)
   - Filter by status (Active, Completed, Draft, etc.)
   - Search by title or ID

---

## Troubleshooting

### Problem: Librarian shows "No artifacts found"

**Solution**:
1. Check DEMO_MODE is set: `echo $DEMO_MODE`
2. Restart backend with DEMO_MODE: `export DEMO_MODE=true && make restart-backend`
3. Check API: `curl http://localhost:8000/api/v1/artifacts`
4. Check browser console (F12) for errors

### Problem: API returns empty array `{"items":[],"total":0}`

**Causes**:
- Backend started without DEMO_MODE=true
- Wrong directory being read
- Artifacts in wrong location

**Solution**:
```bash
# Stop backend
make stop-servers

# Verify demo data exists
ls demo_data/artifacts/implementation_plans/

# Restart with DEMO_MODE
export DEMO_MODE=true
./start_dev.sh
```

### Problem: Backend reading from wrong directory

**Check**:
```bash
# See what backend is using
curl http://localhost:8000/api/v1/health
# Check the response - it might show current directory

# Or check backend logs
tail -f /tmp/backend.log
# Look for "Error parsing" messages with file paths
```

**Fix**: Restart backend with `DEMO_MODE=true`

### Problem: Some artifacts not showing

**Check**:
1. Artifact has valid frontmatter (required: title, type, status)
2. File is in correct subdirectory
3. File has `.md` extension
4. Check backend logs for parsing errors

```bash
# Check for parsing errors
tail -20 /tmp/backend.log | grep -i error
```

---

## Quick Test Script

```bash
#!/bin/bash
# Quick verification script

echo "=== Demo Data Verification ==="
echo ""

# Check demo data
echo "1. Checking demo artifacts..."
COUNT=$(find demo_data/artifacts -name "*.md" | wc -l)
echo "   Found: $COUNT artifacts"

# Check DEMO_MODE
echo "2. Checking DEMO_MODE..."
if [ "$DEMO_MODE" = "true" ]; then
    echo "   ✓ DEMO_MODE is set to true"
else
    echo "   ✗ DEMO_MODE is not set (or not 'true')"
    echo "   Set it with: export DEMO_MODE=true"
fi

# Test API
echo "3. Testing API endpoint..."
RESPONSE=$(curl -s http://localhost:8000/api/v1/artifacts 2>/dev/null)
if [ $? -eq 0 ]; then
    TOTAL=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('total', 0))" 2>/dev/null)
    echo "   API returned: $TOTAL artifacts"
    if [ "$TOTAL" -gt 0 ]; then
        echo "   ✓ API is working correctly"
    else
        echo "   ✗ API returned 0 artifacts - backend may need restart with DEMO_MODE=true"
    fi
else
    echo "   ✗ Backend not responding (may not be running)"
fi

echo ""
echo "=== Summary ==="
echo "If API shows 0 artifacts but demo data exists, restart backend:"
echo "  export DEMO_MODE=true"
echo "  make stop-servers"
echo "  ./start_dev.sh"
```

---

## Expected Behavior

When everything is configured correctly:

1. **Librarian page loads** → Shows all 18 artifacts
2. **Filter by type** → Shows filtered results (e.g., 4 Implementation Plans)
3. **Filter by status** → Shows filtered results (e.g., 3 Active artifacts)
4. **Search** → Filters by title/ID/type matching query
5. **Click artifact** → Shows full details with content

---

## Summary

✅ **YES**, demo data will populate the Librarian page  
✅ **BUT** you must:
- Set `export DEMO_MODE=true` 
- Start/restart backend with DEMO_MODE set
- Refresh the browser page

The demo data is already created (18 artifacts), you just need to ensure the backend is reading from the right directory!
