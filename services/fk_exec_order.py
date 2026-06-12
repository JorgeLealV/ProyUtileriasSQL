# -*- coding: utf-8 -*-
"""
Lógica de separación, ordenamiento topológico por FK y ejecución de archivos
Ins_*.sql respetando la jerarquía padre-hijo del esquema PostgreSQL 'public'.

Todas las funciones son puras (sin PySide6) y reutilizables desde la CLI.
"""

import datetime
import os
from graphlib import CycleError, TopologicalSorter

import psycopg2


# ── Constantes de estado ────────────────────────────────────────────────────

EN_COLA = "En cola"
EJECUTADO = "Ejecutado"
PENDIENTE = "Pendiente"
FALLIDO = "Fallido"
ABORTADO = "Abortado"

LIMITE_REVISITAS = 5

# ── Query FK ────────────────────────────────────────────────────────────────

_FK_QUERY = """
SELECT DISTINCT
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
    AND tc.table_name = %s
"""


# ── Helpers internos ────────────────────────────────────────────────────────

def _write_fk_log(log_file: str, archivo: str, estado: str, motivo: str):
    if not log_file:
        return
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{ts}] {archivo} | {estado} | {motivo}\n"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(linea)
    except Exception:
        pass


# ── T002: separar_archivos ──────────────────────────────────────────────────

def separar_archivos(archivos: list) -> tuple:
    """
    Separa rutas de archivos en Generales e Ins_, conservando orden relativo.
    Un archivo es Ins_ si su basename empieza con 'Ins_' y termina en '.sql'.
    """
    generales = []
    ins_files = []
    for ruta in archivos:
        nombre = os.path.basename(ruta)
        if nombre.startswith("Ins_") and nombre.endswith(".sql"):
            ins_files.append(ruta)
        else:
            generales.append(ruta)
    return generales, ins_files


# ── T003: extraer_tabla ─────────────────────────────────────────────────────

def extraer_tabla(nombre_archivo: str) -> str:
    """Extrae nombre de tabla de 'Ins_TipAlcance.sql' → 'TipAlcance'."""
    return nombre_archivo[4:-4]


# ── T004: obtener_padres_fk ─────────────────────────────────────────────────

def obtener_padres_fk(conn, tabla: str) -> list:
    """
    Retorna lista de tablas padre según FK del esquema 'public'.
    Recibe conexión abierta; no la cierra.
    Retorna lista vacía si la tabla no tiene FK o no existe.
    """
    with conn.cursor() as cur:
        cur.execute(_FK_QUERY, (tabla,))
        return [row[0] for row in cur.fetchall()]


# ── T005: construir_grafo ───────────────────────────────────────────────────

def construir_grafo(ins_files: list, conn_params: dict) -> dict:
    """
    Construye grafo {archivo_ruta: set_de_rutas_padre} para los archivos Ins_.
    Solo se registran dependencias entre archivos presentes en ins_files.
    Lanza RuntimeError si falla la conexión o alguna query FK.
    """
    # Índice principal y alias en minúsculas para comparación case-insensitive.
    # Las tablas en PostgreSQL suelen estar en minúsculas aunque los archivos
    # usen CamelCase (p.ej. "Usuarios" en el archivo vs "usuarios" en PG).
    tabla_a_ruta = {}
    tabla_a_ruta_lower = {}
    for ruta in ins_files:
        tabla = extraer_tabla(os.path.basename(ruta))
        tabla_a_ruta[tabla] = ruta
        tabla_a_ruta_lower[tabla.lower()] = ruta

    grafo = {ruta: set() for ruta in ins_files}

    conn = None
    try:
        conn = psycopg2.connect(
            dbname=conn_params["my_db"],
            user=conn_params["my_user"],
            password=conn_params["my_pass"],
            host=conn_params["my_host"],
            port=conn_params["my_port"],
        )
        for ruta in ins_files:
            tabla = extraer_tabla(os.path.basename(ruta))
            try:
                padres = obtener_padres_fk(conn, tabla.lower())
            except Exception as e:
                raise RuntimeError(
                    f"Error consultando FK para tabla '{tabla}': {e}"
                ) from e
            for padre in padres:
                # Buscar primero exacto, luego case-insensitive
                ruta_padre = tabla_a_ruta.get(padre) or tabla_a_ruta_lower.get(padre.lower())
                if ruta_padre:
                    grafo[ruta].add(ruta_padre)
    except psycopg2.Error as e:
        raise RuntimeError(
            f"Error de conexión al consultar dependencias FK: {e}"
        ) from e
    finally:
        if conn:
            conn.close()

    return grafo


# ── T006 / T011: ordenar_topologicamente ───────────────────────────────────

def ordenar_topologicamente(grafo: dict) -> list:
    """
    Retorna lista de rutas en orden topológico (padres antes que hijos).
    Lanza graphlib.CycleError si hay ciclo de dependencias.
    """
    return list(TopologicalSorter(grafo).static_order())


# ── T007: ejecutar_generales ────────────────────────────────────────────────

