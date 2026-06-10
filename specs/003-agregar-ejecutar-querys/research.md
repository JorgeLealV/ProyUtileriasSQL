# Research: Agregar Pestaña Ejecutar Querys

**Feature Branch**: `003-agregar-ejecutar-querys` | **Date**: 2026-06-10

## Decisión 1 — Ejecución en hilo separado (UI no bloqueante)

**Decision**: `QThread` + worker `QObject` con señales (`progress_updated`, `file_finished`, `execution_finished`, `cancelled`).

**Rationale**: `PanelPrincipalView` es un `QMainWindow`; ejecutar `psycopg2` en el hilo principal congela el event loop Qt y deja la UI sin respuesta. `QThread` + señales es el patrón canónico de PySide6 para tareas largas; es compatible con el principio III (el worker importa de `services/`, nunca de PySide6 directamente más allá de `QObject`/`pyqtSignal`).

**Alternatives considered**:
- `QRunnable` + `QThreadPool`: no permite cancelación limpia con rollback.
- `concurrent.futures.ThreadPoolExecutor`: no integra señales Qt; requiere polling o `QTimer`.

**How to apply**: Crear clase `EjecutarQuerysWorker(QObject)` en `views/panel_principal_view.py`. La vista crea el thread y el worker, mueve el worker al thread (`worker.moveToThread(thread)`), conecta señales antes de iniciar, y llama `thread.start()`. El worker llama `execute_sql_from_file` por cada archivo.

---

## Decisión 2 — Parseo de instrucciones SQL por archivo

**Decision**: Dividir el contenido del archivo `.sql` por `;` y filtrar líneas vacías y comentarios (`--`, `/*...*/`).

**Rationale**: La función actual `execute_sql_from_file` ejecuta `cur.execute(sql_script)` sobre el script completo, lo que impide rastrear el resultado de cada instrucción individual. Para implementar log por instrucción y rollback selectivo, necesitamos iterar instrucción por instrucción. Un `split(';')` simple cubre la mayoría de casos de uso (scripts de INSERT/UPDATE/CREATE sin bloques PL/pgSQL complejos).

**Alternatives considered**:
- `sqlparse` (librería externa): más robusto pero requiere nueva dependencia — prohibido por constitución sin justificación.
- Ejecutar todo el script de una vez con `psycopg2.extras`: no permite log por instrucción ni rollback selectivo por instrucción.

**Limitation**: Los bloques `DO $$...$$` o funciones con `;` internos no se parsearán correctamente. Se asume que los scripts de esta herramienta son INSERT/UPDATE/CREATE simples.

---

## Decisión 3 — Formato y parseo de ConexionBD.txt

**Decision**: Parsear línea a línea con `split("=", 1)`. La clave es el texto antes del `=` (stripped); el valor es el texto después, sin comillas dobles y con strip(). Líneas que empiecen con `#` se ignoran.

**Rationale**: El formato documentado en el spec es `my_db = "<Base datos>"`, etc. No existe un parser de ConexionBD.txt en el código actual; se implementa uno inline en el método `_leer_conexion_bd()` de la vista.

**Expected format**:
```
# Conexión a la base de datos
my_db = "CFDI1"
my_user = "postgres"
my_pass = "nicol8899"
my_host = "localhost"
my_port = "5432"
```

---

## Decisión 4 — Colisión de nombre de archivo de log

**Decision**: Si `<nombre>.log` ya existe en el directorio, crear `<nombre>_YYYYMMDD_HHMMSS.<ext>` (sufijo timestamp antes del punto de extensión). Si el nombre no tiene extensión, añadir el sufijo al final.

**Rationale**: Preserva logs históricos sin sobrescribir. El usuario escoge el nombre base una vez; la herramienta garantiza que no se pierda ninguna ejecución anterior.

**How to apply**: Función auxiliar `_resolve_log_path(directory, filename) -> str` en `views/panel_principal_view.py`.

---

## Decisión 5 — Señal de tab cambiada

**Decision**: Conectar `tabWidget.currentChanged` en `connect_signals()`. El índice de "Ejecutar Querys" es `1` (segunda pestaña, índice base-0).

**Rationale**: Qt emite `currentChanged(int)` cada vez que el usuario cambia de pestaña. Conectarlo permite cargar configuración previa solo cuando se activa la pestaña, sin costo en las otras pestañas.

**How to apply**:
```python
tab_widget = self.findChild(QTabWidget, "tabWidget")
if tab_widget:
    tab_widget.currentChanged.connect(self._on_tab_changed)
```
En `_on_tab_changed(index)`: si index == 1, llamar `_load_ejecutar_querys_config()`.

---

## Decisión 6 — Widgets nuevos en tab_ejecuta_querys

**Decision**: Construir el layout de `tab_ejecuta_querys` directamente en `PanelPrincipal.ui` (no inyectado dinámicamente como en tab_genera_inserts) para mayor claridad y mantenibilidad.

**Rationale**: La inyección dinámica de `_inject_missing_components()` en tab_genera_inserts fue una solución de compromiso para compatibilidad. Para la nueva pestaña, que se implementa desde cero, es preferible declarar todos los widgets en el `.ui`.

**Structure**:
```
tab_ejecuta_querys  [QGridLayout: gridLayout_eq]
├── Row 0, col 0-1: label_dir_querys
├── Row 1, col 0  : lineEdit_dir_querys
├── Row 1, col 1  : btn_browse_dir_querys
├── Row 2, col 0  : label_querys_disponibles
├── Row 2, col 2  : label_querys_seleccionados
├── Row 3, col 0  : listWidget_querys_disponibles
├── Row 3, col 1  : [VBoxLayout con botones de gestión]
│                     btn_eq_agregar
│                     btn_eq_agregar_todos
│                     btn_eq_quitar
│                     btn_eq_quitar_todos
│                     verticalSpacer_eq
├── Row 3, col 2  : listWidget_querys_seleccionados
└── Row 3, col 3  : [QGroupBox "OPCIONES DE EJECUCIÓN"]
                      btn_limpiar_config_eq
                      checkBox_crear_log
                      checkBox_permitir_parcial
                      label_nom_log
                      lineEdit_nom_log
                      btn_guardar_nom_log
                      btn_ejecutar_querys
```

El prefijo `eq_` evita colisiones de objectName con widgets de tab_genera_inserts.
