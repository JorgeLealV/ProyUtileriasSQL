# Feature Specification: Agregar Pestaña Ejecutar Querys

**Feature Branch**: `003-agregar-ejecutar-querys`

**Created**: 2026-06-10

**Status**: Draft

**Input**: User description: "Agregar funcionalidad completa de la pestaña Ejecutar Querys: selección de directorio, gestión de archivos .sql seleccionados, configuración de log y ejecución contra base de datos con soporte de rollback."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configurar Directorio de Querys (Priority: P1)

El usuario abre la pestaña "Ejecutar Querys" y selecciona un directorio que contiene archivos `.sql`. El sistema muestra los archivos disponibles en la lista "Querys Disponibles" y restaura la configuración previa si existe.

**Why this priority**: Es el punto de entrada obligatorio para toda la funcionalidad de la pestaña. Sin un directorio seleccionado no se puede hacer nada más.

**Independent Test**: Se puede probar de forma aislada seleccionando un directorio con archivos `.sql` y verificando que aparecen en la lista izquierda, y que la ruta queda persistida en `ConfInsert.conf`.

**Acceptance Scenarios**:

1. **Given** la pestaña está abierta y no hay configuración previa, **When** el usuario hace clic en el botón de selección de directorio y elige una carpeta con archivos `.sql`, **Then** la ruta aparece en el text box y los archivos `.sql` se listan en "Querys Disponibles".
2. **Given** existe una entrada `02|DirEnt|<Directorio>` válida en `ConfInsert.conf`, **When** el usuario abre la pestaña "Ejecutar Querys", **Then** la ruta se restaura en el text box, los archivos `.sql` del directorio se distribuyen correctamente entre ambas listas según la entrada `02|Querys|...`.
3. **Given** la entrada `02|DirEnt|<Directorio>` apunta a un directorio que ya no existe, **When** el usuario abre la pestaña, **Then** las entradas `02|DirEnt` y `02|Querys` se eliminan de `ConfInsert.conf` y ambas listas quedan vacías.
4. **Given** existe `02|DirEnt` pero no `02|Querys`, **When** el usuario abre la pestaña, **Then** todos los archivos `.sql` del directorio aparecen en "Querys Disponibles" y "Querys Seleccionados" queda vacío.

---

### User Story 2 - Gestionar Querys Seleccionados (Priority: P2)

El usuario mueve archivos `.sql` entre la lista "Querys Disponibles" y "Querys Seleccionados" usando los botones Agregar, Agregar Todos, Quitar y Quitar Todos. Cada operación actualiza `ConfInsert.conf`.

**Why this priority**: Define qué archivos serán ejecutados. Sin esta selección no hay ejecución posible.

**Independent Test**: Se puede probar con un directorio ya seleccionado, moviendo elementos entre listas y verificando que `ConfInsert.conf` se actualiza correctamente tras cada operación.

**Acceptance Scenarios**:

1. **Given** hay un elemento seleccionado en "Querys Disponibles", **When** el usuario presiona "Agregar", **Then** el elemento se mueve a "Querys Seleccionados" y se actualiza `02|Querys|...` en `ConfInsert.conf`.
2. **Given** "Querys Disponibles" tiene elementos (seleccionados o no), **When** el usuario presiona "Agregar Todos", **Then** todos los elementos pasan a "Querys Seleccionados" y la lista origen queda vacía.
3. **Given** hay un elemento seleccionado en "Querys Seleccionados", **When** el usuario presiona "Quitar", **Then** el elemento regresa a "Querys Disponibles".
4. **Given** "Querys Seleccionados" tiene elementos, **When** el usuario presiona "Quitar Todos", **Then** todos los elementos regresan a "Querys Disponibles" y `02|Querys|...` queda vacío o se elimina.
5. **Given** no hay elemento seleccionado en la lista origen, **When** el usuario ve los botones "Agregar" y "Quitar", **Then** dichos botones están deshabilitados.

---

### User Story 3 - Configurar y Guardar Opciones de Ejecución (Priority: P3)

El usuario configura si desea generar un log de operación, si permite continuar ejecución ante errores, y especifica el nombre del archivo de log. Puede limpiar toda la configuración con un botón.

