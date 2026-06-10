# Implementation Plan: Agregar Botones "Agregar Todos" y "Quitar Todos"

**Branch**: `002-agregar-botones` | **Date**: 2026-06-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-agregar-botones/spec.md`

## Summary

Añadir dos botones ("Agregar Todos" y "Quitar Todos") en la pestaña "Crear Inserts" del panel principal. Los botones trasladan masivamente todos los elementos entre los dos QListWidget del transfer list existente. La implementación es exclusivamente de UI: modificar el archivo `.ui` para añadir los widgets y extender `PanelPrincipalView` para conectar señales, manejar estado habilitado/deshabilitado y ejecutar la lógica de traslado.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: PySide6 6.11.1 (Qt 6), QUiLoader

**Storage**: `ConfInsert.conf` (configuración de usuario, formato `01|Clave|Valor`)

**Testing**: Manual (ver `quickstart.md`)

**Target Platform**: Windows 10 / 11

**Project Type**: Desktop app PySide6

**Performance Goals**: Operación perceptiblemente instantánea (<100 ms) para listas de hasta 200 hojas.

**Constraints**: Sin nuevas dependencias. Sin cambios en `services/`. Solo `ui/` y `views/`.

**Scale/Scope**: 2 nuevos widgets, ~40 líneas de código en total.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principio | Verificación requerida | Estado |
|---|-----------|------------------------|--------|
| I | Arquitectura en Capas | Cambios solo en `ui/PanelPrincipal.ui` y `views/panel_principal_view.py`; ningún servicio nuevo | ✅ |
| II | Identidad Visual Ejecutiva | `btn_agregar_todos` hereda paleta verde petróleo de `btn_agregar`; `btn_quitar_todos` hereda rojo vino de `btn_quitar`; sin fondos blancos ni saturados | ✅ |
| III | Separación Estricta UI–BD | `views/` sin imports de psycopg2/pandas; `services/` sin PySide6; no hay capa de servicio en esta feature | ✅ |
| IV | Navegación Controlada | Sin cambios de navegación; ventana mantiene X deshabilitado y `closeEvent` existente | ✅ |
| V | Calidad y Persistencia | `_update_button_states()` extendido como punto único de verdad; `_save_tables_config()` llamado tras cada operación masiva | ✅ |

## Project Structure

### Documentation (this feature)

```text
specs/002-agregar-botones/
├── plan.md          ← este archivo
├── research.md      ← decisiones de diseño y alternativas descartadas
├── data-model.md    ← componentes UI, invariantes y transiciones de estado
├── quickstart.md    ← guía de prueba manual
└── tasks.md         ← generado por /speckit-tasks (pendiente)
```

### Source Code — Archivos a modificar

```text
ui/
└── PanelPrincipal.ui          ← añadir btn_agregar_todos y btn_quitar_todos

views/
└── panel_principal_view.py    ← declarar atributos, find, connect, states, slots, styles
```

**No se crean archivos nuevos en `views/` ni en `services/`.**

## Implementation Steps

### Paso 1 — `ui/PanelPrincipal.ui`

Dentro del `<layout class="QVBoxLayout" name="verticalLayout_2">` (columna central de `tab_genera_inserts`), insertar dos nuevos `QPushButton` entre `btn_agregar` y `btn_quitar`, y entre `btn_quitar` y el `verticalSpacer` existente.

**Orden final en `verticalLayout_2`**:
1. `btn_agregar`
2. `btn_agregar_todos`  ← nuevo
3. `btn_quitar`
4. `btn_quitar_todos`   ← nuevo
5. `verticalSpacer`

### Paso 2 — `views/panel_principal_view.py` — Declarar atributos

En `__init__`, junto a `self.btn_agregar` y `self.btn_quitar`, añadir:

```python
self.btn_agregar_todos = None
self.btn_quitar_todos = None
```

### Paso 3 — `setup_ui()` — Find children

Tras las líneas que buscan `btn_agregar` y `btn_quitar`, añadir:

```python
self.btn_agregar_todos = self.findChild(QPushButton, "btn_agregar_todos")
self.btn_quitar_todos = self.findChild(QPushButton, "btn_quitar_todos")
```

### Paso 4 — `connect_signals()` — Conectar señales

Tras las conexiones de `btn_agregar` y `btn_quitar`, añadir:

```python
if self.btn_agregar_todos:
    self.btn_agregar_todos.clicked.connect(self._add_all_items)
if self.btn_quitar_todos:
    self.btn_quitar_todos.clicked.connect(self._remove_all_items)
```

### Paso 5 — `_update_button_states()` — Extender

```python
def _update_button_states(self):
    self.btn_agregar.setEnabled(len(self.listWidget_hojas.selectedItems()) > 0)
    self.btn_quitar.setEnabled(len(self.listWidget_tablas_seleccionadas.selectedItems()) > 0)
    if self.btn_agregar_todos:
        self.btn_agregar_todos.setEnabled(self.listWidget_hojas.count() > 0)
    if self.btn_quitar_todos:
        self.btn_quitar_todos.setEnabled(self.listWidget_tablas_seleccionadas.count() > 0)
```

### Paso 6 — Añadir slots `_add_all_items` y `_remove_all_items`

```python
def _add_all_items(self):
    while self.listWidget_hojas.count() > 0:
        item = self.listWidget_hojas.takeItem(0)
        self.listWidget_tablas_seleccionadas.addItem(item.text())
    self._update_button_states()
    self._save_tables_config()

def _remove_all_items(self):
    while self.listWidget_tablas_seleccionadas.count() > 0:
        item = self.listWidget_tablas_seleccionadas.takeItem(0)
        self.listWidget_hojas.addItem(item.text())
    self._update_button_states()
    self._save_tables_config()
```

### Paso 7 — `_apply_styles()` — Añadir reglas CSS

```css
QPushButton#btn_agregar_todos {
    background-color: #0A2018;
    border: 1px solid #143024;
    color: #4A9068;
}
QPushButton#btn_agregar_todos:hover {
    background-color: #0F2C22;
    border-color: #205840;
    color: #70B090;
}
QPushButton#btn_quitar_todos {
    background-color: #200A0A;
    border: 1px solid #301010;
    color: #905858;
}
QPushButton#btn_quitar_todos:hover {
    background-color: #2C1010;
    border-color: #502020;
    color: #B07878;
}
```

## Complexity Tracking

Sin violaciones de constitución. No aplica.
