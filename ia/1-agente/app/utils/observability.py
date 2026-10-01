"""Registro estructurado / observabilidad para el agente IA 1.

Cada turno del agente se registra como una sola linea JSON en stdout para que
pueda ser ingerida por cualquier agregador de logs. El registro incluye:
  - timestamp   (ISO-8601, America/Bogota)
  - session_id
  - message_preview  (primeros 100 caracteres del mensaje del usuario)
  - tools_invoked    (lista de nombres de herramientas ejecutadas en este turno)
  - latency_ms       (tiempo real de ejecucion del turno en milisegundos)
  - tokens_in / tokens_out  (desde la metadata del LLM cuando este disponible)
  - status           (ok | needs_confirmation | cancelled | error)
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

_TZ_BOGOTA = ZoneInfo("America/Bogota")

# Configuramos el handler raiz una vez; llamadas subsecuentes a get_logger()
# retornan el mismo logger para no duplicar handlers al reimportar el modulo.
_logger: logging.Logger | None = None


def get_logger() -> logging.Logger:
    """Retorna (y configura perezosamente) el logger del agente."""
    global _logger
    if _logger is not None:
        return _logger

    logger = logging.getLogger("agent")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        # Formateador plano — nosotros emitimos JSON manualmente en log_turn()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.propagate = False

    _logger = logger
    return _logger


def log_turn(
    *,
    session_id: str,
    user_message: str,
    tool_calls_invoked: list[str],
    results: list[dict[str, Any]],
    latency_ms: float,
    tokens_in: int = 0,
    tokens_out: int = 0,
    status: str = "ok",
) -> None:
    """Emite una sola linea de log JSON para un turno del agente.

    Args:
        session_id: Identificador de la sesion de conversacion.
        user_message: La entrada de texto cruda del usuario.
        tool_calls_invoked: Nombres de las herramientas que fueron llamadas.
        results: Diccionarios de resultados devueltos por execute_tool_call().
        latency_ms: Duracion total en milisegundos.
        tokens_in: Tokens de entrada reportados por el LLM (0 si no aplica).
        tokens_out: Tokens de salida reportados por el LLM (0 si no aplica).
        status: Cadena de texto con el estado final del turno.
    """
    record = {
        "timestamp": datetime.now(tz=_TZ_BOGOTA).isoformat(),
        "session_id": session_id,
        "message_preview": user_message[:100],
        "tools_invoked": tool_calls_invoked,
        "latency_ms": round(latency_ms, 2),
        "tokens": {"in": tokens_in, "out": tokens_out},
        "status": status,
        "tool_errors": [r.get("error") for r in results if r.get("error")],
    }
    get_logger().info(json.dumps(record, ensure_ascii=False, default=str))
