# Implementation Plan: Agregar Pestaña Ejecutar Querys

**Branch**: `003-agregar-ejecutar-querys` | **Date**: 2026-06-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-agregar-ejecutar-querys/spec.md`

## Summary

Implementar la funcionalidad completa de la pestaña "Ejecutar Querys" que ya existe vacía en `ui/PanelPrincipal.ui`. La implementación abarca: (1) poblar el layout de la pestaña con widgets de selección de directorio, dos listas de transfer, botones de gestión y panel de opciones; (2) extender `PanelPrincipalView` con toda la lógica de la nueva pestaña; (3) modificar `execute_sql_from_file` en `services/funciones.py` para soportar log por instrucción y control de rollback; (4) implementar ejecución en hilo separado (`QThread`) para no bloquear la UI.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: PySide6 6.11.1 (Qt 6), psycopg2-binary 2.9.12, QUiLoader

**Storage**: `ConfInsert.conf` (02|Clave|Valor), `ConexionBD.txt` (parámetros BD)

**Testing**: Manual (ver `quickstart.md`)

**Target Platform**: Windows 10 / 11

**Project Type**: Desktop app PySide6

**Performance Goals**: Escaneo de directorio < 2 s; progreso de ejecución visible por archivo procesado.

**Constraints**: Sin nuevas dependencias externas. `execute_sql_from_file` se extiende con parámetros opcionales (compatibilidad backward). La llamada existente en `ejecutar_sql.py` no se rompe.

**Scale/Scope**: ~1 nueva pestaña UI, ~400 líneas en `panel_principal_view.py`, ~50 líneas en `funciones.py`, 1 clase worker.

## Constitution Check

| # | Principio | Verificación | Estado |
|---|-----------|--------------|--------|
| I | Arquitectura en Capas | Lógica SQL en `services/funciones.py`; UI y orquestación en `views/panel_principal_view.py`; ningún SQL directo en `views/` | ✅ |
| II | Identidad Visual Ejecutiva | Paleta Dark Executive; QGroupBox con título dorado para panel derecho; botones siguen jerarquía (ejecutar=ámbar, agregar=verde petróleo, quitar=rojo vino) | ✅ |
| III | Separación Estricta UI–BD | `views/` importa de `services/` únicamente; worker usa señales Qt pero invoca la función de servicio sin importar psycopg2 directamente; `services/funciones.py` sin PySide6 | ✅ |
| IV | Navegación Controlada | Sin ventanas nuevas; la pestaña vive dentro del panel principal existente; X deshabilitado y `closeEvent` ya implementados | ✅ |
| V | Calidad y Persistencia | `execute_sql_from_file` mantiene `try/except/finally` con `conn.close()` garantizado; errores comunicados vía `_show_message_box()`; `_update_eq_button_states()` como punto único de verdad | ✅ |

## Project Structure

### Documentation (this feature)

```text
specs/003-agregar-ejecutar-querys/
├── plan.md          <- este archivo
├── research.md      <- decisiones de diseño y alternativas descartadas
├── data-model.md    <- componentes UI, invariantes y transiciones de estado
├── quickstart.md    <- guía de prueba manual
└── tasks.md         <- generado por /speckit-tasks (pendiente)
```

### Source Code — Archivos a modificar

```text
ui/
└── PanelPrincipal.ui                <- poblar tab_ejecuta_querys con layout y widgets

services/
└── funciones.py                     <- extender execute_sql_from_file (log + rollback)

views/
└── panel_principal_view.py          <- nueva lógica completa de tab_ejecuta_querys
                                        + clase EjecutarQuerysWorker
