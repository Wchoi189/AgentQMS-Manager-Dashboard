import glob
import os
from datetime import datetime
from typing import Any

import frontmatter
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/artifacts", tags=["artifacts"])

# Configuration
# Resolve paths relative to project root
# This file is at: backend/routes/artifacts.py
# Project root is: backend/../ (one level up from backend/)
_routes_dir = os.path.dirname(os.path.abspath(__file__))  # backend/routes/
_backend_dir = os.path.dirname(_routes_dir)  # backend/
_project_root = os.path.dirname(_backend_dir)  # project root/

def get_artifacts_root():
    """Get artifacts root directory based on current DEMO_MODE setting."""
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    
    # Try the configured path first
    artifacts_rel = "demo_data/artifacts" if demo_mode else "docs/artifacts"
    artifacts_root = os.path.join(_project_root, artifacts_rel)
    
    # Auto-detect: if configured path doesn't exist, try the alternative
    if not os.path.exists(artifacts_root):
        alt_artifacts_rel = "docs/artifacts" if demo_mode else "demo_data/artifacts"
        alt_artifacts_root = os.path.join(_project_root, alt_artifacts_rel)
        if os.path.exists(alt_artifacts_root):
            print(f"INFO: DEMO_MODE={demo_mode} but using alternative path: {alt_artifacts_root}")
            return alt_artifacts_root
    
    return artifacts_root

# Default ARTIFACTS_ROOT (can be overridden per request)
ARTIFACTS_ROOT = get_artifacts_root()
ARTIFACT_TYPES = {
    "implementation_plan": "implementation_plans",
    "assessment": "assessments",
    "audit": "audits",
    "bug_report": "bug_reports",
    "design": "design_documents"  # Add design_documents support
}

# Models
class ArtifactBase(BaseModel):
    type: str
    title: str
    status: str = "draft"
    category: str | None = None
    tags: list[str] = []

class ArtifactCreate(ArtifactBase):
    content: str

class ArtifactUpdate(BaseModel):
    content: str | None = None
    frontmatter_updates: dict[str, Any] | None = None

class ArtifactResponse(ArtifactBase):
    id: str
    path: str
    created_at: str | None = None
    content: str | None = None # Only for detail view

class ArtifactListResponse(BaseModel):
    items: list[ArtifactResponse]
    total: int

# Helpers
def get_artifact_path(artifact_type: str, artifact_id: str) -> str:
    subdir = ARTIFACT_TYPES.get(artifact_type)
    if not subdir:
        raise ValueError(f"Invalid artifact type: {artifact_type}")
    # Assuming ID matches filename without extension, or we search for it
    # The ID in spec is "2025-12-08_1430_plan_dashboard-integration"
    # The file is "2025-12-08_1430_plan_dashboard-integration.md"
    artifacts_root = get_artifacts_root()
    return os.path.join(artifacts_root, subdir, f"{artifact_id}.md")

def parse_artifact(file_path: str, include_content: bool = False) -> ArtifactResponse:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    post = frontmatter.load(file_path)
    filename = os.path.basename(file_path)
    artifact_id = os.path.splitext(filename)[0]

    # Extract metadata
    metadata = post.metadata

    return ArtifactResponse(
        id=artifact_id,
        path=file_path,
        type=metadata.get("type", "unknown"),
        title=metadata.get("title", "Untitled"),
        status=metadata.get("status", "draft"),
        category=metadata.get("category"),
        tags=metadata.get("tags", []),
        created_at=metadata.get("date"), # Or parse from filename
        content=post.content if include_content else None
    )

# Endpoints
@router.get("", response_model=ArtifactListResponse)
async def list_artifacts(
    type: str | None = None,
    status: str | None = None,
    limit: int = 50
):
    """List artifacts with filtering."""
    items = []
    
    # Get current artifacts root (check DEMO_MODE at request time)
    artifacts_root = get_artifacts_root()
    
    # Debug logging
    if not os.path.exists(artifacts_root):
        demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        demo_mode_env = os.getenv("DEMO_MODE", "not set")
        print(f"WARNING: Artifacts root does not exist: {artifacts_root}")
        print(f"DEMO_MODE env var: '{demo_mode_env}' (interpreted as: {demo_mode})")
        print(f"Expected path: {'demo_data/artifacts' if demo_mode else 'docs/artifacts'}")
        
        # Try the alternative path
        alt_artifacts_root = os.path.join(_project_root, "demo_data/artifacts" if not demo_mode else "docs/artifacts")
        if os.path.exists(alt_artifacts_root):
            print(f"INFO: Found artifacts at alternative path: {alt_artifacts_root}")
            artifacts_root = alt_artifacts_root
        else:
            return {"items": [], "total": 0}

    # Determine directories to search
    subdirs = [ARTIFACT_TYPES[type]] if type and type in ARTIFACT_TYPES else ARTIFACT_TYPES.values()

    for subdir in subdirs:
        search_path = os.path.join(artifacts_root, subdir, "*.md")
        files = glob.glob(search_path)
        
        if not files:
            # Try alternative: search all subdirectories if specific one is empty
            alt_path = os.path.join(artifacts_root, "**", "*.md")
            files = glob.glob(alt_path, recursive=True)
            # Filter by type if specified
            if type:
                files = [f for f in files if subdir in f]

        for f in files:
            try:
                artifact = parse_artifact(f, include_content=False)

                # Filter by status
                if status and artifact.status != status:
                    continue
                
                # Filter by type if specified (double-check)
                if type and artifact.type != type:
                    continue

                items.append(artifact)
            except Exception as e:
                print(f"Error parsing {f}: {e}")
                continue

    # Sort by ID (descending -> newest first)
    items.sort(key=lambda x: x.id, reverse=True)

    return {
        "items": items[:limit],
        "total": len(items)
    }

