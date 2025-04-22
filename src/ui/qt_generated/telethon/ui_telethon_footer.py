# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'telethon_footerpKuRhA.ui'
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

class Ui_TelethonFooter(object):
    def setupUi(self, TelethonFooter):
        if not TelethonFooter.objectName():
            TelethonFooter.setObjectName(u"TelethonFooter")
        TelethonFooter.resize(750, 70)
        TelethonFooter.setMinimumSize(QSize(0, 70))
        TelethonFooter.setMaximumSize(QSize(16777215, 70))
        TelethonFooter.setStyleSheet(u"background-color: #F9FAFB;")
        self.horizontalLayout = QHBoxLayout(TelethonFooter)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(40, 10, 40, 10)
        self.cancelButton = QPushButton(TelethonFooter)
        self.cancelButton.setObjectName(u"cancelButton")
        self.cancelButton.setMinimumSize(QSize(120, 50))
        self.cancelButton.setMaximumSize(QSize(120, 50))
        self.cancelButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #EBF5FB;\n"
"    color: #3498DB;\n"
"    border: 1px solid #BFDBFE;\n"
"    border-radius: 6px;\n"
"    padding: 15px;\n"
"    font-size: 16px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #D1E6FA;\n"
"}")

        self.horizontalLayout.addWidget(self.cancelButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.saveButton = QPushButton(TelethonFooter)
        self.saveButton.setObjectName(u"saveButton")
        self.saveButton.setMinimumSize(QSize(120, 50))
        self.saveButton.setMaximumSize(QSize(120, 50))
        self.saveButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #3498DB;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 15px;\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2980B9;\n"
"}")

        self.horizontalLayout.addWidget(self.saveButton)


        self.retranslateUi(TelethonFooter)

        QMetaObject.connectSlotsByName(TelethonFooter)
    # setupUi

    def retranslateUi(self, TelethonFooter):
        self.cancelButton.setText(QCoreApplication.translate("TelethonFooter", u"H\u1ee7y", None))
        self.cancelButton.setProperty(u"class", QCoreApplication.translate("TelethonFooter", u"secondaryButton", None))
        self.saveButton.setText(QCoreApplication.translate("TelethonFooter", u"L\u01b0u c\u00e0i \u0111\u1eb7t", None))
        self.saveButton.setProperty(u"class", QCoreApplication.translate("TelethonFooter", u"primaryButton", None))
        pass
    # retranslateUi

