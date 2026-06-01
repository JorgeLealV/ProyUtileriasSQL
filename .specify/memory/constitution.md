<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version change  : N/A (initial) → 1.0.0
Bump type       : MINOR — primera ratificación; template vacío reemplazado con
                  contenido específico del proyecto.

Principles added (5):
  I.   Arquitectura en Capas
  II.  Identidad Visual Ejecutiva
  III. Separación Estricta UI–Negocio
  IV.  Navegación Controlada
  V.   Calidad y Persistencia

Sections added:
  ✅  Stack Técnico Fijo
  ✅  Convenciones de Código
  ✅  Governance

Templates updated:
  ✅  .specify/memory/constitution.md     — ratificado v1.0.0
  ✅  .specify/templates/plan-template.md — añadida Opción 4 (desktop app)
  ✅  .specify/templates/tasks-template.md— añadida convención de rutas desktop

Deferred TODOs:
  - Ninguno. Todos los campos resueltos desde constitution.txt.
================================================================================
-->

# ProyUtileriasSQL Constitution

## Core Principles

### I. Arquitectura en Capas

El proyecto DEBE mantener una separación estricta en cuatro capas con
responsabilidades exclusivas y no intercambiables:

- **`main.py`** — Punto de entrada único. Solo instancia `QApplication`,
  crea `MainWindow` e inicia el event loop. No contiene lógica de negocio.
- **`ui/`** — Archivos `.ui` (Qt Designer) y clases generadas. Sin lógica.
- **`views/`** — Clases `QMainWindow`. Responsabilidades: cargar `.ui` con
  `QUiLoader`, conectar señales, validar input del usuario, mostrar
  resultados y gestionar configuración persistente (`ConfInsert.txt`).
- **`services/`** — Funciones de negocio puras. Operan sobre archivos y BD.
  DEBEN ser importables sin efectos secundarios.
- **`controllers/`** — Scripts CLI que llaman directamente a servicios.

La configuración de usuario se persiste en `ConfInsert.txt` con formato
`01|Clave|Valor`. Toda nueva configuración DEBE seguir este formato.

**Rationale**: La mezcla de lógica UI con lógica de negocio produce código
difícil de probar, mantener y extender. La capa `services/` DEBE poder
ejecutarse sin entorno gráfico.

### II. Identidad Visual Ejecutiva

La aplicación DEBE mantener un tema *Dark Executive* coherente en todas
las ventanas y features futuras. Paleta fija:

| Token              | Valor     | Uso                          |
|--------------------|-----------|------------------------------|
| Fondo principal    | `#0D1117` | Ventanas y fondos base       |
| Superficie         | `#111827` | Paneles, pestañas activas    |
| Superficie elevada | `#141B27` | Inputs, combos               |
| Borde              | `#1A2435` | Todos los bordes por defecto |
| Acento primario    | `#B8922A` | Dorado — foco, secciones     |
| Acento hover       | `#E0C570` | Dorado claro — hover activo  |
| Texto principal    | `#C8D0DF` | Contenido                    |
| Texto secundario   | `#68748A` | Labels y subtítulos          |

Reglas no negociables:
- Secciones DEBEN delimitarse con `QGroupBox`; título en dorado, borde
  `#1A2D40`, `letter-spacing: 2px`, texto en MAYÚSCULAS.
- Bordes redondeados DEBEN ser ≤ 2 px. Prohibido `border-radius > 2px`.
- Fondos blancos y colores saturados (>50% S en HSL) están prohibidos.
- Tipografía: Segoe UI, 10 pt base; labels 8.5 pt bold + letter-spacing.
- Jerarquía de botones (de mayor a menor prominencia):
  1. Acción principal → fondo ámbar oscuro, texto dorado.
  2. Acción constructiva → fondo verde petróleo oscuro.
  3. Acción destructiva → fondo rojo vino oscuro.
  4. Navegación/regresar → `#111827`, borde superior dorado en hover.
  5. Examinar archivos → gris neutro, dorado en hover.

**Rationale**: El público objetivo incluye clientes ejecutivos que evalúan
la herramienta visualmente antes de evaluar su funcionalidad. Un tema
inconsistente transmite falta de cuidado técnico.

### III. Separación Estricta UI–Negocio

- Las clases en `views/` DEBEN PROHIBIR la importación de `psycopg2`,
  `pandas` u otras librerías de datos directamente. DEBEN llamar a funciones
  de `services/`.
- Los módulos en `services/` DEBEN PROHIBIR la importación de cualquier
  símbolo de `PySide6`.
- Los stylesheets DEBEN definirse exclusivamente en el método `_apply_styles()`
  de cada vista. El uso de `setStyleSheet()` inline solo se permite con
  comentario de justificación explícita.
- La secuencia de inicialización de toda clase View DEBE ser:
  `load_ui()` → `setup_ui()` → `connect_signals()` → `_apply_styles()`
  → `_update_button_states()` → `_load_config_file()` (si aplica).
- Toda conexión de señales Qt DEBE centralizarse en `connect_signals()`.

**Rationale**: Sin esta separación los servicios se vuelven inprobables y
las vistas se convierten en monolitos imposibles de refactorizar.

### IV. Navegación Controlada

- La navegación entre ventanas DEBE usar `hide()` / `show()`. PROHIBIDO
  llamar `close()` sobre ventanas secundarias.
- Toda ventana secundaria DEBE deshabilitar el botón X del SO en `__init__`:
  ```python
  self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
  ```
