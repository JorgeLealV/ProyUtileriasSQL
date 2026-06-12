# Data Model: Ejecución Ordenada de Inserts por Dependencias FK

**Feature**: `004-ins-fk-exec-order`
**Date**: 2026-06-12

---

## Entidades Principales

### ArchivoEjecucion

Representa un archivo `.sql` en la cola de ejecución. Existe únicamente en memoria durante la ejecución (no se persiste).

| Campo              | Tipo       | Descripción                                                      |
|--------------------|------------|------------------------------------------------------------------|
| `nombre_archivo`   | `str`      | Nombre completo del archivo (p. ej. `Ins_TipAlcance.sql`)       |
| `ruta_completa`    | `str`      | Ruta absoluta en disco                                           |
| `tipo`             | `str`      | `"General"` o `"Ins"`                                            |
| `tabla`            | `str\|None`| Nombre de tabla extraído (solo para tipo `"Ins"`)               |
| `estado`           | `str`      | Ver `EstadoArchivo`                                              |
| `errores`          | `list[str]`| Mensajes de error de PostgreSQL (para archivos Fallidos)         |
| `padres_pendientes`| `set[str]` | Nombres de archivos padre que bloquearon este archivo            |

**Reglas de validación**:
- `tabla` = `nombre_archivo[4:-4]` (quitar prefijo `Ins_` y sufijo `.sql`)
- `estado` solo puede tomar valores del enum `EstadoArchivo`
- Para tipo `"General"`, `tabla` y `padres_pendientes` son `None`/`set()`

---

### EstadoArchivo

Enum de cadenas (no `Enum` de Python; strings literales para compatibilidad con logs y signals).

| Constante  | Valor string | Descripción                                                                    |
|------------|--------------|--------------------------------------------------------------------------------|
| `EN_COLA`  | `"En cola"`  | Aún no ha sido procesado                                                        |
| `EJECUTADO`| `"Ejecutado"`| Se ejecutó exitosamente                                                          |
| `PENDIENTE`| `"Pendiente"`| Al menos un padre en Grupo Ins no está Ejecutado                               |
| `FALLIDO`  | `"Fallido"`  | Error SQL al ejecutar (no es problema de dependencia); ejecución continúa      |
| `ABORTADO` | `"Abortado"` | Truncado por ciclo detectado o por superar límite de revisitas                 |

**Transiciones válidas**:
```
EN_COLA → EJECUTADO (ejecución exitosa)
EN_COLA → PENDIENTE (padre en estado Pendiente)
EN_COLA → FALLIDO   (error SQL de PostgreSQL)
EN_COLA → ABORTADO  (ciclo detectado antes de ejecutar)
PENDIENTE → EJECUTADO (segunda pasada, padres resueltos)
PENDIENTE → ABORTADO  (límite de revisitas superado)
PENDIENTE → FALLIDO   (segunda pasada, error SQL)
```

---

### GrafoDependencias

Estructura de grafo dirigido en memoria para el ordenamiento topológico.

| Campo          | Tipo                      | Descripción                                                     |
|----------------|---------------------------|-----------------------------------------------------------------|
| `nodos`        | `set[str]`                | Nombres de archivos `Ins_` en el grupo                          |
| `aristas`      | `dict[str, set[str]]`     | `aristas[hijo] = {padre1, padre2}` — padre debe ejecutar antes  |
| `contadores`   | `dict[str, int]`          | Visitas de cada archivo padre en estado Pendiente (límite: 5)   |

**Regla**: Solo se registran dependencias entre archivos **dentro del grupo Ins**. Padres que no tienen archivo `Ins_` correspondiente se ignoran.

---

### EntradaLog

Representa una línea del archivo de log de ejecución.

| Campo       | Tipo   | Descripción                                             |
|-------------|--------|---------------------------------------------------------|
| `timestamp` | `str`  | Fecha y hora: `YYYY-MM-DD HH:MM:SS`                    |
| `archivo`   | `str`  | Nombre del archivo `.sql`                               |
| `estado`    | `str`  | Valor de `EstadoArchivo`                               |
| `motivo`    | `str`  | Descripción del resultado (ver reglas abajo)            |

**Reglas del campo `motivo`**:
- Ejecutado: `"OK - {n} instrucciones ejecutadas"`
- Fallido: `"ERROR SQL: {mensaje de PostgreSQL}"`
- Pendiente: `"BLOQUEADO: padre pendiente {nombre_padre}"`
- Abortado (ciclo): `"CICLO DETECTADO: {archivos en ciclo}"`
- Abortado (revisitas): `"LIMITE DE REVISITAS ALCANZADO ({n} visitas)"`

---

### ResumenEjecucion

Dict retornado por `EjecutarQuerysWorker` vía signal `execution_finished`. Extiende el resumen actual.

| Campo            | Tipo        | Descripción                                                     |
|------------------|-------------|-----------------------------------------------------------------|
| `total`          | `int`       | Total de archivos procesados (Generales + Ins_)                 |
| `ok`             | `int`       | Archivos ejecutados exitosamente                                 |
| `failed`         | `int`       | Archivos con estado Fallido                                      |
| `pendientes`     | `list[str]` | Nombres de archivos que quedaron Pendientes                      |
| `abortado`       | `bool`      | True si la ejecución fue truncada                               |
| `motivo_abort`   | `str`       | Descripción del motivo de abort (ciclo o revisitas)             |
| `cancelled`      | `bool`      | True si el usuario canceló (cancelación manual)                 |
| `ciclo_archivos` | `list[str]` | Archivos involucrados en el ciclo (vacío si no hay ciclo)       |
| `entradas_log`   | `list[dict]`| Todas las entradas de log del resumen (para display en UI)      |

**Compatibilidad**: Los campos `total`, `ok`, `failed`, `cancelled` mantienen los mismos nombres y semántica que el resumen actual para que `_on_execution_finished` siga funcionando con lógica mínima de cambio.

---

## Relaciones entre Entidades

```
EjecutarQuerysWorker
    ├── crea → GrafoDependencias (en memoria, durante run())
    ├── mantiene → dict[nombre_archivo → EstadoArchivo]
    ├── produce → ResumenEjecucion (emitido en execution_finished)
    └── escribe → EntradaLog[] (a archivo .log si configurado)

GrafoDependencias
    └── contiene → ArchivoEjecucion[] (referencias por nombre)
```

---

## Módulos Afectados

| Archivo                              | Cambio                                                    |
|--------------------------------------|-----------------------------------------------------------|
| `services/fk_exec_order.py`          | **NUEVO**: toda la lógica de FK, grafo y ejecución Ins    |
| `views/panel_principal_view.py`      | **MODIFICAR**: `EjecutarQuerysWorker.run()` + `_on_execution_finished()` |
| `services/funciones.py`              | **SIN CAMBIOS**: `execute_sql_from_file` y `_write_log` se reutilizan |
