# IA 1 — Agente de actividades Ihungo

Servicio conversacional sobre la API del backend de actividades. El usuario escribe en lenguaje natural; el agente consulta, crea o reprograma actividades usando *function calling* con confirmacion humana antes de cualquier escritura.

## Arquitectura

```
app/
  main.py                 — Composición FastAPI, middleware, routers y health
  api/routes/chat.py      — Endpoints HTTP y streaming SSE
  api/dependencies.py     — Inyección de Settings, proveedores y sesiones
  config/settings.py      — Settings tipado con pydantic-settings
  models/chat.py          — DTOs HTTP de entrada/salida
  models/tools.py         — Contratos Pydantic de las herramientas
  services/session_manager.py — Sesiones, TTL y aislamiento por JWT
  services/agent.py        — Servicio de aplicación: memoria, ciclo LLM y confirmación
  providers/llm.py       — Puerto LLM + adaptadores Gemini/OpenAI/Mock
  tools/activity_tools.py — Adaptador de herramientas al backend REST
  utils/dates.py          — Fechas relativas en America/Bogota
  utils/observability.py  — Logging estructurado JSON
  clients/cli.py          — Cliente interactivo CLI sobre SSE
evals/
  casos.yaml       — 16 casos de evaluacion (consulta, busqueda, escritura, ambiguedad, inyeccion)
  run_evals.py     — Script offline o real con reporte por categoria
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

Con el servicio levantado, define `AGENT_JWT` y ejecuta el cliente interactivo:

```bash
python -m app.clients.cli --session-id demo
```

## Endpoints

### `GET /health`
Verifica que el servicio esta en linea.

### `POST /api/chat`
Envia un mensaje del usuario. Devuelve un stream SSE con dos eventos:
1. `{"status": "thinking"}` — inmediato
2. Resultado del turno: `{"status": "ok"|"needs_confirmation"|"needs_input"|"error", "content": "...", "tool_calls": [...], "results": [...]}`

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

Reporte por categoria (16 casos: consulta, busqueda, disponibilidad, creacion, actualizacion, eliminacion, ambiguedad x3, inyeccion x3). El evaluador offline no levanta el backend y no relaja los casos de ambigüedad: una ambigüedad debe terminar en `needs_input`.

Para ejecutar contra Gemini/OpenAI y el backend configurado, define `LLM_PROVIDER`, la clave del proveedor y `EVAL_JWT`, y usa `python evals/run_evals.py --real`. El script no imprime el JWT.

La separación sigue el patrón de aplicaciones grandes de FastAPI: `main.py` compone
routers, los modelos solo describen contratos, las dependencias construyen recursos
reutilizables y los servicios contienen la lógica de aplicación. La configuración se
valida una sola vez mediante `get_settings()` y puede sustituirse en pruebas.

## Seguridad

- El agente opera con el token JWT del usuario; nunca usa credenciales propias.
- Ninguna escritura ocurre sin confirmacion explicita del usuario.
- El system prompt resiste inyeccion de instrucciones: el agente ignora intentos de cambiar su rol.
- Las fechas relativas se normalizan en `America/Bogota` antes de invocar herramientas.
- La disponibilidad se calcula contra actividades visibles y reporta error si el token no permite verificarla; nunca asume disponibilidad.
- Ningun secreto se versionea; usar `.env` excluido por `.gitignore`.
