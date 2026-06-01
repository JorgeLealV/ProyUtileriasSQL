# -*- coding: utf-8 -*-
"""
Este script genera un archivo .sql con sentencias INSERT a partir de un archivo Excel.

Utiliza la función 'excel_to_postgres_inserts' del módulo 'funciones' para
realizar la conversión.
"""

# Se importa la función específica que necesitamos desde nuestro módulo de funciones.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.funciones import excel_to_postgres_inserts

# --- Parámetros de Ejecución ---

# Ruta al archivo Excel que contiene los datos a convertir.
# Usar 'r' antes de la cadena (raw string) es una buena práctica en Windows para
# evitar que los caracteres '\' se interpreten como secuencias de escape.
my_archexcel = r"C:\Users\jleal\Documents\AAAA_Trabajo\CFDI_CSHARP\BaseDatos\ArchivosExcel\DatosCatalogosOriginales.xlsx"

# Ruta al archivo Sql donde se guardarán los INSERTs.
# Usar 'r' antes de la cadena (raw string) es una buena práctica en Windows para
# evitar que los caracteres '\' se interpreten como secuencias de escape.
my_archsql = r"C:\Users\jleal\Documents\AAAA_Trabajo\CFDI_CSHARP\BaseDatos\ArchivosSQL\carga_dinamica.sql"


# --- Llamadas a la Función ---
# A continuación se listan las llamadas para convertir cada hoja de Excel en SQL.
# Actualmente están comentadas. Para usarlas, simplemente elimina el '#' del inicio.

# Llama a la función para la hoja 'Usuario'.
# - my_archexcel: El archivo de Excel de donde leer.
# - 'Usuario': El nombre de la hoja dentro del Excel.
# - 'usuarios': El nombre de la tabla de la base de datos donde irán los datos.
# - 'carga_dinamica.sql': El archivo .sql donde se guardarán los INSERTs.
# - append=False: Indica que se debe crear el archivo .sql desde cero (o sobreescribirlo).
excel_to_postgres_inserts(my_archexcel, 'Usuario', 'usuarios', my_archsql, False)

# Las siguientes llamadas usan append=True para AÑADIR los nuevos INSERTs al
# final del mismo archivo 'carga_dinamica.sql' sin borrar el contenido anterior.
excel_to_postgres_inserts(my_archexcel, 'TiposEstaSAT', 'TiposEstaSAT', my_archsql, True)
excel_to_postgres_inserts(my_archexcel, 'TipoNomina', 'TipoNomina', my_archsql, True)
excel_to_postgres_inserts(my_archexcel, 'TipDivision', 'TipDivision', my_archsql, True)
excel_to_postgres_inserts(my_archexcel, 'Tip_EstNom', 'Tip_EstNom', my_archsql, True)
excel_to_postgres_inserts(my_archexcel, 'TipoParam', 'TipoParam', my_archsql, True)
excel_to_postgres_inserts(my_archexcel, 'Parametros', 'Parametros', my_archsql, True)
