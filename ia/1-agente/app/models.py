"""Modelos Pydantic de peticion/respuesta para la API del agente IA 1."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Una sola invocacion de herramienta propuesta o ejecutada por el agente."""

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    """Payload para POST /api/chat."""

    message: str = Field(..., description="Mensaje del usuario en lenguaje natural.")
    session_id: str = Field("default", description="Identificador de sesion de conversacion.")
    token: str = Field(..., description="Token JWT reenviado a la API del backend.")


class ConfirmRequest(BaseModel):
    """Payload para POST /api/chat/confirm."""

    session_id: str = Field("default", description="Sesion cuyas escrituras pendientes se van a resolver.")
    token: str = Field(..., description="Token JWT para reautenticacion.")
    confirmed: bool = Field(..., description="True para ejecutar; False para cancelar.")


class ToolResult(BaseModel):
    """Resultado de una sola ejecucion de herramienta."""

    tool: str
    ok: bool
    result: dict[str, Any] | None = None
    error: str | None = None


class AgentTurn(BaseModel):
    """Respuesta completa del turno del agente."""

    status: Literal["ok", "needs_confirmation", "needs_input", "cancelled", "error"]
    content: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    results: list[ToolResult] = Field(default_factory=list)