**Why this priority**: Son opciones opcionales pero importantes para controlar el comportamiento de la ejecución y mantener trazabilidad.

**Independent Test**: Se puede probar habilitando el checkbox "Crear Log", escribiendo un nombre en el text box, guardando, y verificando que `02|NomLog|...` aparece en `ConfInsert.conf`.

**Acceptance Scenarios**:

1. **Given** el checkbox "Crear Log de Operación" está desmarcado, **When** el usuario lo marca, **Then** el text box "Nombre del archivo log" se habilita y el botón "Guardar nombre" se habilita (si hay texto).
2. **Given** el text box de nombre de log tiene contenido y el checkbox está marcado, **When** el usuario presiona "Guardar nombre", **Then** se guarda `02|NomLog|<nombre>` en `ConfInsert.conf`.
3. **Given** el checkbox "Crear Log de Operación" está desmarcado, **Then** el text box de nombre de log está deshabilitado (grayed out) y el botón "Guardar nombre" está deshabilitado.
4. **Given** hay configuración activa (directorio, querys seleccionados, log), **When** el usuario presiona "Limpiar configuración", **Then** se borran ambas listas, el text box de directorio, los checkboxes quedan desmarcados, el text box de log se limpia y deshabilita, y se eliminan las entradas `02|DirEnt`, `02|Querys` y `02|NomLog` de `ConfInsert.conf`.

---

### User Story 4 - Ejecutar Querys contra la Base de Datos (Priority: P1)

El usuario presiona "Ejecutar Querys" para ejecutar todos los archivos `.sql` seleccionados contra la base de datos configurada en `ConexionBD.conf`, con soporte de rollback por archivo o ejecución continua ante errores.

**Why this priority**: Es el objetivo central de la funcionalidad. Todo lo anterior sirve para configurar esta ejecución.

**Independent Test**: Se puede probar con archivos `.sql` en la lista y un `ConexionBD.conf` válido, verificando que las instrucciones se ejecutan y se muestra el resumen final.

**Acceptance Scenarios**:

1. **Given** "Querys Seleccionados" está vacío, **When** el usuario presiona "Ejecutar Querys", **Then** se muestra un mensaje de error indicando que no hay querys seleccionados y no se procede.
2. **Given** `ConexionBD.conf` no existe, **When** el usuario presiona "Ejecutar Querys", **Then** se muestra un mensaje de error indicando que no se encontró el archivo de conexión.
3. **Given** hay archivos seleccionados y `ConexionBD.conf` existe, **When** el usuario presiona "Ejecutar Querys" con "Permitir ejecución de Operaciones válidas" desmarcado (rollback), **Then** cada archivo se ejecuta en una transacción; si alguna instrucción falla se hace rollback completo del archivo y se continúa con el siguiente.
4. **Given** hay archivos seleccionados y "Permitir ejecución de Operaciones válidas" está marcado, **When** el usuario presiona "Ejecutar Querys", **Then** se continúa ejecutando instrucciones aunque alguna falle, sin rollback.
5. **Given** la ejecución finaliza, **When** se muestra el resumen, **Then** incluye: cantidad de archivos ejecutados, exitosos y fallidos; si hay log, muestra la ruta completa del archivo de log.
6. **Given** "Querys Seleccionados" contiene al menos un elemento, **Then** el botón "Ejecutar Querys" está habilitado; si la lista está vacía, el botón está deshabilitado.

---

### Edge Cases

