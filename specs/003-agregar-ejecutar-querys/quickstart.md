# Quickstart de Prueba: Agregar Pestaña Ejecutar Querys

**Feature Branch**: `003-agregar-ejecutar-querys` | **Date**: 2026-06-10

## Prerrequisitos

1. Python 3.14 en `C:\Users\jleal\AppData\Local\Python\bin\python.exe`
2. `ConexionBD.conf` en la raíz del proyecto con parámetros válidos de PostgreSQL.
3. Al menos un directorio con archivos `.sql` de prueba.
4. Crear archivos de prueba:
   - `C:\temp\querys_test\insert_a.sql` — INSERT válido
   - `C:\temp\querys_test\insert_b.sql` — INSERT con error intencional (tabla inexistente)
   - `C:\temp\querys_test\insert_c.sql` — INSERT válido

## Iniciar la aplicación

```powershell
C:\Users\jleal\AppData\Local\Python\bin\python.exe main.py
```

Abrir el panel principal y seleccionar la pestaña **"Ejecutar Querys"**.

---

## Test 1 — Restauración de configuración vacía

1. Abrir la pestaña "Ejecutar Querys" sin configuración previa (`02|DirEnt` no existe).
2. **Esperado**: ambas listas vacías, todos los botones de gestión deshabilitados, checkbox desmarcados, text box de log deshabilitado.

---

## Test 2 — Selección de directorio

1. Hacer clic en el botón `...` junto al text box de directorio.
2. Seleccionar `C:\temp\querys_test`.
3. **Esperado**:
   - La ruta aparece en el text box.
   - `insert_a.sql`, `insert_b.sql`, `insert_c.sql` aparecen en "Querys Disponibles".
   - "Querys Seleccionados" vacío.
   - `ConfInsert.conf` contiene `02|DirEnt|C:\temp\querys_test`.

---

## Test 3 — Gestión de listas

1. Seleccionar `insert_a.sql` en "Querys Disponibles", presionar **Agregar**.
2. **Esperado**: `insert_a` pasa a "Querys Seleccionados"; `ConfInsert.conf` contiene `02|Querys|insert_a`.
3. Presionar **Agregar Todos**.
4. **Esperado**: `insert_b` e `insert_c` también pasan; "Querys Disponibles" vacío; `02|Querys|insert_a, insert_b, insert_c`.
5. Seleccionar `insert_b` en "Querys Seleccionados", presionar **Quitar**.
6. **Esperado**: `insert_b` regresa a "Querys Disponibles"; `02|Querys|insert_a, insert_c`.
7. Presionar **Quitar Todos**.
8. **Esperado**: todos regresan a "Querys Disponibles"; `02|Querys` se borra o queda vacío.
9. Verificar que el botón "Ejecutar Querys" está deshabilitado cuando "Querys Seleccionados" está vacío.

---

## Test 4 — Configurar log

1. Marcar el checkbox **"Crear Log de Operación"**.
2. **Esperado**: text box "Nombre del archivo log" se habilita.
3. Escribir `mi_log.txt` en el text box; presionar **Guardar nombre**.
4. **Esperado**: `ConfInsert.conf` contiene `02|NomLog|mi_log.txt`.
5. Desmarcar el checkbox.
6. **Esperado**: text box se deshabilita; botón "Guardar nombre" se deshabilita.

---

## Test 5 — Ejecución con rollback (modo seguro)

1. Seleccionar `insert_a.sql`, `insert_b.sql` (con error), `insert_c.sql` en "Querys Seleccionados".
2. Marcar "Crear Log de Operación", ingresar `ejecucion_test.txt`, presionar Guardar.
3. Dejar **desmarcado** "Permitir ejecución de Operaciones válidas".
4. Presionar **Ejecutar Querys**.
5. **Esperado durante ejecución**: aparece indicador de progreso.
6. **Esperado al finalizar**:
   - Resumen: 3 ejecutados, 1 exitoso (`insert_a`), 1 fallido (`insert_b`), 1 exitoso (`insert_c`).
   - `insert_b.sql` tiene rollback completo (tabla queda sin cambios).
   - `insert_a.sql` e `insert_c.sql` se aplicaron.
   - Archivo `ejecucion_test.txt` existe en `C:\temp\querys_test\` con entradas de log.

---

## Test 6 — Ejecución sin rollback (modo parcial)

1. Misma configuración que Test 5.
2. Marcar **"Permitir ejecución de Operaciones válidas"**.
3. Presionar **Ejecutar Querys**.
4. **Esperado**: `insert_b.sql` ejecuta instrucciones válidas, las inválidas se registran en log y se continúa.

---

## Test 7 — Cancelación durante ejecución

1. Con 3+ archivos SQL en "Querys Seleccionados".
2. Presionar **Ejecutar Querys**.
3. Mientras aparece el progreso, presionar **Cancelar**.
4. **Esperado**: el archivo en proceso sufre rollback; los archivos pendientes no se ejecutan; se muestra resumen parcial.

---

## Test 8 — Restauración completa al reabrir pestaña

1. Con configuración activa (directorio + 2 querys seleccionados + nombre log), cambiar a la pestaña "Crear Inserts" y volver a "Ejecutar Querys".
2. **Esperado**: directorio restaurado, listas restauradas correctamente, nombre de log restaurado en el text box.

---

## Test 9 — Directorio guardado eliminado

1. Con `02|DirEnt|C:\temp\querys_test` en ConfInsert.conf, eliminar la carpeta `C:\temp\querys_test`.
2. Cambiar a otra pestaña y volver a "Ejecutar Querys".
3. **Esperado**: ambas listas vacías, text box de directorio vacío, entradas `02|DirEnt` y `02|Querys` borradas de ConfInsert.conf.

---

## Test 10 — Limpiar configuración

1. Con configuración activa, presionar **Limpiar configuración**.
2. **Esperado**: text box de directorio vacío, ambas listas vacías, checkboxes desmarcados, text box log vacío y deshabilitado; entradas `02|DirEnt`, `02|Querys`, `02|NomLog` eliminadas de ConfInsert.conf.

---

## Test 11 — ConexionBD.conf faltante

1. Renombrar `ConexionBD.conf` temporalmente.
2. Con querys seleccionados, presionar **Ejecutar Querys**.
3. **Esperado**: mensaje de error "archivo de conexión no encontrado"; no se procede con ejecución.
4. Restaurar `ConexionBD.conf`.
