---
description: "Task list for feature 001-reorden-menu"
---

# Tasks: Reordenamiento y Renombrado del Menú Principal

**Input**: Design documents from `specs/001-reorden-menu/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | quickstart.md ✅

**Tests**: No requeridos (validación visual manual — ver quickstart.md)

**Organization**: Una sola historia de usuario (P1). Las tareas de los dos
archivos a modificar pueden ejecutarse en paralelo.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: Historia de usuario a la que pertenece la tarea

## Path Conventions

- **Desktop PySide6 (ProyUtileriasSQL)**: `ui/`, `views/`, `services/`, `controllers/`

---

## Phase 1: Setup — Verificación del punto de partida

**Purpose**: Confirmar el estado actual de los archivos antes de modificar.

- [x] T001 Leer `ui/main_window.ui` y verificar que los 4 botones están en el orden actual: Configuración → Ejecución de scripts → Exportación a Excel → Crear Inserts

- [x] T002 Leer `ui/main_window_ui.py` y verificar que `setupUi()` y `retranslateUi()` reflejan ese mismo orden

**Checkpoint**: Estado inicial confirmado — proceder a implementación.

---

## Phase 2: User Story 1 — Reorden y renombrado del menú (Priority: P1) 🎯 MVP

**Goal**: Los cuatro botones del menú principal aparecen en el nuevo orden con
las nuevas etiquetas al iniciar la aplicación.

**Independent Test**: Ejecutar `main.py` y verificar que el primer botón visible
es "Crear Archivos SQL de Archivo Excel" (ver quickstart.md).

### Implementación para User Story 1

- [x] T003 [P] [US1] Editar `ui/main_window.ui`: reordenar los bloques `<item>` de los botones al nuevo orden (btn_creacion primero, btn_configuracion último) y actualizar los textos `<string>` de los 4 botones según el mapping del plan.md

- [x] T004 [P] [US1] Editar `ui/main_window_ui.py`: reordenar los bloques de instanciación + `addWidget` en `setupUi()` al mismo orden nuevo, y actualizar los 4 textos en `retranslateUi()` para que coincidan con los textos de T003

**Checkpoint**: User Story 1 completa — ejecutar validación del siguiente phase.

---

## Phase 3: Validación

**Purpose**: Verificar que la implementación cumple los criterios de aceptación
del spec sin regresiones visuales ni funcionales.

- [x] T005 Ejecutar `main.py` y confirmar que los botones aparecen en el orden correcto según la tabla de quickstart.md

- [x] T006 Hacer clic en "Crear Archivos SQL de Archivo Excel" y verificar que abre el PanelPrincipal sin errores y que el botón "← Menú principal" regresa al menú

- [x] T007 Verificar que colores, fuentes y estilos del menú son idénticos al estado previo (hover dorado, btn_salida con estilos rojos)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — comenzar inmediatamente
- **User Story 1 (Phase 2)**: Depende de Phase 1 — T003 y T004 pueden ejecutarse en paralelo entre sí
- **Validación (Phase 3)**: Depende de Phase 2 completa

### Within User Story 1

- T003 y T004 son **paralelas** (archivos distintos, cambios independientes)
- T005, T006, T007 son **secuenciales** (validación progresiva)

### Parallel Opportunities

```
# Phase 2 — ejecutar juntas:
T003: Editar ui/main_window.ui
T004: Editar ui/main_window_ui.py

# Phase 3 — secuencial:
T005 → T006 → T007
```

---

## Implementation Strategy

### MVP (único alcance de esta feature)

1. Completar Phase 1: Setup (verificación)
2. Completar Phase 2: T003 + T004 en paralelo
3. Completar Phase 3: Validación
4. **DONE** — feature completa en una iteración

### Mapping de cambios de referencia (del plan.md)

| objectName          | Texto actual           | Texto nuevo                                  | Pos. actual | Pos. nueva |
|---------------------|------------------------|----------------------------------------------|-------------|------------|
| `btn_creacion`      | "Crear Inserts"        | "Crear Archivos SQL de Archivo Excel"         | 4           | 1          |
| `btn_ejecucion`     | "Ejecución de scripts" | "Ejecutar archivos SQL en la base de datos"   | 2           | 2          |
| `btn_exportacion`   | "Exportación a Excel"  | "Obtener tablas de la base de datos a Excel"  | 3           | 3          |
| `btn_configuracion` | "Configuración"        | "Configuración"                               | 1           | 4          |
| `btn_salida`        | "Salida"               | "Salida" (sin cambios)                        | 5           | 5          |

---

## Notes

- [P] tasks = archivos distintos, sin dependencias entre sí
- [US1] mapea esta tarea a User Story 1 del spec
- T003 y T004 deben producir resultados consistentes entre sí (mismo orden, mismos textos)
- `main.py` NO se modifica — los `objectName` son estables
- Validar con quickstart.md al completar Phase 2
