# Backend 4 — API REST de asignación de actividades

Framework elegido: **Django REST Framework** (justificación completa: pendiente, se completa al final).

## Cómo correrlo

```bash
cp .env.example .env
docker compose up --build
```

La plantilla contiene únicamente valores ficticios para desarrollo local. Antes de
desplegar, reemplázalos por valores seguros en `.env` y no subas ese archivo.

## Pruebas (local, sin Docker)

```bash
pip install -r requirements-dev.txt
pytest --cov=apps
ruff check .
```
