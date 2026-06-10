---
description: "Task list for feature 003-agregar-ejecutar-querys"
---

# Tasks: Agregar Pestaña Ejecutar Querys

**Input**: Design documents from `specs/003-agregar-ejecutar-querys/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | quickstart.md ✅

**Tests**: No se incluyen tareas de tests automatizados (no solicitados en el spec). La validación se realiza con quickstart.md (prueba manual).

**Organization**: Tareas agrupadas por user story para implementación y prueba independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Se puede ejecutar en paralelo (archivo diferente, sin dependencias en tareas incompletas)
- **[Story]**: User story correspondiente (US1–US4 del spec.md)
- Todas las tareas incluyen ruta exacta de archivo

---

## Phase 1: Setup (Infraestructura Compartida)

**Purpose**: Agregar el layout de la pestaña "Ejecutar Querys" al archivo .ui existente. Este es el punto de partida obligatorio: sin los widgets en el .ui, ningún `findChild()` puede funcionar.

- [x] T001 Reemplazar el widget vacío `tab_ejecuta_querys` en `ui/PanelPrincipal.ui` con `QGridLayout` (`gridLayout_eq`) conteniendo los 17 widgets documentados en plan.md Paso 1 (objectNames: `lineEdit_dir_querys`, `btn_browse_dir_querys`, `listWidget_querys_disponibles`, `btn_eq_agregar`, `btn_eq_agregar_todos`, `btn_eq_quitar`, `btn_eq_quitar_todos`, `listWidget_querys_seleccionados`, `btn_limpiar_config_eq`, `checkBox_crear_log`, `checkBox_permitir_parcial`, `label_nom_log`, `lineEdit_nom_log`, `btn_guardar_nom_log`, `btn_ejecutar_querys` dentro de `groupBox_eq_opciones`)

---

## Phase 2: Foundational (Prerequisitos Bloqueantes)

**Purpose**: Infraestructura central que DEBE completarse antes de implementar cualquier user story. Incluye: extensión del servicio, wiring de widgets y método de estado de botones.

**⚠️ CRÍTICO**: Ninguna user story puede comenzar hasta que esta fase esté completa.

- [x] T002 [P] Extender `execute_sql_from_file()` en `services/funciones.py` para aceptar `log_file=""` y `allow_partial=False`; implementar ejecución instrucción-por-instrucción (split por `;`), control de rollback y retorno de dict `{success, total_stmts, ok_stmts, failed_stmts, errors}`; agregar función auxiliar privada `_write_log()` debajo (plan.md Paso 10)
- [x] T003 Agregar imports nuevos al bloque de imports de `views/panel_principal_view.py`: `datetime`, `QTabWidget`, `QProgressDialog` (a la lista de `QWidgets`), `QObject`, `QThread`, `Signal` (a la línea de `PySide6.QtCore`) (plan.md Paso 2)
- [x] T004 Insertar clase `EjecutarQuerysWorker(QObject)` con señales `progress_updated`, `file_finished`, `execution_finished` y método `run()` inmediatamente antes de `class PanelPrincipalView` en `views/panel_principal_view.py` (plan.md Paso 3)
- [x] T005 Declarar los 17 nuevos atributos de widgets EQ (`self.lineEdit_dir_querys`, `self.btn_browse_dir_querys`, etc.) más `self._eq_thread`, `self._eq_worker`, `self._progress_dialog` en el bloque `__init__` de `PanelPrincipalView` en `views/panel_principal_view.py` (plan.md Paso 4)
- [x] T006 Agregar llamadas `self.findChild()` para los 15 nuevos widgets EQ al final de `setup_ui()`, más los estados iniciales (`lineEdit_nom_log.setEnabled(False)`, checkboxes en `False`) en `views/panel_principal_view.py` (plan.md Paso 5)
- [x] T007 Implementar método `_update_eq_button_states()` en `PanelPrincipalView` con las invariantes de estado de los 7 botones y los 2 widgets condicionales (plan.md Paso 7) en `views/panel_principal_view.py`
- [x] T008 Agregar conexiones de señales EQ al final de `connect_signals()`: `tabWidget.currentChanged`, clicks de los 7 botones EQ, `itemSelectionChanged` de las 2 listas EQ, `stateChanged` de `checkBox_crear_log` y `textChanged` de `lineEdit_nom_log` en `views/panel_principal_view.py` (plan.md Paso 6)

**Checkpoint**: Con T001–T008 completos, la pestaña "Ejecutar Querys" carga sin errores y todos los botones arrancan deshabilitados. Las user stories pueden comenzar.

---

## Phase 3: User Story 1 — Configurar Directorio de Querys (Priority: P1) 🎯 MVP

**Goal**: El usuario puede seleccionar un directorio `.sql`, ver los archivos en "Querys Disponibles", y la configuración se restaura automáticamente al reabrir la pestaña.

**Independent Test**: Ejecutar Tests 1 y 2 del quickstart.md — sin configuración previa y con `02|DirEnt` guardado en `ConfInsert.conf`.

### Implementación US1

- [x] T009 [US1] Implementar método `_eq_write_config(key, value)` en `views/panel_principal_view.py`: escribe/actualiza/elimina entradas `02|key|value` en `ConfInsert.conf` sin afectar entradas `01|` (plan.md Paso 8)
- [x] T010 [US1] Implementar método `_on_tab_changed(index)` en `views/panel_principal_view.py`: llama `_load_ejecutar_querys_config()` cuando `index == 1` (plan.md Paso 8)
- [x] T011 [US1] Implementar método `_load_ejecutar_querys_config()` en `views/panel_principal_view.py`: lee entradas `02|DirEnt`, `02|Querys`, `02|NomLog` de `ConfInsert.conf`; verifica existencia del directorio; distribuye archivos `.sql` entre ambas listas; limpia entradas inválidas (plan.md Paso 8)
- [x] T012 [US1] Implementar método `_browse_dir_querys()` en `views/panel_principal_view.py`: abre `QFileDialog.getExistingDirectory`, actualiza `lineEdit_dir_querys`, limpia ambas listas, escribe `02|DirEnt` en `ConfInsert.conf` y escanea archivos `.sql` del nuevo directorio (plan.md Paso 8)

**Checkpoint**: Test 1 y 2 del quickstart.md pasan. La pestaña restaura directorio y listas correctamente.

---

## Phase 4: User Story 2 — Gestionar Querys Seleccionados (Priority: P2)

**Goal**: El usuario mueve archivos `.sql` entre "Querys Disponibles" y "Querys Seleccionados" con los cuatro botones; cada operación actualiza `ConfInsert.conf` inmediatamente.

**Independent Test**: Test 3 del quickstart.md — agregar, agregar todos, quitar, quitar todos, verificar `02|Querys` en `ConfInsert.conf` tras cada operación.

### Implementación US2

- [x] T013 [US2] Implementar método `_eq_add_item()` en `views/panel_principal_view.py`: mueve elementos seleccionados de `listWidget_querys_disponibles` a `listWidget_querys_seleccionados` y llama `_eq_save_querys_config()` (plan.md Paso 8)
- [x] T014 [US2] Implementar método `_eq_add_all_items()` en `views/panel_principal_view.py`: mueve todos los elementos de disponibles a seleccionados y llama `_eq_save_querys_config()` (plan.md Paso 8)
- [x] T015 [US2] Implementar método `_eq_remove_item()` en `views/panel_principal_view.py`: mueve elementos seleccionados de `listWidget_querys_seleccionados` a `listWidget_querys_disponibles` y llama `_eq_save_querys_config()` (plan.md Paso 8)
- [x] T016 [US2] Implementar método `_eq_remove_all_items()` en `views/panel_principal_view.py`: mueve todos los elementos de seleccionados a disponibles y llama `_eq_save_querys_config()` (plan.md Paso 8)
- [x] T017 [US2] Implementar método `_eq_save_querys_config()` en `views/panel_principal_view.py`: serializa el contenido de `listWidget_querys_seleccionados` como lista separada por comas y llama `_eq_write_config("Querys", ...)` (plan.md Paso 8)

**Checkpoint**: Test 3 del quickstart.md pasa. Botón "Ejecutar Querys" se habilita/deshabilita según contenido de la lista derecha.

---

## Phase 5: User Story 3 — Configurar y Guardar Opciones de Ejecución (Priority: P3)

**Goal**: El usuario puede activar/desactivar el log, escribir el nombre del archivo, guardarlo en `ConfInsert.conf` y limpiar toda la configuración con un botón.

**Independent Test**: Test 4 y 10 del quickstart.md — activar checkbox log, guardar nombre, verificar `02|NomLog` en `ConfInsert.conf`; luego limpiar y verificar que las entradas `02|*` desaparecen.

### Implementación US3

- [x] T018 [US3] Implementar método `_on_crear_log_changed()` en `views/panel_principal_view.py`: llama `_update_eq_button_states()` para recalcular estado de `lineEdit_nom_log` y `btn_guardar_nom_log` según estado del checkbox (plan.md Paso 8)
- [x] T019 [US3] Implementar método `_eq_guardar_nom_log()` en `views/panel_principal_view.py`: guarda `02|NomLog|<texto>` en `ConfInsert.conf` si `lineEdit_nom_log` tiene contenido; muestra confirmación con `_show_message_box()` (plan.md Paso 8)
- [x] T020 [US3] Implementar método `_resolve_log_path(directory, filename)` en `views/panel_principal_view.py`: retorna ruta completa; si el archivo ya existe añade sufijo `_YYYYMMDD_HHMMSS` antes de la extensión usando `datetime.datetime.now()` (plan.md Paso 8)
- [x] T021 [US3] Implementar método `_eq_limpiar_configuracion()` en `views/panel_principal_view.py`: limpia ambas listas, `lineEdit_dir_querys`, `lineEdit_nom_log`; desmarca ambos checkboxes; deshabilita `lineEdit_nom_log`; elimina todas las entradas `02|*` de `ConfInsert.conf` (plan.md Paso 8)

**Checkpoint**: Tests 4 y 10 del quickstart.md pasan.

---

## Phase 6: User Story 4 — Ejecutar Querys contra la Base de Datos (Priority: P1)

**Goal**: El usuario ejecuta todos los archivos `.sql` seleccionados contra la BD de `ConexionBD.txt`, con progreso visible, opción de cancelar, rollback por archivo o ejecución continua, y resumen final.

**Independent Test**: Tests 5–9 y 11 del quickstart.md — ejecución con rollback, ejecución parcial, cancelación, archivo faltante, BD no disponible.

### Implementación US4

- [x] T022 [US4] Implementar método `_leer_conexion_bd()` en `views/panel_principal_view.py`: parsea `ConexionBD.txt` (líneas `clave = "valor"`, ignorando `#`); valida que existen `my_db`, `my_user`, `my_pass`, `my_host`, `my_port`; muestra error específico con `_show_message_box()` si faltan (plan.md Paso 8)
- [x] T023 [US4] Implementar método `_eq_ejecutar_querys()` en `views/panel_principal_view.py`: verificaciones previas (lista vacía, `ConexionBD.txt` faltante); llama `_leer_conexion_bd()` y `_resolve_log_path()`; escribe encabezado en log si aplica; crea `QProgressDialog` modal; instancia `EjecutarQuerysWorker` y `QThread`; conecta señales; inicia ejecución (plan.md Paso 8)
- [x] T024 [US4] Implementar método `_on_execution_finished(summary)` en `views/panel_principal_view.py`: cierra `QProgressDialog`; detiene y espera `QThread`; construye mensaje de resumen (total/exitosos/fallidos/cancelado + ruta del log si existe); muestra con `_show_message_box()` (plan.md Paso 8)

