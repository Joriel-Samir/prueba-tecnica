# Backend 2 — Refactorización de análisis de sentimientos

Refactor del procesador Excel con el proveedor de sentimiento desacoplado mediante
`SentimentProvider`. Las llamadas externas se aíslan en `ParallelDotsProvider`; el
analizador recibe el proveedor por constructor y puede probarse sin red ni credenciales.

## Requisitos y configuración

Requiere **Python 3.10 o superior**. Desde `backend/2-refactor`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
python -m pip install -r requirements-dev.txt
```

En Linux/macOS, activa con `source .venv/bin/activate` y copia la plantilla con
`cp .env.example .env`. Edita `.env` y asigna una clave válida a
`PARALLELDOTS_API_KEY`; la plantilla solo contiene un marcador ficticio. No subas
`.env` al repositorio.

## Uso

Desde esta carpeta ejecuta:

```powershell
python -m src.main entrada.xlsx --output salida.xlsx --sheet Hoja1 --col 3
```

`--output` es opcional (por defecto `sentimentAnalysis.xlsx`), `--sheet` selecciona
la hoja y `--col` indica la columna de texto en numeración desde 1. La API key se lee
del entorno o del `.env` local. El proveedor reintenta ante fallos y el analizador
continúa con las demás filas si una falla.

## Pruebas y calidad

```powershell
python -m pytest
ruff check src test
mypy src
```

Las pruebas usan proveedores dobles y mocks para no llamar a ParallelDots. La
configuración de pytest mide `src` y exige al menos 80 % de cobertura.
