"""Gestion de sesiones HTTP fuera de las rutas FastAPI."""
from __future__ import annotations

import time
from collections.abc import Callable

from fastapi import HTTPException

from ..providers.llm import LLMProvider
from .agent import AgentSession


class SessionManager:
    def __init__(self, provider_factory: Callable[[], LLMProvider], session_ttl_minutes: int):
        self._provider_factory = provider_factory
        self._session_ttl_minutes = session_ttl_minutes
        self._sessions: dict[str, AgentSession] = {}
        self._last_seen: dict[str, float] = {}

    def get(self, session_id: str, token: str) -> AgentSession:
        now = time.monotonic()
        last_seen = self._last_seen.get(session_id)
        if last_seen is not None and now - last_seen > self._session_ttl_minutes * 60:
            self._sessions.pop(session_id, None)
            self._last_seen.pop(session_id, None)

        session = self._sessions.get(session_id)
        if session is None:
            session = AgentSession(provider=self._provider_factory(), user_token=token)
            self._sessions[session_id] = session
        elif session.user_token != token:
            raise HTTPException(status_code=403, detail="La sesion no pertenece a este usuario.")
        self._last_seen[session_id] = now
        return session
