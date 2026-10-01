"""DTOs de entrada y salida HTTP."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = Field("default", min_length=1)
    token: str = Field(..., min_length=1)


class ConfirmRequest(BaseModel):
    session_id: str = Field("default", min_length=1)
    token: str = Field(..., min_length=1)
    confirmed: bool


class ToolResult(BaseModel):
    tool: str
    ok: bool
    result: dict[str, Any] | None = None
    error: str | None = None


class AgentTurn(BaseModel):
    status: Literal["ok", "needs_confirmation", "needs_input", "cancelled", "error"]
    content: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    results: list[ToolResult] = Field(default_factory=list)
