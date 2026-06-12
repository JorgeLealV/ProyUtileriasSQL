# Tasks: Ejecución Ordenada de Inserts por Dependencias FK

**Input**: Design documents from `specs/004-ins-fk-exec-order/`

**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: No incluidos — no solicitados en el spec.

**Organization**: Tareas agrupadas por User Story para permitir implementación y prueba independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede correr en paralelo (archivos distintos, sin dependencias incompletas)
- **[Story]**: User Story a la que pertenece la tarea (US1, US2, US3)
- Sin label: Setup/Foundational/Polish

---

## Phase 1: Setup

**Purpose**: Crear la estructura base del nuevo módulo de servicio.

- [x] T001 Crear archivo `services/fk_exec_order.py` con imports base (`os`, `graphlib`, `psycopg2`) y docstring del módulo

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Funciones de utilidad compartidas que TODAS las User Stories necesitan. Deben estar completas antes de comenzar cualquier User Story.

**⚠️ CRÍTICO**: Ninguna User Story puede implementarse hasta completar esta fase.

- [x] T002 Implementar `separar_archivos(archivos: list[str]) -> tuple[list[str], list[str]]` en `services/fk_exec_order.py` — separa lista por prefijo `Ins_`, mantiene orden relativo
- [x] T003 Implementar `extraer_tabla(nombre_archivo: str) -> str` en `services/fk_exec_order.py` — quita prefijo `Ins_` y sufijo `.sql` del basename
- [x] T004 Implementar `obtener_padres_fk(conn, tabla: str) -> list[str]` en `services/fk_exec_order.py` — query a `information_schema` con la SQL parametrizada del spec (sección 3)
- [x] T005 Implementar `construir_grafo(ins_files: list[str], conn_params: dict) -> dict[str, set[str]]` en `services/fk_exec_order.py` — abre conexión psycopg2, llama `obtener_padres_fk` por tabla, filtra padres dentro del grupo, retorna grafo con todos los nodos; lanza `RuntimeError` si falla la conexión o query

**Checkpoint**: Fundación lista — las funciones `separar_archivos`, `extraer_tabla`, `obtener_padres_fk` y `construir_grafo` están implementadas y la implementación de User Stories puede comenzar.

---

## Phase 3: User Story 1 — Ejecución correcta respetando jerarquía (Priority: P1) 🎯 MVP

**Goal**: Los archivos `Ins_` se ejecutan en orden topológico padre→hijo. Los archivos Generales se ejecutan primero. Si un General falla, se detiene todo sin procesar Ins_.

**Independent Test**: Agregar `Ins_TipDocumento` (hijo) antes que `Ins_TipAlcance` (padre) al listbox; al ejecutar, el log debe mostrar `Ins_TipAlcance.sql` ejecutado primero. (Ver Escenario 1 de `quickstart.md`)

### Implementation for User Story 1

- [x] T006 [US1] Implementar `ordenar_topologicamente(grafo: dict[str, set[str]]) -> list[str]` en `services/fk_exec_order.py` — usa `graphlib.TopologicalSorter(grafo).static_order()`; ciclos no manejados aquí (US2 lo agrega)
- [x] T007 [US1] Implementar `ejecutar_generales(archivos: list[str], conn_params: dict, log_file: str, progress_cb) -> tuple[bool, dict]` en `services/fk_exec_order.py` — itera archivos Generales con `execute_sql_from_file`; retorna `(False, summary)` al primer fallo; llama `progress_cb` con cada nombre de archivo
- [x] T008 [US1] Implementar `ejecutar_ins_ordenado(archivos_ordenados: list[str], grafo: dict, conn_params: dict, log_file: str, progress_cb) -> dict` en `services/fk_exec_order.py` — versión básica: ejecuta cada archivo en orden con `execute_sql_from_file`; sin tracking de Pendiente (se agrega en US3); retorna dict con `total`, `ok`, `failed`, `pendientes=[]`, `abortado=False`
- [x] T009 [US1] Adaptar `EjecutarQuerysWorker.run()` en `views/panel_principal_view.py` — importar funciones de `services.fk_exec_order`; llamar `separar_archivos` → `ejecutar_generales` → `construir_grafo` → `ordenar_topologicamente` → `ejecutar_ins_ordenado`; manejar `RuntimeError` de `construir_grafo` emitiendo `execution_finished` con `abortado=True`
- [x] T010 [US1] Extender `_on_execution_finished()` en `views/panel_principal_view.py` — leer campos nuevos del summary: `abortado`, `motivo_abort`, `ciclo_archivos`, `pendientes`; mostrar en `_show_message_box()` el resumen enriquecido (ejecutados / pendientes / fallidos); mantener compatibilidad con resumen actual

