# Implementation Plan: Ejecución Ordenada de Inserts por Dependencias FK

**Branch**: `004-ins-fk-exec-order` | **Date**: 2026-06-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-ins-fk-exec-order/spec.md`

## Summary

Extender el botón "Ejecutar Querys" para que los archivos `Ins_*.sql` se ejecuten respetando las dependencias FK del esquema PostgreSQL `public`. El sistema separa los archivos en dos grupos (Generales e Ins_), consulta las relaciones padre-hijo vía `information_schema`, construye un grafo de dependencias, lo ordena topológicamente con `graphlib.TopologicalSorter`, y ejecuta los archivos con control de estados Pendiente/Fallido y límite de revisitas. Toda la lógica de negocio nueva va en el módulo `services/fk_exec_order.py`; el worker en `views/panel_principal_view.py` solo orquesta y emite signals.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: PySide6 6.11.1, psycopg2-binary 2.9.12, `graphlib` (stdlib Python 3.9+)

**Storage**: PostgreSQL (esquema `public`) — solo lectura para consultar FK; escritura para ejecutar los INSERT scripts

**Testing**: Manual (ver `quickstart.md`); no se añaden tests automáticos en esta feature

**Target Platform**: Windows 10/11 (desktop app)

**Project Type**: Desktop app PySide6

**Performance Goals**: La consulta FK por tabla es O(FK count) — despreciable. El ordenamiento topológico es O(V+E). Para listas típicas de 5-50 archivos, el overhead es < 100 ms.

**Constraints**: Sin dependencias nuevas (solo stdlib + stack fijo). Sin cambios al esquema de `ConfInsert.conf`. Sin modificar el orden visual del listbox.

**Scale/Scope**: Listas de 1-100 archivos `.sql`. Grafos de dependencia < 100 nodos.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principio                   | Verificación requerida                                              | Estado |
|---|-----------------------------|---------------------------------------------------------------------|--------|
| I | Arquitectura en Capas       | Lógica FK/grafo/ordenamiento en `services/fk_exec_order.py`; worker solo coordina | ✅ PASS |
| II| Identidad Visual Ejecutiva  | Sin cambios de UI; resumen via `_show_message_box()` existente     | ✅ PASS |
|III| Separación Estricta UI–BD   | `fk_exec_order.py` importa solo `psycopg2`, `graphlib`, `os`; sin PySide6 | ✅ PASS |
| IV| Navegación Controlada       | Sin nuevas ventanas; sin cambios de navegación                     | ✅ PASS |
| V | Calidad y Persistencia      | Todas las operaciones BD en `try/except/finally`; errores via `_show_message_box()` | ✅ PASS |

**Resultado**: Todos los principios pasan. No hay violaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/004-ins-fk-exec-order/
├── plan.md              # Este archivo
├── research.md          # Decisiones técnicas (graphlib, information_schema, arquitectura)
├── data-model.md        # Entidades: ArchivoEjecucion, EstadoArchivo, GrafoDependencias, ResumenEjecucion
├── quickstart.md        # 6 escenarios de prueba manual
└── tasks.md             # (generado por /speckit-tasks)
```

### Source Code (archivos afectados)

```text
services/
└── fk_exec_order.py          # NUEVO: lógica FK, grafo, ordenamiento, ejecución Ins_

views/
└── panel_principal_view.py   # MODIFICAR: EjecutarQuerysWorker.run() y _on_execution_finished()

services/
├── funciones.py              # SIN CAMBIOS: execute_sql_from_file y _write_log se reutilizan
└── ejecutar_sql.py           # SIN CAMBIOS: script CLI independiente
```

**Structure Decision**: Patrón Desktop app PySide6 (Option 4). Un único módulo nuevo en `services/` concentra toda la lógica de la feature. El worker en `views/` delega a ese módulo sin importar PySide6 en el service.

## Phase 0: Research ✅

Ver [research.md](research.md). Decisiones tomadas:

- **Topological sort**: `graphlib.TopologicalSorter` (stdlib Python 3.9+, detección de ciclos integrada)
- **FK query**: `information_schema` con JOIN a `key_column_usage` y `constraint_column_usage`
- **Ciclos**: Captura de `graphlib.CycleError`; `e.args[1]` proporciona los nodos del ciclo
- **Estado de archivos**: Strings literales (no Enum) en dict en memoria
- **Segunda pasada**: Subconjunto de Pendientes, mismo orden topológico, contadores preservados

## Phase 1: Diseño e Implementación

### Paso 1 — Crear `services/fk_exec_order.py`

**Funciones a implementar**:

#### `separar_archivos(archivos: list[str]) -> tuple[list[str], list[str]]`
- Recibe lista de rutas completas de archivos `.sql`
- Retorna `(generales, ins_files)` manteniendo orden relativo
- Un archivo es Ins_ si `os.path.basename(f).startswith("Ins_") and f.endswith(".sql")`

#### `extraer_tabla(nombre_archivo: str) -> str`
- `nombre_archivo` es solo el basename (p. ej. `Ins_TipAlcance.sql`)
- Retorna `nombre_archivo[4:-4]` → `"TipAlcance"`

#### `obtener_padres_fk(conn, tabla: str) -> list[str]`
- Ejecuta la query de `information_schema` con `%s` parametrizado
- Retorna lista de nombres de tablas padre (puede ser vacía)
- No abre ni cierra conexión — recibe `conn` como parámetro

#### `construir_grafo(ins_files: list[str], conn_params: dict) -> dict[str, set[str]]`
- Para cada archivo Ins_, llama `obtener_padres_fk`
- Filtra solo los padres que tienen archivo Ins_ en el grupo
- Retorna grafo `{archivo: set_de_padres}` con todos los nodos (incluso los sin padres)
- Lanza `RuntimeError` si falla la conexión o la query

#### `ordenar_topologicamente(grafo: dict[str, set[str]]) -> list[str]`
- Usa `graphlib.TopologicalSorter(grafo).static_order()`
- Si lanza `CycleError`, propaga como `CycleError` (el caller la captura)
- Retorna lista ordenada (padres antes que hijos)

#### `ejecutar_generales(archivos: list[str], conn_params: dict, log_file: str, progress_cb) -> tuple[bool, dict]`
- Ejecuta cada archivo General con `execute_sql_from_file`
- Si falla: llama `progress_cb` con mensaje, retorna `(False, summary_parcial)`
- Si todos OK: retorna `(True, summary_parcial)`
- `progress_cb` es callable Python (no Signal Qt)

#### `ejecutar_ins_ordenado(archivos_ordenados: list[str], grafo: dict, conn_params: dict, log_file: str, progress_cb) -> dict`
- Mantiene `estados: dict[str, str]` y `contadores: dict[str, int]`
- Primera pasada: ejecuta cada archivo siguiendo la lógica de pending tracking
- Si `contadores[padre] > 5` → truncar, marcar restantes como Abortado
- Segunda pasada sobre Pendientes (si quedan)
- Retorna `ResumenEjecucion` dict completo

### Paso 2 — Modificar `EjecutarQuerysWorker.run()` en `views/panel_principal_view.py`

**Lógica nueva del método `run()`**:

```python
def run(self):
    from services.fk_exec_order import (
        separar_archivos, construir_grafo, ordenar_topologicamente,
        ejecutar_generales, ejecutar_ins_ordenado
    )
    from graphlib import CycleError

    generales, ins_files = separar_archivos(self._files)

    # Fase Generales
    if generales:
        ok_generales, resumen_g = ejecutar_generales(
            generales, self._conn_params, self._log_file,
            progress_cb=lambda msg: self.progress_updated.emit(msg)
        )
        if not ok_generales:
            resumen_g["cancelled"] = self._cancelled
            self.execution_finished.emit(resumen_g)
            return

    if not ins_files:
        # Solo generales, ya terminamos
        self.execution_finished.emit({...})
        return

    # Fase construcción de grafo
    try:
        self.progress_updated.emit("Consultando dependencias FK...")
        grafo = construir_grafo(ins_files, self._conn_params)
    except RuntimeError as e:
        self.execution_finished.emit({
            "abortado": True, "motivo_abort": str(e), ...
        })
        return

    # Detección de ciclos y ordenamiento
    try:
        ordenados = ordenar_topologicamente(grafo)
    except CycleError as e:
        nodos = list(e.args[1]) if len(e.args) > 1 else []
        self.execution_finished.emit({
            "abortado": True,
            "ciclo_archivos": [os.path.basename(n) for n in nodos],
            ...
        })
        return

    # Fase Ins_
    resumen_ins = ejecutar_ins_ordenado(
        ordenados, grafo, self._conn_params, self._log_file,
        progress_cb=lambda msg: self.progress_updated.emit(msg)
    )

    # Combinar resúmenes
    resumen_final = {**resumen_g_o_vacio, **resumen_ins}
    resumen_final["cancelled"] = self._cancelled
    self.execution_finished.emit(resumen_final)
```