@router.get("/{id}", response_model=ArtifactResponse)
async def get_artifact(id: str):
    """Get a single artifact by ID."""
    # We need to find the file because ID doesn't strictly tell us the type/folder
    # Optimization: Try to guess type from ID if possible, or search all folders
    artifacts_root = get_artifacts_root()

    found_path = None
    for subdir in ARTIFACT_TYPES.values():
        potential_path = os.path.join(artifacts_root, subdir, f"{id}.md")
        if os.path.exists(potential_path):
            found_path = potential_path
            break

    if not found_path:
        raise HTTPException(status_code=404, detail="Artifact not found")

    try:
        return parse_artifact(found_path, include_content=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=ArtifactResponse)
async def create_artifact(artifact: ArtifactCreate):
    """Create a new artifact."""
    if artifact.type not in ARTIFACT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid artifact type. Must be one of {list(ARTIFACT_TYPES.keys())}")

    # Generate ID and Filename
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H%M")
    # Simple slug generation
    slug = artifact.title.lower().replace(" ", "-").replace("/", "-")
    artifact_id = f"{timestamp}_{artifact.type}_{slug}"

    filename = f"{artifact_id}.md"
    subdir = ARTIFACT_TYPES[artifact.type]
    artifacts_root = get_artifacts_root()
    file_path = os.path.join(artifacts_root, subdir, filename)

    # Prepare content with frontmatter
    metadata = artifact.dict(exclude={"content"}, exclude_none=True)
    metadata["date"] = now.strftime("%Y-%m-%d %H:%M (KST)") # Mocking KST for now

    content_body = artifact.content
    # Check if content already has frontmatter and parse it
    if artifact.content.strip().startswith("---"):
        try:
            existing_post = frontmatter.loads(artifact.content)
            # Merge metadata: content metadata overrides form metadata if present
            if existing_post.metadata:
                metadata.update(existing_post.metadata)
            content_body = existing_post.content
        except Exception:
            # If parsing fails, treat as raw content
            pass

    post = frontmatter.Post(content_body, **metadata)

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))

        return parse_artifact(file_path, include_content=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}", response_model=ArtifactResponse)
async def update_artifact(id: str, update: ArtifactUpdate):
    """Update an existing artifact."""
    # Find file
    artifacts_root = get_artifacts_root()
    found_path = None
    for subdir in ARTIFACT_TYPES.values():
        potential_path = os.path.join(artifacts_root, subdir, f"{id}.md")
        if os.path.exists(potential_path):
            found_path = potential_path
            break

    if not found_path:
        raise HTTPException(status_code=404, detail="Artifact not found")

    try:
        post = frontmatter.load(found_path)

        # Update content
        if update.content is not None:
            post.content = update.content

        # Update metadata
        if update.frontmatter_updates:
            post.metadata.update(update.frontmatter_updates)
            post.metadata["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M (KST)")

        with open(found_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))

        return parse_artifact(found_path, include_content=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
async def delete_artifact(id: str):
    """Delete (archive) an artifact."""
    # Find file
    artifacts_root = get_artifacts_root()
    found_path = None
    for subdir in ARTIFACT_TYPES.values():
        potential_path = os.path.join(artifacts_root, subdir, f"{id}.md")
        if os.path.exists(potential_path):
            found_path = potential_path
            break

    if not found_path:
        raise HTTPException(status_code=404, detail="Artifact not found")

    try:
        # Archive instead of delete
        archive_dir = os.path.join(artifacts_root, "archive")
        os.makedirs(archive_dir, exist_ok=True)

        filename = os.path.basename(found_path)
        dest_path = os.path.join(archive_dir, filename)

        os.rename(found_path, dest_path)
        return {"success": True, "message": "Artifact archived", "path": dest_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
