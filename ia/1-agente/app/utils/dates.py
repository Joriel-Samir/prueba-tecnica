"""Resolucion determinista de fechas relativas en la zona horaria del negocio."""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

BOGOTA = ZoneInfo("America/Bogota")
_WEEKDAYS = {
    "lunes": 0,
    "martes": 1,
    "miércoles": 2,
    "miercoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sábado": 5,
    "sabado": 5,
    "domingo": 6,
}


def _next_weekday(today: date, weekday: int) -> date:
    days_ahead = (weekday - today.weekday()) % 7
    return today + timedelta(days=days_ahead or 7)


def resolve_relative_date(value: str, reference: datetime | None = None) -> str:
    """Sustituye expresiones relativas por fechas ISO sin inventar la hora."""
    reference = reference or datetime.now(tz=BOGOTA)
    today = reference.astimezone(BOGOTA).date()
    text = value.strip().lower()

    if text == "esta semana":
        monday = today - timedelta(days=today.weekday())
        return monday.isoformat()
    if text == "hoy":
        return today.isoformat()
    if text == "mañana" or text == "manana":
        return (today + timedelta(days=1)).isoformat()
    if text == "pasado mañana" or text == "pasado manana":
        return (today + timedelta(days=2)).isoformat()

    weekday_match = re.fullmatch(r"(?:el\s+)?([a-záéíóú]+)", text)
    if weekday_match and weekday_match.group(1) in _WEEKDAYS:
        return _next_weekday(today, _WEEKDAYS[weekday_match.group(1)]).isoformat()

    return value


def is_precise_date(value: str) -> bool:
    """Indica si el valor es ISO o una expresión relativa soportada."""
    resolved = resolve_relative_date(value)
    if resolved != value:
        return True
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def resolve_range(
    desde: str | None,
    hasta: str | None,
    reference: datetime | None = None,
) -> tuple[str | None, str | None]:
    """Normaliza rangos de consulta, incluido ``esta semana``."""
    reference = reference or datetime.now(tz=BOGOTA)
    today = reference.astimezone(BOGOTA).date()
    if desde and desde.strip().lower() == "esta semana":
        monday = today - timedelta(days=today.weekday())
        return monday.isoformat(), (monday + timedelta(days=6)).isoformat()
    return (
        resolve_relative_date(desde, reference) if desde else None,
        resolve_relative_date(hasta, reference) if hasta else None,
    )
