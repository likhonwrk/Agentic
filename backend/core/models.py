"""
GitHub MCP Models
Data models for GitHub MCP server
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class Repository(BaseModel):
    """GitHub repository model"""
    owner: str
    name: str
    description: Optional[str] = None
    private: bool = False
    url: str
    default_branch: str = "main"
    created_at: datetime
    updated_at: datetime

class Issue(BaseModel):
    """GitHub issue model"""
    number: int
    title: str
    body: Optional[str] = None
    state: str = "open"
    labels: List[str] = []
    assignees: List[str] = []
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

class PullRequest(BaseModel):
    """GitHub pull request model"""
    number: int
    title: str
    body: Optional[str] = None
    state: str = "open"
    base: str
    head: str
    mergeable: Optional[bool] = None
    merged: bool = False
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None

class CodeAnalysis(BaseModel):
    """Code analysis results"""
    language: str
    loc: int
    complexity: float
    maintainability: float
    coverage: Optional[float] = None
    issues: List[Dict[str, Any]] = []

class SecurityFindings(BaseModel):
    """Security analysis findings"""
    vulnerabilities: List[Dict[str, Any]] = []
    dependencies: List[Dict[str, Any]] = []
    secrets: List[Dict[str, Any]] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)
