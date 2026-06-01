# -*- coding: utf-8 -*-
"""
Este script ejecuta el contenido de un archivo .sql en la base de datos PostgreSQL.

Es útil para aplicar cambios en la base de datos, como crear tablas,
insertar datos (generados por 'generar_inserts.py') o cualquier otra operación SQL.
"""

# Se importa la función necesaria desde nuestro módulo de funciones.
from funciones import execute_sql_from_file

# --- Parámetros de Conexión a la Base de Datos ---
my_db = "CFDI1"
my_user = "postgres"
my_pass = "nicol8899"
my_host = "localhost"
my_port = "5432"

# --- Llamadas a la Función ---
# Las llamadas están comentadas. Descomenta las que necesites para ejecutarlas.

# --- Ejemplo 1 ---
# Ruta al primer archivo .sql que se podría ejecutar.
my_sql_file_1 = r"C:\Users\jleal\Documents\AAAA_Trabajo\CFDI_CSHARP\Modelo\Scrip02.sql"

execute_sql_from_file(
     db_name=my_db,
     user=my_user,
     password=my_pass,
     host=my_host,
     port=my_port,
     sql_file=my_sql_file_1
)

# --- Ejemplo 2 ---
# Ruta al segundo archivo .sql, que es el generado por 'generar_inserts.py'.
my_sql_file_2 = r"C:\Users\jleal\Documents\AAAA_Trabajo\CFDI_CSHARP\BaseDatos\ArchivosSQL\carga_dinamica.sql"

# execute_sql_from_file(
#      db_name=my_db,
#      user=my_user,
#      password=my_pass,
#      host=my_host,
#      port=my_port,
#      sql_file=my_sql_file_2
# )
