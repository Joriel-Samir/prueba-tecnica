# Análisis de Malas Prácticas y Propuesta de Refactorización

## 1. Identificación de Malas Prácticas

---

## 1. Identificación de Malas Prácticas

### 1.1. Credenciales expuestas (Hardcoding)
*   **Línea:** 9 (`key='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'`)
*   **Principio vulnerado:** Seguridad y Configuración externa (The Twelve-Factor App).
*   **Impacto:** Riesgo crítico de seguridad. Subir secretos al control de versiones (Git) expone las credenciales. Además, obliga a modificar el código fuente si la llave cambia.

### 1.2. Fuerte Acoplamiento (Tight Coupling)
*   **Líneas:** 21, 22 (`paralleldots.sentiment(...)`)
*   **Principio vulnerado:** Principio de Inversión de Dependencias (Dependency Inversion Principle - SOLID).
*   **Impacto:** El algoritmo de análisis de Excel está atado directamente a la implementación de la librería `paralleldots`. Si el servicio cambia, deja de existir, o se desea probar otra IA (ej. OpenAI), es necesario reescribir la lógica core. Además, impide realizar pruebas unitarias aisladas sin consumir crédito de la API real.

### 1.3. Lógica Estática e Ignorancia de Estado
*   **Línea:** 19 (`for row in range(2, 4):`)
*   **Principio vulnerado:** Reusabilidad y Principio Abierto/Cerrado.
*   **Impacto:** Aunque en la línea 15 el código calcula correctamente el número total de filas (`max_row = sheet.max_row`), el bucle ignora esta variable y procesa *estrictamente* solo las filas 2 y 3. Esto hace que el script sea inútil para archivos de diferentes tamaños.

### 1.4. Operaciones I/O Ineficientes en Bucle (Problema de Rendimiento)
*   **Línea:** 29 (`workbook.save('sentimentAnalysis.xlsx')`)
*   **Principio vulnerado:** Eficiencia y Gestión de Recursos (Performance).
*   **Impacto:** Guardar un archivo en disco es una operación costosa. Al estar dentro del bucle `for`, el script reescribe todo el archivo Excel por cada fila procesada. Para un archivo de miles de registros, esto colapsará el disco (I/O Bottleneck) y hará la ejecución extremadamente lenta.

### 1.5. Esperas Fijas y Falta de Resiliencia (Tolerancia a fallos)
*   **Líneas:** 22 (Llamada a API sin `try/except`) y 28 (`time.sleep(10)`).
*   **Principio vulnerado:** Resiliencia (Robustness) y Manejo de Excepciones.
*   **Impacto:** Si la API devuelve un error (por falta de red o límite de cuota), el script crashea perdiendo el progreso. Adicionalmente, el `sleep(10)` fuerza una espera incondicional de 10 segundos por iteración, lo que resulta ineficiente.

### 1.6. Llamadas Redundantes
*   **Línea:** 20 (`paralleldots.set_api_key(self.key)`)
*   **Principio vulnerado:** DRY (Don't Repeat Yourself).
*   **Impacto:** Se vuelve a inyectar la llave de la API en cada iteración del bucle de forma innecesaria.

### 1.7. Pobre Interfaz de Usuario y Observabilidad
*   **Líneas:** 10, 20 (`print`) y 34-39 (Manejo rústico de `sys.argv`).
*   **Principio vulnerado:** Observabilidad (Logging) y Clean Code.
*   **Impacto:** El uso de `print` no permite trazabilidad en sistemas de producción (no guarda niveles de severidad ni marcas de tiempo). Leer `sys.argv` condicionalmente es propenso a errores y poco amigable para el usuario que ejecuta el script.

---

## 2. Estrategia de Refactorización

Por ahora defino la arquitectura de la solucion basandonde en principios SOLID 
