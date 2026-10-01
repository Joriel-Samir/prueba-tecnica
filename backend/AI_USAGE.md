# Declaración de uso de inteligencia artificial

Aquí cuento qué asistentes de IA usé en la prueba, para qué los usé en cada reto y qué decisiones tomé yo o qué corregí de lo que me dieron. Cuando no guardé el registro de algo (por ejemplo, la versión exacta del modelo), lo dejo indicado. 

## Herramientas que usé

| Herramienta | Para qué la usé |
| --- | --- |
| **Gemini 3.1 Pro (Google Antigravity)** | Primer borrador del análisis de arquitectura de Backend 1 y propuestas iniciales de los diagramas Mermaid. |
| **GitHub Copilot Chat** | Analizar los requisitos, comparar alternativas y revisar documentación. También apoyo y revisión en Backend 4 y en la verificación final de los entregables. |
| **Claude Sonnet 5.5 (Anthropic, chat en claude.ai)** | Backend 4: armar con él, por partes, la base del proyecto, el usuario con JWT, los modelos y el registro público (detalle más abajo). En Backend 2 y 3 lo usé para consultar y contrastar propuestas. |

### DevOps — Docker, CI/CD y k3s

En esta parte trabajé yo sobre el repositorio de Backend 4 y usé GitHub Copilot Chat
como apoyo puntual. Le pasé el enunciado y le pedí que revisara los riesgos de las
definiciones de referencia, pero no acepté las propuestas sin contrastarlas con el
Dockerfile, los requisitos de Django y la estructura real del repositorio.

Con ese apoyo hice y revisé personalmente lo siguiente:

- Convertí el Dockerfile en un build multi-etapa, instalé las dependencias desde wheels,
  dejé un usuario no root y configuré Gunicorn como proceso principal.
- Separé el pipeline en calidad, construcción/escaneo y publicación. Comprobé que las
  pull requests no publiquen y que solo `main` y los tags `vX.Y.Z` puedan publicar.
- Elegí las etiquetas de rama, versión semántica y SHA largo para poder rastrear cada
  imagen hasta su commit. Para Kubernetes dejé documentado el uso de una etiqueta
  inmutable o un digest.
- Externalicé la configuración en ConfigMap y Secret, sin guardar tokens ni contraseñas
  reales en Git. También revisé que el nombre usado por Kubernetes sea `SECRET_KEY`, que
  es el que realmente lee `config/settings.py`.
- Añadí readiness y liveness sobre `/api/health/`, límites de recursos, ejecución sin
  privilegios y una estrategia `RollingUpdate` con `maxUnavailable: 0`.
- Construí la imagen localmente, ejecuté Ruff y validé los YAML. Cuando el primer build
  falló porque intentaba instalar `requirements.txt` como wheel, corregí el Dockerfile
  y volví a construirlo con éxito.

La configuración de credenciales, la ejecución en GitHub Actions/Jenkins, el despliegue
en k3s y las capturas de operación las hago yo en los servicios correspondientes; no
las considero evidencias hasta comprobarlas allí y registrarlas en `devops/EVIDENCIAS.md`.

## Cómo lo usé en cada reto

