"""
Issue models for DocGuard.
Defines the structure of issues found by agents.
"""

from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Severity(str, Enum):
    """Severity levels for issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class IssueType(str, Enum):
    """Types of issues that can be found."""
    # Code issues
    UNKNOWN_TABLE = "unknown_table"
    UNKNOWN_COLUMN = "unknown_column"
    DEPRECATED_FUNCTION = "deprecated_function"
    DEPRECATED_PACKAGE = "deprecated_package"
    MISSING_WHERE = "missing_where"
    SELECT_STAR = "select_star"
    SQL_INJECTION = "sql_injection"
    
    # Documentation issues
    MISSING_SECTION = "missing_section"
    DEPRECATED_TERM = "deprecated_term"
    MISSING_TABLE = "missing_table"
    
    # General issues
    SYNTAX_ERROR = "syntax_error"
    SECURITY_ISSUE = "security_issue"
    PERFORMANCE_ISSUE = "performance_issue"

class Issue(BaseModel):
    """A single issue found by an agent."""
    
    type: str
    """Type of issue (from IssueType enum)."""
    
    message: str
    """Human-readable description of the issue."""
    
    suggestion: str
    """Suggested fix for the issue."""
    
    severity: str
    """Severity level (from Severity enum)."""
    
    location: Optional[int] = None
    """Character position where the issue was found (0-indexed)."""
    
    line: Optional[int] = None
    """Line number where the issue was found (1-indexed)."""
    
    column: Optional[int] = None
    """Column number where the issue was found (1-indexed)."""
    
    file_path: Optional[str] = None
    """Path to the file where the issue was found."""
    
    context: Optional[str] = None
    """Code snippet or context around the issue."""
    
    metadata: Optional[dict] = None
    """Additional metadata about the issue (e.g., table name, function name)."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "unknown_table",
                "message": "Table 'fake_table' not found in DataHub metadata.",
                "suggestion": "Check the spelling or verify the table exists in DataHub.",
                "severity": "high",
                "location": 14,
                "line": 3,
                "column": 12,
                "file_path": "src/queries/analysis.sql",
                "context": "SELECT * FROM fake_table WHERE id = 1",
                "metadata": {"table_name": "fake_table"}
            }
        }

class IssueList(BaseModel):
    """A list of issues."""
    
    issues: List[Issue]
    """List of issues found."""
    
    total: int
    """Total number of issues."""
    
    file_path: Optional[str] = None
    """Path to the file that was checked."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "issues": [
                    {
                        "type": "unknown_table",
                        "message": "Table 'fake_table' not found in DataHub metadata.",
                        "suggestion": "Check the spelling or verify the table exists in DataHub.",
                        "severity": "high",
                        "location": 14,
                        "line": 3,
                        "column": 12
                    }
                ],
                "total": 1,
                "file_path": "src/queries/analysis.sql"
            }
        }

class IssueSummary(BaseModel):
    """Summary of issues found."""
    
    total_issues: int
    """Total number of issues."""
    
    critical: int
    """Number of critical issues."""
    
    high: int
    """Number of high-severity issues."""
    
    medium: int
    """Number of medium-severity issues."""
    
    low: int
    """Number of low-severity issues."""
    
    info: int
    """Number of info-level issues."""
    
    by_type: dict
    """Count of issues by type."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_issues": 5,
                "critical": 1,
                "high": 2,
                "medium": 1,
                "low": 1,
                "info": 0,
                "by_type": {
                    "unknown_table": 2,
                    "missing_where": 1,
                    "select_star": 2
                }
            }
        }