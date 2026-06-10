# Proyecto de Utilerías SQL

Este proyecto es una aplicación de escritorio desarrollada en Python con la librería PySide6. Su objetivo principal es facilitar la generación de scripts de inserción (`INSERT`) para bases de datos PostgreSQL a partir de datos contenidos en archivos de Microsoft Excel.

## Características

- **Interfaz Gráfica de Usuario (GUI):** Construida con PySide6 (la versión oficial de Qt para Python), permitiendo una interacción amigable.
- **Generación de Scripts SQL:** Lee hojas de un archivo Excel y convierte sus filas en sentencias `INSERT` de SQL.
- **Configuración Persistente:** Guarda las rutas y selecciones del usuario en un archivo de texto (`ConfInsert.conf`) para no tener que reconfigurar todo en cada uso.
- **Flexibilidad:** Permite generar un script SQL por cada tabla o consolidar todos los `INSERTs` en un único archivo.

## Requisitos

Para ejecutar este proyecto, necesitas tener Python instalado en tu sistema. Las dependencias de Python se listan en el archivo `requirements.txt`.

- **Python 3.x**
- **Java:** Necesario para que PlantUML pueda generar los diagramas. Asegúrate de que `java` esté disponible en el PATH de tu sistema.

## Instalación

1.  **Clona o descarga el proyecto:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd ProyUtileriasSQL
    ```

2.  **Crea un entorno virtual (recomendado):**
    Un entorno virtual aísla las dependencias de este proyecto de otros que puedas tener en tu sistema.
    ```bash
    python -m venv venv
    ```

3.  **Activa el entorno virtual:**
    -   En Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    -   En macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Instala las dependencias:**
    El archivo `requirements.txt` contiene todas las librerías de Python necesarias.
    ```bash
    pip install -r requirements.txt
    ```

## Uso

Para iniciar la aplicación, ejecuta el archivo `main.py` desde la raíz del proyecto:

```bash
python main.py
```

Se abrirá la ventana principal que te permitirá acceder a las diferentes funcionalidades de la herramienta.

## Estructura del Proyecto

A continuación se describe la función de cada archivo y directorio importante:

-   **`main.py`**: Es el punto de entrada de la aplicación. Se encarga de iniciar el entorno de PySide6 y mostrar la ventana principal.

-   **`requirements.txt`**: Lista las librerías de Python que el proyecto necesita para funcionar.

-   **`ConfInsert.conf`**: Archivo de configuración de texto plano. La aplicación lo usa para guardar y leer las rutas del archivo Excel, el directorio de salida y las tablas seleccionadas, evitando que el usuario tenga que ingresarlas cada vez.

-   **`diagram_tools.py`**: Un script de utilidad para generar automáticamente los diagramas del proyecto (en formato PNG) a partir de los archivos `.puml`.

-   **`controllers/dbml_erd_previewer.py`**: Convierte un archivo DBML o SQL a PlantUML y opcionalmente renderiza el diagrama ERD.

-   **`diagrama_componentes.puml` / `diagrama_secuencia.puml`**: Archivos de texto con el código en lenguaje PlantUML para describir los diagramas del sistema.

-   **`/ui/`**: Este directorio contiene los archivos de la interfaz de usuario creados con Qt Designer.
    -   **`PanelPrincipal.ui`**: Archivo XML que define la estructura estática de la pestaña principal, la cual es cargada dinámicamente por la aplicación.

-   **`/views/`**: Contiene las clases que definen la lógica y el comportamiento de las ventanas de la aplicación.
    -   **`panel_principal_view.py`**: Es el archivo más importante de la lógica de la GUI. Controla la ventana principal, carga el archivo `.ui`, conecta las acciones de los botones (señales) con los métodos que deben ejecutarlas (slots), y maneja toda la interacción con el usuario en la pestaña "Genera Inserts".

-   **`/services/`**: Contiene la lógica de negocio principal de la aplicación, separada de la interfaz de usuario.
    -   **`funciones.py`**: Aquí se encuentra la función `excel_to_postgres_inserts`, que realiza la tarea central de leer un archivo Excel y escribir los `INSERTs` en un archivo SQL.

-   **`/controllers/`**: Originalmente pensado para lógica de control, pero en la estructura actual su funcionalidad ha sido mayormente absorbida por la clase `PanelPrincipalView`.
    -   **`generar_inserts.py`**: Un script inicial que probablemente se usó para pruebas antes de integrarlo en la interfaz gráfica.

-   **`/Imagenes/`**: Contiene imágenes utilizadas en la aplicación o para documentación.

-   **`/out/`**: Directorio de salida donde se guardarán los diagramas generados.

## Diagramas del Sistema

Para entender mejor la arquitectura y el flujo del programa, puedes consultar los diagramas generados.

### ¿Cómo generar los diagramas?

1.  Asegúrate de haber instalado las dependencias de `requirements.txt`.
2.  Asegúrate de tener **Java** instalado y accesible en el PATH de tu sistema.
3.  Ejecuta el script `diagram_tools.py`:
    ```bash
    python diagram_tools.py
    ```
4.  Los diagramas actualizados aparecerán como archivos PNG en el directorio `/out/`.

### Generar un ERD desde DBML o SQL

También puedes usar el nuevo script de vista previa de ERD para convertir un archivo `.dbml` o `.sql` a PlantUML y obtener un diagrama ERD:

```bash
python controllers/dbml_erd_previewer.py ScriptCRUD04.dbml
python controllers/dbml_erd_previewer.py ScriptCRUD04.dbml --render --outdir out
```

El script guarda un archivo `.puml` con la misma base de nombre y, si se usa `--render`, genera un PNG en el directorio especificado.

### Herramientas para la Generación Automática de Diagramas

La pregunta sobre cómo generar diagramas automáticamente desde el código es muy pertinente.

1.  **Diagramas de Clases/Componentes:**
    Herramientas como **`pyreverse`** (parte de la suite de `pylint`) pueden analizar un proyecto de Python y generar diagramas de clases en formato `.dot` o `.puml`.
    
    *Ejemplo de uso de `pyreverse`:*
    ```bash
    pyreverse -o puml .
    ```
    Este comando analizaría todos los archivos `.py` en el directorio actual y generaría diagramas de paquetes y clases en formato PlantUML.

2.  **Diagramas de Secuencia:**
    La generación de diagramas de secuencia de forma totalmente automática es un desafío mucho mayor, ya que requiere trazar la ejecución del código en tiempo real. No es una práctica común para la documentación general. Por lo general, los diagramas de secuencia se crean manualmente (como se ha hecho en este proyecto en el archivo `diagrama_secuencia.puml`) para ilustrar los flujos más importantes y representativos del sistema.

El script `diagram_tools.py` proporcionado en este proyecto ofrece un enfoque híbrido: los diagramas se definen manualmente en archivos `.puml`, pero su renderizado a un formato de imagen (PNG) se automatiza con el script.
