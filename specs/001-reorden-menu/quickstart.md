# Quickstart: Validación del Reordenamiento del Menú

**Feature**: 001-reorden-menu
**Tiempo estimado de validación**: 2 minutos

## Pasos para validar

### 1. Ejecutar la aplicación

```powershell
& "C:\Users\jleal\AppData\Local\Python\bin\python.exe" main.py
```

### 2. Verificar orden de botones

Al abrir el menú principal, los botones deben aparecer en este orden (de arriba a abajo):

| Posición | Texto esperado |
|---|---|
| 1 | Crear Archivos SQL de Archivo Excel |
| 2 | Ejecutar archivos SQL en la base de datos |
| 3 | Obtener tablas de la base de datos a Excel |
| 4 | Configuración |
| — | Salida (sin cambios) |

### 3. Verificar funcionalidad del botón 1

- Clic en "Crear Archivos SQL de Archivo Excel"
- Debe abrirse el panel principal (PanelPrincipal) sin errores
- El botón "← Menú principal" del panel debe regresar al menú

### 4. Verificar aspecto visual

- Colores, fuentes y estilos idénticos al estado anterior
- Hover dorado al pasar el cursor por cada botón
- Botón "Salida" con estilos rojos conservados

## Criterio de éxito

Si el paso 2 muestra el orden correcto y el paso 3 navega sin errores,
la feature está completa y validada.
