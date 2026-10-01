"""Casos de uso de herramientas y cliente REST del backend de actividades."""
from __future__ import annotations

import unicodedata
from datetime import datetime, time, timedelta
from typing import Any

import httpx

from ..config.settings import get_settings
from ..models.tools import (
    ActualizarActividadArgs,
    BuscarAsociadosArgs,
    ConsultarDisponibilidadArgs,
    CrearActividadArgs,
    EliminarActividadArgs,
    ListarActividadesArgs,
)
from ..utils.dates import BOGOTA, resolve_relative_date

_MODELS = {
    "listar_actividades": ListarActividadesArgs,
    "buscar_asociados": BuscarAsociadosArgs,
    "consultar_disponibilidad": ConsultarDisponibilidadArgs,
    "crear_actividad": CrearActividadArgs,
    "actualizar_actividad": ActualizarActividadArgs,
    "eliminar_actividad": EliminarActividadArgs,
}


def _settings():
    return get_settings()


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def validate_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    model = _MODELS.get(name)
    if model is None:
        raise ValueError(f"Tool no soportada: {name}")
    return model.model_validate(arguments).model_dump(exclude_none=True)


def _schema(model):
    result = model.model_json_schema()
    result.pop("title", None)
    return result


def get_tool_registry() -> list[dict[str, Any]]:
    descriptions = {
        "listar_actividades": "Lista actividades visibles en un rango.",
        "buscar_asociados": "Busca asociados por nombre, email o ciudad.",
        "consultar_disponibilidad": "Consulta disponibilidad por email o ciudad.",
        "crear_actividad": "Propone crear una actividad tras confirmación.",
        "actualizar_actividad": "Propone actualizar una actividad existente.",
        "eliminar_actividad": "Propone eliminar una actividad existente.",
    }
    return [{"type": "function", "function": {"name": name, "description": descriptions[name], "parameters": _schema(model)}} for name, model in _MODELS.items()]


