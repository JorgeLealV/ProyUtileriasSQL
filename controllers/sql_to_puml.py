import re
import os

def sql_to_plantuml():
    # 1. Solicitar el nombre del archivo al usuario
    archivo_sql = input("Introduce el nombre del archivo .sql (ej. Scrip03.sql): ")
    
    if not os.path.exists(archivo_sql):
        print(f"Error: El archivo {archivo_sql} no existe.")
        return

    # Definir nombre de salida
    nombre_base = os.path.splitext(archivo_sql)[0]
    archivo_puml = f"{nombre_base}.puml"

    with open(archivo_sql, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Preparar el encabezado de PlantUML
    puml_content = ["@startuml\n", "!theme plain\n", "hide circle\n", "skinparam linetype ortho\n"]

    # 2. Regex para capturar Tablas y sus columnas
    # Busca bloques 'CREATE TABLE nombre (...);'
    table_pattern = re.compile(r'CREATE TABLE (\w+) \((.*?)\);', re.DOTALL | re.IGNORECASE)
    # Busca llaves foráneas 'CONSTRAINT nombre FOREIGN KEY (col) REFERENCES tabla(col)'
    fk_pattern = re.compile(r'CONSTRAINT \w+ FOREIGN KEY \((\w+)\) REFERENCES (\w+)\((\w+)\)', re.IGNORECASE)

    tablas = table_pattern.findall(contenido)

    # 3. Procesar Tablas
    for tabla_nombre, cuerpo in tablas:
        puml_content.append(f'entity "{tabla_nombre}" as {tabla_nombre} {{')
        
        lineas = cuerpo.strip().split('\n')
        for linea in lineas:
            linea = linea.strip().replace(',', '')
            
            # Identificar PK
            if "PRIMARY KEY" in linea.upper():
                # Extraer el nombre del campo si es inline
                partes = linea.split()
                if partes[0].upper() != "CONSTRAINT":
                    puml_content.append(f'  * **{partes[0]}** : {partes[1]}')
            # Identificar campos normales (evitar lineas de CONSTRAINT en la lista de campos)
            elif "CONSTRAINT" not in linea.upper() and linea:
                partes = linea.split()
                if len(partes) >= 2:
                    puml_content.append(f'  {partes[0]} : {partes[1]}')
        
        puml_content.append("}\n")

    # 4. Procesar Relaciones (Foreign Keys)
    relaciones = fk_pattern.findall(contenido)
    for col_origen, tabla_destino, col_destino in relaciones:
        # Buscamos en qué tabla estamos mediante el contexto del archivo original
        # Para simplificar, asumimos el estándar de PlantUML: TablaOrigen }o--|| TablaDestino
        # Nota: Este regex busca el nombre de la tabla que contiene la restricción
        parent_table = re.search(r'CREATE TABLE (\w+) \(.*?' + re.escape(col_origen) + r'.*?REFERENCES ' + tabla_destino, contenido, re.DOTALL | re.IGNORECASE)
        if parent_table:
            origen = parent_table.group(1)
            puml_content.append(f'{tabla_destino} ||--o{{ {origen} : "{col_origen}"')

    puml_content.append("\n@enduml")

    # 5. Guardar el archivo .puml
    with open(archivo_puml, 'w', encoding='utf-8') as f:
        f.writelines("\n".join(puml_content))
    
    print(f"¡Éxito! Archivo generado: {archivo_puml}")

if __name__ == "__main__":
    sql_to_plantuml()