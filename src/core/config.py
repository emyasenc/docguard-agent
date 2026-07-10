import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "DocGuard"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    PORT: int = 8000
    
    # DataHub
    DATAHUB_ENDPOINT: str = ""
    DATAHUB_TOKEN: str = ""
    
    # GitHub
    GITHUB_TOKEN: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    
    # Agent Settings
    AGENT_MODE: str = "both"
    MAX_ISSUES_PER_REPORT: int = 50
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = {
    "env_file": ".env",
    "case_sensitive": True,
    "extra": "ignore"
    }
    
    def validate_production(self):
        """Ensure required variables are set in production."""
        if self.ENVIRONMENT == "production":
            if not self.DATAHUB_ENDPOINT:
                raise ValueError("DATAHUB_ENDPOINT is required in production")
            if not self.DATAHUB_TOKEN:
                raise ValueError("DATAHUB_TOKEN is required in production")
            if not self.GITHUB_TOKEN:
                raise ValueError("GITHUB_TOKEN is required in production")

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production()
    return settings