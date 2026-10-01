# Plan — carga masiva de asociados

## Unidades de trabajo

### 1. XS — Definir contrato de importación
**Objetivo:** fijar el formato de entrada y la respuesta esperada.  
**Criterio asociado:** HU-01, HU-03.  
**Entregable:** payload de entrada, estructura de salida y errores por fila.

### 2. S — Validación de fila y esquema
**Objetivo:** validar campos obligatorios y tipos.  
**Criterio asociado:** HU-02, HU-03.  
**Entregable:** serializer o validador con reglas mínimas de formato.

### 3. S — Detección de duplicados y reglas de negocio
**Objetivo:** impedir registros repetidos y asegurar integridad.  
**Criterio asociado:** HU-02, HU-04.  
**Entregable:** servicio de registro con chequeos de email e identificación.

### 4. M — Procesamiento por lote y resumen final
**Objetivo:** recorrer archivo, crear registros válidos y acumular errores.  
**Criterio asociado:** HU-01, HU-03.  
**Entregable:** flujo de carga masiva con total, created y errors.

### 5. M — Endpoint HTTP con permisos
**Objetivo:** exponer la operación en la API con autenticación JWT y permisos.  
**Criterio asociado:** HU-02, HU-04.  
**Entregable:** endpoint protegido y respuesta normalizada.

### 6. S — Pruebas de integración y regresión
**Objetivo:** comprobar escenarios válidos y de error.  
**Criterio asociado:** HU-01 a HU-04.  
**Entregable:** suite con casos de éxito, duplicado, fila incompleta y permisos.

## Orden sugerido

1. Contrato de importación.
2. Validación de esquema y filas.
3. Reglas de negocio y duplicados.
4. Ciclo de creación por lote.
5. Endpoint y permisos.
6. Pruebas y correcciones.

## Criterio de fin

La funcionalidad se entregará cuando cada unidad de trabajo tenga prueba asociada y el conjunto de requisitos quede cubierto sin contradicciones entre el plan, el diseño y el código.
