"""Punto de entrada FastAPI para el servicio del agente IA 1.

Endpoints:
  GET  /health            — chequeo de salud
  POST /api/chat          — envia un mensaje del usuario; devuelve un stream SSE
  POST /api/chat/confirm  — confirma o cancela una accion de escritura pendiente
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .agent import AgentSession
from .config import API_BASE_URL, PROVIDER_NAME
from .models import ChatRequest, ConfirmRequest
from .provider import GeminiProvider, LLMProvider, MockProvider, OpenAIProvider

# Cargar .env desde la raiz del proyecto (un nivel arriba de app/)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)


def build_provider() -> LLMProvider:
    """Instancia el proveedor LLM seleccionado por la variable de entorno LLM_PROVIDER."""
    name = (PROVIDER_NAME or "mock").lower()
    if name == "gemini":
        return GeminiProvider()
    if name == "openai":
        return OpenAIProvider()
    return MockProvider()


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

# Almacen de sesiones en memoria (session_id -> AgentSession)
# En produccion esto deberia estar respaldado por Redis con un TTL.
agent_store: dict[str, AgentSession] = {}


def _get_or_create_session(session_id: str, token: str) -> AgentSession:
    if session_id not in agent_store:
        agent_store[session_id] = AgentSession(
            provider=build_provider(), user_token=token
        )
    return agent_store[session_id]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health", tags=["ops"])
def health() -> dict[str, str]:
    """Chequeo de salud — retorna el proveedor actual y la URL base de la API."""
    return {"status": "ok", "provider": PROVIDER_NAME, "api_base_url": API_BASE_URL}


@app.post("/api/chat", tags=["agent"])
def chat(request: ChatRequest) -> StreamingResponse:
    """Envia un mensaje de usuario y recibe un stream de Server-Sent Events.

    El stream emite dos eventos:
      1. ``{"status": "thinking"}`` — de inmediato, para indicar que inicio el proceso.
      2. El resultado completo del turno del agente.

    El cliente debe proporcionar un JWT valido en ``token``; este se reenvia
    intacto a la API del backend para que el agente siempre opere con los
    permisos del usuario.
    """
    session = _get_or_create_session(request.session_id, request.token)

    def event_stream() -> AsyncGenerator[str, None]:
        # Senal de pensamiento
        yield f"data: {json.dumps({'status': 'thinking'}, ensure_ascii=False)}\n\n"
        # Resultado completo
        result = session.handle_message(request.message, request.session_id)
        yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/chat/confirm", tags=["agent"])
def confirm_action(request: ConfirmRequest) -> dict:
    """Confirma o cancela la accion de escritura pendiente mas reciente de una sesion.

    Despues de que ``/api/chat`` retorna ``needs_confirmation``, el cliente debe
    llamar a este endpoint con ``confirmed=true`` para ejecutar la escritura, o
    ``confirmed=false`` para cancelarla.
    """
    session = _get_or_create_session(request.session_id, request.token)
    return session.confirm_action(request.session_id, confirmed=request.confirmed)
