# Data Model: Agregar Botones "Agregar Todos" / "Quitar Todos"

**Branch**: `002-agregar-botones` | **Date**: 2026-06-09

> Esta feature es exclusivamente de UI. No hay entidades de base de datos ni modelos de datos nuevos.
> El "modelo" relevante es el estado de los componentes de la interfaz y su ciclo de vida.

## Componentes UI — Estado y Ciclo de Vida

### Transfer List (vista `tab_genera_inserts`)

```
listWidget_hojas (izquierda)          listWidget_tablas_seleccionadas (derecha)
  - items: List[str]                    - items: List[str]
  - count: int                          - count: int
  
btn_agregar         → enabled = len(selectedItems) > 0
btn_agregar_todos   → enabled = count(listWidget_hojas) > 0        ← NUEVO
btn_quitar          → enabled = len(selectedItems) > 0
btn_quitar_todos    → enabled = count(listWidget_tablas_seleccionadas) > 0   ← NUEVO
```

### Invariantes

| Invariante | Descripción |
|------------|-------------|
| Partición | Cada nombre de hoja aparece exactamente en uno de los dos ListWidgets, nunca en ambos ni en ninguno. |
| Persistencia | `ConfInsert.txt[Tablas]` refleja siempre el contenido de `listWidget_tablas_seleccionadas` tras cualquier operación. |
| Estado botones | El estado habilitado de los 4 botones se recalcula en `_update_button_states()` tras cualquier cambio en las listas. |

### Transiciones de Estado

```
Estado: listWidget_hojas vacío
  → btn_agregar:      disabled (sin selección posible)
  → btn_agregar_todos: disabled  ← NUEVO
  → btn_quitar:       depende de selección en listWidget_tablas_seleccionadas
  → btn_quitar_todos: enabled (si hay items en tablas_seleccionadas)

Estado: listWidget_tablas_seleccionadas vacío
  → btn_quitar:       disabled (sin selección posible)
  → btn_quitar_todos: disabled  ← NUEVO
  → btn_agregar:      depende de selección en listWidget_hojas
  → btn_agregar_todos: enabled (si hay items en hojas)

Estado: ambas listas tienen items
  → btn_agregar_todos: enabled
  → btn_quitar_todos:  enabled
```

## Nuevos Widgets — Especificación

| Widget | objectName | Texto | Posición en .ui | Estilo |
|--------|-----------|-------|-----------------|--------|
| QPushButton | `btn_agregar_todos` | `Agregar Todos` | `verticalLayout_2`, tras `btn_agregar` | Idéntico a `btn_agregar` |
| QPushButton | `btn_quitar_todos` | `Quitar Todos` | `verticalLayout_2`, tras `btn_quitar` | Idéntico a `btn_quitar` |

## Archivos Afectados

| Archivo | Tipo de Cambio |
|---------|---------------|
| `ui/PanelPrincipal.ui` | Añadir 2 widgets `QPushButton` en `verticalLayout_2` |
| `views/panel_principal_view.py` | Declarar atributos, find children, connect signals, extend `_update_button_states`, añadir 2 slots, añadir estilos CSS |
