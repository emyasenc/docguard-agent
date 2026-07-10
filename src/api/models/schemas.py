"""
Pydantic schemas for DocGuard API.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    timestamp: str
    environment: str

class Issue(BaseModel):
    """A single issue found by an agent."""
    type: str
    message: str
    suggestion: str
    severity: str
    location: Optional[int] = None

class LintRequest(BaseModel):
    """Request to lint code."""
    content: str
    file_path: str
    repo: Optional[str] = None
    ref: Optional[str] = "main"

class LintResponse(BaseModel):
    """Response from linting."""
    issues: List[Issue]
    total: int
    file_path: str

class WebhookPayload(BaseModel):
    """Generic webhook payload."""
    event: str
    repo: Optional[str] = None
    pr_number: Optional[int] = None
    payload: Dict[str, Any]

class PRCommentResponse(BaseModel):
    """Response from posting a PR comment."""
    status: str
    comment_url: Optional[str] = None
    issues_found: int