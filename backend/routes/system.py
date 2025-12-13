import os
import glob
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(prefix="/api/v1", tags=["system"])

# Helper to get artifacts root (same logic as artifacts route)
_routes_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_routes_dir)
_project_root = os.path.dirname(_backend_dir)

def get_artifacts_root():
    """Get artifacts root directory based on current DEMO_MODE setting."""
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    artifacts_rel = "demo_data/artifacts" if demo_mode else "docs/artifacts"
    return os.path.join(_project_root, artifacts_rel)

class SystemStats(BaseModel):
    totalDocs: int
    docGrowth: int
    referenceHealth: int
    brokenLinks: int
    pendingMigrations: int
    distribution: List[dict]

class DirectoryNode(BaseModel):
    name: str
    path: str
    type: str  # 'directory' or 'file'
    file_count: int = 0
    children: List['DirectoryNode'] = []

DirectoryNode.model_rebuild()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/version")
async def version():
    return {"version": "0.1.0"}

@router.get("/demo-mode")
async def get_demo_mode():
    """Get current DEMO_MODE setting and artifacts path."""
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    demo_mode_env = os.getenv("DEMO_MODE", "not set")
    
    # Check which paths exist
    demo_path = os.path.join(_project_root, "demo_data/artifacts")
    docs_path = os.path.join(_project_root, "docs/artifacts")
    
    artifacts_root = get_artifacts_root()
    
    return {
        "demo_mode_env": demo_mode_env,
        "demo_mode_interpreted": demo_mode,
        "artifacts_root": artifacts_root,
        "artifacts_root_exists": os.path.exists(artifacts_root),
        "demo_data_exists": os.path.exists(demo_path),
        "docs_artifacts_exists": os.path.exists(docs_path),
        "using_demo_data": "demo_data" in artifacts_root
    }

@router.get("/stats", response_model=SystemStats)
async def get_stats():
    """Get real system statistics from artifacts."""
    try:
        # Count artifacts
        artifacts_root = get_artifacts_root()
        artifact_files = glob.glob(os.path.join(artifacts_root, "**", "*.md"), recursive=True)
        total_docs = len(artifact_files)
        
        # Count by type
        type_counts = {}
        for f in artifact_files:
            try:
                import frontmatter
                post = frontmatter.load(f)
                artifact_type = post.metadata.get("type", "unknown")
                type_counts[artifact_type] = type_counts.get(artifact_type, 0) + 1
            except:
                pass
        
        # Build distribution
        distribution = [
            {"name": "Implementation Plans", "valid": type_counts.get("implementation_plan", 0), "issues": 0},
            {"name": "Assessments", "valid": type_counts.get("assessment", 0), "issues": 0},
            {"name": "Audits", "valid": type_counts.get("audit", 0), "issues": 0},
            {"name": "Bug Reports", "valid": type_counts.get("bug_report", 0), "issues": 0},
            {"name": "Designs", "valid": type_counts.get("design", 0), "issues": 0},
        ]
        
        return SystemStats(
            totalDocs=total_docs,
            docGrowth=0,  # TODO: Calculate from git history
            referenceHealth=100,  # TODO: Check link validity
            brokenLinks=0,  # TODO: Validate links
            pendingMigrations=0,  # TODO: Check for legacy artifacts
            distribution=distribution
        )
    except Exception as e:
        # Fallback to safe defaults
        return SystemStats(
            totalDocs=0,
            docGrowth=0,
            referenceHealth=100,
            brokenLinks=0,
            pendingMigrations=0,
            distribution=[]
        )

def scan_directory_tree(root_path: str, max_depth: int = 5, current_depth: int = 0) -> Dict[str, Any]:
    """Recursively scan directory structure and return tree with file counts."""
    if not os.path.exists(root_path) or current_depth >= max_depth:
        return None
    
    result = {
        "name": os.path.basename(root_path) or root_path,
        "path": root_path,
        "type": "directory",
        "file_count": 0,
        "children": []
    }
    
    try:
        items = sorted(os.listdir(root_path))
        for item in items:
            item_path = os.path.join(root_path, item)
            
            # Skip hidden files and common ignore patterns
            if item.startswith('.') or item in ['__pycache__', 'node_modules', '.git']:
                continue
            
            if os.path.isdir(item_path):
                child = scan_directory_tree(item_path, max_depth, current_depth + 1)
                if child:
                    result["children"].append(child)
                    result["file_count"] += child["file_count"]
            elif os.path.isfile(item_path):
                # Count markdown files and Python files
                if item.endswith(('.md', '.py', '.yaml', '.yml', '.json')):
                    result["file_count"] += 1
    except PermissionError:
        pass
    
    return result

@router.get("/system/directory-structure")
async def get_directory_structure():
    """Get AgentQMS directory structure with file counts."""
    try:
        agentqms_path = os.path.join(_project_root, "AgentQMS")
        
        # If AgentQMS doesn't exist, try demo_data structure
        if not os.path.exists(agentqms_path):
            # Fallback: scan from project root for demo purposes
            agentqms_path = _project_root
        
        tree = scan_directory_tree(agentqms_path, max_depth=4)
        
        if not tree:
            # Return minimal structure if scan fails
            return {
                "tree": {
                    "name": "AgentQMS",
                    "path": agentqms_path,
                    "type": "directory",
                    "file_count": 0,
                    "children": []
                },
                "total_files": 0
            }
        
        # Calculate total files
        def count_total_files(node):
            total = node.get("file_count", 0)
            for child in node.get("children", []):
                total += count_total_files(child)
            return total
        
        total_files = count_total_files(tree)
        
        return {
            "tree": tree,
            "total_files": total_files
        }
    except Exception as e:
        return {
            "tree": {
                "name": "AgentQMS",
                "path": "",
                "type": "directory",
                "file_count": 0,
                "children": [],
                "error": str(e)
            },
            "total_files": 0
        }