**Checkpoint**: US1 completa — ejecutar Escenarios 1, 2 y 3 de `quickstart.md` sin errores.

---

## Phase 4: User Story 2 — Detección y reporte de ciclos (Priority: P2)

**Goal**: Si hay un ciclo de dependencias FK entre archivos `Ins_`, el sistema lo detecta antes de ejecutar cualquier archivo, informa los archivos involucrados y no procede con la ejecución del grupo Ins_.

**Independent Test**: Con un grafo cíclico inyectado directamente en `ordenar_topologicamente`, verificar que se lanza `CycleError` y el worker emite `execution_finished` con `abortado=True` y `ciclo_archivos` poblado. (Ver Escenario 4 de `quickstart.md`)

### Implementation for User Story 2

- [x] T011 [US2] Extender `ordenar_topologicamente()` en `services/fk_exec_order.py` — capturar `graphlib.CycleError`; re-lanzar como `CycleError` (el caller la maneja); extraer `e.args[1]` con los nodos del ciclo
- [x] T012 [US2] Manejar `CycleError` en `EjecutarQuerysWorker.run()` en `views/panel_principal_view.py` — capturar `CycleError` lanzada por `ordenar_topologicamente`; emitir `execution_finished` con `abortado=True`, `ciclo_archivos=[basenames de nodos]`, `motivo_abort="Ciclo detectado"`
- [x] T013 [US2] Extender `_on_execution_finished()` en `views/panel_principal_view.py` — si `ciclo_archivos` está poblado, mostrar mensaje específico: "Ciclo de dependencias detectado. Archivos involucrados: {lista}. No se ejecutó ningún archivo Ins_."

**Checkpoint**: US2 completa — el sistema detecta ciclos y reporta correctamente sin ejecutar nada.

---

## Phase 5: User Story 3 — Control de archivos bloqueados por padres pendientes (Priority: P3)

**Goal**: Si un archivo padre queda Fallido o Pendiente, sus hijos se marcan Pendiente. El sistema lleva contador de revisitas por padre; si supera 5, trunca la ejecución y reporta todos los archivos pendientes. Realiza segunda pasada sobre Pendientes al finalizar el recorrido inicial.

**Independent Test**: `Ins_TipAlcance.sql` con SQL inválido + `Ins_TipDocumento.sql` que depende de él → TipDocumento debe quedar Pendiente, no Fallido. (Ver Escenarios 5 y 6 de `quickstart.md`)

### Implementation for User Story 3

- [x] T014 [US3] Extender `ejecutar_ins_ordenado()` en `services/fk_exec_order.py` — agregar `estados: dict[str, str]` y `contadores: dict[str, int]`; antes de ejecutar cada archivo verificar si algún padre en `grafo[archivo]` está en estado `"Pendiente"` o `"Fallido"`; si sí → marcar archivo como `"Pendiente"`, incrementar contador del padre bloqueante
- [x] T015 [US3] Implementar truncación por límite de revisitas en `ejecutar_ins_ordenado()` en `services/fk_exec_order.py` — si `contadores[padre] > 5` → marcar todos los Pendientes restantes como `"Abortado"`, setear `abortado=True` y `motivo_abort` en el summary, retornar inmediatamente
- [x] T016 [US3] Implementar segunda pasada sobre Pendientes en `ejecutar_ins_ordenado()` en `services/fk_exec_order.py` — al terminar el recorrido inicial, filtrar `[f for f in archivos_ordenados if estados[f] == "Pendiente"]`; repetir la misma lógica de ejecución conservando `contadores` acumulados
- [x] T017 [US3] Extender `_on_execution_finished()` en `views/panel_principal_view.py` — si `pendientes` no vacío: listar archivos en el mensaje; si `abortado=True` por revisitas: mostrar "Ejecución truncada: límite de revisitas alcanzado. Archivos afectados: {lista}"

**Checkpoint**: US3 completa — ejecutar Escenarios 5 y 6 de `quickstart.md`; verificar que Pendiente ≠ Fallido y que el límite de revisitas termina la ejecución limpiamente.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Log de resumen completo y verificación final.

