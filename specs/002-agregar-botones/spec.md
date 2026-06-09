# Feature Specification: Agregar Botones "Agregar Todos" y "Quitar Todos"

**Feature Branch**: `002-agregar-botones`

**Created**: 2026-06-09

**Status**: Clarified

**Input**: User description: "Agregar botones "Agregar Todos" y "Quitar Todos" en la pantalla "Crear Inserts" de la opción "Crear Archivos SQL de Archivo Excel". El botón "Agregar Todos" debe tomar todos los elementos del ListBox izquierdo "Tablas disponibles" y moverlos al ListBox derecho "Tablas seleccionadas". El botón "Quitar Todos" debe tomar todos los elementos del ListBox derecho "Tablas seleccionadas" y moverlos al ListBox izquierdo "Tablas disponibles". Ambos botones se colocan debajo de los botones "Agregar" y "Quitar" respectivamente."

## Clarifications

### Session 2026-06-09

- Q: ¿Los botones "Agregar Todos" y "Quitar Todos" deben deshabilitarse visualmente cuando su ListBox origen está vacío? → A: Sí, el botón debe aparecer deshabilitado (grayed out) cuando el origen está vacío y habilitarse automáticamente en cuanto el origen vuelva a tener elementos.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mover todas las tablas disponibles a seleccionadas (Priority: P1)

El usuario tiene una lista de tablas disponibles en el ListBox izquierdo y desea incluirlas todas en la generación de scripts SQL sin tener que seleccionarlas y moverlas una por una. Presiona el botón "Agregar Todos" y todas las tablas se mueven instantáneamente al ListBox derecho "Tablas seleccionadas".

**Why this priority**: Es la operación más frecuente cuando se desea procesar la totalidad de las tablas; elimina un proceso manual repetitivo y propenso a omisiones.

**Independent Test**: Se puede probar completamente abriendo la pantalla "Crear Inserts", verificando que hay elementos en "Tablas disponibles", presionando "Agregar Todos" y confirmando que todos los elementos aparecen en "Tablas seleccionadas" y el ListBox izquierdo queda vacío.

**Acceptance Scenarios**:

1. **Given** hay al menos un elemento en "Tablas disponibles" y ninguno en "Tablas seleccionadas", **When** el usuario presiona "Agregar Todos", **Then** todos los elementos se trasladan a "Tablas seleccionadas" y "Tablas disponibles" queda vacío.
2. **Given** hay elementos en ambos ListBox, **When** el usuario presiona "Agregar Todos", **Then** los elementos que aún están en "Tablas disponibles" se añaden a "Tablas seleccionadas" sin duplicar los ya existentes.
3. **Given** "Tablas disponibles" está vacío, **When** el usuario intenta presionar "Agregar Todos", **Then** el botón está deshabilitado visualmente y no puede ser presionado.

---

### User Story 2 - Regresar todas las tablas seleccionadas a disponibles (Priority: P1)

El usuario desea limpiar completamente la lista "Tablas seleccionadas" para reiniciar su selección desde cero. Presiona "Quitar Todos" y todos los elementos regresan al ListBox izquierdo "Tablas disponibles".

**Why this priority**: Es el complemento simétrico e indispensable del botón "Agregar Todos"; permite al usuario rehacer su selección sin tener que quitar tabla por tabla.

**Independent Test**: Se puede probar teniendo elementos en "Tablas seleccionadas", presionando "Quitar Todos" y verificando que todos regresan a "Tablas disponibles" y el ListBox derecho queda vacío.

**Acceptance Scenarios**:

1. **Given** hay al menos un elemento en "Tablas seleccionadas", **When** el usuario presiona "Quitar Todos", **Then** todos los elementos se trasladan a "Tablas disponibles" y "Tablas seleccionadas" queda vacío.
2. **Given** "Tablas seleccionadas" está vacío, **When** el usuario intenta presionar "Quitar Todos", **Then** el botón está deshabilitado visualmente y no puede ser presionado.

---

### Edge Cases

