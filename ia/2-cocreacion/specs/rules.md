# Guía de reglas para el asistente de IA

## Propósito

Este documento define cómo debe colaborar la IA durante la construcción del sistema de actividades y, en particular, la funcionalidad de carga masiva de asociados.

## Reglas del proyecto

1. Mantener el dominio delegado a la capa adecuada: vista, serializer, servicio y repositorio.
2. No introducir lógica de negocio en la capa HTTP.
3. No aceptar cambios que contradigan permisos o reglas de negocio ya definidas.
4. Cada historia debe tener un criterio de aceptación verificable antes de la implementación.
5. Todas las decisiones de negocio relevantes deben quedar documentadas en requisitos o diseño.
6. Las pruebas deben ejecutarse antes de cerrar una tarea de implementación.

## Reglas de seguridad

- No escribir tokens, password reales ni secretos en el repositorio.
- No ejecutar comandos destructivos ni despliegues a producción sin aprobación humana.
- No instalar dependencias sin revisar si la política del proyecto las autoriza.
- No crear archivos temporales persistentes con datos sensibles.

## Reglas de calidad

- Hacer cambios pequeños y trazables.
- Mantener subidas limpias y revisar el alcance del PR.
- Evitar cambiar el diseño aprobado a menos que exista una justificación explícita y una decisión de escalamiento.
- Usar pruebas de borde y no solo escenarios felices.

## No hacer nunca

- No asumir reglas de negocio sin confirmación.
- No inventar fechas o zonas horarias sin consultar el contexto del negocio.
- No silenciosamente ignorar errores de fila en la carga masiva.
- No mezclar validación de UI con lógica de persistencia.
- No reemplazar la especificación por una propuesta “bonita” del modelo.

## Criterio de aprobación humana

Toda decisión que afecte permisos, seguridad, datos sensibles o cambios de alcance debe ser revisada por una persona antes de integrarse.