def _get(path: str, token: str, params: dict[str, str] | None = None):
    settings = _settings()
    response = httpx.get(f"{settings.api_base_url}{path}", params=params, headers=_headers(token), timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    return response.json()


def listar_actividades(token: str, desde=None, hasta=None):
    params = {key: value for key, value in {"desde": desde, "hasta": hasta}.items() if value is not None}
    return {"actividades": _get("/api/actividades/", token, params)}


def buscar_asociados(token: str, query=None, ciudad=None):
    data = _get("/api/asociados/", token, {"search": query, "ciudad": ciudad})
    associates = data.get("results", []) if isinstance(data, dict) else data

    def norm(value):
        text = str(value or "").strip().casefold()
        return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")

    q, city = norm(query), norm(ciudad)
    filtered = [item for item in associates if (not city or norm(item.get("ciudad")) == city) and (not q or q in " ".join(norm(item.get(field)) for field in ("identificacion", "nombre", "apellidos", "email")))]
    return {"asociados": filtered}


def _parse_dt(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=BOGOTA)


def consultar_disponibilidad(token, asociado_email=None, ciudad=None, fecha=None, ventana=None):
    if not fecha:
        raise ValueError("Se requiere una fecha para consultar disponibilidad.")
    resolved = resolve_relative_date(fecha)
    try:
        day = datetime.fromisoformat(resolved.replace("Z", "+00:00")).date()
    except ValueError as error:
        raise ValueError("La fecha debe ser ISO o relativa soportada.") from error
    associates = buscar_asociados(token, asociado_email, ciudad)["asociados"]
    if asociado_email:
        associates = [a for a in associates if str(a.get("email", "")).casefold() == asociado_email.casefold()]
    if not associates:
        raise ValueError(f"No se encontraron asociados para {asociado_email or ciudad}.")
    activities = listar_actividades(token, day.isoformat(), day.isoformat())["actividades"]
    if isinstance(activities, dict):
        activities = activities.get("results", [])
    windows = {"mañana": (time(8), time(12)), "manana": (time(8), time(12)), "tarde": (time(13), time(18)), "noche": (time(18), time(23))}
    start_time, end_time = windows.get((ventana or "").casefold(), (time(0), time(23, 59, 59)))
    start_window = datetime.combine(day, start_time, tzinfo=BOGOTA)
    end_window = datetime.combine(day, end_time, tzinfo=BOGOTA)
    availability = []
    for associate in associates:
        conflicts = []
        for activity in activities:
            relation = activity.get("asociado")
            relation_id = relation.get("id") if isinstance(relation, dict) else relation
            if str(relation_id) != str(associate.get("id")):
                continue
            start, end = _parse_dt(activity.get("fecha_inicio")), _parse_dt(activity.get("fecha_fin"))
            if start and end and start < end_window and end > start_window:
                conflicts.append(activity)
        availability.append({"email": associate.get("email"), "nombre": associate.get("nombre"), "apellidos": associate.get("apellidos"), "ciudad": associate.get("ciudad"), "disponible": not conflicts, "conflictos": conflicts})
    return {"asociado": asociado_email, "ciudad": ciudad, "fecha": day.isoformat(), "ventana": ventana, "disponibilidad": availability}


def _associate_id(token, email):
    matches = buscar_asociados(token, query=email)["asociados"]
    exact = next((item for item in matches if str(item.get("email", "")).casefold() == email.casefold()), None)
    if not exact:
        raise ValueError(f"No se encontró el asociado {email}.")
    return int(exact["id"])


def crear_actividad(token, titulo, descripcion, fecha, duracion_minutos, asociado_email):
    start = _parse_dt(fecha)
    if not start:
        raise ValueError("La fecha de inicio debe ser ISO 8601.")
    payload = {"tipo": titulo, "descripcion": descripcion, "fecha_inicio": start.isoformat(), "fecha_fin": (start + timedelta(minutes=duracion_minutos)).isoformat(), "asociado": _associate_id(token, asociado_email)}
    settings = _settings()
    response = httpx.post(f"{settings.api_base_url}/api/actividades/", json=payload, headers=_headers(token), timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    return {"actividad": response.json()}


def actualizar_actividad(token, id, descripcion=None, fecha=None, duracion_minutos=None):
    settings = _settings()
    payload = {"descripcion": descripcion} if descripcion is not None else {}
    if fecha is not None or duracion_minutos is not None:
        response = httpx.get(f"{settings.api_base_url}/api/actividades/{id}/", headers=_headers(token), timeout=settings.request_timeout_seconds)
        response.raise_for_status()
        current = response.json()
        current_start, current_end = _parse_dt(current.get("fecha_inicio")), _parse_dt(current.get("fecha_fin"))
        start = _parse_dt(fecha) if fecha is not None else current_start
        duration = duracion_minutos or int((current_end - current_start).total_seconds() // 60)
        payload.update({"fecha_inicio": start.isoformat(), "fecha_fin": (start + timedelta(minutes=duration)).isoformat()})
    response = httpx.patch(f"{settings.api_base_url}/api/actividades/{id}/", json=payload, headers=_headers(token), timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    return {"actividad": response.json()}


def eliminar_actividad(token, id):
    settings = _settings()
    response = httpx.delete(f"{settings.api_base_url}/api/actividades/{id}/", headers=_headers(token), timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    return {"deleted": True, "id": id}


def execute_tool_call(name, arguments, token):
    try:
        args = validate_tool_call(name, arguments)
        handlers = {"listar_actividades": listar_actividades, "buscar_asociados": buscar_asociados, "consultar_disponibilidad": consultar_disponibilidad, "crear_actividad": crear_actividad, "actualizar_actividad": actualizar_actividad, "eliminar_actividad": eliminar_actividad}
        return handlers[name](token, **args)
    except Exception as error:  # noqa: BLE001 - tool failures are returned to the agent
        return {"error": str(error)}
