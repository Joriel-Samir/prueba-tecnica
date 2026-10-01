# IA 1 — Agente de actividades Ihungo

Servicio conversacional sobre la API del backend de actividades. El usuario escribe en lenguaje natural; el agente consulta, crea o reprograma actividades usando *function calling* con confirmacion humana antes de cualquier escritura.

## Arquitectura

```
app/
  main.py          — FastAPI: /api/chat (SSE) + /api/chat/confirm
  agent.py         — AgentSession: historial, tool loop, confirmacion, system prompt
  provider.py      — LLMProvider abstracto + GeminiProvider + OpenAIProvider + MockProvider
  tools.py         — 6 herramientas con esquemas tipados (Pydantic-compatible)
  models.py        — Modelos de request/response (Pydantic v2)
  config.py        — Variables de entorno
  observability.py — Logging estructurado JSON (latencia, tokens, herramientas)
evals/
  casos.yaml       — 15 casos de evaluacion (consulta, busqueda, escritura, ambiguedad, inyeccion)
  run_evals.py     — Script de evaluacion con reporte por categoria
tests/
  test_agent.py    — Pruebas unitarias con MockProvider (sin llamadas reales al LLM)
```

## Requisitos

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Variables de entorno

Copia `.env.example` a `.env` y completa los valores:

```env
API_BASE_URL=http://localhost:8000   # URL del backend de actividades
LLM_PROVIDER=mock                   # gemini | openai | mock
GEMINI_API_KEY=                      # Solo si LLM_PROVIDER=gemini
OPENAI_API_KEY=                      # Solo si LLM_PROVIDER=openai
SESSION_TTL=20
MAX_TOOL_ITERATIONS=3
REQUEST_TIMEOUT_SECONDS=10
```

## Ejecutar

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## Endpoints

### `GET /health`
Verifica que el servicio esta en linea.

### `POST /api/chat`
Envia un mensaje del usuario. Devuelve un stream SSE con dos eventos:
1. `{"status": "thinking"}` — inmediato
2. Resultado del turno: `{"status": "ok"|"needs_confirmation", "content": "...", "tool_calls": [...], "results": [...]}`

```bash
curl -N -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Que actividades tengo esta semana?","session_id":"demo","token":"<JWT>"}'
```

### `POST /api/chat/confirm`
Confirma o cancela una escritura pendiente (despues de recibir `needs_confirmation`):

```bash
# Confirmar
curl -X POST http://localhost:8001/api/chat/confirm \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo","token":"<JWT>","confirmed":true}'

# Cancelar
curl -X POST http://localhost:8001/api/chat/confirm \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo","token":"<JWT>","confirmed":false}'
```

## Pruebas unitarias

```bash
pytest tests/ -v
```

## Evaluaciones

```bash
python evals/run_evals.py
```

Reporte por categoria (15 casos: consulta, busqueda, disponibilidad, creacion, actualizacion, eliminacion, ambiguedad x3, inyeccion x3).

## Seguridad

- El agente opera con el token JWT del usuario; nunca usa credenciales propias.
- Ninguna escritura ocurre sin confirmacion explicita del usuario.
- El system prompt resiste inyeccion de instrucciones: el agente ignora intentos de cambiar su rol.
- Ningun secreto se versionea; usar `.env` excluido por `.gitignore`.