- ¿Qué pasa si "Tablas disponibles" está vacío? → "Agregar Todos" aparece deshabilitado (grayed out) y no puede ser presionado.
- ¿Qué pasa si "Tablas seleccionadas" está vacío? → "Quitar Todos" aparece deshabilitado (grayed out) y no puede ser presionado.
- ¿Los botones se rehablitan automáticamente? → Sí; en cuanto el ListBox origen vuelve a tener al menos un elemento, el botón correspondiente se habilita sin necesidad de acción adicional del usuario.
- ¿El orden de los elementos se preserva tras el traslado? → Los elementos se añaden al ListBox destino preservando el orden en que aparecían en el ListBox origen.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE presentar un botón denominado "Agregar Todos" ubicado inmediatamente debajo del botón "Agregar" existente en la pestaña "Crear Inserts".
- **FR-002**: El sistema DEBE presentar un botón denominado "Quitar Todos" ubicado inmediatamente debajo del botón "Quitar" existente en la pestaña "Crear Inserts".
- **FR-003**: Al activar "Agregar Todos", el sistema DEBE trasladar la totalidad de los elementos presentes en el ListBox "Tablas disponibles" al ListBox "Tablas seleccionadas".
- **FR-004**: Al activar "Quitar Todos", el sistema DEBE trasladar la totalidad de los elementos presentes en el ListBox "Tablas seleccionadas" al ListBox "Tablas disponibles".
- **FR-005**: Tras la operación "Agregar Todos", el ListBox "Tablas disponibles" DEBE quedar vacío.
- **FR-006**: Tras la operación "Quitar Todos", el ListBox "Tablas seleccionadas" DEBE quedar vacío.
- **FR-007**: El botón "Agregar Todos" DEBE estar deshabilitado visualmente cuando el ListBox "Tablas disponibles" está vacío, y habilitarse automáticamente en cuanto contenga al menos un elemento.
- **FR-008**: El botón "Quitar Todos" DEBE estar deshabilitado visualmente cuando el ListBox "Tablas seleccionadas" está vacío, y habilitarse automáticamente en cuanto contenga al menos un elemento.
- **FR-009**: Los nuevos botones DEBEN tener apariencia visual consistente con los botones "Agregar" y "Quitar" existentes (tamaño, fuente y colores), incluyendo el estilo de deshabilitado estándar de la plataforma.

### Key Entities

- **ListBox "Tablas disponibles"**: Lista izquierda que contiene las tablas aún no seleccionadas para la generación de scripts.
- **ListBox "Tablas seleccionadas"**: Lista derecha que contiene las tablas que el usuario ha elegido para incluir en los scripts SQL.
- **Botón "Agregar Todos"**: Control nuevo que desencadena el traslado masivo de izquierda a derecha.
- **Botón "Quitar Todos"**: Control nuevo que desencadena el traslado masivo de derecha a izquierda.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El usuario puede mover todas las tablas disponibles a seleccionadas con una sola acción, reduciendo de N clics individuales a 1 clic.
- **SC-002**: El usuario puede limpiar completamente la selección con una sola acción, reduciendo de N clics individuales a 1 clic.
- **SC-003**: Las operaciones de traslado masivo se completan de forma instantánea (perceptiblemente inmediata) independientemente del número de tablas en la lista.
- **SC-004**: El 100% de los elementos del ListBox origen se trasladan al destino sin omisiones ni duplicados.

## Assumptions

- Los botones nuevos seguirán el mismo estilo visual (tamaño, fuente, colores) que los botones "Agregar" y "Quitar" existentes, salvo indicación contraria.
- El orden de los elementos en el ListBox destino preservará el orden del ListBox origen.
- No se requiere confirmación del usuario antes de ejecutar la operación masiva; la acción es inmediata al presionar el botón.
- La funcionalidad aplica únicamente a la pestaña "Crear Inserts" dentro de la pantalla "Crear Archivos SQL de Archivo Excel"; otras pestañas quedan fuera del alcance.
- Los botones "Agregar" y "Quitar" existentes mantienen su comportamiento actual sin modificaciones.
