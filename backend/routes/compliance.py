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

# Request Models
class FixRequest(BaseModel):
    file_path: str
    rule_id: str
    dry_run: bool = False

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
    target: str = Query("all", description="Target to validate: 'all', directory path, or file path"),
    force_real: bool = Query(False, description="Force real validation even in demo mode")
):
    """
    Run the artifact validation tool.
    """
    # Initialize Validator
    try:
        from services.compliance.validator import Validator
        validator = Validator()
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Failed to import compliance service: {e}")

    # Determine artifacts root
    def get_artifacts_root():
        """Get artifacts root directory with auto-detection."""
        _routes_dir = os.path.dirname(os.path.abspath(__file__))
        _backend_dir = os.path.dirname(_routes_dir)
        _project_root = os.path.dirname(_backend_dir)
        
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
    
    # Resolve Target
    target_path = artifacts_root
    if target != "all":
        # Sanitize and resolve relative path
        if ".." in target or target.startswith("/"):
             # Simple security check
             pass 
        else:
             target_path = os.path.join(artifacts_root, target)

    # Execute Validation
    try:
        if os.path.isfile(target_path):
            report = validator.validate_file(target_path)
            # Adapt single report to aggregate result format
            return ValidationResult(
                compliance_rate=100 if report.is_compliant else 0,
                total_files=1,
                valid_files=1 if report.is_compliant else 0,
                violations=[{
                    "file": os.path.basename(report.file_path),
                    "path": report.file_path,
                    "rule_id": v.rule_id,
                    "message": v.message,
                    "severity": v.severity
                } for v in report.violations]
            )
        elif os.path.isdir(target_path):
            result = validator.validate_directory(target_path)
            return ValidationResult(**result)
        else:
            raise HTTPException(status_code=404, detail=f"Target not found: {target_path}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fix")
async def fix_violation(request: FixRequest):
    """
    Attempt to auto-fix a compliance violation.
    """
    try:
        from services.compliance.remediator import Remediator
        remediator = Remediator()
        
        result = remediator.fix_violation(request.file_path, request.rule_id, dry_run=request.dry_run)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
            
        return result
    except ImportError:
        raise HTTPException(status_code=500, detail="Remediator service not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

