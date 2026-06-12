# SPECIFY — Ejecución Ordenada de Archivos SQL con Jerarquía de Dependencias

**Módulo:** Pestaña "Ejecutar Querys"  
**Componente afectado:** Botón "Ejecutar Querys"  
**Fecha:** 2026-06-12  
**Estado:** Borrador v1.0

---

## 1. Contexto

El botón "Ejecutar Querys" recorre el list box "Querys Seleccionados" y ejecuta cada archivo `.sql` contra la base de datos PostgreSQL configurada. Los archivos pueden ser de dos tipos según su nombre:

- **Archivos de tipo General:** no inician con el prefijo `Ins_`. Se ejecutan sin ninguna verificación previa.
- **Archivos de tipo Inserción (`Ins_`):** inician con el prefijo `Ins_` y terminan con `.sql`. El fragmento entre ambos representa el nombre de una tabla en la base de datos (p. ej., `Ins_TipAlcance.sql` → tabla `TipAlcance`).

---

## 2. Objetivo

Garantizar que los archivos de tipo `Ins_` se ejecuten respetando la jerarquía de dependencias padre–hijo definida por las **Foreign Keys (FK)** del esquema PostgreSQL, de modo que ninguna tabla hija se intente insertar antes de que su tabla padre haya sido procesada exitosamente.

---

## 3. Fuente de Dependencias

Las relaciones padre–hijo se obtienen consultando el esquema de la base de datos PostgreSQL a través de `information_schema` y `pg_constraint`. Una tabla **padre** es aquella a la que apunta una Foreign Key de la tabla **hijo**.

**Query de referencia para obtener la tabla padre de una tabla dada:**

```sql
SELECT
    ccu.table_name AS tabla_padre
FROM
    information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
        AND ccu.table_schema = tc.table_schema
WHERE
    tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
    AND tc.table_name = :nombreTablaHijo;
```

> **Nota:** Solo se consideran FK dentro del esquema `public`. Si el esquema es configurable en la aplicación, se deberá usar el esquema activo en lugar de `'public'`.

---

## 4. Flujo Principal de Ejecución

### Fase 1 — Separación de la cola

Al presionar el botón "Ejecutar Querys":

1. Recorrer el list box "Querys Seleccionados" en el orden actual.
2. Separar los archivos en dos grupos, **manteniendo su orden relativo**:
   - **Grupo General:** archivos cuyo nombre **no** inicia con `Ins_`.
   - **Grupo Ins:** archivos cuyo nombre inicia con `Ins_` y termina con `.sql`.

### Fase 2 — Ejecución del Grupo General

3. Ejecutar cada archivo del **Grupo General** en su orden original, uno por uno.
4. Si un archivo del Grupo General falla (error SQL):
   - Registrar el error en el log con: nombre de archivo, mensaje de error de PostgreSQL.
   - Detener la ejecución completa e informar al usuario.
   - **No continuar** con el Grupo Ins.

### Fase 3 — Construcción del grafo de dependencias (Grupo Ins)

5. Para cada archivo del **Grupo Ins**, extraer el nombre de tabla:
   - Quitar el prefijo `Ins_` y el sufijo `.sql`.
   - Ejemplo: `Ins_TipAlcance.sql` → `TipAlcance`.

6. Consultar en la base de datos las tablas padre de cada tabla extraída (ver query en sección 3).

7. Para cada tabla padre encontrada, verificar si existe un archivo correspondiente en el **Grupo Ins**:
   - La comparación es: `tabla_padre == nombre_extraído_de_archivo_Ins`.
   - Si existe → registrar la dependencia: `TablasHijo` depende de `TablaPadre`.
   - Si **no** existe en el Grupo Ins → **ignorar esa dependencia** (se asume que la tabla padre ya existe en la base de datos o no es responsabilidad de esta ejecución).

8. Con las dependencias registradas, construir un **grafo dirigido** donde:
   - Cada nodo es un archivo del Grupo Ins.
   - Una arista `A → B` significa "A debe ejecutarse antes que B" (A es padre de B).

9. Aplicar un **ordenamiento topológico** al grafo para obtener la secuencia de ejecución correcta (padres antes que hijos).

> **Caso especial — ciclo de dependencias:** Si al construir el grafo se detecta un ciclo (p. ej., A depende de B y B depende de A), registrar inmediatamente en el log los nodos involucrados en el ciclo, detener la ejecución del Grupo Ins e informar al usuario. Este caso es un error de configuración de datos.

### Fase 4 — Ejecución del Grupo Ins con control de pendientes

10. Ejecutar los archivos del Grupo Ins en el orden obtenido del ordenamiento topológico.