**Checkpoint**: Tests 5, 6, 7 y 11 del quickstart.md pasan. La ejecución no bloquea la UI.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Estilos visuales y validación integral mediante quickstart.md completo.

- [x] T025 [P] Agregar reglas CSS para los 9 nuevos selectores de widgets EQ (`btn_browse_dir_querys`, `btn_eq_agregar`, `btn_eq_agregar_todos`, `btn_eq_quitar`, `btn_eq_quitar_todos`, `btn_ejecutar_querys` con sus variantes `:hover`, `:disabled`) al final del stylesheet de `_apply_styles()` en `views/panel_principal_view.py` (plan.md Paso 9)
- [ ] T026 Ejecutar Tests 1–4 del `quickstart.md`: directorio sin configuración previa, selección de directorio nuevo, gestión de listas (agregar/quitar/todos), configuración de log
- [ ] T027 Ejecutar Tests 5–7 del `quickstart.md`: ejecución con rollback (modo seguro), ejecución sin rollback (modo parcial), cancelación durante ejecución
- [ ] T028 Ejecutar Tests 8–11 del `quickstart.md`: restauración al reabrir pestaña, directorio guardado eliminado, limpiar configuración, `ConexionBD.txt` faltante

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Sin dependencias — comenzar inmediatamente
- **Phase 2 (Foundational)**: Depende de Phase 1 (T001 completo) — **BLOQUEA** todas las user stories
  - Excepción: T002 (`services/funciones.py`) puede ejecutarse en paralelo con T001 (archivo diferente)
