# Tasks: Agregar Botones "Agregar Todos" y "Quitar Todos"

**Input**: Design documents from `specs/002-agregar-botones/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | quickstart.md ✅

**Tests**: No solicitados en el spec — no se incluyen tareas de test automatizado.

**Organization**: Tareas agrupadas por User Story para habilitar implementación y verificación independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivo diferente, sin dependencias pendientes)
- **[Story]**: User story a la que pertenece la tarea (US1, US2)
- Rutas de archivo exactas incluidas en todas las descripciones

---

## Phase 1: Foundational (Prerequisitos Bloqueantes para Ambas Historias)

**Purpose**: Modificaciones estructurales compartidas que deben completarse antes de implementar cualquiera de las dos User Stories.

**⚠️ CRITICAL**: Ninguna US puede comenzar hasta completar esta fase.

- [x] T001 [P] Añadir `btn_agregar_todos` y `btn_quitar_todos` en `verticalLayout_2` de `ui/PanelPrincipal.ui` (entre `btn_agregar`→`btn_agregar_todos`→`btn_quitar`→`btn_quitar_todos`→`verticalSpacer`)
- [x] T002 [P] Declarar `self.btn_agregar_todos = None` y `self.btn_quitar_todos = None` en `__init__` de `views/panel_principal_view.py` (junto a `self.btn_agregar` y `self.btn_quitar`)
- [x] T003 Añadir `findChild(QPushButton, "btn_agregar_todos")` y `findChild(QPushButton, "btn_quitar_todos")` en `setup_ui()` de `views/panel_principal_view.py` (depende T001)
- [x] T004 [P] Extender `_update_button_states()` en `views/panel_principal_view.py` para deshabilitar `btn_agregar_todos` cuando `listWidget_hojas.count() == 0` y `btn_quitar_todos` cuando `listWidget_tablas_seleccionadas.count() == 0`
- [x] T005 [P] Añadir reglas CSS para `#btn_agregar_todos` (paleta verde petróleo) y `#btn_quitar_todos` (paleta rojo vino) al final del bloque de `_apply_styles()` en `views/panel_principal_view.py`

**Checkpoint**: Con T001–T005 completados, ambos botones aparecen en la UI con estilos correctos y se habilitan/deshabilitan automáticamente. Los slots aún no están conectados.

---

## Phase 2: User Story 1 — Mover todas las tablas disponibles a seleccionadas (Priority: P1) 🎯 MVP

**Goal**: El botón "Agregar Todos" traslada todos los elementos de `listWidget_hojas` a `listWidget_tablas_seleccionadas` y persiste la configuración.

**Independent Test**: Cargar un Excel, verificar que "Agregar Todos" está habilitado → presionar → verificar que `listWidget_hojas` queda vacío, `listWidget_tablas_seleccionadas` contiene todas las hojas, y `btn_agregar_todos` pasa a deshabilitado.

### Implementación US1

- [x] T006 [US1] Implementar slot `_add_all_items()` en `views/panel_principal_view.py` (loop `takeItem(0)` hasta vaciar `listWidget_hojas`, añadir a `listWidget_tablas_seleccionadas`, llamar `_update_button_states()` y `_save_tables_config()`)
- [x] T007 [US1] Conectar `btn_agregar_todos.clicked` → `_add_all_items` en `connect_signals()` de `views/panel_principal_view.py` (depende T003, T006)

**Checkpoint**: "Agregar Todos" funcional y persistido. User Story 1 completamente verificable de forma independiente.

---

## Phase 3: User Story 2 — Regresar todas las tablas seleccionadas a disponibles (Priority: P1)

**Goal**: El botón "Quitar Todos" traslada todos los elementos de `listWidget_tablas_seleccionadas` a `listWidget_hojas` y persiste la configuración.

**Independent Test**: Con elementos en `listWidget_tablas_seleccionadas`, verificar que "Quitar Todos" está habilitado → presionar → verificar que `listWidget_tablas_seleccionadas` queda vacío, `listWidget_hojas` recupera todos los elementos, y `btn_quitar_todos` pasa a deshabilitado.

### Implementación US2

- [x] T008 [US2] Implementar slot `_remove_all_items()` en `views/panel_principal_view.py` (loop `takeItem(0)` hasta vaciar `listWidget_tablas_seleccionadas`, añadir a `listWidget_hojas`, llamar `_update_button_states()` y `_save_tables_config()`)
- [x] T009 [US2] Conectar `btn_quitar_todos.clicked` → `_remove_all_items` en `connect_signals()` de `views/panel_principal_view.py` (depende T003, T008)

**Checkpoint**: "Quitar Todos" funcional y persistido. User Stories 1 Y 2 completamente verificables de forma independiente.

---

## Phase 4: Polish & Verificación Final

**Purpose**: Verificación cruzada y cierre de la feature.

- [x] T010 Ejecutar los 5 casos de prueba de `specs/002-agregar-botones/quickstart.md` con `python main.py` y confirmar que todos pasan

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: Sin dependencias — puede iniciarse de inmediato
- **US1 (Phase 2)**: Requiere Phase 1 completa (T001–T005)
- **US2 (Phase 3)**: Requiere Phase 1 completa (T001–T005); puede ejecutarse en paralelo con US1
- **Polish (Phase 4)**: Requiere US1 y US2 completas

### Dependencias entre tareas

```
T001 ──→ T003 ──→ T007 (US1 conexión)
T002 ──/         T006 ──/
T004 ──/
T005 ──/
                 T003 ──→ T009 (US2 conexión)
                 T008 ──/
```

### Oportunidades de Paralelismo

Las tareas marcadas `[P]` en Phase 1 pueden ejecutarse simultáneamente:
- **T001** (edición de `.ui`) en paralelo con **T002, T004, T005** (distintos métodos en `.py`)
- **T006** y **T008** (slots) pueden implementarse en paralelo (métodos diferentes, mismo archivo)

### Ejecución secuencial mínima (un desarrollador)

```
T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010
```

---

## Parallel Example: Phase 1

```text
# Simultáneamente (distintos archivos o métodos):
Tarea: "Añadir btn_agregar_todos y btn_quitar_todos en ui/PanelPrincipal.ui"        [T001]
Tarea: "Declarar self.btn_agregar_todos = None en __init__ de panel_principal_view.py" [T002]
Tarea: "Extender _update_button_states() en views/panel_principal_view.py"          [T004]
Tarea: "Añadir CSS para #btn_agregar_todos y #btn_quitar_todos en _apply_styles()"  [T005]

# Luego (depende T001):
Tarea: "findChild para los nuevos botones en setup_ui()"                            [T003]
```

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Completar Phase 1 (T001–T005)
2. Completar Phase 2 (T006–T007)
3. **PARAR y VALIDAR**: Probar "Agregar Todos" con quickstart.md casos 1 y 3

### Entrega Completa

1. MVP + Phase 3 (T008–T009)
2. Polish (T010) — todos los casos de quickstart.md

---

## Notes

- `[P]` = archivos diferentes o métodos sin conflicto — pueden ejecutarse simultáneamente
- `[US1]` / `[US2]` = trazabilidad hacia las User Stories del spec.md
- Después de T007 y T009 la feature está completa; T010 es verificación
- Commit recomendado después de cada Phase
- Los slots (`_add_all_items`, `_remove_all_items`) siguen exactamente el patrón de `_add_item` / `_remove_item` existentes en el mismo archivo
