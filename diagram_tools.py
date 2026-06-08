# -*- coding: utf-8 -*-
"""
diagram_tools.py — Renderizador batch de diagramas PlantUML a PNG.

Propósito
---------
Utilidad de desarrollador (sin GUI) que escanea el directorio raíz del
proyecto en busca de archivos PlantUML (*.puml) y los convierte a imágenes
PNG enviándolos al servidor público de PlantUML.

Sirve para materializar visualmente los diagramas de arquitectura del
proyecto (ER, secuencia, componentes) sin necesidad de abrir un IDE ni
instalar PlantUML localmente. El resultado queda en la carpeta 'out/'.

Flujo de ejecución
------------------
1. Conecta con el servidor HTTP de PlantUML (plantuml.com).
2. Crea el directorio de salida 'out/' si no existe.
3. Escanea el directorio raíz en busca de archivos *.puml.
4. Por cada archivo encontrado, envía su contenido al servidor y guarda
   la imagen PNG resultante en 'out/<nombre_diagrama>'.

Uso
---
    python diagram_tools.py

Salida
------
    out/
    └── <nombre_sin_extension>   ← imagen PNG de cada diagrama procesado

Dependencias
------------
    plantuml 0.3.0  (ver requirements.txt)

Limitación conocida
-------------------
El script solo escanea el directorio raíz del proyecto. Los archivos .puml
ubicados en subdirectorios (p. ej. Diagramas/) NO son procesados
automáticamente. Para procesarlos, muévelos al directorio raíz o ajusta
la variable 'current_directory' antes de ejecutar.

Notas
-----
- No requiere Java local: el renderizado ocurre en el servidor remoto.
- Requiere conexión a internet para alcanzar plantuml.com.
- Si un diagrama falla, el script continúa con los siguientes (no se aborta).
"""

import os
from plantuml import PlantUML


def render_diagrams():
    """
    Busca todos los archivos .puml en el directorio raíz del proyecto y los
    convierte a PNG usando el servidor público de PlantUML.

    Para cada archivo .puml encontrado:
    - Construye la ruta de salida dentro de 'out/<nombre_diagrama>'.
    - Envía el archivo al servidor remoto y descarga la imagen generada.
    - Informa el resultado (éxito o error) por consola.

    No retorna ningún valor. Los errores por archivo se imprimen y se
    continúa con el siguiente; no se lanza excepción al llamador.
    """
    # Servidor público de PlantUML. No requiere instalación local de Java ni
    # Graphviz: el procesamiento ocurre en la nube.
    # Nota: se usa http (no https) porque la librería plantuml 0.3.0 no
    # gestiona certificados SSL en todas las plataformas Windows.
    pl_server = PlantUML(url="http://www.plantuml.com/plantuml")

    # Directorio donde reside este script — se usa como raíz de búsqueda.
    # __file__ resuelve la ruta absoluta del script independientemente del
    # directorio desde donde se invoque Python.
    current_directory = os.path.dirname(__file__)

    # Directorio de salida: 'out/' junto al script.
    # Se crea automáticamente si no existe para no interrumpir la ejecución.
    output_directory = os.path.join(current_directory, "out")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Directorio de salida creado en: {output_directory}")

    # Recolectar todos los archivos .puml en el directorio raíz.
    # LIMITACIÓN: no es recursivo; los archivos en Diagramas/ no se procesan.
    puml_files = [f for f in os.listdir(current_directory) if f.endswith(".puml")]

    if not puml_files:
        print("No se encontraron archivos .puml para procesar.")
        print(f"  Directorio revisado: {current_directory}")
        print("  Nota: los archivos en subdirectorios (ej. Diagramas/) no se detectan.")
        return

    print(f"Se encontraron {len(puml_files)} archivos PlantUML: {puml_files}")

    for puml_file in puml_files:
        puml_path = os.path.join(current_directory, puml_file)

        # Nombre del diagrama sin extensión (ej. 'modeloER' para 'modeloER.puml').
        # Se usa como nombre de la carpeta de salida y como identificador en logs.
        diagram_name = os.path.splitext(puml_file)[0]

        # Ruta de salida de la imagen: out/<nombre_diagrama>
        # La librería plantuml agrega la extensión .png automáticamente.
        specific_output_dir = os.path.join(output_directory, diagram_name)

        print(f"\nProcesando '{puml_file}'...")

        try:
            # processes_file() envía el contenido del .puml al servidor HTTP,
            # recibe la imagen PNG en respuesta y la escribe en 'outfile'.
            # Si el servidor no es alcanzable o el diagrama tiene errores de
            # sintaxis PlantUML, lanza una excepción capturada abajo.
            pl_server.processes_file(puml_path, outfile=specific_output_dir)
            print(f"  OK → '{diagram_name}.png' guardado en '{specific_output_dir}'")

        except Exception as e:
            # Error de red, sintaxis PlantUML inválida o timeout del servidor.
            # Se imprime y se continúa con el siguiente archivo sin abortar.
            print(f"  ERROR al procesar '{puml_file}': {e}")
            print("  Verifica: conexión a internet, sintaxis del .puml y acceso a plantuml.com.")


# ── Punto de entrada ─────────────────────────────────────────────────────────
# El bloque __main__ garantiza que render_diagrams() solo se ejecute cuando
# el script se invoca directamente (`python diagram_tools.py`).
# Si otro módulo importa diagram_tools, la función no se llama automáticamente,
# permitiendo reutilizarla desde otros scripts sin efectos secundarios.
if __name__ == "__main__":
    render_diagrams()
