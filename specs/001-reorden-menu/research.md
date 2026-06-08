# Research: Reordenamiento y Renombrado del Menú Principal

**Feature**: 001-reorden-menu
**Date**: 2026-06-08

## Hallazgo 1: Archivo UI correcto

**Decisión**: El menú principal a modificar es `ui/main_window.ui`, no `ui/PanelPrincipal.ui`.

**Rationale**: `PanelPrincipal.ui` es el panel con el `QTabWidget` de funcionalidades
(pestañas Crear Inserts, Ejecutar Querys, Exportar Tablas). El menú raíz con los
cuatro `QPushButton` de navegación está en `main_window.ui`.

**Implicación**: El spec tenía una suposición incorrecta en el campo "Archivo de vista".
Corregida en la sección Assumptions del spec.

---

## Hallazgo 2: Compilado Python requerido

**Decisión**: Además de `ui/main_window.ui`, debe actualizarse `ui/main_window_ui.py`.

**Rationale**: `main.py` importa `from ui.main_window_ui import Ui_Form` — usa el
compilado estático, no `QUiLoader`. El compilado contiene:
- `setupUi()` con los `addWidget` en el orden visual
- `retranslateUi()` con los textos de cada botón

Ambos métodos deben reflejar el nuevo orden y nuevos textos.

**Alternativas consideradas**:
- Regenerar con `pyside6-uic` → válido pero requiere Qt Designer o CLI instalada.
- Editar manualmente `main_window_ui.py` → más directo y sin dependencias externas.
  Elegida por simplicidad dado el alcance del cambio.

**Nota sobre constitución**: El uso de un `.ui` compilado (`main_window_ui.py`) es una
excepción pre-existente al Principio I (que establece `QUiLoader`). El panel principal
`PanelPrincipal.ui` sí usa `QUiLoader` correctamente. Esta excepción NO se corrige en
esta feature — está fuera de alcance.

---

## Hallazgo 3: `main.py` no requiere cambios

**Decisión**: `main.py` permanece sin modificaciones.

**Rationale**: Las conexiones de señales usan `objectName` (`btn_creacion`, `btn_salida`),
no posición en el layout. El reorden visual no altera los `objectName`, por lo que
`btn_creacion.clicked.connect(self.open_panel_principal)` sigue siendo válido.

---

## Hallazgo 4: Texto actual de btn_creacion

**Decisión**: El texto actual en `retranslateUi` es `"Crear Inserts"` (no
`"Creación de scripts"` como aparece en `main_window.ui`). El `.ui` y el compilado
están ligeramente desincronizados en este botón. Se corrige con el nuevo texto.

**Implicación**: Al actualizar el compilado, el texto visible pasará de "Crear Inserts"
a "Crear Archivos SQL de Archivo Excel" de forma consistente.
