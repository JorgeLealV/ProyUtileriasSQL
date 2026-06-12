# Quickstart: Ejecución Ordenada de Inserts por Dependencias FK

**Feature**: `004-ins-fk-exec-order`
**Date**: 2026-06-12

Esta guía describe cómo probar manualmente los flujos principales de la feature, una vez implementada.

---

## Prerequisitos

1. Conexión a PostgreSQL configurada en `ConexionBD.conf`.
2. Al menos dos tablas relacionadas por FK en el esquema `public`. Ejemplo mínimo:

```sql
-- Tabla padre
CREATE TABLE IF NOT EXISTS public."TipAlcance" (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(100)
);

-- Tabla hijo (FK hacia TipAlcance)
CREATE TABLE IF NOT EXISTS public."TipDocumento" (
    id SERIAL PRIMARY KEY,
    id_alcance INT REFERENCES public."TipAlcance"(id),
    descripcion VARCHAR(100)
);
```

3. Archivos `Ins_` generados por "Ejecutar creación" (o creados manualmente):
   - `Ins_TipAlcance.sql` — inserts para la tabla padre
   - `Ins_TipDocumento.sql` — inserts para la tabla hijo

---

## Escenario 1: Ejecución correcta respetando jerarquía (US-1, P1)

**Objetivo**: Verificar que el sistema ejecuta `Ins_TipAlcance.sql` antes que `Ins_TipDocumento.sql` aunque se agreguen en orden inverso.

**Pasos**:
1. Ir a la pestaña "Ejecutar Querys".
2. En el listbox "Querys disponibles", agregar en este orden:
   - `Ins_TipDocumento` (primero)
   - `Ins_TipAlcance` (segundo)
3. Presionar "Ejecutar Querys".

**Resultado esperado**:
- El log muestra primero `Ins_TipAlcance.sql → Ejecutado`, luego `Ins_TipDocumento.sql → Ejecutado`.
- Mensaje de resumen: "2 ejecutados, 0 pendientes, 0 fallidos."
- No hay errores de violación de FK en PostgreSQL.

---

## Escenario 2: Archivo Ins_ con padre fuera del grupo (US-1, caso borde)

**Objetivo**: Verificar que un archivo `Ins_` cuya tabla padre no tiene archivo `Ins_` en la lista se ejecuta sin restricción.

**Pasos**:
1. Agregar al listbox solo `Ins_TipDocumento` (sin `Ins_TipAlcance`).
2. Presionar "Ejecutar Querys".

**Resultado esperado**:
- El sistema no bloquea `Ins_TipDocumento.sql`.
- El archivo se ejecuta normalmente (el padre `TipAlcance` se considera fuera del grupo).
- Resumen: "1 ejecutado, 0 pendientes, 0 fallidos."

---

## Escenario 3: Archivos Generales + Ins_ en la misma lista (US-1, acceptance scenario 3)

**Objetivo**: Verificar que los archivos Generales se ejecutan antes que los Ins_.

**Pasos**:
1. Agregar al listbox (en este orden):
   - `Ins_TipDocumento` (Ins_)
   - `CrearVistas` (General, sin prefijo Ins_)
   - `Ins_TipAlcance` (Ins_)
2. Presionar "Ejecutar Querys".

**Resultado esperado**:
- El log muestra primero `CrearVistas.sql → Ejecutado` (General).
- Luego `Ins_TipAlcance.sql → Ejecutado` y `Ins_TipDocumento.sql → Ejecutado` en orden topológico.
- El listbox de "Querys seleccionados" no cambia su orden visual.

---

## Escenario 4: Ciclo de dependencia (US-2)

**Prerequisito**: Crear un ciclo artificial (inusual en producción, pero válido para test):

```sql
-- Nota: solo posible con FK deferidas o sin constraints reales
-- Para test: mockear la consulta FK o crear tablas circulares manualmente
```

**Alternativa de prueba manual** (sin modificar la BD):
- El ciclo se puede simular usando el modo de prueba unitaria del servicio `fk_exec_order.py` inyectando un grafo cíclico directamente.

**Resultado esperado al detectar ciclo**:
- El sistema NO ejecuta ningún archivo Ins_.
- Aparece un mensaje de error: "Ciclo detectado: Ins_TablaA.sql, Ins_TablaB.sql".
- Los archivos Ins_ quedan en estado Abortado en el log.

---

## Escenario 5: Archivo Ins_ con padre Fallido → Pendiente (US-3)

**Prerequisito**: Hacer que `Ins_TipAlcance.sql` falle. Ejemplo: el archivo contiene SQL inválido o una violación de constraint.

**Pasos**:
1. Editar `Ins_TipAlcance.sql` para que contenga SQL inválido (p. ej. `INSERT INTO tabla_inexistente VALUES(1);`).
2. Agregar al listbox: `Ins_TipAlcance`, `Ins_TipDocumento`.
3. Presionar "Ejecutar Querys".

**Resultado esperado**:
- `Ins_TipAlcance.sql` → estado **Fallido** (error SQL registrado).
- `Ins_TipDocumento.sql` → estado **Pendiente** (padre Fallido bloquea al hijo).
- La ejecución continúa hasta agotar la lista (no se detiene por el Fallido del padre).
- Segunda pasada: `Ins_TipDocumento.sql` sigue Pendiente (padre nunca fue Ejecutado).
- Resumen final: "0 ejecutados, 1 pendientes, 1 fallidos."

---

## Escenario 6: Límite de revisitas (US-3, acceptance scenario 2)

**Descripción**: Se verifica que el sistema termina cuando un padre supera 5 revisitas.

**Cómo reproducir** (cadena de 6+ archivos todos bloqueados por el primero fallido):
1. Crear una cadena: `Ins_A.sql` (falla) → `Ins_B.sql` → `Ins_C.sql` → ... → `Ins_F.sql`.
2. `Ins_A.sql` contiene SQL inválido.
3. Agregar todos al listbox.
4. Presionar "Ejecutar Querys".

**Resultado esperado**:
- `Ins_A.sql` → Fallido.
- `Ins_B.sql` a `Ins_F.sql` → Pendiente (luego Abortado cuando el contador de A supera 5).
- Mensaje: "Ejecución truncada: límite de revisitas alcanzado. Archivos afectados: ..."

---

## Verificación del Log

Si se habilitó la opción "Crear Log", el archivo `.log` debe contener:

```
=== Ejecución: 2026-06-12 10:30:00 ===
[2026-06-12 10:30:01] CrearVistas.sql | Ejecutado | OK - 3 instrucciones ejecutadas
[2026-06-12 10:30:02] Ins_TipAlcance.sql | Ejecutado | OK - 5 instrucciones ejecutadas
[2026-06-12 10:30:03] Ins_TipDocumento.sql | Ejecutado | OK - 8 instrucciones ejecutadas

=== RESUMEN ===
Ejecutados: 3
Pendientes: 0
Fallidos: 0
```
