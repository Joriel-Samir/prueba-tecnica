"""Dependencias compartidas de la API."""
from __future__ import annotations

from functools import lru_cache

from ..config.settings import Settings, get_settings
from ..providers.llm import GeminiProvider, LLMProvider, MockProvider, OpenAIProvider
from ..services.session_manager import SessionManager


def build_provider(settings: Settings) -> LLMProvider:
    name = settings.provider_name.lower()
    if name == "gemini":
        return GeminiProvider(api_key=settings.gemini_api_key)
    if name == "openai":
        return OpenAIProvider(api_key=settings.openai_api_key)
    return MockProvider()


@lru_cache
def get_session_manager() -> SessionManager:
    settings = get_settings()
    return SessionManager(
        provider_factory=lambda: build_provider(settings),
        session_ttl_minutes=settings.session_ttl,
    )
