# Research: Ejecución Ordenada de Inserts por Dependencias FK

**Feature**: `004-ins-fk-exec-order`
**Date**: 2026-06-12
**Branch**: `004-ins-fk-exec-order`

---

## 1. Ordenamiento Topológico en Python

### Decisión
Usar `graphlib.TopologicalSorter` de la librería estándar de Python (disponible desde Python 3.9).

### Rationale
- Python 3.14 (stack fijo del proyecto) incluye `graphlib` de forma nativa.
- No requiere dependencias externas (no `networkx`, no `toposort`).
- `TopologicalSorter` detecta ciclos automáticamente: lanza `graphlib.CycleError` si se intenta iterar sobre un grafo cíclico.
- API sencilla: `ts = TopologicalSorter(grafo); list(ts.static_order())`.

### Alternativas consideradas
- **`networkx`**: Librería completa para grafos, excesiva para este caso. Requiere instalación de dependencia adicional (prohibido sin justificación en spec).
- **DFS manual**: Funciona pero es código propio que hay que mantener y testear. `graphlib` es stdlib probada.
- **Kahn's algorithm manual**: Más legible pero más verboso. Sin ventaja vs `graphlib`.

### Uso concreto
```python
from graphlib import TopologicalSorter, CycleError

grafo = {
    "Ins_Hijo.sql": {"Ins_Padre.sql"},
    "Ins_Padre.sql": set(),
}
try:
    orden = list(TopologicalSorter(grafo).static_order())
except CycleError as e:
    # e.args[1] contiene los nodos del ciclo
    nodos_ciclo = e.args[1]
```

---

## 2. Consulta FK en PostgreSQL via information_schema

### Decisión
Usar `information_schema.table_constraints` + `information_schema.key_column_usage` + `information_schema.constraint_column_usage` con JOIN, restringiendo a `tc.table_schema = 'public'`.

### Rationale
- No requiere privilegios de superusuario (a diferencia de `pg_constraint` directo).
- Compatible con psycopg2-binary 2.9.12 (stack fijo del proyecto).
- La query de referencia está validada en el spec (sección 3 del documento original).
- `DISTINCT` en la SELECT evita duplicados cuando hay múltiples columnas en la FK.

### Query final
```sql
SELECT DISTINCT
    ccu.table_name AS tabla_padre
FROM
    information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
        AND ccu.table_schema = tc.table_schema
WHERE
    tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
    AND tc.table_name = %s;
```

### Comportamiento cuando la tabla no existe
Si la tabla no tiene entradas en `information_schema` (tabla inexistente o sin FK), la query retorna 0 filas. Eso se trata como "sin dependencias" — el archivo se ejecuta normalmente.

### Fallo de conexión
Si `psycopg2.connect()` o `cur.execute()` lanza excepción, se propaga con un mensaje claro. El caller (worker) aborta toda la ejecución (FR-004).

---

## 3. Detección de Ciclos

### Decisión
Delegar a `CycleError` de `graphlib`. Al invocar `TopologicalSorter(grafo).static_order()`, si hay ciclo, se lanza `CycleError(msg, nodes_in_cycle)`.

### Rationale
- Detección automática sin código adicional.
- `e.args[1]` proporciona el conjunto de nodos involucrados, suficiente para el mensaje de error del spec.

### Limitación conocida
`CycleError.args[1]` devuelve todos los nodos del ciclo, no necesariamente el camino mínimo. Suficiente para US-2 (informar al usuario qué archivos forman el ciclo).

---

## 4. Control de Pendientes (Estado de Archivos)

### Decisión
Diccionario `estados: dict[str, str]` + `contadores: dict[str, int]`. Constantes de estado como strings (no Enum) para mantener compatibilidad con log y señales.

### Estados
| Constante | Valor string |
|-----------|-------------|
| EN_COLA   | "En cola"   |
| EJECUTADO | "Ejecutado" |
| PENDIENTE | "Pendiente" |
| FALLIDO   | "Fallido"   |
| ABORTADO  | "Abortado"  |

### Algoritmo de segunda pasada
1. Al terminar la primera pasada, filtrar `[f for f, e in estados.items() if e == "Pendiente"]`.
2. Sobre ese subconjunto (en el mismo orden topológico), repetir la lógica de ejecución.
3. El `contadores` no se reinicia — conserva los valores acumulados de la primera pasada.

### Límite de revisitas
El contador se incrementa cuando un padre Pendiente bloquea a un hijo. Si `contadores[padre] > 5`, se trunca la ejecución completa, todos los Pendientes restantes pasan a Abortado.

---

## 5. Arquitectura de Integración con el Worker Existente

### Decisión
Crear un nuevo módulo `services/fk_exec_order.py` con toda la lógica de negocio. El `EjecutarQuerysWorker` en `views/panel_principal_view.py` se adapta para llamar a estas funciones nuevas.

### Rationale
- Cumple Principio I (lógica de negocio en `services/`) y Principio III (`services/` sin PySide6).
- `fk_exec_order.py` no importa ningún símbolo de PySide6.
- Las callbacks de progreso se pasan como callables Python comunes (no signals), permitiendo testear `fk_exec_order.py` sin QApplication.
- El worker sigue siendo el único punto de integración entre el hilo de ejecución y las signals Qt.

### Señales a extender en el worker
El summary actual `{"total", "ok", "failed", "cancelled"}` se extiende con:
- `"pendientes"`: lista de nombres de archivo con estado Pendiente
- `"fallidos"`: lista de dicts `{archivo, errores}`
- `"abortado"`: bool
- `"motivo_abort"`: str (si abortado)
- `"entradas_log"`: lista de dicts para el log (si se usa archivo de log)

La señal `execution_finished = Signal(dict)` ya acepta un dict arbitrario; no se necesita cambiar la firma de la señal.

---

## 6. Impacto en `_on_execution_finished`

### Decisión
Extender `_on_execution_finished` en `PanelPrincipalView` para mostrar el resumen enriquecido mediante `_show_message_box`. El mensaje mostrará:
- Total ejecutados / pendientes / fallidos
- Si hubo ciclo detectado: nombre de archivos involucrados
- Si hubo abort por revisitas: archivos pendientes con motivo

No se necesita nueva ventana ni nuevo widget de log: el texto cabe en el QMessageBox existente para la mayoría de los casos.

---

## 7. Archivo de Log

### Decisión
Reutilizar el mecanismo de log existente (`log_file` path + `_write_log` en `funciones.py`) con entradas adicionales. El nuevo módulo `fk_exec_order.py` escribe directamente al archivo de log usando la misma función `_write_log` (importada desde `funciones.py`) o un helper equivalente.

### Alternativa rechazada
Crear una nueva función de log en `fk_exec_order.py` — innecesario, `_write_log` ya está en `funciones.py` y hace lo que se necesita.
