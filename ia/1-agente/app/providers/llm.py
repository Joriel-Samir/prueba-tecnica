"""Puerto y adaptadores de proveedores LLM."""
from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Any

import httpx

from ..config.settings import get_settings


class LLMProvider(ABC):
    last_usage: dict[str, int]

    @abstractmethod
    def generate(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        raise NotImplementedError


class MockProvider(LLMProvider):
    def __init__(self, responses: list[dict[str, Any]] | None = None):
        self.responses = list(responses or [])
        self.calls: list[tuple[list[dict[str, Any]], list[dict[str, Any]]]] = []
        self.last_usage = {"input_tokens": 0, "output_tokens": 0}

    def generate(self, messages, tools):
        self.calls.append((messages, tools))
        return self.responses.pop(0) if self.responses else {
            "final": "Sin respuesta mock configurada.", "tool_calls": []
        }


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.0-flash"):
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.last_usage = {"input_tokens": 0, "output_tokens": 0}

    @staticmethod
    def _messages_to_contents(messages):
        contents = []
        pending_system = ""
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content") or ""
            if role == "system":
                pending_system = content
                continue
            if role == "tool":
                try:
                    response = json.loads(content)
                except (TypeError, json.JSONDecodeError):
                    response = {"content": content}
                contents.append({"role": "user", "parts": [{"functionResponse": {
                    "name": message.get("name", "tool"), "response": response
                }}]})
                continue
            gemini_role = "user" if role == "user" else "model"
            text = f"{pending_system}\n\n{content}" if pending_system and gemini_role == "user" else content
            pending_system = ""
            contents.append({"role": gemini_role, "parts": [{"text": text}]})
        if pending_system:
            contents.append({"role": "user", "parts": [{"text": pending_system}]})
        return contents

    def generate(self, messages, tools):
        if not self.api_key:
            return {"final": "Gemini no está configurado. Proporciona GEMINI_API_KEY.", "tool_calls": []}
        declarations = []
        for tool in tools:
            function = tool.get("function", tool)
            declarations.append({"name": function["name"], "description": function.get("description", ""), "parameters": function.get("parameters", {})})
        settings = get_settings()
        payload = {"contents": self._messages_to_contents(messages), "tools": [{"function_declarations": declarations}]}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        with httpx.Client(timeout=settings.request_timeout_seconds) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()
        usage = body.get("usageMetadata", {})
        self.last_usage = {"input_tokens": usage.get("promptTokenCount", 0), "output_tokens": usage.get("candidatesTokenCount", 0)}
        parts = ((body.get("candidates") or [{}])[0].get("content") or {}).get("parts", [])
        calls = [{"name": part["functionCall"].get("name", ""), "arguments": part["functionCall"].get("args", {})} for part in parts if "functionCall" in part]
        text = " ".join(part["text"] for part in parts if "text" in part)
        return {"tool_calls": calls, "final": text or "He procesado la solicitud."}


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.last_usage = {"input_tokens": 0, "output_tokens": 0}

    def generate(self, messages, tools):
        if not self.api_key:
            return {"final": "OpenAI no está configurado. Proporciona OPENAI_API_KEY.", "tool_calls": []}
        settings = get_settings()
        payload = {"model": self.model, "messages": messages, "tools": tools, "tool_choice": "auto"}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=settings.request_timeout_seconds) as client:
            response = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
        usage = body.get("usage", {})
        self.last_usage = {"input_tokens": usage.get("prompt_tokens", 0), "output_tokens": usage.get("completion_tokens", 0)}
        message = body["choices"][0]["message"]
        calls = [{"id": call.get("id", f"tool-{index}"), "name": call["function"]["name"], "arguments": json.loads(call["function"]["arguments"])} for index, call in enumerate(message.get("tool_calls") or [])]
        return {"tool_calls": calls, "final": message.get("content") or "He consultado la información."}
