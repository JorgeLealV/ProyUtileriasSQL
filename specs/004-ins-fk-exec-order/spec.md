# Feature Specification: Ejecución Ordenada de Inserts por Dependencias FK

**Feature Branch**: `004-ins-fk-exec-order`

**Created**: 2026-06-12

**Status**: Draft

**Input**: specifyEjecucionSqlJjerarquia.md

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Ejecución correcta respetando jerarquía padre-hijo (Priority: P1)

El operador selecciona una lista de archivos `.sql` que incluye archivos de tipo `Ins_` (inserción de tablas con dependencias FK entre sí). Al presionar "Ejecutar Querys", el sistema detecta automáticamente el orden correcto de ejecución basándose en las relaciones padre-hijo de la base de datos, sin que el operador tenga que conocer ni reordenar manualmente los archivos.

**Why this priority**: Es el valor central de la feature. Sin este ordenamiento automático, los INSERTs fallarían por violaciones de integridad referencial.

**Independent Test**: Se puede probar con 3 archivos `Ins_` donde TipoA es padre de TipoB y TipoB es padre de TipoC. Al presionar el botón en cualquier orden de selección, el sistema debe ejecutarlos siempre en el orden TipoA → TipoB → TipoC.

**Acceptance Scenarios**:

1. **Given** la lista contiene `Ins_TipoB.sql` e `Ins_TipoA.sql` (TipoA es tabla padre de TipoB), **When** el operador presiona "Ejecutar Querys", **Then** el sistema ejecuta primero `Ins_TipoA.sql` y después `Ins_TipoB.sql`, independientemente del orden en el list box.
2. **Given** un archivo `Ins_` cuya tabla padre no tiene archivo `Ins_` correspondiente en la lista, **When** el sistema analiza dependencias, **Then** ese archivo se ejecuta normalmente sin restricción.
3. **Given** la lista contiene archivos generales (sin prefijo `Ins_`) junto con archivos `Ins_`, **When** el operador ejecuta, **Then** los archivos generales se ejecutan primero en su orden original, y los `Ins_` después en orden topológico.

---

### User Story 2 — Detección y reporte de ciclos de dependencia (Priority: P2)

Si la configuración de datos tiene dos tablas que se referencian mutuamente (ciclo A→B→A), el sistema detecta la situación antes de intentar ejecutar cualquier archivo, informa al operador con claridad qué tablas forman el ciclo y no ejecuta nada del grupo afectado.

**Why this priority**: Un ciclo de FK es un error de configuración de datos que no puede resolverse automáticamente. Detectarlo antes evita ejecuciones parciales inconsistentes.

**Independent Test**: Con `Ins_TablaA.sql` e `Ins_TablaB.sql` donde ambas se referencian mutuamente, el sistema debe detectar el ciclo, registrarlo en el log y no ejecutar ninguno de los dos archivos.

**Acceptance Scenarios**:

1. **Given** hay un ciclo de dependencia entre dos o más archivos `Ins_`, **When** el sistema analiza el grafo de dependencias, **Then** registra en el log los archivos involucrados en el ciclo, informa al usuario con un mensaje claro y no procede con la ejecución del grupo Ins.
2. **Given** hay un ciclo en un subconjunto de archivos pero otros archivos no forman parte del ciclo, **When** el sistema detecta el ciclo, **Then** reporta el ciclo como error y detiene la ejecución del grupo Ins completo.

---

### User Story 3 — Control de archivos bloqueados por padres pendientes (Priority: P3)

Si un archivo padre falla durante la ejecución (queda en estado Pendiente), sus archivos hijos no se ejecutan. El sistema lleva control de cuántas veces se revisitó un padre pendiente; si se supera el límite de 5 revisitas, la ejecución se trunca y se informa al operador qué archivos quedaron pendientes.

**Why this priority**: Complementa la ejecución ordenada: no basta con el orden correcto, también hay que manejar graciosamente los casos donde un padre no pudo ejecutarse.

**Independent Test**: Con `Ins_Padre.sql` que falla y `Ins_Hijo.sql` que depende de él, al ejecutar se debe registrar Hijo como Pendiente, y si el Padre supera 5 revisitas, el sistema trunca y reporta ambos como pendientes.

