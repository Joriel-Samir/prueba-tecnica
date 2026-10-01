# Diseño — carga masiva de asociados

## Objetivo

El diseño busca mantener la lógica de carga masiva separada del endpoint HTTP para que la operación pueda ser entendida, testeada y mantenida sin mezclar validación, persistencia y respuesta del cliente.

## Decisiones de diseño

### 1. Separación por capas
La solución se basa en la lógica existente del backend 4: la vista maneja HTTP, el serializer valida campos y el servicio aplica reglas transaccionales. Esa separación sigue el principio de responsabilidad única y permite probar la lógica de negocio sin depender del contexto del request.

### 2. Procesamiento fila por fila
Se recorrerá cada fila del archivo en un ciclo de validación. La fila se valida en aislamiento y se registra el error de esa fila si falla, sin detener el resto. Esto permite que el lote siga siendo útil incluso si hay algunas filas corruptas.

### 3. Validación concentrada en el serializer
La validación formal del esquema, longitud, campos obligatorios y formato del email se hará en el serializer de importación. Las reglas de negocio, como email duplicado o identificación repetida, se manejan en el servicio para no alejar la lógica del dominio.

### 4. Consistencia mínima por fila
Para no perder filas válidas, cada registro se crea de forma independiente en un flujo transaccional por fila. Si el lote total falla por un error inesperado de infraestructura, se documenta la falla y la respuesta debe ser explícita sobre el estado final.

### 5. Resumen de resultados estándar
La respuesta final tendrá un contenido uniforme con `total`, `created` y `errors`, para que el cliente pueda decidir si reintenta la operación o corrige el archivo.

## Alternativas descartadas

### Alternativa A: crear todo en una transacción global
Se descartó porque si una fila falla, el lote entero queda bloqueado o se revierte todo, lo que perjudica la utilidad operativa. La necesidad del negocio es seguir creando registros válidos y reportar los errores.

### Alternativa B: validar en la vista y hacer persistencia directa
Se descartó porque mezcla HTTP con dominio y complica pruebas. El servicio debe concentrar las reglas y la vista solo debe exponer la respuesta correcta.

### Alternativa C: abortar el lote al primer error
Se rechazó por el requisito de continuidad: la carga masiva debe ser tolerante a errores de fila y debe devolver un resumen útil.

## Riesgos y mitigación

- Riesgo de duplicidad: se valida email e identificación antes de persistir.
- Riesgo de cadenas mal formadas: se usa un serializer con tipos explícitos y mensajes legibles.
- Riesgo de carga innecesariamente pesada: se procesa de forma incremental para no acoplar el endpoint a una lógica de archivo completa.

## Criterio de aprobación

La solución se considerará correcta si cumple los criterios de aceptación del documento de requisitos y sigue la separación entre serialización, servicio y respuesta HTTP sin introducir lógica de negocio en la capa web.