```

**No se crean archivos nuevos en ninguna capa.**

## Implementation Steps

### Paso 1 — `ui/PanelPrincipal.ui` — Poblar tab_ejecuta_querys

Reemplazar el `<widget class="QWidget" name="tab_ejecuta_querys">` vacío con un `QGridLayout` (`gridLayout_eq`) que contenga todos los widgets de la pestaña.

Layout objetivo (4 columnas: 0=lista izq, 1=botones gestión, 2=lista der, 3=panel opciones):

```
tab_ejecuta_querys [QGridLayout: gridLayout_eq]
 Fila 0, col 0-1: QLabel "label_dir_querys"  ("Directorio seleccionado de Querys")
 Fila 1, col 0  : QLineEdit "lineEdit_dir_querys"
 Fila 1, col 1  : QPushButton "btn_browse_dir_querys"  (texto "...")
 Fila 2, col 0  : QLabel "label_querys_disponibles"  ("Querys Disponibles")
 Fila 2, col 2  : QLabel "label_querys_seleccionados"  ("Querys Seleccionados")
 Fila 3, col 0  : QListWidget "listWidget_querys_disponibles"
 Fila 3, col 1  : QVBoxLayout "verticalLayout_eq_btns"
                    QPushButton "btn_eq_agregar"         ("Agregar")
                    QPushButton "btn_eq_agregar_todos"   ("Agregar Todos")
                    QPushButton "btn_eq_quitar"          ("Quitar")
                    QPushButton "btn_eq_quitar_todos"    ("Quitar Todos")
                    QSpacerItem "verticalSpacer_eq"
 Fila 3, col 2  : QListWidget "listWidget_querys_seleccionados"
 Fila 0-3, col 3: QGroupBox "groupBox_eq_opciones"  ("OPCIONES DE EJECUCIÓN")
                    QPushButton "btn_limpiar_config_eq"  ("Limpiar configuración")
                    QCheckBox "checkBox_crear_log"       ("Crear Log de Operación")
                    QCheckBox "checkBox_permitir_parcial" ("Permitir ejecución de Operaciones válidas")
                    QLabel "label_nom_log"               ("Nombre del archivo log")
                    QLineEdit "lineEdit_nom_log"
                    QPushButton "btn_guardar_nom_log"    ("Guardar nombre")
                    QSpacerItem verticalSpacer_eq2
                    QPushButton "btn_ejecutar_querys"    ("▶   Ejecutar Querys")
```

---

### Paso 2 — `views/panel_principal_view.py` — Imports nuevos

Añadir al bloque de imports existente:

```python
import datetime
from PySide6.QtWidgets import QTabWidget, QProgressDialog  # añadir a la lista
from PySide6.QtCore import QObject, QThread, Signal         # añadir a la lista
```

---

### Paso 3 — `views/panel_principal_view.py` — Clase Worker

Insertar antes de `class PanelPrincipalView`:

```python
class EjecutarQuerysWorker(QObject):
    progress_updated = Signal(str)
    file_finished = Signal(str, bool)
    execution_finished = Signal(dict)

    def __init__(self, files, conn_params, log_file, allow_partial):
        super().__init__()
        self._files = files
        self._conn_params = conn_params
        self._log_file = log_file
        self._allow_partial = allow_partial
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        from services.funciones import execute_sql_from_file
        summary = {"total": 0, "ok": 0, "failed": 0, "cancelled": False}
        for sql_file in self._files:
            if self._cancelled:
                summary["cancelled"] = True
                break
            nombre = os.path.basename(sql_file)
            self.progress_updated.emit(f"Ejecutando: {nombre}")
            result = execute_sql_from_file(
                db_name=self._conn_params["my_db"],
                user=self._conn_params["my_user"],
                password=self._conn_params["my_pass"],
                host=self._conn_params["my_host"],
                port=self._conn_params["my_port"],
                sql_file=sql_file,
                log_file=self._log_file,
                allow_partial=self._allow_partial,
            )
            summary["total"] += 1
            if result.get("success"):
                summary["ok"] += 1
            else:
                summary["failed"] += 1
            self.file_finished.emit(nombre, result.get("success", False))
        self.execution_finished.emit(summary)