11. Para cada archivo a ejecutar, verificar si alguna de sus tablas padre (dentro del Grupo Ins) está marcada como **Pendiente**:
    - **Si ningún padre está Pendiente** → ejecutar el archivo normalmente.
      - Éxito: marcar el archivo como **Ejecutado**.
      - Error SQL: registrar en log y marcar como **Fallido** (distinto de Pendiente). Detener la ejecución e informar.
    - **Si al menos un padre está Pendiente** → **no ejecutar** el archivo. Marcarlo como **Pendiente**.
      - Incrementar en 1 el contador de visitas del archivo padre que está pendiente.
      - Si el contador de visitas de ese padre **supera 5** → truncar la ejecución completa. Registrar en el log todos los archivos con estado Pendiente y el motivo. Informar al usuario.

### Fase 5 — Reintento de pendientes

12. Al terminar el recorrido inicial del Grupo Ins, si existen archivos con estado **Pendiente**:
    - Realizar una segunda pasada únicamente sobre los archivos Pendientes, en el mismo orden topológico.
    - Aplicar la misma lógica del paso 11.
    - El contador de visitas acumulado en la Fase 4 **se conserva** (no se reinicia).

13. Si al terminar la segunda pasada aún quedan archivos Pendientes:
    - Registrar en el log los archivos pendientes con su motivo.
    - Informar al usuario que la ejecución finalizó con pendientes sin resolver.

---

## 5. Estados posibles de un archivo Ins_

| Estado | Descripción |
|---|---|
| **En cola** | Aún no ha sido procesado. |
| **Ejecutado** | Se ejecutó exitosamente en la base de datos. |
| **Pendiente** | Tiene al menos un padre en el Grupo Ins que no ha sido Ejecutado. |
| **Fallido** | Se intentó ejecutar pero PostgreSQL devolvió un error SQL (no es un problema de dependencia). |
| **Abortado** | La ejecución fue truncada por superar el límite de visitas o por ciclo detectado. |

---

## 6. Registro en el Log

Cada entrada del log debe contener:

| Campo | Descripción |
|---|---|
| Timestamp | Fecha y hora del evento. |
| Archivo | Nombre completo del archivo `.sql`. |
| Estado | Ejecutado / Pendiente / Fallido / Abortado. |
| Motivo | Descripción del resultado: éxito, error SQL (con mensaje de PG), padre pendiente (indicar cuál), ciclo detectado, límite de visitas alcanzado. |

Al finalizar la ejecución completa, el log debe incluir un **resumen** con:
- Total de archivos ejecutados exitosamente.
- Total de archivos pendientes (con sus nombres).
- Total de archivos fallidos (con sus nombres y errores).
- Si la ejecución fue truncada: indicar el motivo y los archivos afectados.

---

## 7. Criterios de Aceptación

- [ ] Los archivos sin prefijo `Ins_` se ejecutan primero, en su orden original del list box, sin ninguna verificación de dependencias.
- [ ] Si un archivo General falla, la ejecución se detiene y no se procesan los archivos `Ins_`.
- [ ] El nombre de tabla se extrae correctamente quitando `Ins_` al inicio y `.sql` al final.
- [ ] Las dependencias se obtienen exclusivamente de las Foreign Keys del esquema PostgreSQL activo.
- [ ] Una tabla padre que no tenga archivo `Ins_` correspondiente en el list box no bloquea la ejecución del hijo.
- [ ] Los archivos `Ins_` se ejecutan en orden topológico (padres antes que hijos).
- [ ] Un archivo hijo con padre en estado Pendiente queda marcado como Pendiente y no se ejecuta.
- [ ] El contador de visitas de un padre Pendiente no supera 5; al alcanzarlo se trunca la ejecución.
- [ ] Los ciclos de dependencia se detectan antes de ejecutar y se reportan como error de configuración.
- [ ] El log registra cada archivo con su estado final y motivo.
- [ ] El log incluye un resumen al finalizar.

---

## 8. Casos Límite y Comportamiento Esperado

| Caso | Comportamiento |
|---|---|
| El list box solo tiene archivos General (ningún `Ins_`) | Se ejecutan todos en orden. Fin normal. |
| El list box solo tiene archivos `Ins_` | Se omite la Fase 2. Se construye el grafo y se ejecuta en orden topológico. |
| Una tabla `Ins_` no existe en la base de datos al consultar sus FK | Se asume que no tiene dependencias dentro del Grupo Ins. Se ejecuta normalmente. |
| Dos archivos `Ins_` apuntan a la misma tabla padre que está fuera del list box | Ambos se ejecutan sin restricción de dependencia entre ellos. |
| Un archivo `Ins_` tiene múltiples padres, solo uno de ellos Pendiente | El archivo hijo queda Pendiente hasta que todos sus padres estén Ejecutados. |

---

## 9. Fuera de Alcance (Out of Scope)

- Modificación del orden de los archivos en el list box "Querys Seleccionados" por parte del sistema.
- Ejecución paralela de archivos.
- Soporte para esquemas PostgreSQL distintos a `public` en esta versión (queda como mejora futura configurable).
- Validación del contenido SQL interno de los archivos (solo se ejecutan; los errores los reporta PostgreSQL).