### Paso 3 — Extender `_on_execution_finished()` en `PanelPrincipalView`

**Mensaje de resumen enriquecido**:
- Si `abortado=True` y `ciclo_archivos`: mostrar "Ciclo detectado: {archivos}. No se ejecutó ningún archivo Ins_."
- Si `abortado=True` y `motivo_abort`: mostrar el motivo y archivos pendientes.
- Si `pendientes`: listar archivos pendientes en el mensaje.
- Si `fallidos > 0`: listar archivos fallidos con primer error.
- Mantener el mensaje actual de éxito cuando todo sale bien.

### Paso 4 — Log de Resumen

Al finalizar toda la ejecución, el worker (o el servicio) escribe en el archivo de log:

```
=== RESUMEN ===
Ejecutados: N
Pendientes: N (archivo1.sql, archivo2.sql)
Fallidos:   N (archivo3.sql - ERROR SQL: ...)
Abortado:   Sí/No (motivo si aplica)
```

## Complexity Tracking

> No hay violaciones de la constitución que justificar.

## Implementation Notes

### Manejo de `_write_log` en el nuevo módulo

`fk_exec_order.py` importa `_write_log` desde `services.funciones`:

```python
from services.funciones import _write_log, execute_sql_from_file
```

Si `_write_log` es privada (prefijo `_`), se considera un detalle de implementación de `funciones.py`. Alternativa: mover `_write_log` a un helper compartido o duplicar la lógica mínima en `fk_exec_order.py`. Decisión: importar directamente por ser en el mismo paquete `services/`.

### Inicialización del grafo con todos los nodos

Es crítico que `construir_grafo` incluya todos los nodos en el grafo, incluso los que no tienen dependencias:

```python
grafo = {archivo: set() for archivo in ins_files}  # todos los nodos
# luego agregar aristas según FK encontradas
```

Si un nodo no está en el grafo como key, `TopologicalSorter` puede no incluirlo en el orden.

### Preservación del orden del listbox

El listbox no se modifica. El orden topológico es **interno** al proceso de ejecución. El usuario ve los archivos en el listbox en el orden original; el log muestra el orden de ejecución real.

### Compatibilidad con `allow_partial`

El parámetro `allow_partial` (checkbox "Permitir parcial") afecta el comportamiento de `execute_sql_from_file` dentro de cada archivo. La lógica de pending/fallido es **adicional** y no reemplaza a `allow_partial`:
- `allow_partial=True`: dentro de un archivo Ins_, si una instrucción SQL falla, las otras continúan; el archivo puede quedar con estado "Ejecutado con errores" (se considera Fallido para el grafo de deps).
- `allow_partial=False` (default): el primer error dentro de un archivo Ins_ lo marca como Fallido.

## Post-Design Constitution Re-check

| # | Principio                   | Estado Post-Diseño |
|---|-----------------------------|--------------------|
| I | Arquitectura en Capas       | ✅ PASS — `fk_exec_order.py` en `services/` |
| II| Identidad Visual Ejecutiva  | ✅ PASS — sin cambios de UI |
|III| Separación Estricta UI–BD   | ✅ PASS — callbacks Python simples como puente |
| IV| Navegación Controlada       | ✅ PASS — sin cambios |
| V | Calidad y Persistencia      | ✅ PASS — try/finally en `construir_grafo` y `ejecutar_ins_ordenado` |