- Si un archivo `.sql` en "Querys Seleccionados" ya no existe en disco al momento de ejecutar: se salta, se cuenta como fallido en el resumen y se registra el error en el log (si existe); la ejecución continúa con los demás archivos.
- ¿Qué sucede si `ConexionBD.conf` existe pero tiene parámetros incorrectos (usuario/contraseña inválidos)?
- Si el nombre del archivo de log ya existe en el directorio: se crea un archivo nuevo con sufijo de timestamp (p. ej. `milog_20260610_143022.txt`) para preservar el log anterior.
- El directorio de querys se escanea de forma plana (no recursiva); los subdirectorios se ignoran.
- Si el directorio guardado no contiene archivos `.sql`, ambas listas quedan vacías y el botón "Ejecutar Querys" permanece deshabilitado.
- ¿Qué pasa si el archivo `.sql` está vacío o contiene solo comentarios?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Al seleccionar la pestaña "Ejecutar Querys", el sistema DEBE leer `ConfInsert.conf` y restaurar la configuración previa (directorio, querys seleccionados, nombre de log) si existe y es válida.
- **FR-002**: El sistema DEBE verificar la existencia del directorio guardado en `02|DirEnt|...`; si no existe, DEBE eliminar las entradas `02|DirEnt` y `02|Querys` de `ConfInsert.conf`.
- **FR-003**: El sistema DEBE escanear el directorio seleccionado y listar únicamente los archivos con extensión `.sql` en "Querys Disponibles".
- **FR-004**: Al seleccionar un nuevo directorio, el sistema DEBE actualizar/crear la entrada `02|DirEnt|<Directorio>` en `ConfInsert.conf` y limpiar ambas listas.
- **FR-005**: Los botones "Agregar" y "Quitar" DEBEN habilitarse únicamente cuando haya un elemento seleccionado en la lista correspondiente.
- **FR-006**: Los botones "Agregar Todos" y "Quitar Todos" DEBEN habilitarse cuando la lista de origen tenga al menos un elemento, sin requerir selección.
- **FR-007**: Cada operación de los cuatro botones de gestión DEBE actualizar la entrada `02|Querys|<Query1>, <Query2>, ...` en `ConfInsert.conf` sin repeticiones, almacenando los nombres sin la extensión `.sql`.
- **FR-008**: El text box "Nombre del archivo log" y el botón "Guardar nombre" DEBEN estar deshabilitados cuando el checkbox "Crear Log de Operación" esté desmarcado.
- **FR-009**: El botón "Guardar nombre" DEBE estar deshabilitado si el text box de nombre de log está vacío (aunque el checkbox esté marcado).
- **FR-010**: El botón "Guardar nombre" DEBE guardar la entrada `02|NomLog|<NombreArchLog>` en `ConfInsert.conf` solo si el text box tiene contenido.
- **FR-011**: El botón "Limpiar configuración" DEBE borrar ambas listas, el text box de directorio, desmarcar ambos checkboxes, limpiar y deshabilitar el text box de log, y eliminar las entradas `02|DirEnt`, `02|Querys` y `02|NomLog` de `ConfInsert.conf`.
- **FR-012**: El botón "Ejecutar Querys" DEBE estar deshabilitado cuando "Querys Seleccionados" esté vacío y habilitarse automáticamente cuando contenga al menos un elemento.
- **FR-013**: Antes de ejecutar, el sistema DEBE verificar que `ConexionBD.conf` existe; si no, mostrar error y no proceder.
- **FR-013b**: Si un archivo `.sql` de la lista "Querys Seleccionados" no existe en disco al momento de la ejecución, el sistema DEBE saltarlo, contarlo como fallido en el resumen y registrar el error en el log (si existe); la ejecución DEBE continuar con los demás archivos sin interrumpirse.
- **FR-014**: El sistema DEBE ejecutar cada archivo `.sql` seleccionado usando la función `execute_sql_from_file` con los parámetros de `ConexionBD.conf`.
- **FR-015**: La función `execute_sql_from_file` DEBE ser modificada para aceptar: nombre del archivo de log (con ruta completa del directorio prepended) y bandera de rollback.
- **FR-016**: Con rollback habilitado (checkbox desmarcado): si alguna instrucción de un archivo falla, se DEBE hacer rollback completo del archivo, registrar en log y continuar con el siguiente archivo.
- **FR-017**: Con rollback deshabilitado (checkbox marcado): si alguna instrucción falla, se DEBE continuar ejecutando las demás instrucciones sin rollback.
- **FR-018**: Durante la ejecución, el sistema DEBE mostrar un indicador de progreso (barra o mensaje de estado) visible al usuario, con una opción para cancelar la ejecución en curso. Si el usuario cancela, se DEBE hacer rollback del archivo que estaba en proceso y no iniciar los archivos pendientes.
- **FR-019**: Al finalizar la ejecución (o al cancelar), el sistema DEBE mostrar un resumen con: archivos ejecutados, exitosos y fallidos. Si existe log, DEBE mostrar la ruta completa del archivo de log.
- **FR-020b**: Si se especificó log (`02|NomLog`), el sistema DEBE registrar en él el nombre de cada archivo procesado, el estado de cada instrucción SQL ejecutada y cualquier error o rollback ocurrido.
- **FR-020**: Al restaurar configuración, si existe `02|NomLog|<NombreArchLog>` en `ConfInsert.conf`, DEBE mostrarse el nombre en el text box de log.