- **Backend 1 — Análisis de arquitectura:** Gemini me ayudó con el borrador sobre `diagnosis`, `auth` y `corozina`. Copilot lo usé para contrastar nombres y comportamientos con el repositorio original. Los riesgos finales y la estrategia de migración los revisé y los dejé como yo los entendí.
- **Backend 2 — Refactorización:** usé Copilot y Claude como apoyo para revisar alternativas de refactorización. Después Copilot me ayudó a revisar la configuración reproducible, los tipos y las herramientas de calidad. La solución mantiene el proveedor detrás de una interfaz y las pruebas no llaman al servicio real.
- **Backend 3 — Números bouncy:** usé Copilot y Claude para contrastar cómo entendía el enunciado y los casos límite. Los resultados, las CLIs y la paridad entre Python y TypeScript los comprobé yo ejecutando las pruebas y los builds de los dos lenguajes.
- **Backend 4 — API de actividades:**
  - Con **Claude** lo fui armando por partes: (1) la estructura inicial con Docker Compose, Nginx, Gunicorn y el CI de GitLab; (2) el usuario personalizado con el correo como identificador y los tokens JWT; (3) los modelos (Administrador, Asociado, Actividad y Solicitud de registro) con el panel de administración; (4) el endpoint público de registro y el formato uniforme de errores. En todas esas partes las pruebas venían antes que el código, o sea, primero se corrían en rojo y después venía la implementación.
  - El resto de la API lo programé yo: el CRUD de actividades, los permisos, la validación de solapamiento, la carga masiva por CSV/XLSX, OpenAPI y la configuración de PostgreSQL. Ahí usé **Copilot** solo como apoyo y para la revisión final. La carga la verifiqué con archivos multipart reales y una base PostgreSQL en Docker.

## Prompts y guías que usé

- Le pasaba el enunciado de cada reto y le pedía revisar requisito por requisito antes de darlo por terminado.
- Backend 1: identificar capas, responsabilidades de paquetes y clases, riesgos y un plan de migración seguro.
- Backend 2: desacoplar el proveedor, procesar todas las filas, reintentar con backoff y comprobar pruebas aisladas, cobertura, Ruff y mypy.
- Backend 3: validar 50 %, 90 % y 99 %, usar aritmética entera, rechazar entradas fuera de rango y comprobar las dos implementaciones y sus CLIs.
- Backend 4: trabajar con TDD (pruebas primero), separar en capas vista → servicio → repositorio, escribir pruebas de permisos e importaciones, validar fila por fila, conservar las filas válidas cuando otras fallan y verificar códigos HTTP, OpenAPI y la configuración de PostgreSQL.

## Decisiones mías y cosas que corregí

- **Backend 1:** puse como riesgos principales la autenticación social sin validar el token, los efectos secundarios de `QuestionOption.save()` y las limitaciones de SQLite. También simplifiqué la sintaxis de Mermaid para que los diagramas sí se vieran bien.
- **Backend 2:** dejé el proveedor detrás de `SentimentProvider`. Decidí guardar el libro una sola vez y dejar vacía la fila cuando el análisis falla, en vez de poner ceros que parecen resultados reales.
- **Backend 3:** comparé las proporciones con aritmética entera para evitar errores de punto flotante y dejé dos implementaciones independientes, una en Python y otra en TypeScript.
- **Backend 4:**
  - Escogí DRF porque ya lo manejo y porque el ORM, las migraciones y el admin de Django me resuelven varios requisitos (el panel y la aprobación de solicitudes, por ejemplo).
  - Pedí que la configuración saliera del `startproject` de Django para que fuera la que conozco, y solo cambié lo que tenía que leer del entorno.
  - Cuando vi contraseñas de prueba escritas en el CI pregunté si era un riesgo. Debido a esto las saqué del archivo y las pasé a variables enmascaradas de GitLab. También me aseguré de que no quedaran claves fijas de respaldo en el código.
  - Pedí hacerlo tal cual dice la prueba: Administrador y Asociado como entidades separadas, y no un solo usuario con un campo de rol.
  - La carga masiva acepta CSV y XLSX, no Word, porque el contrato no pide ese formato. Cada fila inválida se informa sin descartar las válidas.
  - Una falla que encontramos en lo que generó Claude: al crear las migraciones no salieron las de las apps nuevas y las pruebas pasaban igual. Lo detectamos al revisar los archivos y lo corregimos, y desde ahí quedó como paso de revisión que cada app nueva tenga su carpeta `migrations`.
- Al final, lo que me dio una IA lo revisé contra el enunciado, el código y las pruebas, y lo que no cuadraba lo corregí. Las IAs me sirvieron sobre todo para arrancar, contrastar ideas y revisar; el diseño final lo elegí yo y, como cuento arriba, buena parte de la API de Backend 4 la programé yo mismo.