**Acceptance Scenarios**:

1. **Given** `Ins_Padre.sql` está en estado Pendiente, **When** el sistema intenta procesar `Ins_Hijo.sql` (que depende de Padre), **Then** marca Hijo como Pendiente, no lo ejecuta, e incrementa el contador de visitas de Padre.
2. **Given** el contador de visitas de un padre Pendiente supera 5, **When** el sistema revisa ese padre nuevamente, **Then** trunca la ejecución completa, registra en el log todos los archivos pendientes con su motivo, e informa al usuario.
3. **Given** al terminar el recorrido inicial quedan archivos Pendientes, **When** se realiza la segunda pasada sobre ellos, **Then** se aplica la misma lógica sin reiniciar el contador de visitas acumulado.

---

### Edge Cases

- ¿Qué pasa si la lista solo tiene archivos generales (ningún `Ins_`)? → Se ejecutan todos en orden sin análisis de dependencias.
- ¿Qué pasa si la lista solo tiene archivos `Ins_`? → Se omite la fase de archivos generales y se ejecuta directo el análisis FK.
- ¿Qué pasa si una tabla `Ins_` no existe en la base de datos al consultar sus FK? → Se asume que no tiene dependencias dentro del grupo; se ejecuta sin restricción.
- ¿Qué pasa si un archivo `Ins_` tiene múltiples padres y solo uno está Pendiente? → El hijo queda Pendiente hasta que **todos** sus padres estén en estado Ejecutado.
- ¿Qué pasa si dos archivos `Ins_` apuntan a la misma tabla padre que no tiene archivo `Ins_` en la lista? → Ambos se ejecutan sin restricción de dependencia entre ellos.
- ¿Qué pasa si un archivo general falla? → Se detiene toda la ejecución y no se procesa ningún archivo `Ins_`.
- ¿Qué pasa si un archivo `Ins_` falla con error SQL? → Se marca como Fallido, se registra el error y se continúa con el siguiente archivo `Ins_`. No detiene la ejecución del grupo.
- ¿Qué pasa si la consulta de FK a la base de datos falla (error de conexión, timeout)? → Se aborta toda la ejecución con mensaje de error claro. No se ejecuta ningún archivo.

## Clarifications

### Session 2026-06-12

- Q: Si un archivo `Ins_` falla con error SQL, ¿detener toda la ejecución o continuar? → A: Marcar como Fallido, registrar el error y continuar con el siguiente archivo `Ins_`. La ejecución solo se detiene por fallo de archivos Generales o por ciclo de dependencias detectado.
- Q: Si la consulta de FK a la base de datos falla durante el análisis de dependencias, ¿qué debe hacer el sistema? → A: Abortar toda la ejecución con un mensaje de error claro. No ejecutar ningún archivo si no se puede garantizar el orden correcto.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE separar los archivos seleccionados en dos grupos: archivos Generales (sin prefijo `Ins_`) y archivos de Inserción (con prefijo `Ins_` y extensión `.sql`), manteniendo el orden relativo de cada grupo.
- **FR-002**: El sistema DEBE ejecutar todos los archivos Generales primero, en su orden original. Si alguno falla, DEBE detener la ejecución completa sin procesar ningún archivo de Inserción.
- **FR-003**: Para cada archivo de Inserción, el sistema DEBE extraer el nombre de tabla quitando el prefijo `Ins_` y el sufijo `.sql`.
- **FR-004**: El sistema DEBE consultar la base de datos para obtener las tablas padre de cada tabla extraída, considerando únicamente las relaciones FK del esquema activo. Si la consulta falla (error de conexión, timeout u otro error), el sistema DEBE abortar toda la ejecución con un mensaje de error claro y no ejecutar ningún archivo.
- **FR-005**: El sistema DEBE ignorar dependencias hacia tablas padre que no tengan un archivo `Ins_` correspondiente en la lista seleccionada.
- **FR-006**: El sistema DEBE construir un grafo de dependencias entre los archivos `Ins_` y detectar la presencia de ciclos antes de ejecutar.
- **FR-007**: Si se detecta un ciclo de dependencias, el sistema DEBE registrar en el log los archivos involucrados, informar al usuario y detener la ejecución del grupo de Inserción.
- **FR-008**: El sistema DEBE ejecutar los archivos de Inserción en orden topológico (padres antes que hijos).
- **FR-009**: Si al momento de procesar un archivo de Inserción alguno de sus padres está en estado Pendiente, el sistema DEBE marcar ese archivo como Pendiente y no ejecutarlo.
- **FR-009b**: Si un archivo de Inserción falla con un error SQL de la base de datos (no es un problema de dependencia), el sistema DEBE marcarlo como Fallido, registrar el error en el log y **continuar** con el siguiente archivo de Inserción en la secuencia. La ejecución del grupo de Inserción no se detiene por errores SQL individuales.
- **FR-010**: El sistema DEBE llevar un contador de revisitas por cada archivo padre en estado Pendiente. Si el contador supera 5, el sistema DEBE truncar la ejecución, registrar en el log todos los archivos pendientes y su motivo, e informar al usuario.
- **FR-011**: Al terminar el recorrido inicial, si quedan archivos Pendientes, el sistema DEBE realizar una segunda pasada sobre ellos conservando los contadores de revisitas acumulados.
- **FR-012**: El sistema DEBE registrar en el log cada archivo procesado con: timestamp, nombre de archivo, estado final (Ejecutado / Pendiente / Fallido / Abortado) y motivo detallado.
- **FR-013**: Al finalizar toda la ejecución, el log DEBE incluir un resumen con totales de archivos ejecutados, pendientes y fallidos.

