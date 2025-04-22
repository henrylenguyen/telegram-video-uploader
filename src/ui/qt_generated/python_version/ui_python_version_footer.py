# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'python_version_footerrRimSP.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QPushButton, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_PythonVersionFooter(object):
    def setupUi(self, PythonVersionFooter):
        if not PythonVersionFooter.objectName():
            PythonVersionFooter.setObjectName(u"PythonVersionFooter")
        PythonVersionFooter.resize(700, 50)
        self.bottomButtonsLayout = QHBoxLayout(PythonVersionFooter)
        self.bottomButtonsLayout.setObjectName(u"bottomButtonsLayout")
        self.bottomButtonsLayout.setContentsMargins(40, 5, 40, 5)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.bottomButtonsLayout.addItem(self.horizontalSpacer)

        self.exitButton = QPushButton(PythonVersionFooter)
        self.exitButton.setObjectName(u"exitButton")
        self.exitButton.setMinimumSize(QSize(150, 35))
        self.exitButton.setMaximumSize(QSize(150, 35))
        self.exitButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #FFFFFF;\n"
"    color: #64748B;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 4px;\n"
"    padding: 10px 15px;\n"
"    font-size: 13px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #F1F5F9;\n"
"}")

        self.bottomButtonsLayout.addWidget(self.exitButton)

        self.continueButton = QPushButton(PythonVersionFooter)
        self.continueButton.setObjectName(u"continueButton")
        self.continueButton.setMinimumSize(QSize(150, 35))
        self.continueButton.setMaximumSize(QSize(150, 35))
        self.continueButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #F8F9FA;\n"
"    color: #3498DB;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 4px;\n"
"    padding: 10px 15px;\n"
"    font-size: 13px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #EBF5FB;\n"
"}")

        self.bottomButtonsLayout.addWidget(self.continueButton)


        self.retranslateUi(PythonVersionFooter)

        QMetaObject.connectSlotsByName(PythonVersionFooter)
    # setupUi

    def retranslateUi(self, PythonVersionFooter):
        self.exitButton.setText(QCoreApplication.translate("PythonVersionFooter", u"Tho\u00e1t", None))
        self.exitButton.setProperty(u"class", QCoreApplication.translate("PythonVersionFooter", u"outlineButton", None))
        self.continueButton.setText(QCoreApplication.translate("PythonVersionFooter", u"Ti\u1ebfp t\u1ee5c", None))
        self.continueButton.setProperty(u"class", QCoreApplication.translate("PythonVersionFooter", u"linkButton", None))
        pass
    # retranslateUi

