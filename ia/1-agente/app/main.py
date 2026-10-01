"""Composición de la aplicación FastAPI."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.dependencies import build_provider
from .api.routes import chat
from .config.settings import Settings, get_settings
from .models.system import HealthResponse

app = FastAPI(
    title="IA 1 — Agente de actividades Ihungo",
    description="Agente conversacional sobre la API de actividades con function calling.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)


@app.get("/health", tags=["ops"], response_model=HealthResponse)
def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    return HealthResponse(
        status="ok",
        provider=settings.provider_name,
        api_base_url=settings.api_base_url,
    )


# Compatibilidad para el evaluador y consumidores existentes.
__all__ = ["app", "build_provider"]
