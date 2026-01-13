"""
CANOPI Backend Configuration

Uses Pydantic Settings to load configuration from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://canopi:canopi_dev_password@localhost:5432/canopi"
    TIMESCALE_URL: str = "postgresql://timescale:timescale_dev_password@localhost:5433/timescale"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # API Keys
    MAPBOX_API_KEY: str = ""
    CAISO_API_KEY: str = ""
    NOAA_API_KEY: str = ""
    EIA_API_KEY: str = ""

    # Gurobi
    GUROBI_HOME: str = "/opt/gurobi1100/linux64"
    GRB_LICENSE_FILE: str = "/opt/gurobi/gurobi.lic"

    # Application
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "test_secret_key_for_development_only"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
