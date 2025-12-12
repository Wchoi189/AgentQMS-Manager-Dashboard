"""Tracking database status endpoint."""
import os
import subprocess
import sys

from fastapi import APIRouter, Query

# Ensure AgentQMS is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

router = APIRouter(prefix="/api/v1/tracking", tags=["tracking"])

# Check if running in demo mode
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
DEMO_SCRIPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../demo_scripts")
)


@router.get("/status")
async def get_tracking_status(kind: str = Query("all", description="Kind: plan, experiment, debug, refactor, or all")):
    """Get tracking database status for plans, experiments, debug sessions, or refactors."""
    
    if DEMO_MODE:
        # Use demo stub
        try:
            workspace_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../..")
            )
            result = subprocess.run(
                ["python", os.path.join(DEMO_SCRIPTS_DIR, "tracking_stub.py")],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=workspace_root
            )
            return {
                "kind": kind,
                "status": result.stdout,
                "success": result.returncode == 0
            }
        except Exception as e:
            return {
                "kind": kind,
                "status": "",
                "success": False,
                "error": str(e)
            }
    else:
        # Original production code
        try:
            from AgentQMS.agent_tools.utilities.tracking.query import get_status

            status_text = get_status(kind)
            return {
                "kind": kind,
                "status": status_text,
                "success": True
            }
        except Exception as e:
            return {
                "kind": kind,
                "status": "",
                "success": False,
                "error": str(e)
            }
