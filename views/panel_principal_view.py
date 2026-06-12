# -*- coding: utf-8 -*-
"""
Este módulo define la vista principal de la aplicación, que controla la interfaz
de usuario para la generación de scripts SQL.

Clase principal:
- PanelPrincipalView: Hereda de QMainWindow y gestiona todos los componentes
  de la UI, las interacciones del usuario y la comunicación con la lógica de
  negocio (servicios).
"""

import os
import datetime
import pandas as pd

# Ruta absoluta al archivo de configuración, independiente del CWD de lanzamiento
_CONF_FILE = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ConfInsert.conf")
)
_CONN_FILE = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ConexionBD.conf")
)
from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QPushButton,
    QLineEdit,
    QComboBox,
    QListWidget,
    QCheckBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QGroupBox,
    QApplication,
    QTabWidget,
    QProgressDialog,
)
from PySide6.QtWidgets import QMessageBox as QMB
from PySide6.QtCore import QFile, QIODeviceBase, Qt, QObject, QThread, Signal
from PySide6.QtUiTools import QUiLoader
from services.funciones import excel_to_postgres_inserts


class EjecutarQuerysWorker(QObject):
    """Worker que ejecuta archivos .sql en un hilo separado para no bloquear la UI."""

    progress_updated = Signal(str)
    file_finished = Signal(str, bool)
    execution_finished = Signal(dict)

    def __init__(self, files, conn_params, log_file, allow_partial):
        super().__init__()
        self._files = files
        self._conn_params = conn_params
        self._log_file = log_file
        self._allow_partial = allow_partial
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        from graphlib import CycleError
        from services.fk_exec_order import (
            separar_archivos, construir_grafo, ordenar_topologicamente,
            ejecutar_generales, ejecutar_ins_ordenado, escribir_resumen_log,
        )

        _empty = {
            "total": 0, "ok": 0, "failed": 0,
            "pendientes": [], "abortado": False, "motivo_abort": "",
            "ciclo_archivos": [], "cancelled": False,
        }

        generales, ins_files = separar_archivos(self._files)
        summary_g = dict(_empty)

        if generales:
            ok_g, summary_g = ejecutar_generales(
                generales, self._conn_params, self._log_file,
                progress_cb=lambda msg: self.progress_updated.emit(msg),
            )
            if not ok_g:
                summary_g["cancelled"] = self._cancelled
                escribir_resumen_log(self._log_file, summary_g)
                self.execution_finished.emit(summary_g)
                return

        if self._cancelled or not ins_files:
            summary_g["cancelled"] = self._cancelled
            escribir_resumen_log(self._log_file, summary_g)
            self.execution_finished.emit(summary_g)
            return

        # Construir grafo de dependencias FK
        try:
            self.progress_updated.emit("Consultando dependencias FK...")
            grafo = construir_grafo(ins_files, self._conn_params)
        except RuntimeError as e:
            resumen = {**_empty, "abortado": True, "motivo_abort": str(e),
                       "total": summary_g["total"], "ok": summary_g["ok"],
                       "failed": summary_g["failed"], "cancelled": self._cancelled}
            escribir_resumen_log(self._log_file, resumen)
            self.execution_finished.emit(resumen)
            return

        # Ordenamiento topológico (detecta ciclos)
        try:
            self.progress_updated.emit("Analizando orden de ejecución...")
            ordenados = ordenar_topologicamente(grafo)
        except CycleError as e:
            nodos = list(e.args[1]) if len(e.args) > 1 else []
            ciclo_nombres = [os.path.basename(n) for n in nodos]
            resumen = {**_empty, "abortado": True,
                       "motivo_abort": "Ciclo de dependencias detectado",
                       "ciclo_archivos": ciclo_nombres, "pendientes": ciclo_nombres,
                       "total": summary_g["total"], "ok": summary_g["ok"],
                       "failed": summary_g["failed"], "cancelled": self._cancelled}
            escribir_resumen_log(self._log_file, resumen)
            self.execution_finished.emit(resumen)
            return

        # Ejecutar grupo Ins_ con control de pendientes
        resumen_ins = ejecutar_ins_ordenado(
            ordenados, grafo, self._conn_params, self._log_file,
            progress_cb=lambda msg: self.progress_updated.emit(msg),
        )

        resumen_final = {
            "total": summary_g["total"] + resumen_ins.get("total_ins", 0),
            "ok": summary_g["ok"] + resumen_ins.get("ok_ins", 0),
            "failed": summary_g["failed"] + resumen_ins.get("failed_ins", 0),
            "pendientes": resumen_ins.get("pendientes", []),
            "abortado": resumen_ins.get("abortado", False),
            "motivo_abort": resumen_ins.get("motivo_abort", ""),
            "ciclo_archivos": [],
            "cancelled": self._cancelled,
        }
        escribir_resumen_log(self._log_file, resumen_final)
        self.execution_finished.emit(resumen_final)


