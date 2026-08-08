from enum import Enum

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application execution environment."""

    development = "development"
    staging = "staging"
    production = "production"


class Settings(BaseSettings):
    """Application configuration - loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Application Environment ---
    app_env: Environment
    port: int

    # --- Database ---
    database_url: str

    # --- Secrets (Never have defaults) ---
    jwt_secret: str

    # --- Logging ---
    log_level: str = "info"

    @field_validator("port")
    @classmethod
    def validate_port(cls, value: int) -> int:
        """Validate that PORT is in the valid TCP port range."""
        if value < 1 or value > 65535:
            raise ValueError("PORT must be an integer between 1 and 65535.")
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Validate that DATABASE_URL is not empty."""
        if not value.strip():
            raise ValueError("DATABASE_URL must be set.")
        return value

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: str) -> str:
        """Validate that JWT_SECRET meets minimum length requirement."""
        if len(value) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long.")
        return value

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == Environment.production

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == Environment.development

    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.app_env == Environment.staging


def load_settings() -> Settings:
    """Load and validate settings from environment.

    Raises:
        RuntimeError: If configuration is invalid or missing required values.
    """
    try:
        return Settings()
    except Exception as exc:
        raise RuntimeError(
            f"Invalid configuration: {exc}. "
            "Ensure all required variables are set: APP_ENV, PORT, DATABASE_URL, JWT_SECRET"
        ) from exc
