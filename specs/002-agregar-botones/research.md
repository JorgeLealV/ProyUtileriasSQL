# Research: Agregar Botones "Agregar Todos" / "Quitar Todos"

**Branch**: `002-agregar-botones` | **Date**: 2026-06-09

## Decisiones de Diseño

### 1. Placement de botones en el archivo `.ui`

**Decision**: Insertar `btn_agregar_todos` y `btn_quitar_todos` dentro del `QVBoxLayout` (`verticalLayout_2`) existente en la columna central de `tab_genera_inserts`, entre `btn_quitar` y el `verticalSpacer` ya existente.

**Rationale**: El `verticalLayout_2` ya contiene `btn_agregar` → `btn_quitar` → `spacer`. Insertar los nuevos botones justo después de sus pares individuales preserva la agrupación visual lógica (agregar / agregar-todos / quitar / quitar-todos / spacer) sin requerir cambios en la estructura del grid.

**Alternatives considered**:
- Añadir una segunda columna de botones → Descartado: complica el grid y rompe la alineación simétrica de las dos listas.
- Inyectar botones dinámicamente en `_inject_missing_components()` → Descartado: los botones son parte del diseño principal, no componentes opcionales; deben vivir en el `.ui`.

---

### 2. Estrategia de estilo visual

**Decision**: Los nuevos botones reutilizan exactamente los mismos tokens de color que sus pares individuales:
- `btn_agregar_todos` → mismos colores que `btn_agregar` (verde petróleo oscuro `#0A2018`/`#143024`/`#4A9068`)
- `btn_quitar_todos` → mismos colores que `btn_quitar` (rojo vino oscuro `#200A0A`/`#301010`/`#905858`)

**Rationale**: La constitución (Principio II) exige consistencia visual. Usar los mismos tokens garantiza que el usuario asocie el color con la semántica de la acción (verde = agregar, rojo = quitar) sin nueva carga cognitiva.

**Alternatives considered**:
- Color diferenciado (ámbar/dorado) para indicar "bulk action" → Descartado: el dorado está reservado para la acción principal (`btn_ejecutar_creacion`); usarlo aquí rompería la jerarquía.

---

### 3. Lógica de estado habilitado/deshabilitado

**Decision**: Extender `_update_button_states()` para incluir los dos nuevos botones:
- `btn_agregar_todos.setEnabled(listWidget_hojas.count() > 0)` — basado en count total, no en selección.
- `btn_quitar_todos.setEnabled(listWidget_tablas_seleccionadas.count() > 0)` — basado en count total.

**Rationale**: La acción "Todos" es independiente de la selección del usuario; depende únicamente de si hay elementos en el origen. Reutilizar el mismo método `_update_button_states()` mantiene un único punto de verdad para el estado de todos los botones del transfer list, en línea con Principio V.

**Alternatives considered**:
- Conectar a `itemSelectionChanged` → No aplica: "Agregar Todos" no necesita selección previa.
- Conectar a `model().rowsInserted` / `rowsRemoved` → Más explícito pero verboso; `_update_button_states()` ya se llama tras cada operación que modifica las listas, por lo que es suficiente.

---

### 4. Implementación de los slots

**Decision**: Añadir dos métodos nuevos `_add_all_items()` y `_remove_all_items()` en `PanelPrincipalView`:

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

**Rationale**: El patrón `takeItem(0)` en loop preserva el orden original y evita iterar sobre índices que cambian. Llamar a `_save_tables_config()` al final garantiza que la configuración persistida refleje el nuevo estado (Principio V).

**Alternatives considered**:
- `addItems([...])` bulk → Requeriría extraer todos los textos primero y limpiar la lista; más código, sin ventaja de rendimiento para listas de <100 items.

---

### 5. Declaración de atributos

**Decision**: Añadir `self.btn_agregar_todos = None` y `self.btn_quitar_todos = None` en `__init__` junto a los demás atributos UI.

**Rationale**: La convención del proyecto declara todos los atributos UI en `__init__` para evitar advertencias de "atributo desconocido" y documentar el contrato de la clase.