- [x] T018 [P] Implementar escritura del bloque `=== RESUMEN ===` al final del archivo de log en `services/fk_exec_order.py` — incluir totales de Ejecutados, Pendientes, Fallidos; si `abortado`: indicar motivo y archivos afectados
- [ ] T019 Validar los 6 escenarios del `quickstart.md` manualmente ejecutando la aplicación con datos reales de PostgreSQL

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — comenzar inmediatamente
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA todas las User Stories
- **US1 (Phase 3)**: Depende de Foundational — MVP entregable
- **US2 (Phase 4)**: Depende de US1 (necesita `ordenar_topologicamente` base)
- **US3 (Phase 5)**: Depende de US1 (necesita `ejecutar_ins_ordenado` base)
- **Polish (Phase 6)**: Depende de que las User Stories deseadas estén completas

### User Story Dependencies

- **US1 (P1)**: Puede comenzar tras Foundational. Sin dependencias de otras US.
- **US2 (P2)**: Depende de US1 (extiende `ordenar_topologicamente`). Independiente de US3.
- **US3 (P3)**: Depende de US1 (extiende `ejecutar_ins_ordenado`). Independiente de US2.
- **US2 y US3**: Pueden trabajarse en paralelo (tocan funciones distintas) una vez US1 esté completa.

### Within Each User Story

- Funciones en `services/fk_exec_order.py` antes de modificaciones en `views/panel_principal_view.py`
- `ejecutar_generales` antes de `ejecutar_ins_ordenado` (el worker las llama en ese orden)
- `_on_execution_finished` siempre al final (depende del summary completo)

### Parallel Opportunities

- T002, T003 [Foundational]: Pueden implementarse en paralelo (funciones independientes)
- T004, T005 [Foundational]: T005 depende de T004 (llama `obtener_padres_fk`)
- T006, T007 [US1]: Pueden implementarse en paralelo (funciones independientes)
- T011, T012 [US2]: T012 depende de T011 (captura la excepción que T011 lanza)
- T014, T015, T016 [US3]: Secuenciales (todas modifican `ejecutar_ins_ordenado`)
- T018 [Polish]: Paralelo con otras tareas de Polish si hubiera más

---

## Parallel Example: User Story 1

```
# Lanzar en paralelo (funciones independientes en el mismo archivo):
T006: ordenar_topologicamente()   → services/fk_exec_order.py
T007: ejecutar_generales()        → services/fk_exec_order.py

# Luego secuencial (T008 llama a funciones de T006/T007):
T008: ejecutar_ins_ordenado() básico

# Luego secuencial (worker llama a todo):
T009: EjecutarQuerysWorker.run() adaptado → views/panel_principal_view.py
T010: _on_execution_finished() extendido  → views/panel_principal_view.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup (T001)
2. Completar Phase 2: Foundational (T002–T005)
3. Completar Phase 3: User Story 1 (T006–T010)
4. **DETENER Y VALIDAR**: Escenarios 1, 2 y 3 del `quickstart.md`
5. Demostrar funcionalidad básica de ordenamiento

### Incremental Delivery

1. Setup + Foundational → Módulo base listo
2. US1 → Ordenamiento básico funcionando (MVP)
3. US2 → Ciclos detectados y reportados
4. US3 → Pendientes controlados con segunda pasada
5. Polish → Log completo + validación final

### Flujo de Trabajo en Un Solo Developer

1. T001 → T002–T003 (paralelo) → T004 → T005
2. T006–T007 (paralelo) → T008 → T009 → T010 ← **Validar US1**
3. T011 → T012 → T013 ← **Validar US2**
4. T014 → T015 → T016 → T017 ← **Validar US3**
5. T018 → T019

---

## Notes

- [P] tasks = archivos distintos, sin dependencias incompletas entre sí
- [Story] label mapea cada tarea a su User Story para trazabilidad
- `services/fk_exec_order.py` no debe importar PySide6 (Principio III de la constitución)
- `views/panel_principal_view.py` no debe importar psycopg2 directamente (idem)
- Callbacks de progreso: pasar como `lambda msg: self.progress_updated.emit(msg)` desde el worker
- `_write_log` puede importarse desde `services.funciones` para escribir entradas de log
- Verificar con `quickstart.md` Escenario 2 que un hijo sin padre en el grupo se ejecuta normalmente
- El listbox "Querys seleccionados" NO debe modificarse visualmente durante ni después de la ejecución
