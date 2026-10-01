# IA 2 — Co-creación en desarrollo guiado por guías

## A. Fundamentos

### 1. ¿Qué diferencia hay entre usar un asistente de IA de forma ad hoc ("vibe coding") y un desarrollo guiado por guías? ¿Qué problemas concretos resuelve el segundo en un equipo?

La diferencia principal es que el "vibe coding" trata la IA como un generador de texto que puede producir rapidez, pero sin una línea de responsabilidad clara sobre requisitos, decisiones de diseño ni validación. El resultado suele ser código que parece correcto, pero no está ligado a un contrato de negocio ni a una prueba que lo defienda. En cambio, el desarrollo guiado por guías convierte la IA en una herramienta de colaboración dentro de un proceso: se trabaja con reglas de proyecto, especificaciones aprobadas, criterios verificables y puntos de aprobación humana. Esto reduce la deriva del código, porque el equipo no se mueve a ciegas sobre una idea que el modelo “parece entender”.

En un equipo, este enfoque resuelve varios problemas reales: la pérdida de contexto, la solución basada en suposiciones y la inconsistencia entre diseño y código. Cuando varias personas tocan el mismo dominio, la guía evita duplicar decisiones opuestas, deja un histórico de por qué se hizo algo y hace explícito qué se consideró fuera de alcance. También evita que la IA “arme” una solución elegante que contradice el diseño acordado o la seguridad del sistema. En mi experiencia, el valor no está en hacer más código más rápido, sino en mantener la trazabilidad y la calidad del artefacto final.

### 2. En un ciclo con fases de concepción (Inception), construcción (Construction) y operación (Operations), ¿qué artefactos esperaría que salgan de cada fase y quién debe aprobarlos?

En Inception espero definiciones del problema, alcance, usuarios, riesgos, supuestos y una primera visión de arquitectura. El artefacto más importante es una especificación de requisitos con historias de usuario, criterios de aceptación y un diseño preliminar de alto nivel. También debería haber un plan de trabajo con estimación, riesgos y dependencias. La aprobación debe venir del producto y de la parte técnica responsable, y en proyectos con impacto alto también de seguridad o negocio.

En Construction, el artefacto principal es el diseño detallado, la partición en unidades de trabajo y la evidencia de ejecución: pruebas, revisión de código, trazabilidad requisitos → implementación y, si aplica, cambios de configuración. La aprobación debe ser de un responsable de entrega y de la persona o equipo técnico que asumirá la operación. En otras palabras, la construcción no se termina con un “se ve bien”, sino con verificaciones concretas.

En Operations, espero observabilidad, despliegue documentado, runbooks y métricas de incidencia. La aprobación final debería ser del propietario del servicio y de quien opera el sistema, no solo del equipo que lo construyó. Si la solución cambia reglas de negocio o afecta seguridad, el negocio también debe validar la operación final.

### 3. ¿Qué debe contener un archivo de reglas o guía del proyecto (por ejemplo AGENTS.md, CLAUDE.md, reglas de steering) y qué no debe contener nunca?

Un archivo de reglas del proyecto debe definir el contexto operativo del equipo: alcance, stack tecnológico, convenciones de arquitectura, política de seguridad, flujo de aprobación, estrategia de pruebas, criterios de calidad y normas de uso de la IA. Debe decir qué puede hacer el agente, cuál es el repositorio de verdad, qué comandos se consideran seguros y qué artefactos son inamovibles: por ejemplo, “no se despliega sin revisar la seguridad”, “las pruebas deben ser ejecutadas antes de abrir PR” o “este servicio usa Django con permisos por recurso”. También debe indicar cómo se aceptan cambios en diseño y cuándo debe solicitar confirmación humana.

