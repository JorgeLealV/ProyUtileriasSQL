# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PanelPrincipal.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QPushButton, QSizePolicy,
    QSpacerItem, QTabWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.topBarLayout = QHBoxLayout()
        self.topBarLayout.setObjectName(u"topBarLayout")
        self.topBarLayout.setContentsMargins(6)
        self.horizontalSpacer_top = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.topBarLayout.addItem(self.horizontalSpacer_top)

        self.btn_salir = QPushButton(self.centralwidget)
        self.btn_salir.setObjectName(u"btn_salir")

        self.topBarLayout.addWidget(self.btn_salir)


        self.verticalLayout.addLayout(self.topBarLayout)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_genera_inserts = QWidget()
        self.tab_genera_inserts.setObjectName(u"tab_genera_inserts")
        self.gridLayout = QGridLayout(self.tab_genera_inserts)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(0)
        self.label_archivo_excel = QLabel(self.tab_genera_inserts)
        self.label_archivo_excel.setObjectName(u"label_archivo_excel")

        self.gridLayout.addWidget(self.label_archivo_excel, 0, 0, 1, 3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.btn_agregar = QPushButton(self.tab_genera_inserts)
        self.btn_agregar.setObjectName(u"btn_agregar")

        self.verticalLayout_2.addWidget(self.btn_agregar)

        self.btn_agregar_todos = QPushButton(self.tab_genera_inserts)
        self.btn_agregar_todos.setObjectName(u"btn_agregar_todos")

        self.verticalLayout_2.addWidget(self.btn_agregar_todos)

        self.btn_quitar = QPushButton(self.tab_genera_inserts)
        self.btn_quitar.setObjectName(u"btn_quitar")

        self.verticalLayout_2.addWidget(self.btn_quitar)

        self.btn_quitar_todos = QPushButton(self.tab_genera_inserts)
        self.btn_quitar_todos.setObjectName(u"btn_quitar_todos")

        self.verticalLayout_2.addWidget(self.btn_quitar_todos)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.gridLayout.addLayout(self.verticalLayout_2, 5, 1, 1, 1)

        self.label_tablas_disponibles = QLabel(self.tab_genera_inserts)
        self.label_tablas_disponibles.setObjectName(u"label_tablas_disponibles")

        self.gridLayout.addWidget(self.label_tablas_disponibles, 4, 0, 1, 1)

        self.btn_browse_archivo_excel = QPushButton(self.tab_genera_inserts)
        self.btn_browse_archivo_excel.setObjectName(u"btn_browse_archivo_excel")

        self.gridLayout.addWidget(self.btn_browse_archivo_excel, 1, 2, 1, 1)

        self.label_tablas_seleccionadas = QLabel(self.tab_genera_inserts)
        self.label_tablas_seleccionadas.setObjectName(u"label_tablas_seleccionadas")

        self.gridLayout.addWidget(self.label_tablas_seleccionadas, 4, 2, 1, 1)

        self.label_directorio_salida = QLabel(self.tab_genera_inserts)
        self.label_directorio_salida.setObjectName(u"label_directorio_salida")

        self.gridLayout.addWidget(self.label_directorio_salida, 2, 0, 1, 3)

        self.listWidget_tablas_seleccionadas = QListWidget(self.tab_genera_inserts)
        self.listWidget_tablas_seleccionadas.setObjectName(u"listWidget_tablas_seleccionadas")

        self.gridLayout.addWidget(self.listWidget_tablas_seleccionadas, 5, 2, 1, 1)

        self.lineEdit_directorio_salida = QLineEdit(self.tab_genera_inserts)
        self.lineEdit_directorio_salida.setObjectName(u"lineEdit_directorio_salida")

        self.gridLayout.addWidget(self.lineEdit_directorio_salida, 3, 0, 1, 2)

        self.btn_browse_directorio_salida = QPushButton(self.tab_genera_inserts)
        self.btn_browse_directorio_salida.setObjectName(u"btn_browse_directorio_salida")

        self.gridLayout.addWidget(self.btn_browse_directorio_salida, 3, 2, 1, 1)

        self.lineEdit_archivo_excel = QLineEdit(self.tab_genera_inserts)
        self.lineEdit_archivo_excel.setObjectName(u"lineEdit_archivo_excel")

        self.gridLayout.addWidget(self.lineEdit_archivo_excel, 1, 0, 1, 2)

        self.listWidget_hojas = QListWidget(self.tab_genera_inserts)
        self.listWidget_hojas.setObjectName(u"listWidget_hojas")

        self.gridLayout.addWidget(self.listWidget_hojas, 5, 0, 1, 1)

        self.tabWidget.addTab(self.tab_genera_inserts, "")
        self.tab_ejecuta_querys = QWidget()
        self.tab_ejecuta_querys.setObjectName(u"tab_ejecuta_querys")
        self.gridLayout_eq = QGridLayout(self.tab_ejecuta_querys)
        self.gridLayout_eq.setObjectName(u"gridLayout_eq")
        self.label_dir_querys = QLabel(self.tab_ejecuta_querys)
        self.label_dir_querys.setObjectName(u"label_dir_querys")

        self.gridLayout_eq.addWidget(self.label_dir_querys, 0, 0, 1, 2)

        self.lineEdit_dir_querys = QLineEdit(self.tab_ejecuta_querys)
        self.lineEdit_dir_querys.setObjectName(u"lineEdit_dir_querys")

        self.gridLayout_eq.addWidget(self.lineEdit_dir_querys, 1, 0, 1, 1)

        self.btn_browse_dir_querys = QPushButton(self.tab_ejecuta_querys)
        self.btn_browse_dir_querys.setObjectName(u"btn_browse_dir_querys")

        self.gridLayout_eq.addWidget(self.btn_browse_dir_querys, 1, 1, 1, 1)

        self.label_querys_disponibles = QLabel(self.tab_ejecuta_querys)
        self.label_querys_disponibles.setObjectName(u"label_querys_disponibles")

        self.gridLayout_eq.addWidget(self.label_querys_disponibles, 2, 0, 1, 1)

        self.label_querys_seleccionados = QLabel(self.tab_ejecuta_querys)
        self.label_querys_seleccionados.setObjectName(u"label_querys_seleccionados")

        self.gridLayout_eq.addWidget(self.label_querys_seleccionados, 2, 2, 1, 1)

        self.listWidget_querys_disponibles = QListWidget(self.tab_ejecuta_querys)
        self.listWidget_querys_disponibles.setObjectName(u"listWidget_querys_disponibles")

        self.gridLayout_eq.addWidget(self.listWidget_querys_disponibles, 3, 0, 1, 1)

        self.verticalLayout_eq_btns = QVBoxLayout()
        self.verticalLayout_eq_btns.setSpacing(0)
        self.verticalLayout_eq_btns.setObjectName(u"verticalLayout_eq_btns")
        self.btn_eq_agregar = QPushButton(self.tab_ejecuta_querys)
        self.btn_eq_agregar.setObjectName(u"btn_eq_agregar")

        self.verticalLayout_eq_btns.addWidget(self.btn_eq_agregar)

        self.btn_eq_agregar_todos = QPushButton(self.tab_ejecuta_querys)
        self.btn_eq_agregar_todos.setObjectName(u"btn_eq_agregar_todos")

        self.verticalLayout_eq_btns.addWidget(self.btn_eq_agregar_todos)

        self.btn_eq_quitar = QPushButton(self.tab_ejecuta_querys)
        self.btn_eq_quitar.setObjectName(u"btn_eq_quitar")

        self.verticalLayout_eq_btns.addWidget(self.btn_eq_quitar)

        self.btn_eq_quitar_todos = QPushButton(self.tab_ejecuta_querys)
        self.btn_eq_quitar_todos.setObjectName(u"btn_eq_quitar_todos")

        self.verticalLayout_eq_btns.addWidget(self.btn_eq_quitar_todos)

        self.verticalSpacer_eq = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_eq_btns.addItem(self.verticalSpacer_eq)


        self.gridLayout_eq.addLayout(self.verticalLayout_eq_btns, 3, 1, 1, 1)

        self.listWidget_querys_seleccionados = QListWidget(self.tab_ejecuta_querys)
        self.listWidget_querys_seleccionados.setObjectName(u"listWidget_querys_seleccionados")

        self.gridLayout_eq.addWidget(self.listWidget_querys_seleccionados, 3, 2, 1, 1)

        self.groupBox_eq_opciones = QGroupBox(self.tab_ejecuta_querys)
        self.groupBox_eq_opciones.setObjectName(u"groupBox_eq_opciones")
        self.verticalLayout_eq_panel = QVBoxLayout(self.groupBox_eq_opciones)
        self.verticalLayout_eq_panel.setSpacing(10)
        self.verticalLayout_eq_panel.setObjectName(u"verticalLayout_eq_panel")
        self.verticalLayout_eq_panel.setContentsMargins(16)
        self.btn_limpiar_config_eq = QPushButton(self.groupBox_eq_opciones)
        self.btn_limpiar_config_eq.setObjectName(u"btn_limpiar_config_eq")

        self.verticalLayout_eq_panel.addWidget(self.btn_limpiar_config_eq)

        self.checkBox_crear_log = QCheckBox(self.groupBox_eq_opciones)
        self.checkBox_crear_log.setObjectName(u"checkBox_crear_log")

        self.verticalLayout_eq_panel.addWidget(self.checkBox_crear_log)

        self.checkBox_permitir_parcial = QCheckBox(self.groupBox_eq_opciones)
        self.checkBox_permitir_parcial.setObjectName(u"checkBox_permitir_parcial")

        self.verticalLayout_eq_panel.addWidget(self.checkBox_permitir_parcial)

        self.label_nom_log = QLabel(self.groupBox_eq_opciones)
        self.label_nom_log.setObjectName(u"label_nom_log")

        self.verticalLayout_eq_panel.addWidget(self.label_nom_log)

        self.lineEdit_nom_log = QLineEdit(self.groupBox_eq_opciones)
        self.lineEdit_nom_log.setObjectName(u"lineEdit_nom_log")

        self.verticalLayout_eq_panel.addWidget(self.lineEdit_nom_log)

        self.btn_guardar_nom_log = QPushButton(self.groupBox_eq_opciones)
        self.btn_guardar_nom_log.setObjectName(u"btn_guardar_nom_log")

        self.verticalLayout_eq_panel.addWidget(self.btn_guardar_nom_log)

        self.verticalSpacer_eq2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_eq_panel.addItem(self.verticalSpacer_eq2)

        self.btn_ejecutar_querys = QPushButton(self.groupBox_eq_opciones)
        self.btn_ejecutar_querys.setObjectName(u"btn_ejecutar_querys")

        self.verticalLayout_eq_panel.addWidget(self.btn_ejecutar_querys)


        self.gridLayout_eq.addWidget(self.groupBox_eq_opciones, 0, 3, 4, 1)

        self.tabWidget.addTab(self.tab_ejecuta_querys, "")
        self.tab_exportar_tablas = QWidget()
        self.tab_exportar_tablas.setObjectName(u"tab_exportar_tablas")
        self.tabWidget.addTab(self.tab_exportar_tablas, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Herramienta de Carga de Datos", None))
        self.btn_salir.setText(QCoreApplication.translate("MainWindow", u"\u2190  Men\u00fa principal", None))
        self.label_archivo_excel.setText(QCoreApplication.translate("MainWindow", u"Proporciona la direcci\u00f3n del archivo excel que contiene los datos", None))
        self.btn_agregar.setText(QCoreApplication.translate("MainWindow", u"Agregar", None))
        self.btn_agregar_todos.setText(QCoreApplication.translate("MainWindow", u"Agregar Todos", None))
        self.btn_quitar.setText(QCoreApplication.translate("MainWindow", u"Quitar", None))
        self.btn_quitar_todos.setText(QCoreApplication.translate("MainWindow", u"Quitar Todos", None))
        self.label_tablas_disponibles.setText(QCoreApplication.translate("MainWindow", u"Tablas disponibles", None))
        self.btn_browse_archivo_excel.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_tablas_seleccionadas.setText(QCoreApplication.translate("MainWindow", u"Tablas seleccionadas", None))
        self.label_directorio_salida.setText(QCoreApplication.translate("MainWindow", u"Proporciona el directorio de salida donde se depositaran los archivos", None))
        self.btn_browse_directorio_salida.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_genera_inserts), QCoreApplication.translate("MainWindow", u"Crear Inserts", None))
        self.label_dir_querys.setText(QCoreApplication.translate("MainWindow", u"Directorio seleccionado de Querys", None))
        self.btn_browse_dir_querys.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_querys_disponibles.setText(QCoreApplication.translate("MainWindow", u"Querys Disponibles", None))
        self.label_querys_seleccionados.setText(QCoreApplication.translate("MainWindow", u"Querys Seleccionados", None))
        self.btn_eq_agregar.setText(QCoreApplication.translate("MainWindow", u"Agregar", None))
        self.btn_eq_agregar_todos.setText(QCoreApplication.translate("MainWindow", u"Agregar Todos", None))
        self.btn_eq_quitar.setText(QCoreApplication.translate("MainWindow", u"Quitar", None))
        self.btn_eq_quitar_todos.setText(QCoreApplication.translate("MainWindow", u"Quitar Todos", None))
        self.groupBox_eq_opciones.setTitle(QCoreApplication.translate("MainWindow", u"OPCIONES DE EJECUCI\u00d3N", None))
        self.btn_limpiar_config_eq.setText(QCoreApplication.translate("MainWindow", u"Limpiar configuraci\u00f3n", None))
        self.checkBox_crear_log.setText(QCoreApplication.translate("MainWindow", u"Crear Log de Operaci\u00f3n", None))
        self.checkBox_permitir_parcial.setText(QCoreApplication.translate("MainWindow", u"Permitir ejecuci\u00f3n de Operaciones v\u00e1lidas", None))
        self.label_nom_log.setText(QCoreApplication.translate("MainWindow", u"Nombre del archivo log", None))
        self.btn_guardar_nom_log.setText(QCoreApplication.translate("MainWindow", u"Guardar nombre", None))
        self.btn_ejecutar_querys.setText(QCoreApplication.translate("MainWindow", u"\u25b6   Ejecutar Querys", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ejecuta_querys), QCoreApplication.translate("MainWindow", u"Ejecutar Querys", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_exportar_tablas), QCoreApplication.translate("MainWindow", u"Exportar Tablas", None))
    # retranslateUi

