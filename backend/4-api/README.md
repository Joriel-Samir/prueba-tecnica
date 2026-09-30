# Backend 4 — API REST de asignación de actividades

Framework elegido: **Django REST Framework** (justificación completa: pendiente, se completa al final).

## Cómo correrlo

```bash
cp .env.example .env
docker compose up --build
curl http://localhost/api/health/
```

La plantilla contiene únicamente valores ficticios para desarrollo local. Antes de
desplegar, reemplázalos por valores seguros en `.env` y no subas ese archivo.

## API

- `POST /api/registro/`: crea una solicitud pública con `nombre`, `email` y
	`password` (mínimo 8 caracteres). La solicitud queda pendiente; la contraseña
	se guarda hasheada y no se devuelve en la respuesta.
- `GET/POST /api/actividades/` y `GET/PATCH/PUT/DELETE
	/api/actividades/{id}/`: requieren JWT. Los administradores tienen acceso total.
	Un asociado puede crear actividades solo para sí mismo, consultar las asignadas
	o creadas por él, y modificar/eliminar únicamente las que creó.
- La lista de actividades acepta `desde=YYYY-MM-DD` y `hasta=YYYY-MM-DD` para
	filtrar inclusivamente por `fecha_inicio`. No se permiten intervalos que se
	solapen para un mismo asociado; actividades contiguas sí son válidas.

Para autenticarse, usa `POST /api/auth/token/` con `email` y `password` y envía
el token `access` como `Authorization: Bearer <token>`.

## Pruebas (local, sin Docker)

Requiere **Python 3.12**, la misma versión utilizada por Docker y CI. Ejecuta los
comandos desde `backend/4-api` con el entorno virtual activado.

```bash
pip install -r requirements-dev.txt
pytest --cov=apps
ruff check .
```
