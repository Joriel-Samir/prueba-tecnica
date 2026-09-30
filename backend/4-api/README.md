# Backend 4 — API REST de asignación de actividades

Framework elegido: **Django REST Framework (DRF)**. El requisito incluye panel de
administración, ORM con migraciones, autenticación JWT y permisos por recurso; Django
resuelve estas piezas de forma integrada y DRF permite exponerlas con serializers,
views y permisos probables de forma aislada. Para importaciones y validación fila por
fila, la capa de servicios mantiene las reglas fuera de los endpoints.

## Diseño y principios SOLID

- **S — Responsabilidad única:** las vistas gestionan HTTP; los serializers validan
	y transforman datos; los servicios aplican reglas; los repositorios encapsulan
	consultas y persistencia.
- **O — Abierto/cerrado:** las vistas y servicios de importación aceptan serializers
	por contexto; se pueden agregar formatos o entidades sin mezclar su validación con
	el ciclo HTTP.
- **L — Sustitución de Liskov:** las vistas y permisos personalizados respetan los
	contratos de `APIView`, `ModelViewSet` y `BasePermission` de DRF.
- **I — Segregación de interfaces:** cada endpoint depende del serializer y permiso
	mínimo de su recurso; el importador común recibe el serializer específico de cada
	tipo de archivo.
- **D — Inversión de dependencias:** los servicios usan módulos de repositorio en vez
	de ejecutar consultas ORM desde las vistas; la persistencia queda detrás de esa
	frontera de dominio.

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
	/api/actividades/{id}/`: requieren JWT. Solo los administradores crean
	actividades. Los asociados consultan las actividades asignadas o creadas por
	ellos, y pueden editar/eliminar las asignadas que siguen vigentes; las ya
	finalizadas son de solo lectura.
- La lista de actividades acepta `desde=YYYY-MM-DD` y `hasta=YYYY-MM-DD` para
	filtrar inclusivamente por `fecha_inicio`. No se permiten intervalos que se
	solapen para un mismo asociado; actividades contiguas sí son válidas.
- `GET/POST /api/asociados/`: consulta y creación de asociados por un administrador.
- `POST /api/carga-masiva/asociados/` y
	`POST /api/cargamasiva/actividades/`: importan archivos CSV/XLSX fila por fila
	y devuelven las filas creadas y los errores sin abortar las filas válidas.
- `GET /api/health/`: estado del servicio y la base de datos.

Para autenticarse, usa `POST /api/auth/token/` con `email` y `password` y envía
el token `access` como `Authorization: Bearer <token>`.

La especificación OpenAPI está en `GET /api/schema/`; la interfaz Swagger UI está en
`/api/docs/` y Redoc en `/api/redoc/`. Las cargas usan un campo multipart llamado
`file`; se admiten `.csv` y `.xlsx`. La carga de asociados requiere `email`, `password`,
`identificacion`, `nombre`, `apellidos` y `ciudad`. La carga de actividades requiere
`tipo`, `fecha_inicio`, `fecha_fin` y `asociado` (email); `descripcion` es opcional.
Cada respuesta informa `created`, `total` y los errores por fila, sin descartar las
filas válidas.

Los errores de la API tienen la forma `error.code`, `error.message` y
`error.details`. Un solapamiento o email duplicado se informa como `409`; los errores
de validación como `400`.

## Pruebas locales (con PostgreSQL)

Requiere **Python 3.12**, la misma versión utilizada por Docker y CI. Ejecuta estos
comandos desde `backend/4-api`.

Primero crea el archivo local de variables (queda ignorado por Git):

```powershell
Copy-Item .env.example .env
```

En Linux/macOS usa `cp .env.example .env`.
Inicia PostgreSQL desde Docker Compose antes de ejecutar Django desde el host.

```bash
docker compose up -d db
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest --cov=apps
ruff check .
python manage.py check
python manage.py makemigrations --check --dry-run
```

Al terminar las pruebas, detén PostgreSQL con `docker compose down`.

Para usar Docker, copia `.env.example` a `.env` (PowerShell:
`Copy-Item .env.example .env`; Linux/macOS: `cp .env.example .env`) y ejecuta
`docker compose up --build`. Cambia todos los valores de ejemplo antes de desplegar.