No debe contener nunca secretos, tokens, endpoints reales, datos sensibles ni instrucciones que dependan de un entorno privado. Debe evitar prometer “todo lo que haga la IA será correcto” o caer en receta de programación genérica sin contexto. Tampoco debe imponer una arquitectura ficticia ni directivas contradictorias con el repositorio real. En mi práctica, el mejor documento de reglas es prescriptivo, breve y verificable: da límites, no solo buenos deseos. Si el agente no puede inferir la decisión de negocio a partir de la regla, no es una regla útil; es simplemente un comentario.

## B. Especificaciones como contrato

### 4. ¿Cómo redacta un criterio de aceptación para que sea verificable tanto por una persona como por una prueba automática? Escriba dos ejemplos para la regla "el asociado solo puede editar actividades presentes y futuras".

Un criterio de aceptación verificable debe limitarse a un comportamiento observable, con datos concretos y una condición que pueda evaluarse automáticamente. Lo ideal es usar una acción, un contexto de usuario y un resultado esperado: “Dado X, cuando Y, entonces Z”. Eso produce un criterio entendible por una persona y ejecutable por una prueba de integración o backend.

Ejemplo 1: “Dado un asociado autenticado con actividades en 2026-09-01 y 2026-09-10, cuando intenta editar la actividad del 2026-09-05, entonces el sistema permite la actualización si la fecha de inicio es mayor o igual a hoy y rechaza la operación si la actividad ya finalizó”. La prueba se ejecuta con dos registros: uno futuro y otro terminado; la respuesta debe ser 200 para el primero y 403 o 400 para el segundo.

Ejemplo 2: “Dado un asociado que intenta actualizar una actividad histórica del 2026-08-30, cuando la fecha de finalización es anterior a la fecha actual, entonces el sistema no persiste cambios y devuelve un error de validación con código de negocio `actividad_no_vigente`.” Aquí la parte verificable es doble: no hay persistencia y el error tiene un código estable. Ese tipo de criterio sirve tanto para QA humana como para tests automáticos porque no depende de interpretación subjetiva.

### 5. Durante la construcción, la IA propone una solución que funciona pero contradice el documento de diseño aprobado. ¿Qué hace: corrige el código, actualiza el diseño o escala la decisión? ¿Con qué criterio?

La respuesta depende del tipo de contradicción y del riesgo. Si la propuesta funciona pero rompe un contrato de seguridad, un flujo de permisos o un requisito ya aprobado, no se corrige el código “porque funciona”; se corrige la solución y se revalida. Si la diferencia es en un detalle de implementación que no afecta el contrato ni la operación, el criterio suele ser si la decisión aumenta complejidad sin beneficio claro. Si la contradicción es real y el diseño aprobada no era suficiente, entonces hay que escalar la decisión: se abre un cambio de alcance, se documenta el motivo y se revisa el documento de diseño antes de seguir.

El criterio más útil es el riesgo e impacto: si la solución compromete seguridad, compatibilidad, trazabilidad o costo de operación, no se acepta. Si la contradicción solo cambia el mecanismo y mantiene el comportamiento, puede quedarse solo si no rompe la especificación ni la política del sistema. En resumen, la IA no decide por sí sola sobre el diseño; la decisión la toma el responsable del servicio, con base en impacto, no en estética de código.

### 6. ¿Cómo evita que la especificación y el código diverjan con el tiempo? Describa el mecanismo, no la intención.

La forma más efectiva es establecer una trazabilidad formal entre requisitos y código. En la práctica eso significa que cada historia o criterio lleva un identificador único, y cada commit o PR referencia la unidad de trabajo o el criterio que implementa. La especificación queda viva en un repositorio y el código no se puede mergear si no cumple con las pruebas que validan esos criterios. Luego, la revisión de diseño y la bitácora documentan cualquier excepción o cambio de alcance.

En un flujo bien hecho, cada requisito genera pruebas de aceptación y cada PR se asocia con la historia. Esto permite detectar divergencia con automatización: si un criterio de aceptación no tiene evidencia de prueba, es sospechoso; si el código ya no cumple una historia que fue aprobada, el sistema de revisión lo ve. La divergencia no se evita solo por disciplina, sino por un mecanismo de enlace explícito entre contrato, implementación y validación. Esa es la única forma de que la especificación siga siendo una fuente de verdad y no un documento que quedó atrás.