```

---

### Paso 4 — `__init__` — Atributos nuevos

En el bloque de declaraciones de `__init__`, añadir:

```python
# Widgets tab_ejecuta_querys
self.lineEdit_dir_querys = None
self.btn_browse_dir_querys = None
self.listWidget_querys_disponibles = None
self.btn_eq_agregar = None
self.btn_eq_agregar_todos = None
self.btn_eq_quitar = None
self.btn_eq_quitar_todos = None
self.listWidget_querys_seleccionados = None
self.btn_limpiar_config_eq = None
self.checkBox_crear_log = None
self.checkBox_permitir_parcial = None
self.lineEdit_nom_log = None
self.btn_guardar_nom_log = None
self.btn_ejecutar_querys = None
# Estado de ejecución
self._eq_thread = None
self._eq_worker = None
self._progress_dialog = None
```

---

### Paso 5 — `setup_ui()` — findChild para widgets nuevos

Añadir al final de `setup_ui()`:

```python
# --- Widgets de Ejecutar Querys ---
self.lineEdit_dir_querys = self.findChild(QLineEdit, "lineEdit_dir_querys")
self.btn_browse_dir_querys = self.findChild(QPushButton, "btn_browse_dir_querys")
self.listWidget_querys_disponibles = self.findChild(QListWidget, "listWidget_querys_disponibles")
self.btn_eq_agregar = self.findChild(QPushButton, "btn_eq_agregar")
self.btn_eq_agregar_todos = self.findChild(QPushButton, "btn_eq_agregar_todos")
self.btn_eq_quitar = self.findChild(QPushButton, "btn_eq_quitar")
self.btn_eq_quitar_todos = self.findChild(QPushButton, "btn_eq_quitar_todos")
self.listWidget_querys_seleccionados = self.findChild(QListWidget, "listWidget_querys_seleccionados")
self.btn_limpiar_config_eq = self.findChild(QPushButton, "btn_limpiar_config_eq")
self.checkBox_crear_log = self.findChild(QCheckBox, "checkBox_crear_log")
self.checkBox_permitir_parcial = self.findChild(QCheckBox, "checkBox_permitir_parcial")
self.lineEdit_nom_log = self.findChild(QLineEdit, "lineEdit_nom_log")
self.btn_guardar_nom_log = self.findChild(QPushButton, "btn_guardar_nom_log")
self.btn_ejecutar_querys = self.findChild(QPushButton, "btn_ejecutar_querys")

# Estado inicial
if self.lineEdit_nom_log:
    self.lineEdit_nom_log.setEnabled(False)
if self.checkBox_crear_log:
    self.checkBox_crear_log.setChecked(False)
if self.checkBox_permitir_parcial:
    self.checkBox_permitir_parcial.setChecked(False)
```

---

### Paso 6 — `connect_signals()` — Conexiones nuevas

Añadir al final de `connect_signals()`:

```python
# --- Señales de Ejecutar Querys ---
tab_widget = self.findChild(QTabWidget, "tabWidget")
if tab_widget:
    tab_widget.currentChanged.connect(self._on_tab_changed)

if self.btn_browse_dir_querys:
    self.btn_browse_dir_querys.clicked.connect(self._browse_dir_querys)
if self.btn_eq_agregar:
    self.btn_eq_agregar.clicked.connect(self._eq_add_item)
if self.btn_eq_agregar_todos:
    self.btn_eq_agregar_todos.clicked.connect(self._eq_add_all_items)
if self.btn_eq_quitar:
    self.btn_eq_quitar.clicked.connect(self._eq_remove_item)
if self.btn_eq_quitar_todos:
    self.btn_eq_quitar_todos.clicked.connect(self._eq_remove_all_items)
if self.listWidget_querys_disponibles:
    self.listWidget_querys_disponibles.itemSelectionChanged.connect(self._update_eq_button_states)
if self.listWidget_querys_seleccionados:
    self.listWidget_querys_seleccionados.itemSelectionChanged.connect(self._update_eq_button_states)
if self.btn_limpiar_config_eq:
    self.btn_limpiar_config_eq.clicked.connect(self._eq_limpiar_configuracion)
if self.checkBox_crear_log:
    self.checkBox_crear_log.stateChanged.connect(self._on_crear_log_changed)
if self.lineEdit_nom_log:
    self.lineEdit_nom_log.textChanged.connect(self._update_eq_button_states)
if self.btn_guardar_nom_log:
    self.btn_guardar_nom_log.clicked.connect(self._eq_guardar_nom_log)
if self.btn_ejecutar_querys:
    self.btn_ejecutar_querys.clicked.connect(self._eq_ejecutar_querys)
