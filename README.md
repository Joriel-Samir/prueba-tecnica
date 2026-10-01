# Prueba técnica Ihungo

Repositorio de la prueba técnica, organizado por áreas del reto:

- `backend/`: análisis, refactorización, ejercicio Bouncy y API de actividades.
- `ia/1-agente/`: agente conversacional con function calling sobre la API de actividades.
- `ia/2-cocreacion/`: respuestas y artefactos del proceso guiado por especificaciones.
- `devops/`: Docker, CI/CD y despliegue reproducible en Kubernetes/k3s.

## Requisitos

- Git
- Python 3.12+
- PostgreSQL 15+ para Backend 4
- Docker y Docker Compose para la ejecución reproducible de Backend 4
- Node.js 20+ para la implementación TypeScript de Bouncy

## Backend 4 — API de actividades

La API está implementada con Django REST Framework y soporta autenticación JWT,
permisos por rol, actividades, asociados, cargas masivas CSV/XLSX y documentación
OpenAPI.

### Ejecución local

```powershell
cd backend/4-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

El archivo `backend/4-api/.env.example` documenta la configuración necesaria.
No se deben versionar archivos `.env`, contraseñas ni claves reales.

### Pruebas

```powershell
cd backend/4-api
pytest -q
```

Para levantar PostgreSQL mediante Docker Compose:

```powershell
cd backend/4-api
docker compose up -d db
pytest -q
```

La API expone el health check en `GET /api/health/`.

## IA 1 — Agente conversacional

Servicio independiente en FastAPI con proveedores Gemini, OpenAI y Mock. Incluye:

- herramientas tipadas para listar, buscar, consultar disponibilidad, crear,
  actualizar y eliminar actividades;
- confirmación humana antes de cualquier escritura;
- memoria limitada por sesión y aislamiento por JWT;
- fechas relativas en `America/Bogota`;
- streaming SSE, límites de iteraciones y timeouts;
- logging estructurado con herramientas, latencia y tokens;
- evaluaciones offline sin llamadas reales a proveedores.

Consulta `ia/1-agente/README.md` para instalación, variables de entorno, ejecución
del servicio y del cliente CLI.

```powershell
cd ia/1-agente
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
python evals/run_evals.py
```

Las claves de Gemini/OpenAI se configuran únicamente mediante `.env`, excluido por
`.gitignore`. El archivo `.env.example` contiene valores de referencia seguros.

## IA 2 — Co-creación guiada

Los entregables se encuentran en `ia/2-cocreacion/`:

- `RESPUESTAS.md`: respuestas razonadas a las preguntas del reto.
- `specs/requirements.md`: historias y criterios verificables.
- `specs/design.md`: decisiones de diseño y alternativas descartadas.
- `specs/plan.md`: unidades de trabajo y trazabilidad.
- `specs/rules.md`: reglas entregadas al asistente.
- `specs/bitacora.md`: aprobaciones, rechazos y correcciones.

## DevOps

Los artefactos de automatización y despliegue están en:

- `.github/workflows/`: calidad, construcción, escaneo y publicación.
- `Jenkinsfile`: pipeline alternativo.
- `devops/k8s/`: namespace, configuración, secretos de plantilla, PostgreSQL y API.
- `devops/EVIDENCIAS.md`: evidencias y matriz de cumplimiento.

El despliegue usa configuración externa, contenedores sin root, probes de salud,
recursos definidos, rolling updates y PostgreSQL persistente.

## Seguridad y uso de IA

No incluir API keys, JWT, contraseñas ni secretos en el repositorio o en su historial.
La declaración de herramientas, prompts relevantes y decisiones humanas está en
`AI_USAGE.md`.

## Estado de validación

- IA 1: 22 pruebas unitarias exitosas.
- Evaluaciones IA 1: 16/16 casos exitosos en modo offline.
- Backend 4: ejecutar `pytest -q` con PostgreSQL disponible.
