# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'telethon_api_hash_inputfOKAne.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_TelethonApiHashInput(object):
    def setupUi(self, TelethonApiHashInput):
        if not TelethonApiHashInput.objectName():
            TelethonApiHashInput.setObjectName(u"TelethonApiHashInput")
        TelethonApiHashInput.resize(700, 81)
        self.verticalLayout = QVBoxLayout(TelethonApiHashInput)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout = QHBoxLayout()
        self.headerLayout.setSpacing(10)
        self.headerLayout.setObjectName(u"headerLayout")
        self.apiHashLabel = QLabel(TelethonApiHashInput)
        self.apiHashLabel.setObjectName(u"apiHashLabel")
        self.apiHashLabel.setStyleSheet(u"font-size: 16px; font-weight: bold; color: #1E293B;")

        self.headerLayout.addWidget(self.apiHashLabel)

        self.apiHashHintLabel = QLabel(TelethonApiHashInput)
        self.apiHashHintLabel.setObjectName(u"apiHashHintLabel")
        self.apiHashHintLabel.setStyleSheet(u"font-size: 16px; color: #64748B;")

        self.headerLayout.addWidget(self.apiHashHintLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.headerLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.headerLayout)

        self.inputLayout = QHBoxLayout()
        self.inputLayout.setSpacing(0)
        self.inputLayout.setObjectName(u"inputLayout")
        self.apiHashLineEdit = QLineEdit(TelethonApiHashInput)
        self.apiHashLineEdit.setObjectName(u"apiHashLineEdit")
        self.apiHashLineEdit.setMinimumSize(QSize(0, 45))
        self.apiHashLineEdit.setMaximumSize(QSize(16777215, 45))
        self.apiHashLineEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.inputLayout.addWidget(self.apiHashLineEdit)

        self.togglePasswordButton = QPushButton(TelethonApiHashInput)
        self.togglePasswordButton.setObjectName(u"togglePasswordButton")
        self.togglePasswordButton.setMinimumSize(QSize(60, 45))
        self.togglePasswordButton.setMaximumSize(QSize(45, 16777215))
        self.togglePasswordButton.setStyleSheet(u"background-color: #F1F5F9;\n"
"border: 1px solid #E4E7EB;\n"
"border-left: none;\n"
"border-top-left-radius: 0px;\n"
"border-bottom-left-radius: 0px;\n"
"border-top-right-radius: 6px;\n"
"border-bottom-right-radius: 6px;\n"
"font-size: 18px;\n"
"color: #64748B;")

        self.inputLayout.addWidget(self.togglePasswordButton)


        self.verticalLayout.addLayout(self.inputLayout)


        self.retranslateUi(TelethonApiHashInput)

        QMetaObject.connectSlotsByName(TelethonApiHashInput)
    # setupUi

    def retranslateUi(self, TelethonApiHashInput):
        self.apiHashLabel.setText(QCoreApplication.translate("TelethonApiHashInput", u"API Hash", None))
        self.apiHashLabel.setProperty(u"class", QCoreApplication.translate("TelethonApiHashInput", u"fieldLabel", None))
        self.apiHashHintLabel.setText(QCoreApplication.translate("TelethonApiHashInput", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: 7xxxxe)", None))
        self.apiHashHintLabel.setProperty(u"class", QCoreApplication.translate("TelethonApiHashInput", u"fieldHint", None))
        self.apiHashLineEdit.setText(QCoreApplication.translate("TelethonApiHashInput", u"\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", None))
        self.togglePasswordButton.setText(QCoreApplication.translate("TelethonApiHashInput", u"\ud83d\udc41\ufe0f", None))
        self.togglePasswordButton.setProperty(u"class", QCoreApplication.translate("TelethonApiHashInput", u"iconButton", None))
        pass
    # retranslateUi

