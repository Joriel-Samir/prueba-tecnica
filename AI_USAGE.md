# Declaración de uso de inteligencia artificial

En esta prueba usé asistentes de inteligencia artificial como apoyo para investigar,
comparar alternativas, revisar documentación y detectar errores. La implementación,
las decisiones finales y las verificaciones las hice sobre el repositorio real. Cuando
no conservé el registro exacto de una versión del modelo, lo indico expresamente.

## Herramientas que usé

| Herramienta | Cómo la usé |
| --- | --- |
| **Gemini 3.1 Pro (Google Antigravity)** | Primer borrador del análisis de arquitectura de Backend 1 y propuestas iniciales de diagramas Mermaid. |
| **GitHub Copilot Chat** | Analizar requisitos, comparar alternativas, revisar documentación y apoyar la revisión final de Backend 4 y DevOps. |
| **Claude Sonnet 5.5 (Anthropic, chat en claude.ai)** | Construir por partes la base de Backend 4, consultar alternativas de Backend 2 y 3 y contrastar decisiones técnicas. |

## Cómo lo usé en cada reto

- **Backend 1 — Análisis de arquitectura:** Gemini me ayudó con el borrador sobre
  `diagnosis`, `auth` y `corozina`. Usé Copilot para contrastar nombres y comportamientos
  con el repositorio original. Los riesgos finales y la estrategia de migración los
  revisé y los dejé como yo los entendí.
- **Backend 2 — Refactorización:** usé Copilot y Claude para revisar alternativas de
  diseño. Después comprobé la configuración reproducible, los tipos, las herramientas
  de calidad y que las pruebas no llamaran al servicio real.
- **Backend 3 — Números bouncy:** usé Copilot y Claude para contrastar el enunciado y
  los casos límite. Yo comprobé los resultados, las CLIs y la paridad entre Python y
  TypeScript ejecutando pruebas y builds.
- **Backend 4 — API de actividades:** Claude me ayudó a construir por partes la base
  con Docker Compose, Nginx, Gunicorn, el CI de GitLab, el usuario personalizado,
  JWT, modelos, admin, registro público y errores uniformes. El CRUD, permisos,
  solapamientos, cargas CSV/XLSX, OpenAPI y configuración PostgreSQL los programé y
  revisé yo, usando Copilot como apoyo puntual.
- **Frontend — React y TypeScript:** usé GitHub Copilot Chat para explorar la estructura
  de componentes, aislar la capa API, implementar el calendario, revisar el flujo JWT,
  preparar pruebas con Testing Library/Playwright y diseñar los adaptadores de mapa.
  También lo usé para revisar Docker/Nginx, CI, carga masiva y accesibilidad.
  Verifiqué manualmente los contratos contra Backend 4 y corregí propuestas que no
  cumplían React 18, TypeScript, la resolución de módulos de Vite, las reglas de roles,
  el rollback del drag-and-drop, los matchers de Vitest y la compatibilidad de
  React-Leaflet. La selección de proveedores públicos, el modelo de permisos y la
  decisión de separar Frontend 1 y Frontend 2 fueron decisiones finales mías.

## DevOps — Docker, CI/CD y k3s

En DevOps trabajé yo sobre el repositorio de Backend 4 y usé GitHub Copilot Chat
como apoyo para interpretar el enunciado, revisar riesgos y contrastar la solución.
No acepté propuestas sin comprobarlas contra el código real, Django, Docker y k3d.

Mis decisiones y verificaciones fueron:

- Convertí el Dockerfile en un build multi-etapa, instalé dependencias desde wheels,
  configuré un usuario no root y dejé Gunicorn como proceso principal.
- Separé GitHub Actions en calidad, construcción/escaneo y publicación. Comprobé que
  las pull requests no publiquen y que solo `main` y tags `vX.Y.Z` publiquen imágenes.
- Elegí etiquetas de rama, versión semántica y SHA largo para rastrear cada imagen.
  En Kubernetes usé la versión `v1.0.1` y documenté el uso preferente de digest.
- Externalicé la configuración mediante ConfigMap y Secret. No guardé tokens,
  contraseñas ni claves reales en Git. Verifiqué que Kubernetes use `SECRET_KEY`, que
  es el nombre leído por `config/settings.py`.
- Añadí readiness y liveness sobre `/api/health/`, recursos, ejecución sin privilegios
  y `RollingUpdate` con `maxUnavailable: 0`.
- Añadí PostgreSQL reproducible como StatefulSet con volumen persistente, probes y
  credenciales tomadas del Secret de Kubernetes.
- Construí la imagen localmente, ejecuté Ruff, validé YAML y corregí un fallo real del
  primer build: el comodín intentaba instalar `requirements.txt` como wheel.
- Ejecuté GitHub Actions y verifiqué exitosamente lint, pruebas, build, Trivy y
  publicación en Docker Hub. En k3d verifiqué dos réplicas Ready, PostgreSQL, las
  migraciones, `/api/health/` y un rolling update sin caída.

Las credenciales se configuraron directamente en GitHub Actions o Kubernetes. Las
capturas y enlaces comprobables están en `devops/EVIDENCIAS.md`; los secretos no se
incluyeron en el repositorio ni en sus commits.

## Prompts y guías que usé

- Revisar el enunciado requisito por requisito antes de cerrar cada reto.
- Backend 1: identificar capas, responsabilidades, riesgos y estrategia de migración.
- Backend 2: desacoplar el proveedor, procesar filas, reintentar y comprobar pruebas.
- Backend 3: validar porcentajes, casos límite, aritmética entera y paridad de CLIs.
- Backend 4: trabajar con pruebas, separar vista → servicio → repositorio, validar
  cargas fila por fila y comprobar permisos, OpenAPI y PostgreSQL.
- DevOps: revisar seguridad de imágenes, publicación trazable, escaneo, configuración
  externa, probes, recursos y rolling update.

## Decisiones mías y correcciones

- En Backend 1 prioricé los riesgos de autenticación social, efectos secundarios en
  `QuestionOption.save()` y limitaciones de SQLite.
- En Backend 2 mantuve el proveedor detrás de `SentimentProvider` y decidí dejar vacía
  una fila cuando el análisis falla, en lugar de inventar un cero.
- En Backend 3 usé aritmética entera y mantuve implementaciones independientes.
- En Backend 4 escogí DRF, mantuve Administrador y Asociado como entidades separadas,
  y corregí la ausencia inicial de migraciones de las aplicaciones nuevas.
- En DevOps corregí la ejecución como root, la falta de Gunicorn, el orden incorrecto
  del pipeline, la falta de escaneo, las etiquetas poco trazables, la configuración
  embebida, la falta de readiness y la ausencia de PostgreSQL reproducible en k3d.

Al final revisé todo lo generado con el código, las pruebas, los logs de Docker, los
resultados de GitHub Actions y el despliegue real. La IA me sirvió como apoyo para
arrancar, contrastar ideas y revisar; el diseño final y la validación fueron míos.
