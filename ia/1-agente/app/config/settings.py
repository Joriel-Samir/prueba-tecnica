"""Configuración tipada de la aplicación."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_base_url: str = "http://localhost:8000"
    provider_name: str = Field(default="mock", validation_alias="LLM_PROVIDER")
    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    session_ttl: int = Field(default=20, validation_alias="SESSION_TTL", gt=0)
    max_tool_iterations: int = Field(default=3, validation_alias="MAX_TOOL_ITERATIONS", gt=0)
    request_timeout_seconds: int = Field(default=10, validation_alias="REQUEST_TIMEOUT_SECONDS", gt=0)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
