# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(800, 600)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.btn_creacion = QPushButton(Form)
        self.btn_creacion.setObjectName(u"btn_creacion")

        self.verticalLayout.addWidget(self.btn_creacion)

        self.btn_ejecucion = QPushButton(Form)
        self.btn_ejecucion.setObjectName(u"btn_ejecucion")

        self.verticalLayout.addWidget(self.btn_ejecucion)

        self.btn_exportacion = QPushButton(Form)
        self.btn_exportacion.setObjectName(u"btn_exportacion")

        self.verticalLayout.addWidget(self.btn_exportacion)

        self.btn_configuracion = QPushButton(Form)
        self.btn_configuracion.setObjectName(u"btn_configuracion")

        self.verticalLayout.addWidget(self.btn_configuracion)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.btn_salida = QPushButton(Form)
        self.btn_salida.setObjectName(u"btn_salida")

        self.verticalLayout.addWidget(self.btn_salida)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.btn_creacion.setText(QCoreApplication.translate("Form", u"Crear Archivos SQL de Archivo Excel", None))
        self.btn_ejecucion.setText(QCoreApplication.translate("Form", u"Ejecutar archivos SQL en la base de datos", None))
        self.btn_exportacion.setText(QCoreApplication.translate("Form", u"Obtener tablas de la base de datos a Excel", None))
        self.btn_configuracion.setText(QCoreApplication.translate("Form", u"Configuraci\u00f3n", None))
        self.btn_salida.setText(QCoreApplication.translate("Form", u"Salida", None))
    # retranslateUi

