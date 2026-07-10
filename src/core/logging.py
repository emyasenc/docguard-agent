import logging
from src.core.config import get_settings

settings = get_settings()

def setup_logging():
    """Configure logging for the application."""
    level = logging.DEBUG if settings.DEBUG else getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("docguard.log")
        ]
    )
    
    # Set third-party log levels
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 DocGuard logging initialized at {settings.LOG_LEVEL} level")