```

---

### Paso 7 — `_update_button_states()` — Llamada al método EQ

El método existente `_update_button_states()` gestiona solo la pestaña "Crear Inserts". No modificarlo. La nueva pestaña usa `_update_eq_button_states()` (método independiente):

```python
def _update_eq_button_states(self):
    if self.btn_eq_agregar:
        self.btn_eq_agregar.setEnabled(
            bool(self.listWidget_querys_disponibles and
                 self.listWidget_querys_disponibles.selectedItems())
        )
    if self.btn_eq_agregar_todos:
        self.btn_eq_agregar_todos.setEnabled(
            bool(self.listWidget_querys_disponibles and
                 self.listWidget_querys_disponibles.count() > 0)
        )
    if self.btn_eq_quitar:
        self.btn_eq_quitar.setEnabled(
            bool(self.listWidget_querys_seleccionados and
                 self.listWidget_querys_seleccionados.selectedItems())
        )
    if self.btn_eq_quitar_todos:
        self.btn_eq_quitar_todos.setEnabled(
            bool(self.listWidget_querys_seleccionados and
                 self.listWidget_querys_seleccionados.count() > 0)
        )
    if self.btn_ejecutar_querys:
        self.btn_ejecutar_querys.setEnabled(
            bool(self.listWidget_querys_seleccionados and
                 self.listWidget_querys_seleccionados.count() > 0)
        )
    crear_log = bool(self.checkBox_crear_log and self.checkBox_crear_log.isChecked())
    nom_log_texto = self.lineEdit_nom_log.text().strip() if self.lineEdit_nom_log else ""
    if self.lineEdit_nom_log:
        self.lineEdit_nom_log.setEnabled(crear_log)
    if self.btn_guardar_nom_log:
        self.btn_guardar_nom_log.setEnabled(crear_log and bool(nom_log_texto))
```

---

### Paso 8 — Métodos de lógica — Ejecutar Querys

Añadir todos los métodos al final de la clase `PanelPrincipalView`, antes de `closeEvent`:

```python
def _on_tab_changed(self, index):
    if index == 1:
        self._load_ejecutar_querys_config()

def _load_ejecutar_querys_config(self):
    config_path = "ConfInsert.conf"
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("02|"):
                    parts = line.strip().split("|", 2)
                    if len(parts) == 3:
                        config[parts[1]] = parts[2]

    dir_ent = config.get("DirEnt", "").strip()
    querys_guardados = [q.strip() for q in config.get("Querys", "").split(",") if q.strip()]
    nom_log = config.get("NomLog", "").strip()

    if self.listWidget_querys_disponibles:
        self.listWidget_querys_disponibles.clear()
    if self.listWidget_querys_seleccionados:
        self.listWidget_querys_seleccionados.clear()

    if not dir_ent:
        self._update_eq_button_states()
        return

    if not os.path.isdir(dir_ent):
        self._eq_write_config("DirEnt", None)
        self._eq_write_config("Querys", None)
        self._update_eq_button_states()
        return

    if self.lineEdit_dir_querys:
        self.lineEdit_dir_querys.setText(dir_ent)

    archivos_sql = sorted([
        f[:-4] for f in os.listdir(dir_ent)
        if f.lower().endswith(".sql") and os.path.isfile(os.path.join(dir_ent, f))
    ])

    querys_validos = [q for q in querys_guardados if q in archivos_sql]
    if querys_validos != querys_guardados:
        self._eq_write_config("Querys", ",".join(querys_validos) if querys_validos else None)

    for nombre in archivos_sql:
        if nombre in querys_validos:
            if self.listWidget_querys_seleccionados:
                self.listWidget_querys_seleccionados.addItem(nombre)
        else:
            if self.listWidget_querys_disponibles:
                self.listWidget_querys_disponibles.addItem(nombre)

    if nom_log and self.lineEdit_nom_log:
        self.lineEdit_nom_log.setText(nom_log)

    self._update_eq_button_states()

def _browse_dir_querys(self):
    dirpath = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio de Querys")
    if not dirpath:
        return
    if self.lineEdit_dir_querys:
        self.lineEdit_dir_querys.setText(dirpath)
    if self.listWidget_querys_disponibles:
        self.listWidget_querys_disponibles.clear()
    if self.listWidget_querys_seleccionados:
        self.listWidget_querys_seleccionados.clear()
    self._eq_write_config("DirEnt", dirpath)
    self._eq_write_config("Querys", None)

    archivos_sql = sorted([
        f[:-4] for f in os.listdir(dirpath)
        if f.lower().endswith(".sql") and os.path.isfile(os.path.join(dirpath, f))
    ])
    for nombre in archivos_sql:
        if self.listWidget_querys_disponibles:
            self.listWidget_querys_disponibles.addItem(nombre)

    self._update_eq_button_states()

