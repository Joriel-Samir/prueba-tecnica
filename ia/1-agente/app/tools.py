from __future__ import annotations

import json
import os
from typing import Any

import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _build_tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "listar_actividades",
                "description": "Lista actividades visibles para el usuario en un rango de fechas.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "desde": {"type": "string", "description": "Fecha inicial ISO o texto relativo."},
                        "hasta": {"type": "string", "description": "Fecha final ISO o texto relativo."},
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "buscar_asociados",
                "description": "Busca asociados por nombre, email o ciudad.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "ciudad": {"type": "string"},
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "consultar_disponibilidad",
                "description": "Consulta la disponibilidad de un asociado en una fecha o rango.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asociado_email": {"type": "string"},
                        "fecha": {"type": "string"},
                        "ventana": {"type": "string"},
                    },
                    "required": ["asociado_email"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "crear_actividad",
                "description": "Crea una actividad tras confirmación del usuario.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "titulo": {"type": "string"},
                        "descripcion": {"type": "string"},
                        "fecha": {"type": "string"},
                        "duracion_minutos": {"type": "integer"},
                        "asociado_email": {"type": "string"},
                    },
                    "required": ["titulo", "descripcion", "fecha", "duracion_minutos", "asociado_email"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "actualizar_actividad",
                "description": "Actualiza parcialmente una actividad existente.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "descripcion": {"type": "string"},
                        "fecha": {"type": "string"},
                        "duracion_minutos": {"type": "integer"},
                    },
                    "required": ["id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "eliminar_actividad",
                "description": "Elimina una actividad existente.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                    },
                    "required": ["id"],
                },
            },
        },
    ]


def listar_actividades(token: str, desde: str | None = None, hasta: str | None = None) -> dict[str, Any]:
    params = {}
    if desde is not None:
        params["desde"] = desde
    if hasta is not None:
        params["hasta"] = hasta
    response = httpx.get(f"{API_BASE_URL}/api/actividades/", params=params, headers=_headers(token), timeout=10.0)
    response.raise_for_status()
    return {"actividades": response.json()}


def buscar_asociados(token: str, query: str | None = None, ciudad: str | None = None) -> dict[str, Any]:
    params = {}
    if query is not None:
        params["search"] = query
    if ciudad is not None:
        params["ciudad"] = ciudad
    response = httpx.get(f"{API_BASE_URL}/api/asociados/", params=params, headers=_headers(token), timeout=10.0)
    response.raise_for_status()
    return {"asociados": response.json()}


def consultar_disponibilidad(token: str, asociado_email: str, fecha: str | None = None, ventana: str | None = None) -> dict[str, Any]:
    return {"asociado": asociado_email, "fecha": fecha, "ventana": ventana, "disponible": True}


def crear_actividad(token: str, titulo: str, descripcion: str, fecha: str, duracion_minutos: int, asociado_email: str) -> dict[str, Any]:
    payload = {
        "tipo": titulo,
        "descripcion": descripcion,
        "fecha_inicio": fecha,
        "fecha_fin": fecha,
        "asociado": asociado_email,
    }
    response = httpx.post(f"{API_BASE_URL}/api/actividades/", json=payload, headers=_headers(token), timeout=10.0)
    response.raise_for_status()
    return {"actividad": response.json()}


def actualizar_actividad(token: str, id: int, descripcion: str | None = None, fecha: str | None = None, duracion_minutos: int | None = None) -> dict[str, Any]:
    payload = {}
    if descripcion is not None:
        payload["descripcion"] = descripcion
    if fecha is not None:
        payload["fecha_inicio"] = fecha
        payload["fecha_fin"] = fecha
    if duracion_minutos is not None:
        payload["duracion_minutos"] = duracion_minutos
    response = httpx.patch(f"{API_BASE_URL}/api/actividades/{id}/", json=payload, headers=_headers(token), timeout=10.0)
    response.raise_for_status()
    return {"actividad": response.json()}


def eliminar_actividad(token: str, id: int) -> dict[str, Any]:
    response = httpx.delete(f"{API_BASE_URL}/api/actividades/{id}/", headers=_headers(token), timeout=10.0)
    response.raise_for_status()
    return {"deleted": True, "id": id}


def get_tool_registry() -> list[dict[str, Any]]:
    return _build_tool_schema()


def execute_tool_call(name: str, arguments: dict[str, Any], token: str) -> dict[str, Any]:
    try:
        if name == "listar_actividades":
            return listar_actividades(token, arguments.get("desde"), arguments.get("hasta"))
        if name == "buscar_asociados":
            return buscar_asociados(token, arguments.get("query"), arguments.get("ciudad"))
        if name == "consultar_disponibilidad":
            return consultar_disponibilidad(token, arguments.get("asociado_email", ""), arguments.get("fecha"), arguments.get("ventana"))
        if name == "crear_actividad":
            return crear_actividad(token, arguments["titulo"], arguments["descripcion"], arguments["fecha"], int(arguments["duracion_minutos"]), arguments["asociado_email"])
        if name == "actualizar_actividad":
            return actualizar_actividad(token, int(arguments["id"]), arguments.get("descripcion"), arguments.get("fecha"), int(arguments["duracion_minutos"]) if arguments.get("duracion_minutos") is not None else None)
        if name == "eliminar_actividad":
            return eliminar_actividad(token, int(arguments["id"]))
        raise ValueError(f"Tool no soportada: {name}")
    except Exception as exc:  # pragma: no cover - safe fallback
        return {"error": str(exc)}