# --- Clase de la Vista Principal ---
class PanelPrincipalView(QMainWindow):
    """
    Clase que representa la ventana principal de la aplicación.

    Esta clase es el "cerebro" de la interfaz gráfica. Se encarga de:
    1. Cargar el diseño de la interfaz desde un archivo .ui.
    2. Encontrar y referenciar los widgets (botones, campos de texto, etc.) definidos en el .ui.
    3. Conectar las acciones del usuario (ej. hacer clic en un botón) a funciones específicas.
    4. Implementar la lógica que responde a esas acciones.
    5. Comunicarse con el "backend" (en este caso, el módulo `services.funciones`) para
       realizar las operaciones principales.
    """

    def __init__(self, main_window):
        """
        Constructor de la clase. Se ejecuta una sola vez al crear la ventana.

        Args:
            main_window: Referencia a la ventana anterior o principal que la invocó.
                         Se usa para poder regresar a ella.
        """
        # `super()` llama al constructor de la clase padre (QMainWindow). Es fundamental.
        super(PanelPrincipalView, self).__init__()
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        self.main_window = (
            main_window  # Guardamos la referencia a la ventana que nos llamó.
        )
        self.config_tablas = []  # Lista para mantener en memoria las tablas seleccionadas.

        # Declaración de atributos de la UI para evitar advertencias de "atributo desconocido"
        self.central_widget = None
        self.lineEdit_archivo_excel = None
        self.btn_browse_archivo_excel = None
        self.lineEdit_directorio_salida = None
        self.btn_browse_directorio_salida = None
        self.listWidget_hojas = None
        self.btn_agregar = None
        self.btn_agregar_todos = None
        self.btn_quitar = None
        self.btn_quitar_todos = None
        self.listWidget_tablas_seleccionadas = None
        self.btn_salir = None
        self.btn_borrar_config = None
        self.checkBox_un_solo_archivo = None
        self.lineEdit_archivo_todos = None
        self.btn_guardar_todos = None
        self.btn_ejecutar_creacion = None

        # Widgets tab_ejecuta_querys
        self.lineEdit_dir_querys = None
        self.btn_browse_dir_querys = None
        self.listWidget_querys_disponibles = None
        self.btn_eq_agregar = None
        self.btn_eq_agregar_todos = None
        self.btn_eq_quitar = None
        self.btn_eq_quitar_todos = None
        self.listWidget_querys_seleccionados = None
        self.btn_limpiar_config_eq = None
        self.checkBox_crear_log = None
        self.checkBox_permitir_parcial = None
        self.lineEdit_nom_log = None
        self.btn_guardar_nom_log = None
        self.btn_ejecutar_querys = None
        # Estado de ejecución
        self._eq_thread = None
        self._eq_worker = None
        self._progress_dialog = None

        # --- Secuencia de inicialización de la ventana ---
        self.load_ui()  # 1. Carga el archivo .ui y lo convierte en objeto.
        self.setup_ui()  # 2. Busca y asigna los widgets del .ui a variables de la clase.
        self.connect_signals()  # 3. Conecta las "señales" (clics) de los widgets a "slots" (métodos).
        self._apply_styles()  # 4. Aplica una hoja de estilos CSS para dar apariencia a la app.
        self._update_button_states()  # 5. Ajusta el estado inicial (habilitado/deshabilitado) de los botones.
        self._load_config_file()  # 6. Carga la configuración previa desde "ConfInsert.conf".
        self._load_ejecutar_querys_config()  # 7. Carga la configuración previa de la pestaña "Ejecutar Querys".

        primary_screen = QApplication.primaryScreen()
        screen = primary_screen.geometry()
        offset_px = round(primary_screen.logicalDotsPerInchY() / 2.54 * 1.5)

        self.resize(min(1500, screen.width() - 80), min(920, screen.height() - 80) - offset_px)

        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(screen.center())
        top_left = frame_geometry.topLeft()
        self.move(top_left.x(), top_left.y() - offset_px)

    def load_ui(self):
        """
        Carga la interfaz de usuario desde el archivo `PanelPrincipal.ui`.

        PySide6 permite separar el diseño (en un archivo .ui) de la lógica (en Python).
        `QUiLoader` es la clase que lee el XML del archivo .ui y construye los widgets.
        """
        loader = QUiLoader()
        # Creamos una ruta relativa al archivo .ui para que funcione sin importar desde dónde se ejecute el script.
        path = os.path.join(os.path.dirname(__file__), "..", "ui", "PanelPrincipal.ui")
        ui_file = QFile(path)
        ui_file.open(QIODeviceBase.OpenModeFlag.ReadOnly)

        # Carga el contenido del .ui en un widget que será el widget central de nuestra ventana.
        self.central_widget = loader.load(ui_file)
        self.setCentralWidget(self.central_widget)

        ui_file.close()

    def setup_ui(self):
        """
        Encuentra los widgets definidos en el .ui por su "objectName" y los asigna
        a atributos de la clase (ej. self.btn_agregar) para poder manipularlos.

        También inyecta componentes si no se encuentran y establece estados iniciales.
        """
        # `findChild` busca un widget hijo dentro del widget principal por su tipo y nombre.
        self.lineEdit_archivo_excel = self.findChild(
            QLineEdit, "lineEdit_archivo_excel"
        )
        self.btn_browse_archivo_excel = self.findChild(
            QPushButton, "btn_browse_archivo_excel"
        )
        self.lineEdit_directorio_salida = self.findChild(
            QLineEdit, "lineEdit_directorio_salida"
        )
        self.btn_browse_directorio_salida = self.findChild(
            QPushButton, "btn_browse_directorio_salida"
        )
        self.listWidget_hojas = self.findChild(QListWidget, "listWidget_hojas")
        self.btn_agregar = self.findChild(QPushButton, "btn_agregar")
        self.btn_agregar_todos = self.findChild(QPushButton, "btn_agregar_todos")
        self.btn_quitar = self.findChild(QPushButton, "btn_quitar")
        self.btn_quitar_todos = self.findChild(QPushButton, "btn_quitar_todos")
        self.listWidget_tablas_seleccionadas = self.findChild(
            QListWidget, "listWidget_tablas_seleccionadas"
        )
        self.btn_salir = self.findChild(QPushButton, "btn_salir")

        # Componentes que se inyectan dinámicamente si no existen en el .ui
        self.btn_borrar_config = self.findChild(QPushButton, "btn_borrar_config")
        self.checkBox_un_solo_archivo = self.findChild(
            QCheckBox, "checkBox_un_solo_archivo"
        )
        self.lineEdit_archivo_todos = self.findChild(
            QLineEdit, "lineEdit_archivo_todos"
        )
        self.btn_guardar_todos = self.findChild(QPushButton, "btn_guardar_todos")
        self.btn_ejecutar_creacion = self.findChild(
            QPushButton, "btn_ejecutar_creacion"
        )

        # --- Widgets de Ejecutar Querys ---
        self.lineEdit_dir_querys = self.findChild(QLineEdit, "lineEdit_dir_querys")
        self.btn_browse_dir_querys = self.findChild(QPushButton, "btn_browse_dir_querys")
        self.listWidget_querys_disponibles = self.findChild(QListWidget, "listWidget_querys_disponibles")
        self.btn_eq_agregar = self.findChild(QPushButton, "btn_eq_agregar")
        self.btn_eq_agregar_todos = self.findChild(QPushButton, "btn_eq_agregar_todos")
        self.btn_eq_quitar = self.findChild(QPushButton, "btn_eq_quitar")
        self.btn_eq_quitar_todos = self.findChild(QPushButton, "btn_eq_quitar_todos")
        self.listWidget_querys_seleccionados = self.findChild(QListWidget, "listWidget_querys_seleccionados")
        self.btn_limpiar_config_eq = self.findChild(QPushButton, "btn_limpiar_config_eq")
        self.checkBox_crear_log = self.findChild(QCheckBox, "checkBox_crear_log")
        self.checkBox_permitir_parcial = self.findChild(QCheckBox, "checkBox_permitir_parcial")
        self.lineEdit_nom_log = self.findChild(QLineEdit, "lineEdit_nom_log")
        self.btn_guardar_nom_log = self.findChild(QPushButton, "btn_guardar_nom_log")
        self.btn_ejecutar_querys = self.findChild(QPushButton, "btn_ejecutar_querys")

        # Estado inicial de Ejecutar Querys
        if self.lineEdit_nom_log:
            self.lineEdit_nom_log.setEnabled(False)
        if self.checkBox_crear_log:
            self.checkBox_crear_log.setChecked(False)
        if self.checkBox_permitir_parcial:
            self.checkBox_permitir_parcial.setChecked(False)

        # Si un componente clave no está en el .ui, lo creamos y añadimos a la fuerza.
        # Esto da flexibilidad si se modifica el .ui.
        if not self.btn_borrar_config:
            self._inject_missing_components()

        # Estado inicial del checkbox.
        if self.checkBox_un_solo_archivo:
            self.checkBox_un_solo_archivo.setChecked(False)

        # Habilitar o deshabilitar el botón principal basado en si existe el archivo de config.
        if self.btn_ejecutar_creacion:
            self.btn_ejecutar_creacion.setEnabled(os.path.exists(_CONF_FILE))

    def connect_signals(self):
        """
        Conecta las "señales" de los widgets (ej. 'clicked' para un botón) a los
        "slots" (métodos de esta clase que deben ejecutarse como respuesta).
        Este es el corazón del manejo de eventos en Qt.
        """
        # Señales de los botones para buscar archivos y directorios.
        if self.btn_browse_archivo_excel:
            self.btn_browse_archivo_excel.clicked.connect(self._browse_excel_file)
        if self.btn_browse_directorio_salida:
            self.btn_browse_directorio_salida.clicked.connect(
                self._browse_output_directory
            )

        # Si el texto del QLineEdit cambia, se ejecutan estos métodos.
        if self.lineEdit_archivo_excel:
            self.lineEdit_archivo_excel.textChanged.connect(self._load_excel_sheets)
            self.lineEdit_archivo_excel.textChanged.connect(self._save_config_file)
        if self.lineEdit_directorio_salida:
            self.lineEdit_directorio_salida.textChanged.connect(
                self._save_output_dir_config
            )

        # Botones para mover tablas entre la lista de disponibles y seleccionadas.
        if self.btn_agregar:
            self.btn_agregar.clicked.connect(self._add_item)
        if self.btn_agregar_todos:
            self.btn_agregar_todos.clicked.connect(self._add_all_items)
        if self.btn_quitar:
            self.btn_quitar.clicked.connect(self._remove_item)
        if self.btn_quitar_todos:
            self.btn_quitar_todos.clicked.connect(self._remove_all_items)
        if self.btn_salir:
            self.btn_salir.clicked.connect(self._go_to_main_window)

        # Actualiza el estado de los botones si cambia la selección en las listas.
        if self.listWidget_hojas:
            self.listWidget_hojas.itemSelectionChanged.connect(self._update_button_states)
            self.listWidget_hojas.itemDoubleClicked.connect(self._add_item)
        if self.listWidget_tablas_seleccionadas:
            self.listWidget_tablas_seleccionadas.itemSelectionChanged.connect(
                self._update_button_states
            )
            self.listWidget_tablas_seleccionadas.itemDoubleClicked.connect(self._remove_item)

        # Conexiones para los botones inyectados dinámicamente.
        if self.btn_borrar_config:
            self.btn_borrar_config.clicked.connect(self._borrar_configuracion)

        if self.btn_guardar_todos:
            self.btn_guardar_todos.clicked.connect(self._guardar_arch_todos)

        if self.btn_ejecutar_creacion:
            self.btn_ejecutar_creacion.clicked.connect(self._ejecutar_creacion_scripts)

        # --- Señales de Ejecutar Querys ---
        tab_widget = self.central_widget.findChild(QTabWidget, "tabWidget")
        if tab_widget:
            tab_widget.currentChanged.connect(self._on_tab_changed)

        if self.btn_browse_dir_querys:
            self.btn_browse_dir_querys.clicked.connect(self._browse_dir_querys)
        if self.btn_eq_agregar:
            self.btn_eq_agregar.clicked.connect(self._eq_add_item)
        if self.btn_eq_agregar_todos:
            self.btn_eq_agregar_todos.clicked.connect(self._eq_add_all_items)
        if self.btn_eq_quitar:
            self.btn_eq_quitar.clicked.connect(self._eq_remove_item)
        if self.btn_eq_quitar_todos:
            self.btn_eq_quitar_todos.clicked.connect(self._eq_remove_all_items)
        if self.listWidget_querys_disponibles:
            self.listWidget_querys_disponibles.itemSelectionChanged.connect(
                self._update_eq_button_states)
            self.listWidget_querys_disponibles.itemDoubleClicked.connect(self._eq_add_item)
        if self.listWidget_querys_seleccionados:
            self.listWidget_querys_seleccionados.itemSelectionChanged.connect(
                self._update_eq_button_states)
            self.listWidget_querys_seleccionados.itemDoubleClicked.connect(self._eq_remove_item)
        if self.btn_limpiar_config_eq:
            self.btn_limpiar_config_eq.clicked.connect(self._eq_limpiar_configuracion)
        if self.checkBox_crear_log:
            self.checkBox_crear_log.stateChanged.connect(self._on_crear_log_changed)
        if self.checkBox_permitir_parcial:
            self.checkBox_permitir_parcial.stateChanged.connect(self._on_permitir_parcial_changed)
        if self.lineEdit_nom_log:
            self.lineEdit_nom_log.textChanged.connect(self._update_eq_button_states)
        if self.btn_guardar_nom_log:
            self.btn_guardar_nom_log.clicked.connect(self._eq_guardar_nom_log)
        if self.btn_ejecutar_querys:
            self.btn_ejecutar_querys.clicked.connect(self._eq_ejecutar_querys)

    # --- Métodos (Slots) de Lógica de la Aplicación ---

    def _ejecutar_creacion_scripts(self):
        """
        Slot que se ejecuta al presionar "Ejecutar creación".
        Orquesta la validación y la llamada al servicio de generación de SQL.
        """
        config_path = _CONF_FILE
        if not os.path.exists(config_path):
            self._show_message_box(
                "Error",
                "El archivo de configuración 'ConfInsert.conf' no se encuentra.",
                QMessageBox.Icon.Critical,
            )
            return

        # 1. Leer y parsear el archivo de configuración.
        config = {}
        with open(config_path, "r") as f:
            for line in f:
                if line.startswith("01|"):
                    parts = line.strip().split("|", 2)
                    if len(parts) == 3:
                        config[parts[1]] = parts[2]

        # 2. Realizar validaciones de consistencia.
        errors = []
        arch_excel = config.get("ArchExcel", "").strip()
        if not arch_excel:
            errors.append("La entrada '01|ArchExcel|' no puede estar vacía.")

        if not config.get("DirSal", "").strip():
            errors.append("La entrada '01|DirSal|' no puede estar vacía.")

        if arch_excel and not config.get("Tablas", "").strip():
            errors.append(
                "La entrada '01|Tablas|' no puede estar vacía si '01|ArchExcel|' tiene un valor."
            )

        # 3. Si hay errores, mostrarlos todos juntos y detener la ejecución.
        if errors:
            error_message = (
                "Se encontraron los siguientes errores en 'ConfInsert.conf':\n\n"
                + "\n".join(f"- {error}" for error in errors)
            )
            self._show_message_box(
                "Errores de Configuración", error_message, QMessageBox.Icon.Warning
            )
            return

        # 4. Si todo es correcto, proceder con la generación.
        try:
            tablas = [
                tabla.strip()
                for tabla in config.get("Tablas", "").split(",")
                if tabla.strip()
            ]
            my_archexcel = config.get("ArchExcel")
            output_dir = config.get("DirSal")
            un_solo_archivo = self.checkBox_un_solo_archivo.isChecked()

            # Itera sobre cada tabla seleccionada para generar su SQL.
            for i, tabla_nombre in enumerate(tablas):
                # Parámetros para la función de servicio.
                hoja_de_lexcel = tabla_nombre
                nombre_tabla = tabla_nombre
                tip_boolean = False

                # Lógica para determinar el archivo de salida y el modo (append/write).
                if un_solo_archivo:
                    my_archsql = os.path.join(
                        output_dir, config.get("ArchTodos", "salida_unica.sql")
                    )
                    # El primer archivo se sobreescribe, los siguientes se añaden.
                    if i > 0:
                        tip_boolean = True
                else:
                    my_archsql = os.path.join(output_dir, f"Ins_{tabla_nombre}.sql")
                    # Siempre se sobreescribe para crear archivos separados.
                    tip_boolean = False

                # Llamada a la función de servicio que hace el trabajo pesado.
                excel_to_postgres_inserts(
                    excel_file=my_archexcel,
                    sheet_name=hoja_de_lexcel,
                    table_name=nombre_tabla,
                    output_file=my_archsql,
                    append=tip_boolean,
                )

            self._show_message_box(
                "Éxito",
                "Los scripts SQL han sido generados correctamente.",
                QMessageBox.Icon.Information,
            )

        except Exception as e:
            self._show_message_box(
                "Error Inesperado",
                f"Ocurrió un error durante la generación de scripts:\n{e}",
                QMessageBox.Icon.Critical,
            )

    def _inject_missing_components(self):
        """
        Crea y añade widgets al panel derecho de la interfaz si estos no fueron
        cargados desde el archivo .ui.
        """
        tab_widget = self.findChild(QWidget, "tab_genera_inserts")
        if not tab_widget:
            return

        layout = tab_widget.layout()
        if not layout or not isinstance(layout, QGridLayout):
            return

        # Panel derecho como QGroupBox para delimitar visualmente la sección.
        right_panel = QGroupBox("OPCIONES DE EXPORTACIÓN")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 22, 16, 16)
        right_layout.setSpacing(10)

        self.btn_borrar_config = QPushButton("Limpiar configuración")
        self.btn_borrar_config.setObjectName("btn_borrar_config")
        right_layout.addWidget(self.btn_borrar_config)

        right_layout.addSpacing(12)

        self.checkBox_un_solo_archivo = QCheckBox("Consolidar en un solo archivo")
        self.checkBox_un_solo_archivo.setObjectName("checkBox_un_solo_archivo")
        right_layout.addWidget(self.checkBox_un_solo_archivo)

        right_layout.addSpacing(8)

        lbl = QLabel("NOMBRE DEL ARCHIVO SQL:")
        right_layout.addWidget(lbl)

        self.lineEdit_archivo_todos = QLineEdit()
        self.lineEdit_archivo_todos.setObjectName("lineEdit_archivo_todos")
        self.lineEdit_archivo_todos.setPlaceholderText("Ej: carga_completa.sql")
        right_layout.addWidget(self.lineEdit_archivo_todos)

        self.btn_guardar_todos = QPushButton("Guardar nombre")
        self.btn_guardar_todos.setObjectName("btn_guardar_todos")
        right_layout.addWidget(self.btn_guardar_todos)

        right_layout.addSpacing(20)

        self.btn_ejecutar_creacion = QPushButton("▶   Ejecutar creación")
        self.btn_ejecutar_creacion.setObjectName("btn_ejecutar_creacion")
        right_layout.addWidget(self.btn_ejecutar_creacion)

        right_layout.addStretch()

        layout.addWidget(right_panel, 0, layout.columnCount(), -1, 1)

    def _browse_excel_file(self):
        """Abre un diálogo para que el usuario seleccione un archivo Excel."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Archivo Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        if filepath:
            self.lineEdit_archivo_excel.setText(filepath)

    def _browse_output_directory(self):
        """Abre un diálogo para que el usuario seleccione un directorio de salida."""
        dirpath = QFileDialog.getExistingDirectory(
            self, "Seleccionar Directorio de Salida"
        )
        if dirpath:
            self.lineEdit_directorio_salida.setText(dirpath)

    def _load_excel_sheets(self, filepath):
        """
        Lee las hojas de un archivo Excel y las carga en el ComboBox.
        También actualiza la lista de tablas seleccionadas si el archivo cambia.
        """
        self.listWidget_hojas.clear()
        self.listWidget_tablas_seleccionadas.clear()

        if not filepath or not os.path.exists(filepath):
            self.config_tablas = []
            self._save_tables_config()
            self._update_button_states()
            return

        try:
            xls = pd.ExcelFile(filepath)
            sheet_names = xls.sheet_names

            self.config_tablas = [
                tabla for tabla in self.config_tablas if tabla in sheet_names
            ]

            for sheet_name in sheet_names:
                if sheet_name in self.config_tablas:
                    self.listWidget_tablas_seleccionadas.addItem(sheet_name)
                else:
                    self.listWidget_hojas.addItem(sheet_name)

            self._save_tables_config()

        except Exception as e:
            self._show_message_box(
                "Error al leer archivo",
                f"No se pudo leer el archivo Excel: {e}",
                QMessageBox.Icon.Critical,
            )

        self._update_button_states()

    def _update_button_states(self):
        """Habilita o deshabilita los botones 'Agregar', 'Quitar' y sus variantes masivas según el contexto."""
        self.btn_agregar.setEnabled(
            len(self.listWidget_hojas.selectedItems()) > 0
        )
        self.btn_quitar.setEnabled(
            len(self.listWidget_tablas_seleccionadas.selectedItems()) > 0
        )
        if self.btn_agregar_todos:
            self.btn_agregar_todos.setEnabled(self.listWidget_hojas.count() > 0)
        if self.btn_quitar_todos:
            self.btn_quitar_todos.setEnabled(self.listWidget_tablas_seleccionadas.count() > 0)

    def _update_eq_button_states(self):
        """Recalcula el estado habilitado/deshabilitado de todos los botones de Ejecutar Querys."""
        if self.btn_eq_agregar:
            self.btn_eq_agregar.setEnabled(
                bool(self.listWidget_querys_disponibles and
                     self.listWidget_querys_disponibles.selectedItems())
            )
        if self.btn_eq_agregar_todos:
            self.btn_eq_agregar_todos.setEnabled(
                bool(self.listWidget_querys_disponibles and
                     self.listWidget_querys_disponibles.count() > 0)
            )
        if self.btn_eq_quitar:
            self.btn_eq_quitar.setEnabled(
                bool(self.listWidget_querys_seleccionados and
                     self.listWidget_querys_seleccionados.selectedItems())
            )
        if self.btn_eq_quitar_todos:
            self.btn_eq_quitar_todos.setEnabled(
                bool(self.listWidget_querys_seleccionados and
                     self.listWidget_querys_seleccionados.count() > 0)
            )
        if self.btn_ejecutar_querys:
            self.btn_ejecutar_querys.setEnabled(
                bool(self.listWidget_querys_seleccionados and
                     self.listWidget_querys_seleccionados.count() > 0)
            )
        crear_log = bool(self.checkBox_crear_log and self.checkBox_crear_log.isChecked())
        nom_log_texto = self.lineEdit_nom_log.text().strip() if self.lineEdit_nom_log else ""
        if self.lineEdit_nom_log:
            self.lineEdit_nom_log.setEnabled(crear_log)
        if self.btn_guardar_nom_log:
            self.btn_guardar_nom_log.setEnabled(crear_log and bool(nom_log_texto))

    def _add_item(self):
        """Mueve una tabla de la lista de disponibles a la de seleccionadas."""
        selected_items = self.listWidget_hojas.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            self.listWidget_tablas_seleccionadas.addItem(item.text())
            self.listWidget_hojas.takeItem(self.listWidget_hojas.row(item))

        self._update_button_states()
        self._save_tables_config()

    def _add_all_items(self):
        """Mueve todas las tablas de disponibles a seleccionadas."""
        while self.listWidget_hojas.count() > 0:
            item = self.listWidget_hojas.takeItem(0)
            self.listWidget_tablas_seleccionadas.addItem(item.text())
        self._update_button_states()
        self._save_tables_config()

    def _remove_item(self):
        """Mueve una tabla de la lista de seleccionadas a la de disponibles."""
        selected_items = self.listWidget_tablas_seleccionadas.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            self.listWidget_hojas.addItem(item.text())
            self.listWidget_tablas_seleccionadas.takeItem(
                self.listWidget_tablas_seleccionadas.row(item)
            )

        self._update_button_states()
        self._save_tables_config()  # Guarda el cambio en ConfInsert.conf

    def _remove_all_items(self):
        """Mueve todas las tablas de seleccionadas a disponibles."""
        while self.listWidget_tablas_seleccionadas.count() > 0:
            item = self.listWidget_tablas_seleccionadas.takeItem(0)
            self.listWidget_hojas.addItem(item.text())
        self._update_button_states()
        self._save_tables_config()

    def set_active_tab(self, index: int):
        """Selecciona la pestaña indicada por índice (0=Crear Inserts, 1=Ejecutar Querys, …)."""
        tab_widget = self.central_widget.findChild(QTabWidget, "tabWidget")
        if tab_widget:
            tab_widget.setCurrentIndex(index)

    def _go_to_main_window(self):
        """Oculta la ventana actual y muestra la ventana principal."""
        self.hide()
        self.main_window.show()

    # --- Métodos para la gestión del archivo de configuración ---

    def _save_config_file(self):
        """Guarda la ruta del archivo Excel en ConfInsert.conf."""
        self._write_to_config("01|ArchExcel|", self.lineEdit_archivo_excel.text())

    def _save_output_dir_config(self):
        """Guarda la ruta del directorio de salida en ConfInsert.conf."""
        self._write_to_config("01|DirSal|", self.lineEdit_directorio_salida.text())

    def _save_tables_config(self):
        """Guarda la lista de tablas seleccionadas en ConfInsert.conf."""
        items = [
            self.listWidget_tablas_seleccionadas.item(i).text()
            for i in range(self.listWidget_tablas_seleccionadas.count())
        ]
        value = ",".join(items)
        if value:
            self._write_to_config("01|Tablas|", value)
        else:
            config_path = _CONF_FILE
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    lines = [l for l in f if not l.strip().startswith("01|Tablas|")]
                with open(config_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)

    def _write_to_config(self, key, value):
        """
        Función auxiliar para escribir una clave y valor en ConfInsert.conf.
        Si la clave ya existe, la actualiza; si no, la añade al final.
        """
        if not value:
            return
        config_path = _CONF_FILE
        lines = []
        found = False
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                if line.strip().startswith(key):
                    lines[i] = f"{key}{value}\n"
                    found = True
                    break
        if not found:
            lines.append(f"{key}{value}\n")
        with open(config_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def _load_config_file(self):
        """
        Carga la configuración desde ConfInsert.conf al iniciar la aplicación
        y la aplica a los widgets correspondientes.
        """
        config_path = _CONF_FILE
        if not os.path.exists(config_path):
            return

        config = {}
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 3 and parts[0] == "01":
                    config[parts[1]] = "|".join(parts[2:])

        if "ArchTodos" in config and self.lineEdit_archivo_todos:
            self.lineEdit_archivo_todos.setText(config["ArchTodos"])

        if "ArchExcel" in config and os.path.exists(config["ArchExcel"]):
            if "Tablas" in config:
                self.config_tablas = [
                    tabla.strip()
                    for tabla in config["Tablas"].split(",")
                    if tabla.strip()
                ]

            self.lineEdit_archivo_excel.setText(config["ArchExcel"])

            if "DirSal" in config and os.path.isdir(config["DirSal"]):
                self.lineEdit_directorio_salida.setText(config["DirSal"])
        elif "ArchExcel" in config:
            self._show_message_box(
                "Error",
                "El archivo de Excel especificado en la configuración no existe.",
                QMessageBox.Icon.Critical,
            )
            if "DirSal" in config and os.path.isdir(config["DirSal"]):
                self.lineEdit_directorio_salida.setText(config["DirSal"])

    def _borrar_configuracion(self):
        """Limpia la UI y borra las entradas de configuración del archivo."""
        if self.lineEdit_archivo_excel:
            self.lineEdit_archivo_excel.clear()
        if self.lineEdit_directorio_salida:
            self.lineEdit_directorio_salida.clear()
        if self.listWidget_hojas:
            self.listWidget_hojas.clear()
        if self.listWidget_tablas_seleccionadas:
            self.listWidget_tablas_seleccionadas.clear()
        if self.lineEdit_archivo_todos:
            self.lineEdit_archivo_todos.clear()
        self.config_tablas = []

        config_path = _CONF_FILE
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                lines = [line for line in f if not line.startswith("01|")]
            with open(config_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

        self._show_message_box(
            "Información",
            "Datos de configuración borrados.",
            QMessageBox.Icon.Information,
        )

    def _guardar_arch_todos(self):
        """Guarda el nombre del archivo SQL único en la configuración."""
        if not self.lineEdit_archivo_todos:
            return

        text = self.lineEdit_archivo_todos.text().strip()

        if not text or " " in text:
            self._show_message_box(
                "Error",
                "El nombre del archivo no puede ser vacío ni contener espacios.",
                QMessageBox.Icon.Critical,
            )
            return

        if not text.lower().endswith(".sql"):
            text += ".sql"

        self.lineEdit_archivo_todos.setText(text)
        self._write_to_config("01|ArchTodos|", text)
        self._show_message_box(
            "Éxito",
            "Nombre de archivo guardado correctamente.",
            QMessageBox.Icon.Information,
        )

    # --- Métodos de Utilidad ---

    def _show_message_box(self, title, text, icon):
        """Muestra un cuadro de diálogo modal con un mensaje personalizado."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        msg_box.setStyleSheet(self.styleSheet())  # Reutiliza el stylesheet principal.
        msg_box.exec()

    def _apply_styles(self):
        """Aplica una hoja de estilos ejecutiva a la ventana y sus widgets."""
        stylesheet = """
            QMainWindow, QWidget {
                background-color: #0D1117;
                color: #C8D0DF;
                font-family: 'Segoe UI';
                font-size: 10pt;
            }
            QWidget#tab_genera_inserts,
            QWidget#tab_ejecuta_querys,
            QWidget#tab_exportar_tablas {
                background-color: #111827;
                padding: 20px;
            }
            QLabel {
                color: #68748A;
                font-size: 8.5pt;
                font-weight: 700;
                background: transparent;
                letter-spacing: 0.8px;
            }
            QLineEdit {
                background-color: #141B27;
                border: 1px solid #1A2435;
                border-bottom: 2px solid #1A2435;
                border-radius: 0px;
                padding: 9px 12px;
                color: #C8D0DF;
                font-size: 10pt;
                selection-background-color: #1E3A5A;
            }
            QLineEdit:focus {
                border-bottom-color: #B8922A;
                background-color: #141E30;
            }
            QComboBox {
                background-color: #141B27;
                border: 1px solid #1A2435;
                border-bottom: 2px solid #1A2435;
                padding: 9px 12px;
                color: #C8D0DF;
                font-size: 10pt;
                border-radius: 0px;
            }
            QComboBox:focus { border-bottom-color: #B8922A; }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #141B27;
                border: 1px solid #1A2435;
                selection-background-color: #1A2D45;
                selection-color: #E0C570;
                color: #C8D0DF;
                padding: 4px;
                outline: none;
            }
            QListWidget {
                background-color: #0C1018;
                border: 1px solid #1A2435;
                color: #C8D0DF;
                font-size: 10pt;
                outline: none;
                padding: 2px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #111827;
            }
            QListWidget::item:selected {
                background-color: #152035;
                color: #E0C570;
                border-left: 3px solid #B8922A;
                padding-left: 9px;
            }
            QListWidget::item:hover:!selected {
                background-color: #111827;
            }
            QTabWidget::pane {
                border: 1px solid #1A2435;
                border-top: none;
                background-color: #111827;
            }
            QTabBar { background: transparent; }
            QTabBar::tab {
                background-color: #090D13;
                color: #3A4558;
                padding: 11px 30px;
                border: 1px solid #111827;
                border-bottom: none;
                font-size: 9.5pt;
                font-weight: 700;
                letter-spacing: 0.8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #111827;
                color: #E0C570;
                border-color: #1A2435;
                border-bottom: 2px solid #B8922A;
            }
            QTabBar::tab:hover:!selected {
                color: #5A6880;
                background-color: #0C1420;
            }
            QPushButton {
                background-color: #131E30;
                color: #7A88A0;
                font-weight: 700;
                border: 1px solid #1A2D45;
                border-radius: 2px;
                padding: 9px 18px;
                font-size: 10pt;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background-color: #182540;
                border-color: #3A5A88;
                color: #C0D0E8;
            }
            QPushButton:pressed {
                background-color: #0C1520;
                border-color: #2A4068;
            }
            QPushButton:disabled {
                background-color: #0A0F18;
                color: #1E2638;
                border-color: #111820;
            }
            QPushButton#btn_browse_archivo_excel,
            QPushButton#btn_browse_directorio_salida {
                background-color: #0F1520;
                border: 1px solid #1A2435;
                color: #404A5E;
                padding: 9px 16px;
                font-size: 11pt;
                font-weight: 400;
                letter-spacing: 0;
            }
            QPushButton#btn_browse_archivo_excel:hover,
            QPushButton#btn_browse_directorio_salida:hover {
                border-color: #B8922A;
                color: #D4A848;
                background-color: #181408;
            }
            QPushButton#btn_agregar {
                background-color: #0A2018;
                border: 1px solid #143024;
                color: #4A9068;
            }
            QPushButton#btn_agregar:hover {
                background-color: #0F2C22;
                border-color: #205840;
                color: #70B090;
            }
            QPushButton#btn_agregar_todos {
                background-color: #0A2018;
                border: 1px solid #143024;
                color: #4A9068;
            }
            QPushButton#btn_agregar_todos:hover {
                background-color: #0F2C22;
                border-color: #205840;
                color: #70B090;
            }
            QPushButton#btn_quitar {
                background-color: #200A0A;
                border: 1px solid #301010;
                color: #905858;
            }
            QPushButton#btn_quitar:hover {
                background-color: #2C1010;
                border-color: #502020;
                color: #B07878;
            }
            QPushButton#btn_quitar_todos {
                background-color: #200A0A;
                border: 1px solid #301010;
                color: #905858;
            }
            QPushButton#btn_quitar_todos:hover {
                background-color: #2C1010;
                border-color: #502020;
                color: #B07878;
            }
            QPushButton#btn_ejecutar_creacion {
                background-color: #1C1408;
                border: 1px solid #40300A;
                color: #C8A03A;
                font-size: 10.5pt;
                font-weight: 700;
                padding: 13px 20px;
                letter-spacing: 0.5px;
            }
            QPushButton#btn_ejecutar_creacion:hover {
                background-color: #281C08;
                border-color: #6A500E;
                color: #E0BE58;
            }
            QPushButton#btn_ejecutar_creacion:pressed {
                background-color: #120E06;
                border-color: #4A3808;
            }
            QPushButton#btn_ejecutar_creacion:disabled {
                background-color: #0A0A08;
                color: #2A2010;
                border-color: #181408;
            }
            QPushButton#btn_salir {
                background-color: #0F1825;
                border: 1px solid #1E2D40;
                border-bottom: 2px solid #243550;
                color: #7A8CA8;
                font-size: 9.5pt;
                padding: 6px 20px;
                font-weight: 600;
                letter-spacing: 0.8px;
            }
            QPushButton#btn_salir:hover {
                background-color: #141E30;
                border-color: #2A3D58;
                border-bottom-color: #B8922A;
                color: #C0CCDC;
            }
            QPushButton#btn_salir:pressed {
                background-color: #0A1020;
                border-bottom-color: #8A6D1A;
                color: #8898A8;
            }
            QGroupBox {
                border: 1px solid #1A2D40;
                border-radius: 0px;
                margin-top: 22px;
                padding: 16px 12px 12px 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 2px 10px;
                background-color: #0D1117;
                color: #B8922A;
                font-size: 8pt;
                font-weight: 700;
                letter-spacing: 2px;
            }
            QCheckBox {
                color: #6878A0;
                spacing: 10px;
                font-size: 10pt;
                background: transparent;
                letter-spacing: 0.3px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #2A3A50;
                border-radius: 0px;
                background-color: #141B27;
            }
            QCheckBox::indicator:checked {
                background-color: #B8922A;
                border-color: #B8922A;
            }
            QCheckBox::indicator:hover { border-color: #B8922A; }
            QScrollBar:vertical {
                background: #0D1117;
                width: 7px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #1A2435;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #2A3A55; }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0; border: none; }
            QScrollBar:horizontal {
                background: #0D1117;
                height: 7px;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background: #1A2435;
                border-radius: 3px;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal { width: 0; border: none; }
            QPushButton#btn_browse_dir_querys {
                background-color: #0F1520;
                border: 1px solid #1A2435;
                color: #404A5E;
                padding: 9px 16px;
                font-size: 11pt;
                font-weight: 400;
                letter-spacing: 0;
            }
            QPushButton#btn_browse_dir_querys:hover {
                border-color: #B8922A;
                color: #D4A848;
                background-color: #181408;
            }
            QPushButton#btn_eq_agregar,
            QPushButton#btn_eq_agregar_todos {
                background-color: #0A2018;
                border: 1px solid #143024;
                color: #4A9068;
            }
            QPushButton#btn_eq_agregar:hover,
            QPushButton#btn_eq_agregar_todos:hover {
                background-color: #0F2C22;
                border-color: #205840;
                color: #70B090;
            }
            QPushButton#btn_eq_agregar:disabled,
            QPushButton#btn_eq_agregar_todos:disabled {
                background-color: #0A0F18;
                color: #1E2638;
                border-color: #111820;
            }
            QPushButton#btn_eq_quitar,
            QPushButton#btn_eq_quitar_todos {
                background-color: #200A0A;
                border: 1px solid #301010;
                color: #905858;
            }
            QPushButton#btn_eq_quitar:hover,
            QPushButton#btn_eq_quitar_todos:hover {
                background-color: #2C1010;
                border-color: #502020;
                color: #B07878;
            }
            QPushButton#btn_eq_quitar:disabled,
            QPushButton#btn_eq_quitar_todos:disabled {
                background-color: #0A0F18;
                color: #1E2638;
                border-color: #111820;
            }
            QPushButton#btn_ejecutar_querys {
                background-color: #1C1408;
                border: 1px solid #40300A;
                color: #C8A03A;
                font-size: 10.5pt;
                font-weight: 700;
                padding: 13px 20px;
                letter-spacing: 0.5px;
            }
            QPushButton#btn_ejecutar_querys:hover {
                background-color: #281C08;
                border-color: #6A500E;
                color: #E0BE58;
            }
            QPushButton#btn_ejecutar_querys:pressed {
                background-color: #120E06;
                border-color: #4A3808;
            }
            QPushButton#btn_ejecutar_querys:disabled {
                background-color: #0A0A08;
                color: #2A2010;
                border-color: #181408;
            }
            QPushButton#btn_limpiar_config_eq {
                background-color: #1C0E08;
                border: 1px solid #382010;
                color: #906040;
                font-size: 9.5pt;
            }
            QPushButton#btn_limpiar_config_eq:hover {
                background-color: #241408;
                border-color: #584028;
                color: #B08060;
            }
            QPushButton#btn_guardar_nom_log {
                background-color: #0A1520;
                border: 1px solid #142030;
                color: #507090;
                font-size: 9.5pt;
            }
            QPushButton#btn_guardar_nom_log:hover {
                background-color: #0F1C2C;
                border-color: #204060;
                color: #70A0C0;
            }
            QPushButton#btn_guardar_nom_log:disabled {
                background-color: #0A0F18;
                color: #1E2638;
                border-color: #111820;
            }
        """
        self.setStyleSheet(stylesheet)

    def findChild(self, type, name):
        """
        Sobreescritura del método findChild para buscar siempre dentro del
        widget central cargado desde el .ui, simplificando las llamadas.
        """
        return self.central_widget.findChild(type, name)

    # =========================================================================
    # Métodos de la pestaña "Ejecutar Querys"
    # =========================================================================

    # --- US1: Configurar Directorio ---

    def _eq_write_config(self, key: str, value):
        """Escribe o elimina una entrada 02|key|value en ConfInsert.conf."""
        config_path = _CONF_FILE
        prefix = f"02|{key}|"
        lines = []
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        lines = [l for l in lines if not l.strip().startswith(prefix)]
        if value is not None:
            lines.append(f"{prefix}{value}\n")
        with open(config_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def _on_tab_changed(self, index):
        """Carga la configuración de Ejecutar Querys al activar la pestaña."""
        if index == 1:
            self._load_ejecutar_querys_config()

    def _load_ejecutar_querys_config(self):
        """Lee ConfInsert.conf y restaura la configuración 02|* en la pestaña Ejecutar Querys."""
        config_path = _CONF_FILE
        config = {}
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("02|"):
                        parts = line.strip().split("|", 2)
                        if len(parts) == 3:
                            config[parts[1]] = parts[2]

        dir_ent = config.get("DirEnt", "").strip()
        querys_guardados = [q.strip() for q in config.get("Querys", "").split(",") if q.strip()]
        nom_log = config.get("NomLog", "").strip()
        chek_log = config.get("ChekLog", "").strip().upper() == "SI"
        chek_oper_v = config.get("ChekOperV", "").strip().upper() == "SI"

        # Restaurar checkboxes y nom_log siempre, sin importar el directorio
        if self.checkBox_crear_log:
            self.checkBox_crear_log.blockSignals(True)
            self.checkBox_crear_log.setChecked(chek_log)
            self.checkBox_crear_log.blockSignals(False)
        if self.checkBox_permitir_parcial:
            self.checkBox_permitir_parcial.blockSignals(True)
            self.checkBox_permitir_parcial.setChecked(chek_oper_v)
            self.checkBox_permitir_parcial.blockSignals(False)
        if nom_log and self.lineEdit_nom_log:
            self.lineEdit_nom_log.setText(nom_log)

        if self.listWidget_querys_disponibles:
            self.listWidget_querys_disponibles.clear()
        if self.listWidget_querys_seleccionados:
            self.listWidget_querys_seleccionados.clear()

        if not dir_ent:
            self._update_eq_button_states()
            return

        if not os.path.isdir(dir_ent):
            self._eq_write_config("DirEnt", None)
            self._eq_write_config("Querys", None)
            if self.lineEdit_dir_querys:
                self.lineEdit_dir_querys.clear()
            self._update_eq_button_states()
            return

        if self.lineEdit_dir_querys:
            self.lineEdit_dir_querys.setText(dir_ent)

        archivos_sql = sorted([
            f[:-4] for f in os.listdir(dir_ent)
            if f.lower().endswith(".sql") and os.path.isfile(os.path.join(dir_ent, f))
        ])

        querys_validos = [q for q in querys_guardados if q in archivos_sql]
        if set(querys_validos) != set(querys_guardados):
            self._eq_write_config("Querys", ",".join(querys_validos) if querys_validos else None)

        for nombre in archivos_sql:
            if nombre in querys_validos:
                if self.listWidget_querys_seleccionados:
                    self.listWidget_querys_seleccionados.addItem(nombre)
            else:
                if self.listWidget_querys_disponibles:
                    self.listWidget_querys_disponibles.addItem(nombre)

        self._update_eq_button_states()

    def _browse_dir_querys(self):
        """Abre diálogo para seleccionar directorio de querys y actualiza la UI."""
        dirpath = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio de Querys")
        if not dirpath:
            return
        if self.lineEdit_dir_querys:
            self.lineEdit_dir_querys.setText(dirpath)
        if self.listWidget_querys_disponibles:
            self.listWidget_querys_disponibles.clear()
        if self.listWidget_querys_seleccionados:
            self.listWidget_querys_seleccionados.clear()
        self._eq_write_config("DirEnt", dirpath)
        self._eq_write_config("Querys", None)

        archivos_sql = sorted([
            f[:-4] for f in os.listdir(dirpath)
            if f.lower().endswith(".sql") and os.path.isfile(os.path.join(dirpath, f))
        ])
        for nombre in archivos_sql:
            if self.listWidget_querys_disponibles:
                self.listWidget_querys_disponibles.addItem(nombre)

        self._update_eq_button_states()

    # --- US2: Gestión de Listas ---

    def _eq_add_item(self):
        """Mueve elementos seleccionados de Disponibles a Seleccionados."""
        selected = self.listWidget_querys_disponibles.selectedItems()
        for item in selected:
            self.listWidget_querys_seleccionados.addItem(item.text())
            self.listWidget_querys_disponibles.takeItem(
                self.listWidget_querys_disponibles.row(item))
        self._update_eq_button_states()
        self._eq_save_querys_config()

    def _eq_add_all_items(self):
        """Mueve todos los elementos de Disponibles a Seleccionados."""
        while self.listWidget_querys_disponibles.count() > 0:
            item = self.listWidget_querys_disponibles.takeItem(0)
            self.listWidget_querys_seleccionados.addItem(item.text())
        self._update_eq_button_states()
        self._eq_save_querys_config()

    def _eq_remove_item(self):
        """Mueve elementos seleccionados de Seleccionados a Disponibles."""
        selected = self.listWidget_querys_seleccionados.selectedItems()
        for item in selected:
            self.listWidget_querys_disponibles.addItem(item.text())
            self.listWidget_querys_seleccionados.takeItem(
                self.listWidget_querys_seleccionados.row(item))
        self._update_eq_button_states()
        self._eq_save_querys_config()

    def _eq_remove_all_items(self):
        """Mueve todos los elementos de Seleccionados a Disponibles."""
        while self.listWidget_querys_seleccionados.count() > 0:
            item = self.listWidget_querys_seleccionados.takeItem(0)
            self.listWidget_querys_disponibles.addItem(item.text())
        self._update_eq_button_states()
        self._eq_save_querys_config()

    def _eq_save_querys_config(self):
        """Persiste la lista de Querys Seleccionados en ConfInsert.conf."""
        items = [
            self.listWidget_querys_seleccionados.item(i).text()
            for i in range(self.listWidget_querys_seleccionados.count())
        ]
        self._eq_write_config("Querys", ",".join(items) if items else None)

    # --- US3: Opciones de Ejecución y Log ---

    def _on_crear_log_changed(self):
        """Persiste el estado del checkbox Crear Log y recalcula estados de botones."""
        checked = bool(self.checkBox_crear_log and self.checkBox_crear_log.isChecked())
        self._eq_write_config("ChekLog", "Si" if checked else None)
        self._update_eq_button_states()

    def _on_permitir_parcial_changed(self):
        """Persiste el estado del checkbox Permitir ejecución parcial."""
        checked = bool(self.checkBox_permitir_parcial and self.checkBox_permitir_parcial.isChecked())
        self._eq_write_config("ChekOperV", "Si" if checked else None)

    def _eq_guardar_nom_log(self):
        """Guarda el nombre del archivo de log en ConfInsert.conf."""
        if not self.lineEdit_nom_log:
            return
        texto = self.lineEdit_nom_log.text().strip()
        if not texto:
            return
        self._eq_write_config("NomLog", texto)
        self._show_message_box("Información", "Nombre de log guardado.", QMessageBox.Icon.Information)

    def _resolve_log_path(self, directory: str, filename: str) -> str:
        """Retorna la ruta completa del log con sufijo _DDMMYY_HHMMSS.log siempre."""
        name = os.path.splitext(filename)[0]
        timestamp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        return os.path.join(directory, f"{name}_{timestamp}.log")

    def _eq_limpiar_configuracion(self):
        """Borra toda la configuración de Ejecutar Querys de la UI y de ConfInsert.conf."""
        if self.lineEdit_dir_querys:
            self.lineEdit_dir_querys.clear()
        if self.listWidget_querys_disponibles:
            self.listWidget_querys_disponibles.clear()
        if self.listWidget_querys_seleccionados:
            self.listWidget_querys_seleccionados.clear()
        if self.checkBox_crear_log:
            self.checkBox_crear_log.blockSignals(True)
            self.checkBox_crear_log.setChecked(False)
            self.checkBox_crear_log.blockSignals(False)
        if self.checkBox_permitir_parcial:
            self.checkBox_permitir_parcial.blockSignals(True)
            self.checkBox_permitir_parcial.setChecked(False)
            self.checkBox_permitir_parcial.blockSignals(False)
        if self.lineEdit_nom_log:
            self.lineEdit_nom_log.clear()

        config_path = _CONF_FILE
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                lines = [l for l in f if not l.startswith("02|")]
            with open(config_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

        self._update_eq_button_states()

    # --- US4: Ejecución de Querys ---

    def _leer_conexion_bd(self) -> dict:
        """Parsea ConexionBD.conf y retorna dict con my_db, my_user, my_pass, my_host, my_port."""
        params = {}
        try:
            with open(_CONN_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, _, val = line.partition("=")
                        params[key.strip()] = val.strip().strip('"')
        except Exception as e:
            self._show_message_box(
                "Error", f"No se pudo leer ConexionBD.conf:\n{e}", QMessageBox.Icon.Critical)
            return {}

        required = ["my_db", "my_user", "my_pass", "my_host", "my_port"]
        missing = [k for k in required if not params.get(k)]
        if missing:
            self._show_message_box(
                "Error",
                f"ConexionBD.conf no contiene los parámetros: {', '.join(missing)}",
                QMessageBox.Icon.Critical,
            )
            return {}
        return params

    def _eq_ejecutar_querys(self):
        """Valida precondiciones y lanza la ejecución de los archivos .sql en un hilo separado."""
        if not self.listWidget_querys_seleccionados or \
                self.listWidget_querys_seleccionados.count() == 0:
            self._show_message_box(
                "Error", "No hay Querys seleccionados.", QMessageBox.Icon.Warning)
            return

        if not os.path.exists(_CONN_FILE):
            self._show_message_box(
                "Error",
                "No se encontró el archivo 'ConexionBD.conf' en el directorio raíz del proyecto.",
                QMessageBox.Icon.Critical,
            )
            return

        conn_params = self._leer_conexion_bd()
        if not conn_params:
            return

        directorio = self.lineEdit_dir_querys.text().strip() if self.lineEdit_dir_querys else ""
        archivos = [
            os.path.join(directorio, self.listWidget_querys_seleccionados.item(i).text() + ".sql")
            for i in range(self.listWidget_querys_seleccionados.count())
        ]

        log_file = ""
        crear_log = bool(self.checkBox_crear_log and self.checkBox_crear_log.isChecked())
        if crear_log:
            nom_log = self.lineEdit_nom_log.text().strip() if self.lineEdit_nom_log else ""
            if not nom_log:
                self._show_message_box(
                    "Dato requerido",
                    "Proporciona un nombre de archivo para el Log de Operaciones.",
                    QMessageBox.Icon.Warning,
                )
                return
            log_file = self._resolve_log_path(directorio, nom_log)

        allow_partial = bool(
            self.checkBox_permitir_parcial and self.checkBox_permitir_parcial.isChecked())

        if log_file:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(
                    f"\n=== Ejecución: "
                    f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
                )

        self._progress_dialog = QProgressDialog(
            "Iniciando ejecución...", "Cancelar", 0, 0, self)
        self._progress_dialog.setWindowTitle("Ejecutar Querys")
        self._progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self._progress_dialog.setMinimumDuration(0)
        self._progress_dialog.setValue(0)
        self._progress_dialog.show()

        self._eq_thread = QThread(self)
        self._eq_worker = EjecutarQuerysWorker(archivos, conn_params, log_file, allow_partial)
        self._eq_worker.moveToThread(self._eq_thread)

        self._eq_thread.started.connect(self._eq_worker.run)
        self._eq_worker.progress_updated.connect(self._progress_dialog.setLabelText)
        self._eq_worker.execution_finished.connect(self._on_execution_finished)
        self._progress_dialog.canceled.connect(self._eq_worker.cancel)

        self._eq_thread.start()

    def _on_execution_finished(self, summary):
        """Cierra el progreso, detiene el hilo y muestra el resumen al usuario."""
        if self._progress_dialog:
            self._progress_dialog.close()
        if self._eq_thread:
            self._eq_thread.quit()
            self._eq_thread.wait()

        total = summary.get("total", 0)
        ok = summary.get("ok", 0)
        failed = summary.get("failed", 0)
        cancelled = summary.get("cancelled", False)
        abortado = summary.get("abortado", False)
        motivo_abort = summary.get("motivo_abort", "")
        ciclo_archivos = summary.get("ciclo_archivos", [])
        pendientes = summary.get("pendientes", [])

        if ciclo_archivos:
            msg = "Ciclo de dependencias detectado.\n\n"
            msg += "Archivos involucrados en el ciclo:\n"
            for a in ciclo_archivos:
                msg += f"  • {a}\n"
            msg += "\nNo se ejecutó ningún archivo Ins_."
            icono = QMessageBox.Icon.Critical
        elif abortado and motivo_abort:
            msg = f"Ejecución truncada.\n\nMotivo: {motivo_abort}\n"
            if pendientes:
                msg += f"\nArchivos afectados ({len(pendientes)}):\n"
                for a in pendientes:
                    msg += f"  • {a}\n"
            icono = QMessageBox.Icon.Warning
        else:
            msg = f"Ejecución {'cancelada' if cancelled else 'finalizada'}.\n\n"
            msg += f"Archivos procesados: {total}\n"
            msg += f"Exitosos: {ok}\n"
            msg += f"Fallidos: {failed}\n"
            if pendientes:
                msg += f"\nArchivos pendientes ({len(pendientes)}):\n"
                for a in pendientes:
                    msg += f"  • {a}\n"
            icono = (
                QMessageBox.Icon.Information
                if not failed and not pendientes
                else QMessageBox.Icon.Warning
            )

        log_file = self._eq_worker._log_file if self._eq_worker else ""
        if log_file and os.path.exists(log_file):
            msg += f"\nLog de detalle:\n{log_file}"

        self._show_message_box("Resumen de Ejecución", msg, icono)

    def closeEvent(self, event):
        """
        Intercepta el intento de cierre de ventana (botón X del SO).
        En lugar de cerrar el programa, regresa al menú principal.
        """
        event.ignore()
        self._go_to_main_window()
