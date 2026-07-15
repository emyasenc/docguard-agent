"""
Health check endpoint for DocGuard.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
from src.core.config import get_settings

router = APIRouter()
settings = get_settings()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.ENVIRONMENT
    }