### Key Entities

- **Archivo General**: Archivo `.sql` sin prefijo `Ins_`. Se ejecuta en su orden original sin análisis de dependencias.
- **Archivo de Inserción (Ins_)**: Archivo `.sql` con prefijo `Ins_` que representa la inserción de datos en una tabla específica de la base de datos.
- **Tabla**: Entidad de base de datos cuyo nombre se extrae del nombre del archivo `Ins_`.
- **Dependencia FK**: Relación padre-hijo entre dos tablas según el esquema de la base de datos.
- **Estado de archivo**: Valor que describe el resultado del procesamiento de un archivo (`En cola`, `Ejecutado`, `Pendiente`, `Fallido`, `Abortado`).
- **Contador de revisitas**: Número de veces que un archivo padre en estado Pendiente fue encontrado bloqueando a un hijo. Límite máximo: 5.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los archivos `Ins_` se ejecutan en un orden que respeta las dependencias FK declaradas en la base de datos (ningún hijo se ejecuta antes que su padre).
- **SC-002**: Los ciclos de dependencia se detectan antes de iniciar cualquier ejecución, en el 100% de los casos.
- **SC-003**: El operador recibe un log completo al finalizar que le permite identificar, sin ambigüedad, qué archivos se ejecutaron, cuáles quedaron pendientes y cuál fue el motivo de cada estado.
- **SC-004**: La ejecución nunca entra en un bucle infinito: el límite de 5 revisitas garantiza que siempre termina en un tiempo acotado.
- **SC-005**: Los archivos generales siempre se ejecutan antes de cualquier archivo `Ins_`, en el 100% de las ejecuciones.

## Assumptions

- El esquema de base de datos relevante es `public`. Soporte para esquemas configurables queda fuera del alcance de esta versión.
- La consulta de FK a la base de datos se realiza en el momento de presionar "Ejecutar Querys", usando la conexión ya configurada en `ConexionBD.conf`.
- El sistema no modifica el orden visual del list box "Querys Seleccionados"; el ordenamiento es interno al proceso de ejecución.
- La ejecución de archivos es secuencial (no paralela).
- El contenido SQL de los archivos no se valida previamente; los errores son reportados por la base de datos al momento de ejecutar.
- Un archivo `Ins_` con una tabla que no existe en la base de datos (sin FK) se considera sin dependencias y se ejecuta normalmente.
- El límite de revisitas de 5 se aplica por archivo padre pendiente (no es un límite global de la ejecución).