### Key Entities

- **ConfInsert.conf**: Archivo de configuración persistente con entradas clave-valor en formato `XX|Clave|Valor`. Las entradas de esta funcionalidad usan el prefijo `02`.
- **ConexionBD.conf**: Archivo de parámetros de conexión a base de datos (`my_db`, `my_user`, `my_pass`, `my_host`, `my_port`). Las líneas que comienzan con `#` se ignoran.
- **Archivo SQL**: Archivo con extensión `.sql` que contiene instrucciones SQL a ejecutar. Se identifica por su nombre sin extensión en `ConfInsert.conf`.
- **Archivo Log**: Archivo de texto donde se registra el resultado de cada instrucción ejecutada, errores y rollbacks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El usuario puede seleccionar un directorio y ver los archivos `.sql` disponibles en menos de 2 segundos.
- **SC-002**: La configuración previa (directorio, querys seleccionados, nombre de log) se restaura correctamente al 100% al reabrir la pestaña, siempre que el directorio exista.
- **SC-003**: Cada operación de gestión de listas (Agregar/Quitar/Todos) refleja cambios en `ConfInsert.conf` de forma inmediata (en la misma operación, sin pasos adicionales).
- **SC-004**: La ejecución de archivos `.sql` con rollback produce exactamente el mismo estado en la base de datos que si ningún archivo fallido hubiera sido aplicado.
- **SC-005**: El resumen de ejecución muestra conteos correctos (ejecutados, exitosos, fallidos) para todos los archivos procesados.
- **SC-006**: El archivo de log captura el estado de cada instrucción SQL y los eventos de rollback sin omisiones.

## Clarifications

### Session 2026-06-10

- Q: ¿Qué sucede cuando un archivo `.sql` en "Querys Seleccionados" ya no existe en disco al momento de ejecutar? → A: Se salta el archivo, se cuenta como fallido en el resumen y se registra el error en el log (si existe); la ejecución continúa con los demás archivos.
- Q: ¿Cómo se comporta la interfaz durante la ejecución de los archivos `.sql`? → A: Mostrar indicador de progreso (barra o mensaje de estado) con opción de cancelar la ejecución.
- Q: ¿Qué ocurre cuando el archivo de log especificado ya existe en el directorio? → A: Crear un archivo nuevo con sufijo de timestamp (p. ej. `milog_20260610_143022.txt`) para no perder el log anterior.

## Assumptions

- Los archivos `.sql` están en el directorio raíz seleccionado; no se escanean subdirectorios (escaneo plano).
- `ConexionBD.conf` se encuentra en el directorio raíz del proyecto y sigue el formato documentado.
- Los parámetros de `ConexionBD.conf` sin líneas `#` son válidos y completos.
- El archivo de log se crea en el mismo directorio que los archivos `.sql` (directorio seleccionado en el text box del paso 1), concatenando la ruta del directorio al nombre del log.
- Los checkboxes "Crear Log de Operación" y "Permitir ejecución de Operaciones válidas" inician siempre desmarcados (no se persisten en `ConfInsert.conf`).
- Los nombres de los querys en `02|Querys|...` se almacenan sin la extensión `.sql`; la extensión se añade al reconstruir la ruta completa.
- La función existente `execute_sql_from_file` en `services/funciones.py` se extiende (no se reemplaza) para soportar los nuevos parámetros de log y rollback.
- El archivo de log se nombra tal como el usuario lo escribe en el text box, sin validación de extensión. Si ya existe un archivo con ese nombre en el directorio, se crea uno nuevo agregando un sufijo de timestamp al nombre base (p. ej. `milog_20260610_143022.txt`).