- **Phase 3 (US1)**: Depende de Phase 2 completa
- **Phase 4 (US2)**: Depende de Phase 3 completa (necesita directorio seleccionado para tener items en las listas)
- **Phase 5 (US3)**: Depende de Phase 2 completa (independiente de US1/US2 funcionalmente)
- **Phase 6 (US4)**: Depende de Phase 3, 4 y 5 completas (necesita directorio, listas y opciones de log)
- **Phase 7 (Polish)**: Depende de todas las fases anteriores

### User Story Dependencies

- **US1 (P1)**: Después de Phase 2 — Sin dependencias de otras US
- **US2 (P2)**: Después de US1 — Necesita listas con contenido para probar
- **US3 (P3)**: Después de Phase 2 — Funcionalmente independiente de US1/US2 (puede desarrollarse en paralelo con US1/US2 si se prefiere)
- **US4 (P1)**: Después de US1 + US2 + US3 — Orquesta todos los componentes anteriores

### Within Each User Story

- Primero: métodos auxiliares (`_eq_write_config`, `_resolve_log_path`)
- Luego: métodos de carga/restauración (`_load_ejecutar_querys_config`)
- Luego: métodos de interacción (botones, señales)
- Finalmente: integración y validación con quickstart.md

### Parallel Opportunities

