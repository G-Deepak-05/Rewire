"""
Application configuration — loaded from environment variables via pydantic-settings.
API keys are read from .env (gitignored) and never hardcoded.
"""

from functools import lru_cache
from typing import Any, Literal

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ──────────────────────────────────────────────────────────
    app_name: str = "Rewire"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # ─── Security ─────────────────────────────────────────────────────────────
    secret_key: str = "supersecretkey-change-in-production-min-32chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # ─── Database ─────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://rewire:rewire@localhost:5432/rewire"

    # ─── Redis ────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ─── Celery ───────────────────────────────────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ─── AI / LLM ────────────────────────────────────────────────────────────
    # The API key is loaded from .env via LLM_API_KEY — never in source
    llm_api_key: str = ""
    llm_api_base: str | None = None
    llm_model: str = "openrouter/google/gemini-2.5-flash"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096

    # ─── Email / Mailpit ──────────────────────────────────────────────────────
    mailpit_host: str = "localhost"
    mailpit_port: int = 1025
    email_from: str = "noreply@rewire.local"

    # ─── CORS ─────────────────────────────────────────────────────────────────
    allowed_origins: Any = ["http://localhost:3000", "http://localhost:8000"]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | list) -> list[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",")]
        return v

    # ─── Rate Limiting ────────────────────────────────────────────────────────
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 20

    # ─── Monitoring ───────────────────────────────────────────────────────────
    prometheus_enabled: bool = True

    @field_validator("secret_key", mode="after")
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo) -> str:
        """Enforce strong secret key in production."""
        env = info.data.get("environment", "development")
        if env == "production":
            placeholder_indicators = ["supersecretkey", "change-in-production"]
            if any(ind in v.lower() for ind in placeholder_indicators) or len(v) < 32:
                raise ValueError(
                    "SECURITY: `secret_key` must be set to a strong random value in production."
                )
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
