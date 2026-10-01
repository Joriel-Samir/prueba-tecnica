"""Cliente CLI mínimo para probar el agente IA 1 mediante SSE."""
from __future__ import annotations

import argparse
import json
import os
import sys

import httpx


def _event_payload(line: str) -> dict | None:
    if not line.startswith("data: "):
        return None
    try:
        return json.loads(line[6:])
    except json.JSONDecodeError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente CLI del agente de actividades")
    parser.add_argument("--base-url", default="http://localhost:8001")
    parser.add_argument("--session-id", default="cli")
    args = parser.parse_args()

    token = os.getenv("AGENT_JWT")
    if not token:
        raise SystemExit("Define AGENT_JWT en el entorno; no se acepta el token como argumento visible.")

    print("Escribe 'salir' para terminar.")
    while True:
        try:
            message = input("Tú> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if message.lower() in {"salir", "exit", "quit"}:
            return
        if not message:
            continue

        payload = {"message": message, "session_id": args.session_id, "token": token}
        with httpx.stream("POST", f"{args.base_url}/api/chat", json=payload, timeout=None) as response:
            response.raise_for_status()
            result = None
            for line in response.iter_lines():
                event = _event_payload(line)
                if event and event.get("status") != "thinking":
                    result = event
            if result is None:
                print("Agente> No se recibió una respuesta válida.")
                continue

        print(f"Agente> {result.get('content', '')}")
        if result.get("status") != "needs_confirmation":
            continue

        answer = input("¿Confirmar escritura? [s/N] ").strip().lower()
        confirmed = answer in {"s", "si", "sí", "y", "yes"}
        confirmation = {
            "session_id": args.session_id,
            "token": token,
            "confirmed": confirmed,
        }
        confirmed_response = httpx.post(
            f"{args.base_url}/api/chat/confirm",
            json=confirmation,
            timeout=None,
        )
        confirmed_response.raise_for_status()
        print(f"Agente> {confirmed_response.json().get('content', '')}")


if __name__ == "__main__":
    try:
        main()
    except httpx.HTTPError as error:
        print(f"Error HTTP: {error}", file=sys.stderr)
        raise SystemExit(1) from error