def _eq_add_item(self):
    selected = self.listWidget_querys_disponibles.selectedItems()
    for item in selected:
        self.listWidget_querys_seleccionados.addItem(item.text())
        self.listWidget_querys_disponibles.takeItem(
            self.listWidget_querys_disponibles.row(item))
    self._update_eq_button_states()
    self._eq_save_querys_config()

def _eq_add_all_items(self):
    while self.listWidget_querys_disponibles.count() > 0:
        item = self.listWidget_querys_disponibles.takeItem(0)
        self.listWidget_querys_seleccionados.addItem(item.text())
    self._update_eq_button_states()
    self._eq_save_querys_config()

def _eq_remove_item(self):
    selected = self.listWidget_querys_seleccionados.selectedItems()
    for item in selected:
        self.listWidget_querys_disponibles.addItem(item.text())
        self.listWidget_querys_seleccionados.takeItem(
            self.listWidget_querys_seleccionados.row(item))
    self._update_eq_button_states()
    self._eq_save_querys_config()

def _eq_remove_all_items(self):
    while self.listWidget_querys_seleccionados.count() > 0:
        item = self.listWidget_querys_seleccionados.takeItem(0)
        self.listWidget_querys_disponibles.addItem(item.text())
    self._update_eq_button_states()
    self._eq_save_querys_config()

def _eq_save_querys_config(self):
    items = [
        self.listWidget_querys_seleccionados.item(i).text()
        for i in range(self.listWidget_querys_seleccionados.count())
    ]
    self._eq_write_config("Querys", ",".join(items) if items else None)

def _on_crear_log_changed(self):
    self._update_eq_button_states()

def _eq_guardar_nom_log(self):
    if not self.lineEdit_nom_log:
        return
    texto = self.lineEdit_nom_log.text().strip()
    if not texto:
        return
    self._eq_write_config("NomLog", texto)
    self._show_message_box("Información", "Nombre de log guardado.", QMessageBox.Icon.Information)

