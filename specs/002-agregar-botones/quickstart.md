# Quickstart — Feature 002: Agregar Todos / Quitar Todos

**Branch**: `002-agregar-botones` | **Date**: 2026-06-09

## Cómo probar la feature una vez implementada

### Prerrequisitos

```
python main.py
```

Abrir la aplicación y seleccionar "Crear Archivos SQL de Archivo Excel" desde el menú principal.
La pantalla se abre en la pestaña "Crear Inserts" por defecto.

### Caso de prueba 1 — Agregar Todos (P1)

1. Seleccionar un archivo Excel con al menos 2 hojas usando el botón `...`.
2. Verificar que el botón **"Agregar Todos"** aparece habilitado (color verde petróleo).
3. Verificar que el botón **"Quitar Todos"** aparece deshabilitado (grayed out).
4. Presionar **"Agregar Todos"**.
5. Verificar:
   - `Tablas disponibles` queda vacío.
   - `Tablas seleccionadas` contiene todas las hojas, en el mismo orden.
   - `Agregar Todos` pasa a estar deshabilitado.
   - `Quitar Todos` pasa a estar habilitado.

### Caso de prueba 2 — Quitar Todos (P1)

1. (Continuación del caso 1, con items en `Tablas seleccionadas`.)
2. Presionar **"Quitar Todos"**.
3. Verificar:
   - `Tablas seleccionadas` queda vacío.
   - `Tablas disponibles` contiene todas las hojas de vuelta.
   - `Quitar Todos` pasa a estar deshabilitado.
   - `Agregar Todos` pasa a estar habilitado.

### Caso de prueba 3 — Estado inicial con ListBox vacío

1. Sin cargar ningún archivo Excel, abrir la pantalla.
2. Verificar que **ambos botones** nuevos aparecen deshabilitados.

### Caso de prueba 4 — Persistencia de configuración

1. Usar "Agregar Todos" para seleccionar todas las hojas.
2. Regresar al menú principal ("← Menú principal").
3. Volver a abrir "Crear Archivos SQL de Archivo Excel".
4. Verificar que las tablas siguen en `Tablas seleccionadas` (persistidas en `ConfInsert.conf`).

### Caso de prueba 5 — Interoperabilidad con Agregar/Quitar individual

1. Cargar un Excel con 4+ hojas.
2. Usar **"Agregar"** para mover 1 hoja individualmente.
3. Presionar **"Agregar Todos"**: debe mover las hojas restantes (no duplicar la ya movida).
4. Presionar **"Quitar"** individual para quitar 1 tabla.
5. Presionar **"Quitar Todos"**: debe mover las restantes de vuelta.

## Verificación de estilo

- Los nuevos botones deben tener exactamente el mismo tamaño y fuente que `Agregar` y `Quitar`.
- `Agregar Todos` debe tener el mismo color verde petróleo que `Agregar`.
- `Quitar Todos` debe tener el mismo color rojo vino que `Quitar`.
- El estado deshabilitado debe mostrar el estilo grayed out definido en `QPushButton:disabled`.
