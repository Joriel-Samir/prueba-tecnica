# Plan — carga masiva de asociados

## Unidades de trabajo

### IA2-UT-01 — XS — Definir contrato de importación
**Objetivo:** fijar el formato de entrada y la respuesta esperada.  
**Criterio asociado:** HU-01, HU-03.  
**Entregable:** payload de entrada, estructura de salida y errores por fila.

### IA2-UT-02 — S — Validación de fila y esquema
**Objetivo:** validar campos obligatorios y tipos.  
**Criterio asociado:** HU-02, HU-03.  
**Entregable:** serializer o validador con reglas mínimas de formato.

### IA2-UT-03 — S — Detección de duplicados y reglas de negocio
**Objetivo:** impedir registros repetidos y asegurar integridad.  
**Criterio asociado:** HU-02, HU-04.  
**Entregable:** servicio de registro con chequeos de email e identificación.

### IA2-UT-04 — M — Procesamiento por lote y resumen final
**Objetivo:** recorrer archivo, crear registros válidos y acumular errores.  
**Criterio asociado:** HU-01, HU-03.  
**Entregable:** flujo de carga masiva con total, created y errors.

### IA2-UT-05 — M — Endpoint HTTP con permisos
**Objetivo:** exponer la operación en la API con autenticación JWT y permisos.  
**Criterio asociado:** HU-02, HU-04.  
**Entregable:** endpoint protegido y respuesta normalizada.

### IA2-UT-06 — S — Pruebas de integración y regresión
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

## Trazabilidad de la implementación existente

La funcionalidad de carga masiva de asociados fue implementada en Backend 4 antes
de que estas unidades recibieran sus identificadores estables. Por transparencia,
la relación histórica verificable es:

- `IA2-UT-01` a `IA2-UT-05`: `c84149e` (`feat: complete associate and activity API requirements`).
- `IA2-UT-06`: `07f1403` (`test: verify XLSX associate imports and invalid files`).
- Especificación y guía: `27154d0` (`docs: add co-creation specs for bulk-load feature`).

Los commits nuevos deben incluir explícitamente el identificador de la unidad,
por ejemplo `IA2-UT-06: ampliar pruebas de carga masiva`.
