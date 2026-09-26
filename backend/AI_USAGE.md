# Declaración de Uso de Inteligencia Artificial

En cumplimiento con los lineamientos de la prueba técnica, a continuación se detalla el uso de herramientas de Inteligencia Artificial como apoyo durante el desarrollo de los retos.

## Herramientas Usadas
* **Asistente:** Asistente de IA integrado en mi editor de código y Google antigravity especificamente Gemini 3.1 Pro 
* **Propósito:** Leer los archivos más rápido, generar la estructura base para los documentos de texto (Markdown) y ayudar con la sintaxis de los diagramas Mermaid.

## Retos en los que se utilizó
* **Backend 1 — Análisis de Arquitectura:** Utilicé el asistente para procesar de forma rápida el código fuente de los paquetes principales (`diagnosis`, `auth`, `corozina`) y armar el primer borrador del documento `ANALISIS.md`.

## Prompts y Guías Relevantes
* *"Se analiza una Web API existente construida con Python 3.7 y Django 3 para el registro de pacientes... Defina las capas de la aplicación... Defina la responsabilidad de cada paquete..."* -> Le pasé el enunciado original para darle contexto inicial de lo que se iba a evaluar.
* *"Devuelve los cambios, no se ven bien los flujogramas ni los modelos..."* -> Le pedí a la IA que revirtiera y corrigiera los diagramas, ya que inicialmente los había sobrecargado con estilos visuales que no cargaban bien.

## Decisiones tomadas sin la IA y correcciones manuales

Si bien el asistente fue de gran ayuda para extraer el código y armar la estructura inicial, el análisis final tiene mi revisión detallada y decisiones propias:

1. **Definición de la estrategia de migración:** Al principio, la IA sugería pasar a Django 5 directamente. Fui yo quien decidió plantear una estrategia más segura: definí que el primer paso indispensable debía ser reactivar y reparar las pruebas unitarias (`test_views.py`), y que la migración debía hacerse paso a paso por versiones LTS (3.2 -> 4.2 -> 5.x) para no romper el sistema.
2. **Corrección técnica de los Diagramas Mermaid:** La IA generó diagramas con estilos CSS y una sintaxis compleja que rompía la visualización normal de Markdown. Tuve que intervenir, echar atrás esos cambios y obligarla a usar la sintaxis clásica y universal para asegurar que los gráficos se pudieran ver bien en cualquier visor.
3. **Selección y enfoque de Riesgos Arquitecturales:** La herramienta me listaba riesgos muy genéricos. Fui yo quien filtró, analizó y eligió los 3 riesgos reales que más afectarían a este proyecto:
   * El problema de seguridad en `CustomAuth` donde se confía ciegamente en el token social.
   * El mal uso de métodos como `save()` en `QuestionOption` que mezcla lógica y base de datos.
   * El gran problema que causaría usar `sqlite3` cuando la aplicación tenga muchos usuarios interactuando al mismo tiempo.
4. **Límites de exploración:** Fui yo quien guió y limitó qué carpetas debía revisar el asistente, enfocándome solo en el código fuente importante y dejando por fuera archivos irrelevantes, para asegurar que el análisis fuera exacto.