- `closeEvent` en ventanas secundarias DEBE interceptar el evento con
  `event.ignore()` y redirigir a `_go_to_main_window()`.
- El botón de regreso DEBE ser claramente visible con texto descriptivo y
  flecha: `"←  Menú principal"`.

**Rationale**: El usuario podría cerrar accidentalmente toda la aplicación
creyendo que solo cierra una ventana. Esto ya ocurrió durante el desarrollo
— la restricción es definitiva.

### V. Calidad y Persistencia

- Las operaciones sobre BD DEBEN usar bloque `try/except/finally` con
  `conn.close()` garantizado en `finally`.
- Los errores DEBEN comunicarse al usuario vía `_show_message_box()`.
  PROHIBIDO silenciar errores con `bare except`.
- Las validaciones DEBEN reportar TODOS los errores encontrados juntos,
  no uno por uno.
- La configuración del usuario DEBE guardarse al ocultar la ventana (no
  solo al cerrar).
- Los labels en la UI DEBEN ser cortos y descriptivos (ej. "Tablas
  disponibles"), sin instrucciones técnicas largas.
- Los scripts en `controllers/` DEBEN poder ejecutarse de forma autónoma
  con rutas documentadas.

**Rationale**: Un fallo silencioso en una operación de BD puede corromper
datos sin que el usuario lo sepa. La claridad en mensajes de error reduce
el tiempo de soporte.

## Stack Técnico Fijo

Las siguientes versiones están fijas para este proyecto. No se DEBEN
actualizar sin un spec aprobado que justifique la migración.

| Componente         | Versión / Detalle                                          |
|--------------------|------------------------------------------------------------|
| Lenguaje           | Python 3.14                                                |
| GUI Framework      | PySide6 6.11.1 (Qt 6)                                      |
| Diseño de UI       | Archivos `.ui` + `QUiLoader` (sin compilación a Python)    |
| Datos / Excel      | pandas 3.0.3 + openpyxl 3.1.5                              |
| Base de datos      | psycopg2-binary 2.9.12 (PostgreSQL)                        |
| Diagramas          | plantuml 0.3.0 + servidor plantuml.com                     |
| SO objetivo        | Windows 10 / 11                                            |
| Python ejecutable  | `C:\Users\jleal\AppData\Local\Python\bin\python.exe`       |

No se DEBEN agregar dependencias externas sin justificación escrita en el
spec de la feature correspondiente.

Funcionalidades implementadas:
- **Crear Inserts** (operativa): convierte hojas Excel → scripts SQL INSERT.
- **Ejecutar Querys** (reservada): ejecutar `.sql` sobre PostgreSQL.
- **Exportar Tablas** (reservada): exportar tablas PostgreSQL → Excel.

Utilidades de desarrollador (sin GUI):
- `controllers/sql_to_puml.py` — SQL CREATE TABLE → diagrama PlantUML.
- `diagram_tools.py` — renderiza `.puml` → PNG vía servidor público.

## Convenciones de Código

**Idioma**:
- Comentarios, docstrings y mensajes al usuario: **español**.
- Identificadores (variables, funciones, clases, archivos): **inglés** (PEP 8).

**Estructura de directorios para features desktop**:
```
views/<nombre>_view.py        # lógica de la ventana
services/<nombre>.py          # funciones de negocio puras
controllers/<nombre>.py       # scripts CLI opcionales
ui/<nombre>.ui                # diseño Qt Designer
```

**Extensión de funcionalidades**:
1. Crear pestaña en `PanelPrincipal.ui` (o nuevo `.ui`).
2. Crear clase view en `views/<nombre>_view.py`.
3. Crear funciones en `services/funciones.py` o `services/<nombre>.py`.
4. Conectar botón en `MainWindow` (`main.py`) siguiendo el patrón de
   `open_panel_principal()`.
5. La nueva ventana DEBE deshabilitar X y redirigir al menú (Principio IV).

**Prohibiciones explícitas**:
- No agregar lógica SQL directamente en `views/`.
- No crear ventanas sin retorno al menú principal.
- No cambiar paleta de colores sin actualizar `_apply_styles()` de todas
  las vistas existentes.
- No compilar archivos `.ui` a Python para uso en runtime.

## Governance

Esta constitución DEBE ser la fuente de verdad para todas las decisiones
de diseño y arquitectura del proyecto. Toda práctica que contradiga un
principio aquí definido DEBE ser corregida o justificada mediante enmienda.

**Proceso de enmienda**:
1. Documentar el cambio propuesto en un archivo `.specify/amendments/`.
2. Incrementar la versión según semántica:
   - MAJOR: eliminación o redefinición incompatible de principios.
   - MINOR: nuevo principio o sección con guía material.
   - PATCH: clarificaciones, correcciones de redacción.
3. Actualizar `LAST_AMENDED_DATE` a la fecha de la enmienda.
4. Propagar cambios a templates dependientes (plan, spec, tasks).

**Cumplimiento**: Todo plan de implementación (`plan.md`) DEBE incluir un
"Constitution Check" que verifique los cinco principios antes de comenzar.
El incumplimiento de cualquier principio MUST/PROHIBIDO bloquea el avance
de la feature hasta ser resuelto o justificado con enmienda aprobada.

**Version**: 1.0.0 | **Ratified**: 2026-06-01 | **Last Amended**: 2026-06-01
