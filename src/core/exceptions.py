"""
Custom exceptions for DocGuard.
"""

from fastapi import HTTPException, status

class DocGuardError(Exception):
    """Base exception for all DocGuard errors."""
    pass

class DataHubConnectionError(DocGuardError):
    """Raised when DataHub is unreachable."""
    pass

class GitHubAPIError(DocGuardError):
    """Raised when GitHub API returns an error."""
    pass

class ValidationError(DocGuardError):
    """Raised when validation fails."""
    pass

def raise_datahub_error(detail: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "error": "DATAHUB_UNAVAILABLE",
            "message": detail,
            "suggestion": "Check your DataHub endpoint and token."
        }
    )

def raise_github_error(detail: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail={
            "error": "GITHUB_API_ERROR",
            "message": detail,
            "suggestion": "Check your GitHub token and permissions."
        }
    )