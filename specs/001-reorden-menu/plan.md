# Implementation Plan: Reordenamiento y Renombrado del Menú Principal

**Branch**: `001-reorden-menu` | **Date**: 2026-06-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-reorden-menu/spec.md`

## Summary

Reordenar los cuatro botones de navegación del menú principal y actualizar sus
etiquetas de texto. El cambio afecta únicamente `ui/main_window.ui` (fuente XML)
y `ui/main_window_ui.py` (compilado Python que importa `main.py`). No se toca
lógica de negocio, señales, estilos ni archivos de vista.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: PySide6 6.11.1 (Qt 6)

**Storage**: N/A

**Testing**: Validación visual manual (ver quickstart.md)

**Target Platform**: Windows 10 / 11

**Project Type**: Desktop app PySide6 (ProyUtileriasSQL)

**Performance Goals**: N/A — cambio puramente visual

**Constraints**: Los `objectName` de los botones NO deben cambiar para preservar
las conexiones de señales en `main.py`.

**Scale/Scope**: 2 archivos, ~10 líneas modificadas en total.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verificar los cinco principios de la constitución v1.1.0:

| # | Principio                     | Verificación requerida                                                | Estado |
|---|-------------------------------|-----------------------------------------------------------------------|--------|
| I | Arquitectura en Capas         | ¿Solo se modifica UI? ¿Sin lógica en views/ ni services/?             | ✅     |
| II| Identidad Visual Ejecutiva    | ¿Paleta y estilos sin cambios? ¿Solo texto y orden de widgets?        | ✅     |
|III| Separación Estricta UI–Negocio| ¿Sin imports psycopg2/pandas en views/? ¿Sin PySide6 en services/?    | ✅     |
| IV| Navegación Controlada         | ¿objectNames intactos? ¿Señales en main.py sin cambios?               | ✅     |
| V | Calidad y Persistencia        | ¿Sin operaciones BD? ¿Sin cambios en manejo de errores?               | ✅     |

**Nota**: `main_window_ui.py` es un compilado pre-existente — excepción documentada
en `research.md`. No se corrige en esta feature.

## Project Structure

### Documentation (this feature)

```text
specs/001-reorden-menu/
├── plan.md              # Este archivo
├── research.md          # Hallazgos de investigación de archivos
├── quickstart.md        # Guía de validación manual
├── spec.md              # Especificación de la feature
└── checklists/
    └── requirements.md  # Checklist de calidad del spec
```

### Source Code (archivos a modificar)

```text
ui/
├── main_window.ui       # MODIFICAR: reordenar <item> y actualizar <string>
└── main_window_ui.py    # MODIFICAR: reordenar addWidget() y retranslateUi()

# Sin cambios:
main.py
views/
services/
```

## Mapping de cambios

| objectName          | Texto actual           | Texto nuevo                                  | Pos. actual | Pos. nueva |
|---------------------|------------------------|----------------------------------------------|-------------|------------|
| `btn_creacion`      | "Crear Inserts"        | "Crear Archivos SQL de Archivo Excel"         | 4           | 1          |
| `btn_ejecucion`     | "Ejecución de scripts" | "Ejecutar archivos SQL en la base de datos"   | 2           | 2          |
| `btn_exportacion`   | "Exportación a Excel"  | "Obtener tablas de la base de datos a Excel"  | 3           | 3          |
| `btn_configuracion` | "Configuración"        | "Configuración"                               | 1           | 4          |
| `btn_salida`        | "Salida"               | "Salida"                                      | 5           | 5          |

## Fases de implementación

### Fase 1: Modificar main_window.ui

En `ui/main_window.ui`, dentro de `<layout name="verticalLayout">`, reordenar
los bloques `<item>` al nuevo orden:

```
<item> btn_creacion     </item>   ← primero
<item> btn_ejecucion    </item>
<item> btn_exportacion  </item>
<item> btn_configuracion </item>  ← cuarto
<item> spacer           </item>
<item> btn_salida       </item>   ← sin cambio
```

Actualizar el atributo `<string>` de cada botón con el nuevo texto.

### Fase 2: Modificar main_window_ui.py

En `setupUi()`, reordenar los bloques instanciación + `addWidget` al mismo orden.
En `retranslateUi()`, actualizar los textos de los cuatro botones modificados.

### Fase 3: Validación

Ejecutar la aplicación y seguir los pasos de `quickstart.md`.
