from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ArtifactMetadata(BaseModel):
    """Pydantic model for standard artifact metadata (Frontmatter)."""
    type: str = Field(..., description="Type of the artifact (e.g., implementation_plan, assessment)")
    title: str = Field(..., description="Human-readable title")
    status: str = Field(..., description="Current status (e.g., draft, review_needed, active)")
    category: Optional[str] = Field(None, description="Category for organization")
    tags: List[str] = Field(default_factory=list, description="List of tags")
    date: Optional[str] = Field(None, description="Date string")
    
    # Allow extra fields for flexibility
    class Config:
        extra = "allow"

class ValidationViolation(BaseModel):
    """Represents a single compliance violation."""
    rule_id: str
    message: str
    severity: str = "error" # error, warning, info
    field: Optional[str] = None
    line: Optional[int] = None

class ValidationReport(BaseModel):
    """Report for a single file's compliance status."""
    file_path: str
    is_compliant: bool
    violations: List[ValidationViolation]
    metadata: Optional[dict] = None
