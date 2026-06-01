import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

# from PySide6.QtGui import QScreen
from ui.main_window_ui import Ui_Form
from views.panel_principal_view import PanelPrincipalView


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Crear un widget central
        central_widget = QWidget()

        # Usar la clase de la UI pre-compilada y aplicarla al widget central
        self.ui = Ui_Form()
        self.ui.setupUi(central_widget)

        # Conectar el botón a la nueva función
        self.ui.btn_creacion.clicked.connect(self.open_panel_principal)
        self.ui.btn_salida.clicked.connect(self.close)

        # Establecer el widget central en la ventana principal
        self.setCentralWidget(central_widget)

        # Establecer el título y aplicar estilos
        self.setWindowTitle("Herramienta de Carga de Datos")
        self._apply_styles()

        # Redimensionar y centrar la ventana
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        self.resize(max(400, screen_geometry.width() // 5), max(520, screen_geometry.height() * 3 // 5))

        # Centrar la ventana en la pantalla
        frame_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def open_panel_principal(self):
        # Crear una instancia de la nueva ventana
        self.panel_window = PanelPrincipalView(self)
        # Mostrar la nueva ventana
        self.panel_window.show()
        # Ocultar la ventana actual
        self.hide()

    def _apply_styles(self):
        stylesheet = """
            QWidget {
                background-color: #0D1117;
                color: #C8D0DF;
                font-family: 'Segoe UI';
                font-size: 10pt;
            }
            QPushButton {
                background-color: #111827;
                color: #7A8499;
                font-weight: 600;
                border: 1px solid #1A2435;
                border-left: 3px solid #1A2435;
                border-radius: 0px;
                padding: 14px 22px;
                text-align: left;
                font-size: 10pt;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background-color: #161E2E;
                border-left-color: #B8922A;
                color: #E0C570;
            }
            QPushButton:pressed {
                background-color: #0A1020;
                border-left-color: #8A6D1A;
                color: #A88028;
            }
            QPushButton#btn_salida {
                background-color: transparent;
                color: #303848;
                border: 1px solid #111827;
                border-left: 3px solid #111827;
                font-size: 9.5pt;
                font-weight: 400;
                text-align: center;
                margin-top: 10px;
            }
            QPushButton#btn_salida:hover {
                border-left-color: #7A2A2A;
                color: #885050;
                background-color: #100A0A;
            }
        """
        self.setStyleSheet(stylesheet)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
