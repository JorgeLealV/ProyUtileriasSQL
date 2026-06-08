"""
create_excel.py — Generador de archivo Excel de prueba para ProyUtileriasSQL.

Propósito
---------
Genera el archivo 'DatosCatalogosOriginales.xlsx' con cinco hojas de trabajo
(Tabla1, Tabla2, Hoja1, Hoja2, Tabla3), cada una con una columna 'Data' de
cuatro filas de datos numéricos de ejemplo.

Este script sirve como fixture de prueba manual para validar el flujo
"Crear Inserts": permite verificar que la aplicación lee correctamente un
Excel con múltiples hojas y genera los scripts SQL INSERT correspondientes.

Uso
---
    python create_excel.py

Salida
------
    DatosCatalogosOriginales.xlsx  — creado en el directorio de trabajo actual.

Dependencias
------------
    pandas    >= 3.0.3   (ver requirements.txt)
    xlsxwriter           (instalado con pandas[excel])

Notas
-----
- El archivo generado es de prueba; los valores numéricos no tienen
  significado de negocio.
- Si el archivo ya existe en el directorio, será sobreescrito sin advertencia.
- No requiere conexión a base de datos ni entorno gráfico.
"""

import pandas as pd


# Motor XlsxWriter elegido sobre openpyxl aquí porque genera archivos más
# compactos para datos simples de prueba. En servicios de producción se usa
# openpyxl (ver services/).
writer = pd.ExcelWriter("DatosCatalogosOriginalesP01.xlsx", engine="xlsxwriter")

# ── DataFrames de ejemplo ────────────────────────────────────────────────────
# Cada DataFrame representa una hoja de catálogo con cuatro registros.
# Los valores son intencionalmente distintos entre hojas para facilitar
# la detección de mezclas accidentales al leer el Excel.

df1 = pd.DataFrame({"Data": [10, 20, 30, 40]})  # hoja Tabla1
df2 = pd.DataFrame({"Data": [11, 22, 33, 44]})  # hoja Tabla2
df3 = pd.DataFrame({"Data": [12, 23, 34, 45]})  # hoja Hoja1
df4 = pd.DataFrame({"Data": [13, 24, 35, 46]})  # hoja Hoja2
df5 = pd.DataFrame({"Data": [14, 25, 36, 47]})  # hoja Tabla3

# ── Escritura de hojas ───────────────────────────────────────────────────────
# index=False omite la columna de índice de pandas para que el Excel resultante
# coincida con el formato esperado por services/funciones.py al leer cabeceras.

df1.to_excel(writer, sheet_name="Tabla1", index=False)
df2.to_excel(writer, sheet_name="Tabla2", index=False)
df3.to_excel(writer, sheet_name="Hoja1", index=False)
df4.to_excel(writer, sheet_name="Hoja2", index=False)
df5.to_excel(writer, sheet_name="Tabla3", index=False)

# Cierra el writer y vuelca los buffers internos al archivo en disco.
# Sin esta llamada el archivo queda vacío o corrupto.
writer.close()
