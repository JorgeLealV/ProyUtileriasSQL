# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PanelPrincipal.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
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

        self.btn_quitar = QPushButton(self.tab_genera_inserts)
        self.btn_quitar.setObjectName(u"btn_quitar")

        self.verticalLayout_2.addWidget(self.btn_quitar)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.gridLayout.addLayout(self.verticalLayout_2, 7, 1, 1, 1)

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

        self.gridLayout.addWidget(self.listWidget_tablas_seleccionadas, 7, 2, 1, 1)

        self.lineEdit_directorio_salida = QLineEdit(self.tab_genera_inserts)
        self.lineEdit_directorio_salida.setObjectName(u"lineEdit_directorio_salida")

        self.gridLayout.addWidget(self.lineEdit_directorio_salida, 3, 0, 1, 2)

        self.btn_browse_directorio_salida = QPushButton(self.tab_genera_inserts)
        self.btn_browse_directorio_salida.setObjectName(u"btn_browse_directorio_salida")

        self.gridLayout.addWidget(self.btn_browse_directorio_salida, 3, 2, 1, 1)

        self.lineEdit_archivo_excel = QLineEdit(self.tab_genera_inserts)
        self.lineEdit_archivo_excel.setObjectName(u"lineEdit_archivo_excel")

        self.gridLayout.addWidget(self.lineEdit_archivo_excel, 1, 0, 1, 2)

        self.comboBox_hojas = QComboBox(self.tab_genera_inserts)
        self.comboBox_hojas.setObjectName(u"comboBox_hojas")
        font = QFont()
        font.setBold(True)
        self.comboBox_hojas.setFont(font)

        self.gridLayout.addWidget(self.comboBox_hojas, 5, 0, 1, 1)

        self.tabWidget.addTab(self.tab_genera_inserts, "")
        self.tab_ejecuta_querys = QWidget()
        self.tab_ejecuta_querys.setObjectName(u"tab_ejecuta_querys")
        self.tabWidget.addTab(self.tab_ejecuta_querys, "")
        self.tab_exportar_tablas = QWidget()
        self.tab_exportar_tablas.setObjectName(u"tab_exportar_tablas")
        self.tabWidget.addTab(self.tab_exportar_tablas, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.btn_salir = QPushButton(self.centralwidget)
        self.btn_salir.setObjectName(u"btn_salir")

        self.verticalLayout.addWidget(self.btn_salir)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Herramienta de Carga de Datos", None))
        self.label_archivo_excel.setText(QCoreApplication.translate("MainWindow", u"Proporciona la direcci\u00f3n del archivo excel que contiene los datos", None))
        self.btn_agregar.setText(QCoreApplication.translate("MainWindow", u"Agregar", None))
        self.btn_quitar.setText(QCoreApplication.translate("MainWindow", u"Quitar", None))
        self.label_tablas_disponibles.setText(QCoreApplication.translate("MainWindow", u"Proporciona el nombre de las tablas que requieras crear sus inserts", None))
        self.btn_browse_archivo_excel.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_tablas_seleccionadas.setText(QCoreApplication.translate("MainWindow", u"Tablas seleccionadas", None))
        self.label_directorio_salida.setText(QCoreApplication.translate("MainWindow", u"Proporciona el directorio de salida donde se depositaran los archivos", None))
        self.btn_browse_directorio_salida.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.comboBox_hojas.setStyleSheet(QCoreApplication.translate("MainWindow", u"\n"
"            background-color: #36454F;\n"
"            color: white;\n"
"           ", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_genera_inserts), QCoreApplication.translate("MainWindow", u"Genera Inserts", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ejecuta_querys), QCoreApplication.translate("MainWindow", u"Ejecuta Querys", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_exportar_tablas), QCoreApplication.translate("MainWindow", u"Exportar Tablas", None))
        self.btn_salir.setText(QCoreApplication.translate("MainWindow", u"Salida", None))
    # retranslateUi

