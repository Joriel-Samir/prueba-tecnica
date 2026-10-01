# Prueba técnica Ihungo

Repositorio de la prueba técnica, organizado por áreas del reto:

- `backend/`: análisis, refactorización, ejercicio Bouncy y API de actividades.
- `ia/1-agente/`: agente conversacional con function calling sobre la API de actividades.
- `ia/2-cocreacion/`: respuestas y artefactos del proceso guiado por especificaciones.
- `frontend/`: aplicación React obligatoria de actividades y seguimiento geoespacial.
- `devops/`: Docker, CI/CD y despliegue reproducible en Kubernetes/k3s.

## Requisitos

- Git
- Python 3.12+
- PostgreSQL 15+ para Backend 4
- Docker y Docker Compose para la ejecución reproducible de Backend 4
- Node.js 20+ para la implementación TypeScript de Bouncy

### Versiones elegidas

- **Backend 1:** se analiza el sistema legado solicitado (Python 3.7/Django 3); no
    se ejecuta ese sistema original.
- **Backend 2:** Python 3.10+ por las restricciones de `pyproject.toml`.
- **Backend 3:** Python 3.12+ y Node.js 20+ para mantener paridad y builds reproducibles.
- **Backend 4:** Python 3.12 en Docker/CI y Django 5.2.17, versión parcheada compatible
    con el diseño actual. La prueba no obliga una versión exacta para Backend 4; Python
    3.12 es la versión fijada por el Dockerfile y el pipeline, y Django 5.2.17 evita la
    vulnerabilidad HIGH detectada en Django 5.1.15.
- **Frontend:** Node.js 20+, React 18 y TypeScript.
- **IA 1:** Python 3.12+ con FastAPI; el proveedor por defecto es `mock` para CI.

## Backend 1 — Análisis

Es un entregable documental y no requiere instalación. Revisar:

```powershell
Get-Content backend/1-analisis/ANALISIS.md
```

Incluye capas, responsabilidades, diagrama de dependencias, diagrama de clases,
riesgos y estrategia de migración a Python 3.12/Django 5.x.

## Backend 2 — Refactorización

```powershell
cd backend/2-refactor
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
python -m pip install -r requirements-dev.txt
python -m pytest
ruff check src test
mypy src
```

Para procesar un archivo real, configura `PARALLELDOTS_API_KEY` solo en `.env` y ejecuta:

```powershell
python -m src.main entrada.xlsx --output salida.xlsx --sheet Hoja1 --col 3
```

## Backend 3 — Bouncy

### Python

```powershell
cd backend/3-bouncy/python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
python bouncy.py 50
python bouncy.py 90
python bouncy.py 99
```

### TypeScript

```powershell
cd backend/3-bouncy/typescript
npm ci
npm test
npm run build
npm start -- 99
```

Resultados esperados: `538`, `21780` y `1587000`.

## Backend 4 — API de actividades

La API está implementada con Django REST Framework y soporta autenticación JWT,
permisos por rol, actividades, asociados, cargas masivas CSV/XLSX y documentación
OpenAPI.

### Ejecución local rápida (PowerShell)

Abre una terminal de PowerShell y ejecuta:

```powershell
# 1. Entrar al directorio
cd backend/4-api

# 2. Configurar variables de entorno iniciales
Copy-Item .env.example .env

# 3. Levantar la base de datos PostgreSQL con Docker
docker compose up -d db

# 4. Crear el entorno virtual e instalar dependencias
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 5. Aplicar migraciones y ejecutar el servidor
python manage.py migrate
python manage.py runserver
```

> **Nota:** El servidor quedará ejecutándose en esta terminal (http://127.0.0.1:8000/). Para detenerlo, presiona `Ctrl + C`.

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

## Frontend — React y TypeScript

El frontend implementa las pantallas de ingreso/registro, calendario, CRUD, carga
masiva, JWT, drag-and-drop y seguimiento geoespacial real con Leaflet, Nominatim y
OSRM.

```powershell
cd frontend
Copy-Item .env.example .env
npm ci
npm run lint
npm run typecheck
npm run test:run
npx playwright install chromium
npm run test:e2e
npm run build
```

Para ejecutarlo detrás de Nginx:

```powershell
cd frontend
docker compose up --build
```

La aplicación queda disponible en `http://localhost:5173`. Consulta
`frontend/README.md` para arquitectura, mapas y variables cartográficas.

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

### Ejecución rápida (PowerShell)

Abre una terminal de PowerShell y ejecuta:

```powershell
# 1. Entrar al directorio
cd ia/1-agente

# 2. Configurar variables de entorno
Copy-Item .env.example .env

# 3. Crear entorno virtual e instalar dependencias
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 4. (Opcional) Correr pruebas y evaluaciones
pytest -q
python evals/run_evals.py

# 5. Levantar el servicio
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

> **Nota:** El servicio quedará ejecutándose en esta terminal. Para el cliente, abre otra terminal, activa el entorno (`.\.venv\Scripts\Activate.ps1`) y ejecuta: `python -m app.clients.cli --session-id demo`

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
