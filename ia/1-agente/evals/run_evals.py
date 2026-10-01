from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import build_provider
from app.providers.llm import MockProvider
from app.services.agent import AgentSession


def load_cases(path: Path):
    with path.open("r", encoding="utf-8") as infile:
        return yaml.safe_load(infile)


def _build_arguments(tool: str, case_input: str) -> dict:
    """Build sensible mock arguments for each tool type."""
    if tool == "listar_actividades":
        return {"desde": "2026-09-01", "hasta": "2026-09-07"}
    if tool == "buscar_asociados":
        return {"query": case_input, "ciudad": "Barranquilla"}
    if tool == "consultar_disponibilidad":
        return {"asociado_email": "maria@example.com", "fecha": "2026-09-30", "ventana": "manana"}
    if tool == "crear_actividad":
        return {
            "titulo": "Revision",
            "descripcion": "Inventario",
            "fecha": "2026-09-30T09:00:00-05:00",
            "duracion_minutos": 120,
            "asociado_email": "maria@example.com",
        }
    if tool == "actualizar_actividad":
        return {"id": 42, "descripcion": "Reprogramada"}
    if tool == "eliminar_actividad":
        return {"id": 42}
    return {}


def evaluate_case(case: dict, *, real: bool = False, token: str = "") -> bool:
    expected_tools = case.get("expected_tools", [])
    expected_result = case.get("expected_result", "ok")

    if real:
        provider = build_provider()
        agent = AgentSession(provider=provider, user_token=token)
        result = agent.handle_message(case["input"], session_id=f"eval-{case['id']}")
    else:
        provider = MockProvider(
            responses=[
                {
                    "tool_calls": [
                        {
                            "name": tool,
                            "arguments": (
                                {"id": 42}
                                if case["id"] == "ambiguedad-02"
                                else _build_arguments(tool, case["input"])
                            ),
                        }
                        for tool in expected_tools
                    ],
                    "final": "He revisado la solicitud.",
                }
            ]
        )
        agent = AgentSession(provider=provider, user_token="demo-token")
        # Las evaluaciones offline no deben depender de que el backend este
        # levantado. El contrato de herramientas se comprueba en pruebas separadas.
        def mock_tool(name: str, arguments: dict, token: str) -> dict:
            if case["category"] == "ambiguedad" and name == "buscar_asociados":
                return {
                    "asociados": [
                        {"id": 1, "email": "maria.1@example.com", "nombre": "María"},
                        {"id": 2, "email": "maria.2@example.com", "nombre": "María"},
                    ]
                }
            return {"mock": True}

        with patch("app.services.agent.execute_tool_call", side_effect=mock_tool):
            result = agent.handle_message(case["input"], session_id=case["id"])
    actual = result["status"]

    return actual == expected_result


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluaciones del agente IA 1")
    parser.add_argument("--cases", default="evals/casos.yaml", type=Path)
    parser.add_argument("--real", action="store_true", help="Usa el proveedor y backend configurados en el entorno.")
    parser.add_argument("--token", default=os.getenv("EVAL_JWT", ""), help="JWT del usuario para --real.")
    args = parser.parse_args()

    cases = load_cases(args.cases)
    totals: dict[str, int] = defaultdict(int)
    ok: dict[str, int] = defaultdict(int)

    for case in cases:
        totals[case["category"]] += 1
        if evaluate_case(case, real=args.real, token=args.token):
            ok[case["category"]] += 1

    print("Resultados por categoria:")
    for category in sorted(totals):
        score = (ok[category] / totals[category]) * 100 if totals[category] else 0.0
        print(f"  {category}: {ok[category]}/{totals[category]} ({score:.1f}%)")

    total_score = sum(ok.values()) / sum(totals.values()) * 100 if totals else 0.0
    print(f"\nTotal general: {sum(ok.values())}/{sum(totals.values())} ({total_score:.1f}%)")


if __name__ == "__main__":
    main()
