# Data Model: Agregar Pestaña Ejecutar Querys

**Feature Branch**: `003-agregar-ejecutar-querys` | **Date**: 2026-06-10

## Componentes UI — tab_ejecuta_querys

| Widget | Tipo Qt | objectName | Estado inicial |
|--------|---------|------------|---------------|
| Label directorio | QLabel | `label_dir_querys` | Texto: "Directorio seleccionado de Querys" |
| Text box directorio | QLineEdit | `lineEdit_dir_querys` | Vacío, solo lectura (se llena vía diálogo) |
| Botón browse | QPushButton | `btn_browse_dir_querys` | Habilitado |
| Label lista izquierda | QLabel | `label_querys_disponibles` | Texto: "Querys Disponibles" |
| Lista izquierda | QListWidget | `listWidget_querys_disponibles` | Vacía |
| Botón Agregar | QPushButton | `btn_eq_agregar` | **Deshabilitado** (requiere selección) |
| Botón Agregar Todos | QPushButton | `btn_eq_agregar_todos` | **Deshabilitado** (requiere ≥1 ítem) |
| Botón Quitar | QPushButton | `btn_eq_quitar` | **Deshabilitado** (requiere selección) |
| Botón Quitar Todos | QPushButton | `btn_eq_quitar_todos` | **Deshabilitado** (requiere ≥1 ítem) |
| Label lista derecha | QLabel | `label_querys_seleccionados` | Texto: "Querys Seleccionados" |
| Lista derecha | QListWidget | `listWidget_querys_seleccionados` | Vacía |
| Botón limpiar | QPushButton | `btn_limpiar_config_eq` | Habilitado |
| Checkbox log | QCheckBox | `checkBox_crear_log` | **Desmarcado** (no persiste) |
| Checkbox parcial | QCheckBox | `checkBox_permitir_parcial` | **Desmarcado** (no persiste) |
| Label nom log | QLabel | `label_nom_log` | Texto: "Nombre del archivo log" |
| Text box nom log | QLineEdit | `lineEdit_nom_log` | Vacío, **deshabilitado** |
| Botón guardar nom | QPushButton | `btn_guardar_nom_log` | **Deshabilitado** |
| Botón ejecutar | QPushButton | `btn_ejecutar_querys` | **Deshabilitado** (requiere ≥1 ítem en lista derecha) |

## Invariantes de Estado de Botones

```
btn_eq_agregar.enabled      ← listWidget_querys_disponibles.selectedItems() > 0
btn_eq_agregar_todos.enabled ← listWidget_querys_disponibles.count() > 0
btn_eq_quitar.enabled       ← listWidget_querys_seleccionados.selectedItems() > 0
btn_eq_quitar_todos.enabled ← listWidget_querys_seleccionados.count() > 0
btn_ejecutar_querys.enabled ← listWidget_querys_seleccionados.count() > 0

lineEdit_nom_log.enabled    ← checkBox_crear_log.isChecked()
btn_guardar_nom_log.enabled ← checkBox_crear_log.isChecked()
                              AND lineEdit_nom_log.text().strip() != ""
```

Estas invariantes se recalculan en `_update_eq_button_states()`, llamado tras cada evento que pueda cambiar el estado.

## Configuración Persistente — ConfInsert.conf (prefijo 02)

| Entrada | Formato | Descripción |
|---------|---------|-------------|
| `02\|DirEnt\|<path>` | Ruta absoluta del directorio | Directorio de archivos `.sql` seleccionado |
| `02\|Querys\|<q1>, <q2>` | Nombres sin extensión `.sql`, separados por `,` | Archivos en "Querys Seleccionados" |
| `02\|NomLog\|<nombre>` | Nombre de archivo (con o sin extensión) | Nombre base del archivo de log |

Los checkboxes (`checkBox_crear_log`, `checkBox_permitir_parcial`) **no** se persisten.

## Entidades de Negocio

### ConexionBD.txt
Archivo en el directorio raíz del proyecto. Formato de cada línea:
```
# comentario (ignorado)
my_db = "nombre_base"
my_user = "usuario"
my_pass = "contraseña"
my_host = "host_o_ip"
my_port = "5432"
```
Clave: texto antes del `=` (stripped). Valor: texto después del `=`, sin comillas dobles y con strip().

### Archivo SQL
- Extensión `.sql`, en el directorio seleccionado (escaneo plano, no recursivo).
- Almacenado en ConfInsert.conf sin la extensión.
- Ruta completa: `<directorio> + os.sep + <nombre> + ".sql"`.

### Archivo de Log
- Ruta: `<directorio> + os.sep + <nombre_resuelto>`.
- Si `<nombre>` ya existe como archivo: se añade sufijo `_YYYYMMDD_HHMMSS` antes de la extensión.
- Formato de cada entrada de log (por instrucción):
  ```
  [ARCHIVO: nombre.sql] [STMT 1] OK
  [ARCHIVO: nombre.sql] [STMT 2] ERROR: <mensaje de error>
  [ARCHIVO: nombre.sql] ROLLBACK COMPLETO
  ```
- Encabezado de sesión de ejecución:
  ```
  === Ejecución: YYYY-MM-DD HH:MM:SS ===
  ```

## Transiciones de Estado — Ejecución

```
[IDLE] 
  → usuario presiona btn_ejecutar_querys
  → verificación previa (lista vacía / ConexionBD.txt faltante)
  → [ERROR_PREVIO] si falla alguna verificación
  → [RUNNING] si OK

[RUNNING]
  → Worker inicia por archivo:
      · archivo no existe en disco → SKIP (cuenta como fallido, log si aplica)
      · conexión BD falla → ERROR_CONEXION
      · instrucción falla + allow_partial=False → ROLLBACK_ARCHIVO, siguiente
      · instrucción falla + allow_partial=True → LOG_ERROR, continúa
      · todas instrucciones OK → ARCHIVO_EXITOSO
  → usuario presiona Cancelar → ROLLBACK del archivo en proceso, stop
  → todos archivos procesados → [FINISHED]

[FINISHED / CANCELLED]
  → mostrar resumen (archivos ejecutados / exitosos / fallidos)
  → UI regresa a estado IDLE (habilitar controles)
```

## Función Extendida — execute_sql_from_file

### Firma nueva
```python
def execute_sql_from_file(
    db_name: str,
    user: str,
    password: str,
    host: str,
    port: str,
    sql_file: str,
    log_file: str = "",
    allow_partial: bool = False
) -> dict:
```

### Valor de retorno
```python
{
    "file": "<sql_file>",
    "success": bool,          # True si todos los stmts OK (o allow_partial y al menos uno OK)
    "total_stmts": int,
    "ok_stmts": int,
    "failed_stmts": int,
    "errors": ["<stmt>: <error>", ...]
}
```

### Lógica
1. Si `sql_file` no existe → retornar `{"success": False, "errors": ["Archivo no encontrado"]}` sin abrir BD.
2. Leer y dividir el archivo en instrucciones: `split(';')`, filtrar vacíos y comentarios.
3. Abrir conexión BD (try/finally garantiza `conn.close()`).
4. Por cada instrucción:
   - `cur.execute(stmt)`
   - Si OK: incrementar `ok_stmts`, escribir log `[STMT N] OK`
   - Si error y `allow_partial=False`: escribir log de error + rollback, retornar `success=False`
   - Si error y `allow_partial=True`: escribir log de error, continuar
5. Si llegó al final sin rollback: `conn.commit()`, retornar `success=True` (o `False` si hubo errores parciales).
6. Si `log_file` es no vacío, abrir en modo append con encoding UTF-8.