def _eq_limpiar_configuracion(self):
    if self.lineEdit_dir_querys:
        self.lineEdit_dir_querys.clear()
    if self.listWidget_querys_disponibles:
        self.listWidget_querys_disponibles.clear()
    if self.listWidget_querys_seleccionados:
        self.listWidget_querys_seleccionados.clear()
    if self.checkBox_crear_log:
        self.checkBox_crear_log.setChecked(False)
    if self.checkBox_permitir_parcial:
        self.checkBox_permitir_parcial.setChecked(False)
    if self.lineEdit_nom_log:
        self.lineEdit_nom_log.clear()

    config_path = "ConfInsert.conf"
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            lines = [l for l in f if not l.startswith("02|")]
        with open(config_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    self._update_eq_button_states()

def _eq_ejecutar_querys(self):
    if not self.listWidget_querys_seleccionados or self.listWidget_querys_seleccionados.count() == 0:
        self._show_message_box("Error", "No hay Querys seleccionados.", QMessageBox.Icon.Warning)
        return

    if not os.path.exists("ConexionBD.txt"):
        self._show_message_box(
            "Error",
            "No se encontró el archivo 'ConexionBD.txt' en el directorio raíz del proyecto.",
            QMessageBox.Icon.Critical,
        )
        return

    conn_params = self._leer_conexion_bd()
    if not conn_params:
        return

    directorio = self.lineEdit_dir_querys.text().strip() if self.lineEdit_dir_querys else ""
    archivos = [
        os.path.join(directorio, self.listWidget_querys_seleccionados.item(i).text() + ".sql")
        for i in range(self.listWidget_querys_seleccionados.count())
    ]

    log_file = ""
    crear_log = bool(self.checkBox_crear_log and self.checkBox_crear_log.isChecked())
    if crear_log and self.lineEdit_nom_log:
        nom_log = self.lineEdit_nom_log.text().strip()
        if nom_log:
            log_file = self._resolve_log_path(directorio, nom_log)

    allow_partial = bool(self.checkBox_permitir_parcial and self.checkBox_permitir_parcial.isChecked())

    if log_file:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n=== Ejecución: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    self._progress_dialog = QProgressDialog("Iniciando ejecución...", "Cancelar", 0, 0, self)
    self._progress_dialog.setWindowTitle("Ejecutar Querys")
    self._progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
    self._progress_dialog.setMinimumDuration(0)
    self._progress_dialog.setValue(0)
    self._progress_dialog.show()

    self._eq_thread = QThread(self)
    self._eq_worker = EjecutarQuerysWorker(archivos, conn_params, log_file, allow_partial)
    self._eq_worker.moveToThread(self._eq_thread)

    self._eq_thread.started.connect(self._eq_worker.run)
    self._eq_worker.progress_updated.connect(self._progress_dialog.setLabelText)
    self._eq_worker.execution_finished.connect(self._on_execution_finished)
    self._progress_dialog.canceled.connect(self._eq_worker.cancel)

    self._eq_thread.start()

def _on_execution_finished(self, summary):
    if self._progress_dialog:
        self._progress_dialog.close()
    if self._eq_thread:
        self._eq_thread.quit()
        self._eq_thread.wait()

    total = summary.get("total", 0)
    ok = summary.get("ok", 0)
    failed = summary.get("failed", 0)
    cancelled = summary.get("cancelled", False)

    msg = f"Ejecución {'cancelada' if cancelled else 'finalizada'}.\n\n"
    msg += f"Archivos ejecutados: {total}\n"
    msg += f"Exitosos: {ok}\n"
    msg += f"Fallidos: {failed}\n"

    log_file = self._eq_worker._log_file if self._eq_worker else ""
    if log_file and os.path.exists(log_file):
        msg += f"\nLog de detalle:\n{log_file}"

    icono = QMessageBox.Icon.Information if not failed else QMessageBox.Icon.Warning
    self._show_message_box("Resumen de Ejecución", msg, icono)

def _leer_conexion_bd(self) -> dict:
    params = {}
    try:
        with open("ConexionBD.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, val = line.partition("=")
                    params[key.strip()] = val.strip().strip('"')
    except Exception as e:
        self._show_message_box("Error", f"No se pudo leer ConexionBD.txt:\n{e}", QMessageBox.Icon.Critical)
        return {}

    required = ["my_db", "my_user", "my_pass", "my_host", "my_port"]
    missing = [k for k in required if not params.get(k)]
    if missing:
        self._show_message_box(
            "Error",
            f"ConexionBD.txt no contiene los parámetros: {', '.join(missing)}",
            QMessageBox.Icon.Critical,
        )
        return {}
    return params

def _resolve_log_path(self, directory: str, filename: str) -> str:
    full_path = os.path.join(directory, filename)
    if not os.path.exists(full_path):
        return full_path
    name, ext = os.path.splitext(filename)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(directory, f"{name}_{timestamp}{ext}")

def _eq_write_config(self, key: str, value):
    config_path = "ConfInsert.conf"
    prefix = f"02|{key}|"
    lines = []
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    lines = [l for l in lines if not l.strip().startswith(prefix)]
    if value is not None:
        lines.append(f"{prefix}{value}\n")
    with open(config_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
```

---

### Paso 9 — `_apply_styles()` — CSS para widgets nuevos

Añadir al stylesheet existente:

```css
QPushButton#btn_browse_dir_querys {
    background-color: #0F1520;
    border: 1px solid #1A2435;
    color: #404A5E;
    padding: 9px 16px;
    font-size: 11pt;
    font-weight: 400;
    letter-spacing: 0;
}
QPushButton#btn_browse_dir_querys:hover {
    border-color: #B8922A;
    color: #D4A848;
    background-color: #181408;
}
QPushButton#btn_eq_agregar,
QPushButton#btn_eq_agregar_todos {
    background-color: #0A2018;
    border: 1px solid #143024;
    color: #4A9068;
}
QPushButton#btn_eq_agregar:hover,
QPushButton#btn_eq_agregar_todos:hover {
    background-color: #0F2C22;
    border-color: #205840;
    color: #70B090;
}
QPushButton#btn_eq_quitar,
QPushButton#btn_eq_quitar_todos {
    background-color: #200A0A;
    border: 1px solid #301010;
    color: #905858;
}
QPushButton#btn_eq_quitar:hover,
QPushButton#btn_eq_quitar_todos:hover {
    background-color: #2C1010;
    border-color: #502020;
    color: #B07878;
}
QPushButton#btn_ejecutar_querys {
    background-color: #1C1408;
    border: 1px solid #40300A;
    color: #C8A03A;
    font-size: 10.5pt;
    font-weight: 700;
    padding: 13px 20px;
    letter-spacing: 0.5px;
}
QPushButton#btn_ejecutar_querys:hover {
    background-color: #281C08;
    border-color: #6A500E;
    color: #E0BE58;
}
QPushButton#btn_ejecutar_querys:disabled {
    background-color: #0A0A08;
    color: #2A2010;
    border-color: #181408;
}
```

---

### Paso 10 — `services/funciones.py` — Extender `execute_sql_from_file`

Reemplazar la función `execute_sql_from_file` y añadir la función auxiliar `_write_log`:

```python
def execute_sql_from_file(
    db_name, user, password, host, port, sql_file,
    log_file="", allow_partial=False
):
    """
    Conecta a PostgreSQL y ejecuta un script SQL instrucción por instrucción.

    log_file (str): Ruta completa del log. "" = sin log.
    allow_partial (bool): True = continuar aunque falle; False = rollback al primer error.
    Retorna dict: success, total_stmts, ok_stmts, failed_stmts, errors.
    """
    result = {
        "file": sql_file,
        "success": False,
        "total_stmts": 0,
        "ok_stmts": 0,
        "failed_stmts": 0,
        "errors": [],
    }

    if not os.path.exists(sql_file):
        result["errors"].append("Archivo no encontrado en disco")
        _write_log(log_file, sql_file, None, "ARCHIVO NO ENCONTRADO")
        return result

    with open(sql_file, "r", encoding="utf-8") as f:
        contenido = f.read()

    stmts = [s.strip() for s in contenido.split(";")
             if s.strip() and not s.strip().startswith("--")]

    if not stmts:
        result["success"] = True
        _write_log(log_file, sql_file, None, "ARCHIVO VACÍO - sin instrucciones ejecutables")
        return result

    conn = None
    try:
        conn = psycopg2.connect(
            dbname=db_name, user=user, password=password, host=host, port=port
        )
        _write_log(log_file, sql_file, None, f"INICIO - {len(stmts)} instrucciones")

        for i, stmt in enumerate(stmts, start=1):
            result["total_stmts"] += 1
            try:
                with conn.cursor() as cur:
                    cur.execute(stmt)
                result["ok_stmts"] += 1
                _write_log(log_file, sql_file, i, "OK")
            except Exception as err:
                result["failed_stmts"] += 1
                result["errors"].append(f"STMT {i}: {err}")
                _write_log(log_file, sql_file, i, f"ERROR: {err}")
                if not allow_partial:
                    conn.rollback()
                    _write_log(log_file, sql_file, None, "ROLLBACK COMPLETO")
                    return result

        conn.commit()
        result["success"] = result["failed_stmts"] == 0
        estado = "EXITO COMPLETO" if result["success"] else f"PARCIAL ({result['failed_stmts']} errores)"
        _write_log(log_file, sql_file, None, f"FIN - {estado}")

    except Exception as error:
        result["errors"].append(f"Error de conexion: {error}")
        _write_log(log_file, sql_file, None, f"ERROR DE CONEXION: {error}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

    return result


def _write_log(log_file: str, sql_file: str, stmt_num, mensaje: str):
    if not log_file:
        return
    import datetime
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    archivo = os.path.basename(sql_file) if sql_file else ""
    stmt_part = f"[STMT {stmt_num}] " if stmt_num is not None else ""
    linea = f"[{ts}] [{archivo}] {stmt_part}{mensaje}\n"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(linea)
    except Exception:
        pass
```

## Complexity Tracking

Sin violaciones de constitución. No aplica.
