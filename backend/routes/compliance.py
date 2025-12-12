import json
import os
import subprocess
import sys
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/compliance", tags=["compliance"])

# Check if running in demo mode
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
DEMO_SCRIPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../demo_scripts")
)

# Models
class ValidationResult(BaseModel):
    compliance_rate: float
    total_files: int
    valid_files: int
    violations: list[dict[str, Any]]

@router.get("/validate", response_model=ValidationResult)
async def validate_artifacts(
    target: str = Query("all", description="Target to validate: 'all', directory path, or file path")
):
    """
    Run the artifact validation tool.
    """
    if DEMO_MODE:
        # Use demo stub for compliance check
        try:
            workspace_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../..")
            )
            result = subprocess.run(
                ["python", os.path.join(DEMO_SCRIPTS_DIR, "compliance_stub.py")],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=workspace_root
            )
            
            # Parse stub output and return as ValidationResult
            # The stub outputs text, so we'll create a mock response
            return ValidationResult(
                compliance_rate=0.95,
                total_files=5,
                valid_files=5,
                violations=[]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Original production code
        # Determine project root
        # server.py is in apps/agentqms-dashboard/backend/
        # project root is ../../../
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
        script_path = os.path.join(project_root, "AgentQMS/agent_tools/compliance/validate_artifacts.py")

        if not os.path.exists(script_path):
            raise HTTPException(status_code=500, detail=f"Validation script not found at {script_path}")

        cmd = [sys.executable, script_path, "--json"]

        if target == "all":
            cmd.append("--all")
        else:
            # Sanitize target to prevent command injection or path traversal
            # For now, just ensure it's relative and doesn't contain ..
            if ".." in target or target.startswith("/"):
                 raise HTTPException(status_code=400, detail="Invalid target path")
            cmd.extend(["--file", target]) # Assuming --file works for dirs too or we need logic

        try:
            # Run subprocess
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False # Don't raise on non-zero exit, as validation failure returns non-zero
            )

            if not result.stdout:
                 raise HTTPException(status_code=500, detail=f"No output from validator. Stderr: {result.stderr}")

            try:
                data = json.loads(result.stdout)
                return data
            except json.JSONDecodeError:
                 # Fallback if output is not pure JSON (e.g. logs mixed in)
                 # Try to find JSON object in output
                 raise HTTPException(status_code=500, detail=f"Invalid JSON output: {result.stdout[:200]}...")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
