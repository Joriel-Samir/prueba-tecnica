# Frontend — Ihungo

Aplicación React + TypeScript para gestionar actividades de asociados mediante la API REST de Backend 4.

## Requisitos

- Node.js 20+
- npm

## Instalación

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Scripts disponibles

```bash
npm run dev
npm run build
npm run test:run
npm run test:e2e
npm run typecheck
npm run lint
```

Para ejecutar la entrega empaquetada con Nginx:

```bash
docker compose up --build
```

La aplicación queda disponible en `http://localhost:5173`. El proxy de Nginx reenvía `/api/` al backend local publicado en el puerto 80.

## Estructura inicial

- `src/features/auth`: flujo de autenticación y acceso.
- `src/features/activities`: calendario y gestión de eventos.
- `src/lib`: capa aislada para llamadas a la API, mapeo de DTOs, JWT y errores.
- `e2e`: prueba Playwright del flujo ingreso → crear → arrastrar.

## Arquitectura y responsabilidades

- **Presentación:** `App`, `LoginForm`, `ActivityCalendar`, `ActivityModal` y `BulkUploadPanel` solo gestionan interacción y renderizado.
- **Aplicación/estado servidor:** TanStack Query controla caché, cargas, mutaciones e invalidación.
- **Dominio:** `types.ts` define las entidades y `ActivityCalendar` concentra reglas de navegación, fechas y reprogramación.
- **Infraestructura:** `lib/api.ts` encapsula HTTP, DTOs backend/frontend, JWT refresh, multipart y errores.
- **SOLID:** los componentes dependen de callbacks y tipos, no de `fetch`; los adaptadores API pueden sustituirse sin reescribir la UI.

La suite de componentes se ejecuta con Vitest y Testing Library. Playwright cubre el flujo principal con respuestas API interceptadas, de forma reproducible y sin depender de credenciales reales.

## Seguimiento geoespacial

La pantalla `Seguimiento` usa Nominatim para geocodificar, OSRM para obtener una ruta vial real y OpenStreetMap para los tiles, con atribución visible. Los adaptadores están en `src/features/tracking/tracking.ts` y la UI en `TrackingPage.tsx`.

La demo reproduce la geometría devuelta por OSRM; no usa coordenadas ni métricas precargadas. También puede solicitar la ubicación del navegador, informar permisos o pérdida de señal y mostrar distancia, rumbo, velocidad estimada y ETA.