- **T001 y T002**: Pueden ejecutarse en paralelo (archivos distintos: `ui/PanelPrincipal.ui` y `services/funciones.py`)
- **T003–T008**: Secuenciales en `views/panel_principal_view.py` (mismo archivo, dependencias lógicas)
- **T013–T016**: Lógicamente paralelos (métodos independientes), pero en el mismo archivo — implementar secuencialmente
- **T025**: Paralelo al desarrollo de US4 (solo estilos, no lógica)

---

## Parallel Example: Phase 2

```
# Ejecutar en paralelo (archivos diferentes):
T001: Poblar tab_ejecuta_querys en ui/PanelPrincipal.ui
T002: Extender execute_sql_from_file en services/funciones.py

# Una vez T001 completo, continuar secuencialmente:
T003 → T004 → T005 → T006 → T007 → T008
(todos en views/panel_principal_view.py)
```

---

## Implementation Strategy

### MVP First (US1 + US2 — Gestión de archivos sin ejecución)

1. Completar Phase 1: T001
2. Completar Phase 2: T002–T008
3. Completar Phase 3 (US1): T009–T012
4. Completar Phase 4 (US2): T013–T017
5. **PARAR Y VALIDAR**: Tests 1–3 del quickstart.md
6. El usuario puede seleccionar directorio y gestionar listas → valor inmediato

### Incremental Delivery

1. Phase 1 + 2 → Pestaña carga sin errores (estructura visible)
2. + Phase 3 (US1) → Selección de directorio y restauración funcionan
3. + Phase 4 (US2) → Gestión de listas y persistencia funcionan
4. + Phase 5 (US3) → Configuración de log funciona
5. + Phase 6 (US4) → Ejecución completa funciona
6. + Phase 7 → Pulido visual y validación integral

---

## Notes

- `[P]` = archivos diferentes, sin dependencias entre tareas paralelas
- `[Story]` mapea cada tarea a su user story para trazabilidad
- T001 y T002 son las únicas tareas verdaderamente paralelizables (archivos distintos)
- Verificar con quickstart.md tras cada fase completada
- Si `execute_sql_from_file` se rompe (T002), `ejecutar_sql.py` existente también se rompe — verificar compatibilidad backward al finalizar T002
- El prefijo `eq_` en los objectNames evita colisiones con widgets de `tab_genera_inserts`
