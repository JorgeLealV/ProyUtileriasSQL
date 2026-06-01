# -*- coding: utf-8 -*-
"""
Este script sirve como una herramienta para desarrolladores para renderizar
automáticamente los diagramas del sistema definidos en archivos PlantUML (.puml).

Requiere la librería `plantuml` de Python y una instalación de Java en el sistema.
"""

import os
from plantuml import PlantUML


def render_diagrams():
    """
    Encuentra todos los archivos .puml en el directorio actual y los convierte
    a imágenes PNG, guardándolas en un subdirectorio '/out'.
    """
    # URL del servidor de PlantUML. Se puede usar el servidor público o uno local.
    # Usar el servidor público es más sencillo ya que no requiere instalar PlantUML localmente.
    pl_server = PlantUML(url="http://www.plantuml.com/plantuml")

    # Directorio raíz del proyecto
    current_directory = os.path.dirname(__file__)

    # Directorio de salida para las imágenes
    output_directory = os.path.join(current_directory, "out")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Directorio de salida creado en: {output_directory}")

    # Buscar todos los archivos .puml en el directorio raíz
    puml_files = [f for f in os.listdir(current_directory) if f.endswith(".puml")]

    if not puml_files:
        print("No se encontraron archivos .puml para procesar.")
        return

    print(f"Se encontraron {len(puml_files)} archivos PlantUML: {puml_files}")

    # Procesar cada archivo encontrado
    for puml_file in puml_files:
        puml_path = os.path.join(current_directory, puml_file)

        # Define el subdirectorio de salida específico para este diagrama
        diagram_name = os.path.splitext(puml_file)[0]
        specific_output_dir = os.path.join(output_directory, diagram_name)

        print(f"\nProcesando '{puml_file}'...")

        try:
            # La librería `plantuml` toma la ruta del archivo de entrada y
            # el directorio de salida para generar la imagen.
            pl_server.processes_file(puml_path, outfile=specific_output_dir)
            print(
                f"Diagrama '{diagram_name}.png' generado exitosamente en '{specific_output_dir}'"
            )

        except Exception as e:
            print(f"Error al procesar '{puml_file}': {e}")
            print(
                "Asegúrate de que Java esté instalado y accesible en el PATH del sistema."
            )


# --- Punto de Entrada del Script ---
if __name__ == "__main__":
    # Esta construcción permite que el código dentro del `if` solo se ejecute
    # cuando el script es llamado directamente (ej. `python diagram_tools.py`),
    # y no cuando es importado por otro script.
    render_diagrams()