### 7. ¿Qué tamaño debe tener una unidad de trabajo que se delega a un agente de IA? ¿Cómo la divide si el requerimiento original es "implementar la carga masiva de asociados"?

La unidad de trabajo debe ser pequeña y acotada: ni un epic enorme ni un detalle micro que no aporte contexto. En general, una tarea delegable a IA debe tener un objetivo claro, un alcance limitado y una prueba de aceptación asociada. En equipos, una tarea útil suele ser de tamaño XS, S o M: no más de una historia principal con una o dos dependencias técnicas, y con resultados observables. Si un requerimiento entra en la categoría de “hacer un módulo completo”, se debe dividir en piezas más pequeñas.

Para la carga masiva de asociados, yo la dividiría en varias unidades: validación del formato del archivo, lectura y normalización de filas, manejo de errores y reintentos por fila, validación de duplicados y reglas de negocio, persistencia con transacción y reporte de resultados. Después vendría el endpoint HTTP, la autenticación y permisos, la documentación de la API, y la cobertura de pruebas de integración. La clave es que cada unidad entregue algo verificable y no dependa de un “gran final” que el agente no pueda sostener sin pérdida de contexto.

## C. Co-creación humano–IA

### 8. ¿En qué momentos del proceso la aprobación humana es innegociable y en cuáles la considera burocracia? Justifique con riesgo e impacto.

La aprobación humana es innegociable cuando el cambio afecta seguridad, permisos, integridad de datos, cumplimiento legal o decisiones de negocio no derivadas del código. Por ejemplo, cualquier cambio en autenticación, autorizaciones, eliminación de registros, tratamiento de datos sensibles, manejo de inventarios o fraccionamiento de pagos requiere aprobación explícita. También es innegociable cuando la IA propone redefinir un criterio de negocio o una regla operativa.

La burocracia, en cambio, aparece cuando el procedimiento repite validaciones sin impacto real: por ejemplo, pedir aprobación humana para un cambio cosmético, un nombre de variable, una reorganización de código sin alteración del comportamiento o una refactorización de bajo riesgo que ya tenía pruebas de regresión. No todo requiere “human review” porque eso hace más lento el proceso y también aumenta el coste de decisión. La regla que uso es simple: si el riesgo es material, la aprobación es obligatoria; si el riesgo es prácticamente nulo y la evidencia es clara, la IA puede avanzar bajo el proceso automatizado y la revisión técnica del responsable.

### 9. Describa una situación real en la que la IA le entregó código plausible pero incorrecto. ¿Cómo lo detectó y qué cambió después en su forma de trabajar?

Una situación típica ocurrió cuando la IA proponía una validación “rápida” de fechas en una carga masiva: evaluaba solo el valor de la cadena, pero no el contexto de negocio ni la regla de no solapamiento. El código parecía correcto y hasta pasaba pruebas unitarias triviales, pero fallaba al comparar fechas en la zona horaria del negocio y al incluir el caso de actividades contiguas. Lo detecté al revisar un caso real del flujo de producción y al ejecutar pruebas de integración con datos límite. La solución no era “más prompt”, sino un cambio de método: validar contra la especificación, forzar criterios aceptables, y exigir pruebas que representen el escenario de negocio, no solo el happy path.

Después cambié mi forma de trabajar. Ya no acepto una solución que no tenga un criterio verificable, un caso de borde y una prueba que muestre el comportamiento exacto. También me volví más estricto con la IA: le pido primero el diseño de la solución y luego la implementación, y nunca la dejo validar un detalle crítico sin contexto del negocio. El criterio de calidad pasó de “se ve bien” a “se demuestra con evidencia”.

### 10. ¿Cómo trabajarían tres desarrolladores y varios agentes de IA sobre la misma especificación sin pisarse? Considere ramas, propiedad del trabajo y revisión.

