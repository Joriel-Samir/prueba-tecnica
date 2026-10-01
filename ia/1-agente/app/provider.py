"""Abstraccion del proveedor LLM.

Proporciona una interfaz comun (LLMProvider) para que la logica del agente
este totalmente desacoplada de cualquier proveedor LLM en particular. Selecciona
el proveedor en tiempo de ejecucion mediante la variable de entorno LLM_PROVIDER:

  - ``gemini``  — Google Gemini (usa API nativa de function-calling)
  - ``openai``  — OpenAI Chat Completions (con tool_choice=auto)
  - cualquier otro valor por defecto usa MockProvider (ideal para tests / CI)
"""
from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Any

import httpx


class LLMProvider(ABC):
    """Base abstracta para todos los backends de LLM."""

    #: Despues de cada llamada, almacena conteo de tokens {"input_tokens": int, "output_tokens": int}
    last_usage: dict[str, int]

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Envia mensajes + esquemas de herramientas al LLM y retorna respuesta procesada.

        Retorna:
            Un diccionario con:
              - ``tool_calls``: lista de diccionarios {name, arguments} (puede estar vacia)
              - ``final``: texto de respuesta opcional del modelo
        """
        raise NotImplementedError


class MockProvider(LLMProvider):
    """Respuestas pre-programadas para pruebas unitarias — sin llamadas de red."""

    def __init__(self, responses: list[dict[str, Any]] | None = None):
        self.responses = list(responses or [])
        self.calls: list[tuple[list[dict[str, Any]], list[dict[str, Any]]]] = []
        self.last_usage: dict[str, int] = {"input_tokens": 0, "output_tokens": 0}

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        self.calls.append((messages, tools))
        if not self.responses:
            return {"final": "Sin respuesta mock configurada.", "tool_calls": []}
        return self.responses.pop(0)


class GeminiProvider(LLMProvider):
    """Backend de Google Gemini usando function-calling nativo.

    Convierte el formato de lista de mensajes estilo OpenAI al formato ``contents``
    de Gemini y extrae las partes ``functionCall`` de la respuesta.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.0-flash",
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.last_usage: dict[str, int] = {"input_tokens": 0, "output_tokens": 0}

    # ------------------------------------------------------------------
    # Ayudantes internos
    # ------------------------------------------------------------------

    @staticmethod
    def _messages_to_contents(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convierte lista de mensajes estilo OpenAI al formato de contenidos de Gemini.

        Los mensajes de sistema se agrupan en el primer turno de usuario como preambulo.
        """
        contents: list[dict[str, Any]] = []
        pending_system = ""

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                pending_system = content
                continue

            gemini_role = "user" if role == "user" else "model"
            text = f"{pending_system}\n\n{content}" if pending_system and gemini_role == "user" else content
            pending_system = ""
            contents.append({"role": gemini_role, "parts": [{"text": text}]})

        # Si solo se proporciono un mensaje de sistema, emitirlo como turno de usuario
        if pending_system:
            contents.append({"role": "user", "parts": [{"text": pending_system}]})

        return contents

    @staticmethod
    def _tools_to_function_declarations(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Extrae function_declarations del formato de esquema de herramientas de OpenAI."""
        declarations = []
        for tool in tools:
            fn = tool.get("function", tool)
            declarations.append(
                {
                    "name": fn.get("name", ""),
                    "description": fn.get("description", ""),
                    "parameters": fn.get("parameters", {}),
                }
            )
        return declarations

    # ------------------------------------------------------------------
    # Interfaz publica
    # ------------------------------------------------------------------

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not self.api_key:
            return {"final": "Gemini no está configurado. Proporciona GEMINI_API_KEY.", "tool_calls": []}

        contents = self._messages_to_contents(messages)
        function_declarations = self._tools_to_function_declarations(tools)

        payload: dict[str, Any] = {"contents": contents}
        if function_declarations:
            payload["tools"] = [{"function_declarations": function_declarations}]

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()

        # Rastrear uso de tokens
        usage = body.get("usageMetadata", {})
        self.last_usage = {
            "input_tokens": usage.get("promptTokenCount", 0),
            "output_tokens": usage.get("candidatesTokenCount", 0),
        }

        # Procesar respuesta candidata
        candidate = (body.get("candidates") or [{}])[0]
        parts = candidate.get("content", {}).get("parts", [])

        tool_calls: list[dict[str, Any]] = []
        text_parts: list[str] = []

        for part in parts:
            if "functionCall" in part:
                fc = part["functionCall"]
                tool_calls.append({"name": fc.get("name", ""), "arguments": fc.get("args", {})})
            elif "text" in part:
                text_parts.append(part["text"])

        return {
            "tool_calls": tool_calls,
            "final": " ".join(text_parts) if text_parts else "He procesado la solicitud.",
        }


class OpenAIProvider(LLMProvider):
    """Backend de OpenAI Chat Completions con tool_choice=auto."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.last_usage: dict[str, int] = {"input_tokens": 0, "output_tokens": 0}

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not self.api_key:
            return {"final": "OpenAI no está configurado. Proporciona OPENAI_API_KEY.", "tool_calls": []}

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            body = response.json()

        # Rastrear uso de tokens
        usage = body.get("usage", {})
        self.last_usage = {
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        }

        message = body["choices"][0]["message"]
        tool_calls = [
            {
                "name": tc["function"]["name"],
                "arguments": json.loads(tc["function"]["arguments"]),
            }
            for tc in message.get("tool_calls") or []
        ]

        return {
            "tool_calls": tool_calls,
            "final": message.get("content") or "He consultado la información.",
        }
