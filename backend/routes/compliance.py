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

@router.get("/metrics")
async def get_compliance_metrics():
    """Get compliance metrics for Strategy Dashboard."""
    import glob
    import frontmatter
    
    # Use same artifacts root logic as artifacts route
    _routes_dir = os.path.dirname(os.path.abspath(__file__))
    _backend_dir = os.path.dirname(_routes_dir)
    _project_root = os.path.dirname(_backend_dir)
    
    def get_artifacts_root():
        """Get artifacts root directory with auto-detection."""
        demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        
        # Try the configured path first
        artifacts_rel = "demo_data/artifacts" if demo_mode else "docs/artifacts"
        artifacts_root = os.path.join(_project_root, artifacts_rel)
        
        # Auto-detect: if configured path doesn't exist, try the alternative
        if not os.path.exists(artifacts_root):
            alt_artifacts_rel = "docs/artifacts" if demo_mode else "demo_data/artifacts"
            alt_artifacts_root = os.path.join(_project_root, alt_artifacts_rel)
            if os.path.exists(alt_artifacts_root):
                return alt_artifacts_root
        
        return artifacts_root
    
    artifacts_root = get_artifacts_root()
    
    # Debug logging
    print(f"DEBUG: Compliance metrics - artifacts_root: {artifacts_root}")
    print(f"DEBUG: Compliance metrics - artifacts_root exists: {os.path.exists(artifacts_root)}")
    
    try:
        search_pattern = os.path.join(artifacts_root, "**", "*.md")
        artifact_files = glob.glob(search_pattern, recursive=True)
        total = len(artifact_files)
        
        print(f"DEBUG: Compliance metrics - found {total} artifact files")
        
        if total == 0:
            print(f"WARNING: No artifacts found in {artifacts_root}")
            # Try to list what's actually there
            if os.path.exists(artifacts_root):
                try:
                    import os as os_module
                    contents = os_module.listdir(artifacts_root)
                    print(f"DEBUG: Contents of {artifacts_root}: {contents}")
                except:
                    pass
            return {
                "schema_compliance": 0,
                "branch_integration": 0,
                "timestamp_accuracy": 0,
                "index_coverage": 0
            }
        
        # Calculate metrics
        valid_schema = 0
        has_timestamps = 0
        has_branch = 0
        
        for f in artifact_files:
            try:
                post = frontmatter.load(f)
                metadata = post.metadata
                
                # Schema compliance: has required fields
                if metadata.get("title") and metadata.get("type") and metadata.get("status"):
                    valid_schema += 1
                
                # Timestamp accuracy: has date field
                if metadata.get("date") or metadata.get("created"):
                    has_timestamps += 1
                
                # Branch integration: has branch_name field
                if metadata.get("branch_name"):
                    has_branch += 1
            except:
                pass
        
        return {
            "schema_compliance": int((valid_schema / total) * 100) if total > 0 else 0,
            "branch_integration": int((has_branch / total) * 100) if total > 0 else 0,
            "timestamp_accuracy": int((has_timestamps / total) * 100) if total > 0 else 0,
            "index_coverage": int((total / max(total, 1)) * 100)  # Simplified
        }
    except Exception as e:
        return {
            "schema_compliance": 0,
            "branch_integration": 0,
            "timestamp_accuracy": 0,
            "index_coverage": 0,
            "error": str(e)
        }

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
        # Determine project root (backend/routes -> backend -> project root)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
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