Lo más sano es dividir la especificación en unidades de trabajo con propietarios claros y ramas de feature separadas. Cada desarrollador toma una parte del contrato: por ejemplo, un responsable del importador, otro del endpoint y permisos, y otro de pruebas y observabilidad. Cada una de esas piezas tiene una historia, una prueba de aceptación y un alcance acotado. Los agentes de IA trabajan sobre la misma rama solo con tareas aisladas y bajo un esquema de revisión de cambios, no con libre edición sobre el mismo módulo.

La propiedad del trabajo es esencial: cada persona es responsable del criterio y del código de su unidad. Se usan pull requests pequeños, revisados por otra persona, y se evita crear cambios cruzados que mezclen dos historias. Para evitar que la IA se “pisotee” a sí misma, se establece un plan de trabajo y una bitácora de decisiones; cada cambio debe estar ligado a un criterio y cada conflicto se resuelve como un cambio de diseño, no como un arreglo manual sin contexto. Esto crea una disciplina de colaboración que es mucho más estable que dejar a 3 desarrolladores y 3 agentes “en paralelo” sin límite.

### 11. ¿Qué información del contexto de negocio le daría a un agente al inicio de la sesión de concepción y qué preguntas esperaría que el agente le haga antes de proponer requisitos?

Le daría el contexto del problema en términos de usuarios, reglas de negocio, riesgos, canales de operación y restricciones. En un sistema de actividades, eso incluye quién puede crear o editar actividades, cómo se definen los permisos, qué significa “presente y futura”, qué zonas horarias aplica, qué ciudades o equipos tienen límites, y cuál es el flujo de aprobación real. También sería importante compartir ejemplos de casos reales: por ejemplo, “María Gómez cambia una reunión y tiene que ser validada por un administrador” o “la carga masiva debe ignorar filas inválidas sin bloquear el resto”.

Antes de proponer requisitos, esperaría que el agente haga preguntas muy concretas: ¿quiénes son los actores y qué permisos tienen? ¿Qué significa no solapar actividades? ¿Qué fechas consideran “presente” y “futura” en la zona horaria del negocio? ¿Qué se hace con filas inválidas en una carga masiva? ¿Qué debe ser visible en la respuesta del sistema y qué debe quedar fuera del log? Si el agente no hace esas preguntas, sospecho que está proponiendo requisitos a partir de suposiciones. En contextos con impacto real, eso es exactamente lo que se debe evitar.

## D. Calidad, seguridad y trazabilidad

### 12. ¿Cómo combina TDD con un agente de IA? ¿Quién escribe las pruebas, quién la implementación y en qué orden?

La combinación más sólida es empezar por una prueba de aceptación escrita por una persona o por una persona con el contexto del negocio, y luego dejar que el agente implemente el mínimo para hacerla pasar. TDD no es un ritual de “escribir primero una prueba” por sí solo; es una manera de fijar el contrato antes de la implementación. La prueba define el comportamiento observável, y la implementación cumple ese contrato. El agente puede ayudar a escribir o refinar la prueba, pero quien debe decidir la intención del negocio es el humano.

El orden ideal es: 1) escribir o revisar el criterio de aceptación; 2) generar la prueba mínima; 3) ejecutar la prueba y confirmar que falla; 4) pedir al agente una propuesta de implementación; 5) validar con las pruebas existentes y con casos de borde; 6) refactorizar con seguridad. Esto evita el clásico problema de que la IA “adivine” el comportamiento y luego haga una prueba para declararlo correcto. En otras palabras, la prueba va primero como contrato, la implementación luego como consecuencia, y la revisión humana cierra la diferencia entre el comportamiento esperado y el que realmente se entrega.

### 13. ¿Qué controles aplica antes de fusionar código generado por IA? Distinga los automatizados de los humanos.

