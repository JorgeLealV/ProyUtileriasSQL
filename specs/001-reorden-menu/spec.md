# Feature Specification: Reordenamiento y Renombrado del Menú Principal

**Feature Branch**: `001-reorden-menu`

**Created**: 2026-06-08

**Status**: Draft

**Input**: Documentacion/spec-reorden-menu.txt

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Nuevo orden y nombres en el menú principal (Priority: P1)

Al iniciar la aplicación, el usuario ve los botones del menú principal en el
orden correcto y con los nombres actualizados que describen con claridad la
función de cada opción.

**Why this priority**: Es el único cambio de esta feature. Sin él la feature
no existe. Todo el valor está en esta historia.

**Independent Test**: Abrir la aplicación y verificar que el primer botón
muestra "Crear Archivos SQL de Archivo Excel" y que los cuatro botones siguen
en el orden indicado.

**Acceptance Scenarios**:

1. **Given** la aplicación está instalada y el usuario la inicia,
   **When** se muestra el menú principal,
   **Then** el primer botón visible es "Crear Archivos SQL de Archivo Excel".

2. **Given** el menú principal está visible,
   **When** el usuario observa los cuatro botones de izquierda a derecha / de
   arriba a abajo,
   **Then** el orden es: (1) Crear Archivos SQL de Archivo Excel,
   (2) Ejecutar archivos SQL en la base de datos,
   (3) Obtener tablas de la base de datos a Excel,
   (4) Configuración.

3. **Given** el menú principal está visible con los nuevos nombres,
   **When** el usuario hace clic en cualquiera de los cuatro botones,
   **Then** la navegación lleva a la misma ventana de siempre,
   sin cambios funcionales.

4. **Given** el menú principal está visible,
   **When** el usuario compara el aspecto visual con el estado anterior,
   **Then** colores, fuentes, tamaños y estilos son idénticos;
   solo difieren el orden y el texto de las etiquetas.

---

### Edge Cases

- ¿Qué ocurre si el archivo `.ui` tiene botones adicionales no listados?
  → Deben conservarse en su posición actual, sin alterarse.
- ¿Qué ocurre si el tamaño del texto nuevo no cabe en el botón?
  → El botón debe adaptarse (wrapping o ajuste automático) sin truncar el texto.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El menú principal DEBE mostrar "Crear Archivos SQL de Archivo Excel"
  como primera opción visible.
- **FR-002**: El menú principal DEBE mostrar "Ejecutar archivos SQL en la base de datos"
  como segunda opción visible.
- **FR-003**: El menú principal DEBE mostrar "Obtener tablas de la base de datos a Excel"
  como tercera opción visible.
- **FR-004**: El menú principal DEBE mostrar "Configuración" como cuarta opción visible.
- **FR-005**: Cada opción DEBE conservar su comportamiento de navegación original
  sin modificaciones funcionales.
- **FR-006**: El aspecto visual del menú (colores, fuentes, tamaños, bordes)
  DEBE permanecer idéntico al estado previo al cambio.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Al abrir la aplicación, el primer botón visible muestra el texto
  "Crear Archivos SQL de Archivo Excel" en el 100% de las ejecuciones.
- **SC-002**: Los cuatro botones navegan correctamente a su ventana
  correspondiente en el 100% de los intentos.
- **SC-003**: Ningún elemento visual del menú (color, fuente, tamaño) difiere
  del estado anterior al cambio — verificable por inspección visual directa.
- **SC-004**: El cambio completo puede validarse en menos de 2 minutos mediante
  inspección visual y prueba de navegación manual.

## Assumptions

- Los botones QPushButton del menú principal están en `ui/main_window.ui`
  (no en `PanelPrincipal.ui`, que contiene el panel de funcionalidades con pestañas).
- El reorden requiere modificar tanto `ui/main_window.ui` (fuente XML) como
  `ui/main_window_ui.py` (compilado Python importado por `main.py`).
- No se tocan `views/panel_principal_view.py` ni la lógica de `main.py`.
- Los `objectName` de los botones NO se modifican; solo cambian el orden visual
  y el texto de las etiquetas. Así las señales de `main.py` siguen siendo válidas.
- No existen pruebas automatizadas que dependan del orden o texto de los botones.
