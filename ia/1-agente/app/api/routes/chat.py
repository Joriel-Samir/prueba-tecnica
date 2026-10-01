"""Rutas HTTP del chat; delegan la lógica al servicio de agente."""
from __future__ import annotations

import json
from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ...models.chat import AgentTurn, ChatRequest, ConfirmRequest
from ...services.session_manager import SessionManager
from ..dependencies import get_session_manager

router = APIRouter(prefix="/api", tags=["agent"])
SessionManagerDep = Annotated[SessionManager, Depends(get_session_manager)]


@router.post("/chat", response_model=None, response_class=StreamingResponse)
def chat(request: ChatRequest, sessions: SessionManagerDep) -> StreamingResponse:
    session = sessions.get(request.session_id, request.token)

    def event_stream() -> Generator[str, None, None]:
        yield f"data: {json.dumps({'status': 'thinking'}, ensure_ascii=False)}\n\n"
        result = session.handle_message(request.message, request.session_id)
        validated = AgentTurn.model_validate(result)
        yield f"data: {validated.model_dump_json(exclude_none=True)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/chat/confirm", response_model=AgentTurn)
def confirm_action(request: ConfirmRequest, sessions: SessionManagerDep) -> dict:
    session = sessions.get(request.session_id, request.token)
    return session.confirm_action(request.session_id, confirmed=request.confirmed)