def ejecutar_generales(archivos: list, conn_params: dict, log_file: str, progress_cb) -> tuple:
    """
    Ejecuta archivos Generales en orden. Detiene al primer fallo.
    progress_cb: callable(str) — recibe mensaje de progreso.
    Retorna (True, summary_dict) si todos OK; (False, summary_dict) si alguno falla.
    """
    from services.funciones import execute_sql_from_file

    summary = {
        "total": 0, "ok": 0, "failed": 0,
        "pendientes": [], "abortado": False, "motivo_abort": "", "ciclo_archivos": [],
    }

    for ruta in archivos:
        nombre = os.path.basename(ruta)
        progress_cb(f"Ejecutando General: {nombre}")
        result = execute_sql_from_file(
            db_name=conn_params["my_db"],
            user=conn_params["my_user"],
            password=conn_params["my_pass"],
            host=conn_params["my_host"],
            port=conn_params["my_port"],
            sql_file=ruta,
            log_file=log_file,
        )
        summary["total"] += 1
        if result.get("success"):
            summary["ok"] += 1
        else:
            summary["failed"] += 1
            errores = result.get("errors", [])
            motivo = f"ERROR en '{nombre}': {errores[0] if errores else 'error desconocido'}"
            summary["abortado"] = True
            summary["motivo_abort"] = motivo
            _write_fk_log(log_file, nombre, FALLIDO, motivo)
            return False, summary

    return True, summary


# ── T008 / T014 / T015 / T016: ejecutar_ins_ordenado ──────────────────────

def ejecutar_ins_ordenado(
    archivos_ordenados: list,
    grafo: dict,
    conn_params: dict,
    log_file: str,
    progress_cb,
) -> dict:
    """
    Ejecuta archivos Ins_ en orden topológico con control de estados Pendiente/Fallido.
    Realiza segunda pasada sobre Pendientes conservando contadores acumulados.
    Trunca si algún padre supera LIMITE_REVISITAS visitas pendientes.
    progress_cb: callable(str) — recibe mensaje de progreso.
    """
    from services.funciones import execute_sql_from_file

    estados = {ruta: EN_COLA for ruta in archivos_ordenados}
    contadores = {ruta: 0 for ruta in archivos_ordenados}

    def _intentar(ruta):
        """Intenta ejecutar un archivo. Retorna (accion, motivo)."""
        nombre = os.path.basename(ruta)
        padres = grafo.get(ruta, set())
        for padre in padres:
            est_padre = estados.get(padre, EJECUTADO)
            if est_padre != EJECUTADO:
                contadores[padre] += 1
                if contadores[padre] > LIMITE_REVISITAS:
                    return "truncar", (
                        f"Límite de revisitas alcanzado para padre "
                        f"'{os.path.basename(padre)}' ({contadores[padre]} visitas)"
                    )
                return "pendiente", f"Bloqueado: padre '{os.path.basename(padre)}' en estado {est_padre}"

        progress_cb(f"Ejecutando Ins_: {nombre}")
        result = execute_sql_from_file(
            db_name=conn_params["my_db"],
            user=conn_params["my_user"],
            password=conn_params["my_pass"],
            host=conn_params["my_host"],
            port=conn_params["my_port"],
            sql_file=ruta,
            log_file=log_file,
        )
        if result.get("success"):
            n_ok = result.get("ok_stmts", 0)
            return "ejecutado", f"OK — {n_ok} instrucciones ejecutadas"
        errores = result.get("errors", [])
        return "fallido", f"Error SQL: {errores[0] if errores else 'error desconocido'}"

    def _procesar_lista(lista) -> tuple:
        """Procesa lista de rutas. Retorna (truncado: bool, motivo: str)."""
        for ruta in lista:
            if estados[ruta] in (EJECUTADO, FALLIDO, ABORTADO):
                continue
            accion, motivo = _intentar(ruta)
            nombre = os.path.basename(ruta)
            if accion == "truncar":
                for r2 in archivos_ordenados:
                    if estados[r2] not in (EJECUTADO, FALLIDO):
                        estados[r2] = ABORTADO
                        _write_fk_log(log_file, os.path.basename(r2), ABORTADO, motivo)
                return True, motivo
            if accion == "ejecutado":
                estados[ruta] = EJECUTADO
            elif accion == "pendiente":
                estados[ruta] = PENDIENTE
            elif accion == "fallido":
                estados[ruta] = FALLIDO
            _write_fk_log(log_file, nombre, estados[ruta], motivo)
        return False, ""

    truncado, motivo_trunc = _procesar_lista(archivos_ordenados)

    if not truncado:
        pendientes_segunda = [r for r in archivos_ordenados if estados[r] == PENDIENTE]
        if pendientes_segunda:
            truncado, motivo_trunc = _procesar_lista(pendientes_segunda)

    total = len(archivos_ordenados)
    ok = sum(1 for e in estados.values() if e == EJECUTADO)
    failed = sum(1 for e in estados.values() if e == FALLIDO)
    pendientes_nombres = [
        os.path.basename(r)
        for r in archivos_ordenados
        if estados[r] in (PENDIENTE, ABORTADO)
    ]

    return {
        "total_ins": total,
        "ok_ins": ok,
        "failed_ins": failed,
        "pendientes": pendientes_nombres,
        "abortado": truncado,
        "motivo_abort": motivo_trunc,
        "ciclo_archivos": [],
    }


# ── T018: escribir_resumen_log ──────────────────────────────────────────────

def escribir_resumen_log(log_file: str, summary: dict):
    """Escribe el bloque === RESUMEN === al final del archivo de log."""
    if not log_file:
        return
    pendientes = summary.get("pendientes", [])
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("\n=== RESUMEN ===\n")
            f.write(f"Ejecutados: {summary.get('ok', 0)}\n")
            f.write(f"Pendientes: {len(pendientes)}")
            if pendientes:
                f.write(f" ({', '.join(pendientes)})")
            f.write("\n")
            f.write(f"Fallidos:   {summary.get('failed', 0)}\n")
            if summary.get("abortado"):
                f.write(f"Abortado:   Sí — {summary.get('motivo_abort', '')}\n")
            ciclo = summary.get("ciclo_archivos", [])
            if ciclo:
                f.write(f"Ciclo detectado: {', '.join(ciclo)}\n")
    except Exception:
        pass
