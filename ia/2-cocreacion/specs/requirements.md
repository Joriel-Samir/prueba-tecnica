# Requisitos — carga masiva de asociados

## Alcance

Se implementará la funcionalidad de carga masiva de asociados sobre la API existente del backend de actividades. La operación recibirá un archivo CSV o XLSX con datos de asociados, validará cada fila, creará únicamente las filas válidas y devolverá un resumen de resultados con errores por fila.

## Historias de usuario

### HU-01 — Carga inicial de asociados desde archivo
**Como** administrador del sistema  
**Quiero** subir un archivo con múltiples asociados  
**Para** registrarlos en lote sin repetir el flujo manual de creación.

**Criterios de aceptación**
1. Dado un archivo CSV o XLSX con filas válidas, cuando el administrador envía la petición con el archivo y el JWT válido, entonces el sistema crea todos los asociados válidos y devuelve un resumen con `created`, `total` y `errors`.
2. Dado un archivo con filas vacías o incompletas, cuando se procesa, entonces el sistema registra el error por fila y no bloquea el resto de registros válidos.
3. Dado un archivo con duplicados de email o identificación dentro del mismo lote, cuando se procesa, entonces el sistema marca las filas duplicadas como error sin interrumpir el resto.

### HU-02 — Validación de integridad y seguridad
**Como** administrador  
**Quiero** que el sistema rechace datos inválidos  
**Para** garantizar unicidad y consistencia del registro.

**Criterios de aceptación**
4. Dado un asociado con email ya registrado, cuando se intenta crear por carga masiva, entonces el sistema devuelve un error asociado a esa fila y conserva las demás filas válidas.
5. Dado un asociado con doble registro de `identificacion`, cuando se procesa, entonces el sistema lo marca como duplicado y no lo crea.
6. Dado un usuario no autenticado o sin permisos, cuando intenta cargar asociados, entonces el sistema responde con `401` o `403` según el tipo de error y no crea registros.

### HU-03 — Resumen operativo
**Como** administrador  
**Quiero** ver el resultado de la carga en un solo bloque  
**Para** decidir si hace corrección manual o repite la operación.

**Criterios de aceptación**
7. Dado un archivo con 10 filas y 7 válidas, cuando termina la operación, entonces la respuesta incluye `total: 10`, `created: 7` y una lista de `errors` con exactamente 3 elementos.
8. Dado un error de formato o valor faltante, cuando la fila se rechaza, entonces la respuesta incluirá el número de fila y el detalle del error.
9. Dado un archivo con filas válidas y rechazadas, cuando la operación termina, entonces la API devuelve `200` en vez de fallar todo el lote.

### HU-04 — Reversión y consistencia transaccional
**Como** equipo técnico  
**Quiero** que el procesamiento del lote sea consistente  
**Para** no dejar el sistema en un estado parcial e inconsistente.

**Criterios de aceptación**
10. Dado una fila válida y otra inválida, cuando se procesa la carga, entonces la aplicación crea las válidas y reporta las inválidas sin revertir las exitosas.
11. Dado una excepción inesperada durante la ejecución, cuando la operación falla, entonces la transacción no deja registros parcialmente creados sin que la respuesta lo indique de forma explícita.

## Restricciones de negocio

- La carga debe aceptar únicamente archivos `.csv` o `.xlsx`.
- La autenticación debe ser JWT de usuario administrador.
- Los campos mínimos requeridos son `email`, `password`, `identificacion`, `nombre`, `apellidos`, `ciudad`.
- Cualquier error de fila debe ser reportado sin abortar el lote.
- La operación debe expirar con un mensaje claro cuando el archivo no cumple con el esquema esperado.

## Definición de listo

La funcionalidad está lista cuando:
- los tests de integración cubren los escenarios de éxito y error;
- la API devuelve un payload consistente;
- la documentación de la ruta está disponible en la OpenAPI del proyecto;
- la validación por permisos es explícita y comprobable.
