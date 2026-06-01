# -*- coding: utf-8 -*-
"""
Este script exporta datos desde tablas de PostgreSQL a un archivo de Excel.

Cada tabla se guarda en una hoja separada dentro del mismo archivo de Excel,
y el encabezado de cada hoja tiene un formato especial para mejor legibilidad.
"""

# Se importa la función necesaria desde nuestro módulo de funciones.
from funciones import postgres_a_excel

# --- Parámetros de Ejecución ---

# Define la ruta y el nombre del archivo Excel de salida.
# Tenerlo en una variable hace que sea más fácil de cambiar si es necesario.
archivo_excel_salida = r"C:\Users\jleal\Documents\AAAA_Trabajo\CFDI_CSHARP\BaseDatos\ArchivosExcel\InfTablasExp.xlsx"

# --- Llamadas a la Función ---

# --- 1. Creación del archivo Excel ---
# La primera llamada se encarga de crear el archivo Excel desde cero.
# - tabla="usuarios": La primera tabla que vamos a exportar.
# - acumular_si_existe=False: Esto es MUY IMPORTANTE. Al ser 'False', si el
#   archivo 'exportado.xlsx' ya existe, lo BORRARÁ y creará uno nuevo.
#   Esto asegura que empecemos con un archivo limpio en cada ejecución.
print("--- Iniciando exportación a Excel (creando archivo nuevo) ---")
postgres_a_excel(
    servidor="localhost",
    puerto="5432",
    base_de_datos="CFDI1",
    usuario="postgres",
    password="nicol8899",
    tabla="usuarios",
    archivo_excel=archivo_excel_salida,
    acumular_si_existe=False
)
print("-" * 20)


# --- 2. Acumulación de hojas en el mismo archivo ---
# Todas las llamadas siguientes usan 'acumular_si_existe=True'.
# Esto hace que la función NO borre el archivo, sino que abra el existente
# y AÑADA una nueva hoja de cálculo con los datos de la nueva tabla.
# Si una hoja con el mismo nombre ya existe, será reemplazada.

print("--- Añadiendo más tablas al mismo archivo Excel ---")
tablas_a_exportar = [
    "parametros",
    "tiposestasat",
    "tiponomina",
    "tipdivision",
    "tip_estnom",
    "tipoparam"
]

for nombre_tabla in tablas_a_exportar:
    print(f"Exportando tabla: {nombre_tabla}...")
    postgres_a_excel(
        servidor="localhost",
        puerto="5432",
        base_de_datos="CFDI1",
        usuario="postgres",
        password="nicol8899",
        tabla=nombre_tabla,
        archivo_excel=archivo_excel_salida,
        acumular_si_existe=True
    )
    print("-" * 10)

print("\n--- Proceso de exportación a Excel completado. ---")
