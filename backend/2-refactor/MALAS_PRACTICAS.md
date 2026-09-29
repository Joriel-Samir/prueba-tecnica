# Análisis de Malas Prácticas y Propuesta de Refactorización

## 1. Identificación de Malas Prácticas

---

### 1.1. Clave configurada por defecto en el código (Hardcoding)
*   **Línea:** 11 (`key="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"`)
*   **Principio vulnerado:** Seguridad y Configuración externa (The Twelve-Factor App).
*   **Impacto:** El valor mostrado parece un placeholder, no una credencial real; aun así, definir la clave como valor por defecto fomenta reemplazarla por un secreto dentro del código. Si se versiona una clave real, queda expuesta, y cambiarla requiere editar el código.

### 1.2. Fuerte Acoplamiento (Tight Coupling)
*   **Línea:** 27 (`paralleldots.sentiment(...)`)
*   **Principio vulnerado:** Principio de Inversión de Dependencias (Dependency Inversion Principle - SOLID).
*   **Impacto:** El algoritmo de análisis de Excel está atado directamente a la implementación de la librería `paralleldots`. Si el servicio cambia, deja de existir, o se desea probar otra IA (ej. OpenAI), es necesario reescribir la lógica core. Además, impide realizar pruebas unitarias aisladas sin consumir crédito de la API real.

### 1.3. Lógica Estática e Ignorancia de Estado
*   **Línea:** 24 (`for row in range(2, 4):`)
*   **Principio vulnerado:** Reusabilidad y procesamiento basado en los datos de entrada.
*   **Impacto:** En la línea 20 se obtiene el número total de filas (`max_row = sheet.max_row`), pero el bucle no lo usa y procesa solo las filas 2 y 3. Los registros posteriores se omiten, independientemente del tamaño del archivo.

### 1.4. Operaciones I/O Ineficientes en Bucle (Problema de Rendimiento)
*   **Línea:** 44 (`workbook.save("sentimentAnalysis.xlsx")`)
*   **Principio vulnerado:** Eficiencia y Gestión de Recursos (Performance).
*   **Impacto:** Guardar un archivo en disco es una operación costosa. Al estar dentro del bucle `for`, el script reescribe todo el archivo Excel por cada fila procesada. Para un archivo de miles de registros, esto colapsará el disco (I/O Bottleneck) y hará la ejecución extremadamente lenta.

### 1.5. Esperas Fijas y Falta de Resiliencia (Tolerancia a fallos)
*   **Líneas:** 27 (llamada a API sin `try/except`) y 43 (`time.sleep(10)`).
*   **Principio vulnerado:** Resiliencia (Robustness) y Manejo de Excepciones.
*   **Impacto:** Si la API devuelve un error (por falta de red o límite de cuota), el script crashea perdiendo el progreso. Adicionalmente, el `sleep(10)` fuerza una espera incondicional de 10 segundos por iteración, lo que resulta ineficiente.

### 1.6. Llamadas Redundantes
*   **Línea:** 26 (`paralleldots.set_api_key(self.key)`; también se configura en la línea 17)
*   **Principio vulnerado:** DRY (Don't Repeat Yourself).
*   **Impacto:** Se vuelve a inyectar la llave de la API en cada iteración del bucle de forma innecesaria.

### 1.7. Pobre Interfaz de Usuario y Observabilidad
*   **Líneas:** 25, 46 y 59 (`print`); 53-55 (manejo manual de `sys.argv`).
*   **Principio vulnerado:** Observabilidad (Logging) y Clean Code.
*   **Impacto:** El uso de `print` no permite trazabilidad en sistemas de producción (no guarda niveles de severidad ni marcas de tiempo). Leer `sys.argv` condicionalmente es propenso a errores y poco amigable para el usuario que ejecuta el script.

---

## 2. Estrategia de Refactorización

La refactorización de `src/` aborda las prácticas anteriores de la siguiente manera:

1. **Credenciales expuestas:** `src/main.py` obtiene `PARALLELDOTS_API_KEY` del entorno después de cargar `.env` mediante `python-dotenv`. Si no está definida, informa el problema con logging y termina sin incluir una clave real en el código.
2. **Acoplamiento al proveedor:** `src/provider.py` define la abstracción `SentimentProvider`; `ExcelSentimentAnalyzer` recibe un proveedor por constructor. Así, la lógica de Excel no depende de ParallelDots y las pruebas pueden inyectar dobles.
3. **Límite fijo de filas:** `src/analyzer.py` recorre desde la fila 2 hasta `sheet.max_row`, por lo que procesa la extensión real de la hoja.
4. **Guardado repetido:** los resultados se escriben en memoria durante el recorrido y `workbook.save(output_path)` se ejecuta una sola vez al terminar.
5. **Errores y espera fija:** `ParallelDotsProvider` reintenta hasta tres veces ante excepciones con backoff exponencial (2 y 4 segundos), registra cada intento y finalmente comunica `SentimentAnalysisError`. El analizador captura ese error por fila y deja sus celdas sin resultados, sin detener el procesamiento del resto del archivo.
6. **Configuración redundante del cliente:** `paralleldots.set_api_key` se llama una vez al construir `ParallelDotsProvider`, no por cada texto procesado.
7. **Interfaz y observabilidad:** `src/main.py` usa `argparse` para entrada, salida, hoja y columna; la aplicación usa `logging` en lugar de `print`.

Además, las funciones de producción y de prueba incluyen anotaciones de tipos; Ruff y mypy se configuran en `pyproject.toml`. Las pruebas usan proveedores dobles y mocks de la llamada a ParallelDots, sin consumir el servicio real. La cobertura se mide sobre `src` con un umbral mínimo del 80 %.

## 3. Comportamiento conservado y diferencias intencionales

El refactor conserva el flujo principal del original: abre un Excel, usa la hoja activa por defecto, lee el texto de la columna 3, escribe los encabezados NEGATIVO/NEUTRAL/POSITIVO en las columnas 4–6 y guarda el resultado como `sentimentAnalysis.xlsx` por defecto. Las puntuaciones de ParallelDots siguen convirtiéndose a porcentajes y redondeándose a tres decimales.

No conserva literalmente los defectos del original: procesa todas las filas existentes en vez de limitarse a las filas 2 y 3; omite celdas vacías; guarda una sola vez al final; obtiene la clave desde el entorno; y reintenta con backoff solo ante errores, en vez de esperar 10 segundos tras cada llamada. Si falla el análisis de una fila, deja sus resultados en blanco en vez de escribir ceros que podrían confundirse con resultados reales. La CLI también se reemplazó por `argparse`; la entrada sigue siendo el archivo indicado por el usuario y la salida predeterminada conserva el mismo nombre.