Los controles automatizados deben incluir lint, type checking, pruebas unitarias e integración, análisis de seguridad y, si aplica, validación de dependencias. En un proyecto con Django, eso implica ruff, pytest, migraciones verificadas, revisión de permisos y el caso de negocio de la historia. También es útil exigir que cada PR referencie la especificación y que las pruebas de aceptación vayan en el mismo cambio.

Los controles humanos incluyen revisión de código por alguien que entienda el dominio, comprobación de riesgos de seguridad y negocio, validación del alcance del PR y aprobación del diseño si hubo cambio. Además, se debe revisar que la IA no haya añadido dependencias no aprobadas, generado logs con datos sensibles o embebido secretos. La disciplina aquí no es “nunca confiar en la IA”, sino construir una capa de defensa que haga que la evidencia sea más importante que la apariencia. Cuando se combina automatización con revisión humana, se reduce la posibilidad de que un cambio plausible pero incorrecto llegue a main.

### 14. ¿Cómo evita que un agente exponga secretos, introduzca dependencias no aprobadas o ejecute comandos destructivos?

La defensa comienza con reglas del proyecto y con un entorno controlado. El agente no debe tener acceso a tokens de producción ni a claves del entorno; en el repositorio, los secretos deben vivir en variables de entorno y nunca versionarse. Debe existir una lista de dependencias autorizadas y una política de instalación: si un paquete no está aprobado, el agente no puede añadirlo sin explicitación y revisión. En la práctica se usan políticas de seguridad, escaneos de dependencias y una validación del lockfile.

Para comandos destructivos, el principio es simple: no ejecutar acciones fuera de un ámbito seguro. Se restringen comandos de `rm -rf`, despliegues a producción, migraciones no autorizadas y rebases agresivos, y se exige confirmación humana para cualquiera de esos escenarios. También es útil separar el entorno de trabajo del entorno de producción y mantener un registro de la acción ejecutada. La seguridad no se resuelve con “confianza”, se resuelve con restricciones, trazabilidad y revisión. Un agente debe operar dentro de un perímetro que el equipo haya validado previamente.

### 15. Seis meses después, alguien pregunta por qué una regla de negocio está implementada de cierta forma. ¿Dónde debería encontrar la respuesta y cómo garantiza que exista?

La respuesta debería encontrarse en la trazabilidad del proyecto: especificación, decisiones de diseño, historial de PR, bitácora de aprobación y, sobre todo, una prueba de aceptación vinculada a la historia. No basta con un comentario en el código, porque se vuelve frágil. La conexión correcta es requisito → diseño → tarea → implementación → prueba → PR. Si la regla de negocio se explica en una historia y se valida con una prueba, esa evidencia permite responder por qué se hizo así.

Para garantizarlo, cada cambio debe tener una historia, un criterio de aceptación y una prueba vinculada. En la revisión del PR comprobaría que el identificador del criterio aparezca en la tarea, en la prueba y en la evidencia de ejecución. La bitácora y el diseño documentan decisiones no evidentes. Si una decisión cambia, exigiría actualizar requisitos, diseño y bitácora en el mismo cambio. Así la documentación permanece conectada al código y no depende de la memoria del equipo.

## E. Ejercicio práctico

Aplicamos el proceso guiado a la funcionalidad de carga masiva de asociados en el backend de actividades. La razón es que ya forma parte del dominio de la API: el sistema debe aceptar archivos CSV/XLSX, validar filas, guardar los asociados válidos y devolver un resumen claro de errores sin perder registros válidos. El objetivo del ejercicio es mantener coherencia entre requisitos, diseño, implementación y evidencia.

La guía elegida para el asistente se concentró en un flujo claro: definir primero el contrato de negocio, luego el diseño, después la partición de tareas y finalmente la ejecución con pruebas. Este mecanismo es útil porque evita que la IA reescriba el problema en un lenguaje más “elegante” que no se corresponde con la realidad del sistema. Las decisiones de negocio quedaron en la especificación y no se aceptaron cambios estructurales fuera de ese marco.

