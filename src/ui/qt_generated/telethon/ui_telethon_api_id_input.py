# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'telethon_api_id_inputuHBMxE.ui'
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

class Ui_TelethonApiIdInput(object):
    def setupUi(self, TelethonApiIdInput):
        if not TelethonApiIdInput.objectName():
            TelethonApiIdInput.setObjectName(u"TelethonApiIdInput")
        TelethonApiIdInput.resize(700, 81)
        self.verticalLayout = QVBoxLayout(TelethonApiIdInput)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout = QHBoxLayout()
        self.headerLayout.setSpacing(10)
        self.headerLayout.setObjectName(u"headerLayout")
        self.apiIdLabel = QLabel(TelethonApiIdInput)
        self.apiIdLabel.setObjectName(u"apiIdLabel")
        self.apiIdLabel.setStyleSheet(u"font-size: 16px; font-weight: bold; color: #1E293B;")

        self.headerLayout.addWidget(self.apiIdLabel)

        self.apiIdHintLabel = QLabel(TelethonApiIdInput)
        self.apiIdHintLabel.setObjectName(u"apiIdHintLabel")
        self.apiIdHintLabel.setStyleSheet(u"font-size: 16px; color: #64748B;")

        self.headerLayout.addWidget(self.apiIdHintLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.headerLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.headerLayout)

        self.inputLayout = QHBoxLayout()
        self.inputLayout.setSpacing(0)
        self.inputLayout.setObjectName(u"inputLayout")
        self.apiIdLineEdit = QLineEdit(TelethonApiIdInput)
        self.apiIdLineEdit.setObjectName(u"apiIdLineEdit")
        self.apiIdLineEdit.setMinimumSize(QSize(0, 45))
        self.apiIdLineEdit.setMaximumSize(QSize(16777215, 45))
        self.apiIdLineEdit.setStyleSheet(u"")

        self.inputLayout.addWidget(self.apiIdLineEdit)

        self.copyApiIdButton = QPushButton(TelethonApiIdInput)
        self.copyApiIdButton.setObjectName(u"copyApiIdButton")
        self.copyApiIdButton.setMinimumSize(QSize(60, 45))
        self.copyApiIdButton.setMaximumSize(QSize(60, 45))
        self.copyApiIdButton.setStyleSheet(u"background-color: #F1F5F9;\n"
"border: 1px solid #E4E7EB;\n"
"border-left: none;\n"
"border-top-left-radius: 0px;\n"
"border-bottom-left-radius: 0px;\n"
"border-top-right-radius: 6px;\n"
"border-bottom-right-radius: 6px;\n"
"font-size: 18px;\n"
"color: #64748B;")

        self.inputLayout.addWidget(self.copyApiIdButton)


        self.verticalLayout.addLayout(self.inputLayout)


        self.retranslateUi(TelethonApiIdInput)

        QMetaObject.connectSlotsByName(TelethonApiIdInput)
    # setupUi

    def retranslateUi(self, TelethonApiIdInput):
        self.apiIdLabel.setText(QCoreApplication.translate("TelethonApiIdInput", u"API ID", None))
        self.apiIdLabel.setProperty(u"class", QCoreApplication.translate("TelethonApiIdInput", u"fieldLabel", None))
        self.apiIdHintLabel.setText(QCoreApplication.translate("TelethonApiIdInput", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: 2xxxxxx)", None))
        self.apiIdHintLabel.setProperty(u"class", QCoreApplication.translate("TelethonApiIdInput", u"fieldHint", None))
        self.apiIdLineEdit.setText(QCoreApplication.translate("TelethonApiIdInput", u"23456789", None))
        self.copyApiIdButton.setText(QCoreApplication.translate("TelethonApiIdInput", u"\ud83d\udccb", None))
        self.copyApiIdButton.setProperty(u"class", QCoreApplication.translate("TelethonApiIdInput", u"iconButton", None))
        pass
    # retranslateUi

