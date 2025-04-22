# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'telethon_info_boxLbXhwh.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_TelethonInfoBox(object):
    def setupUi(self, TelethonInfoBox):
        if not TelethonInfoBox.objectName():
            TelethonInfoBox.setObjectName(u"TelethonInfoBox")
        TelethonInfoBox.resize(700, 80)
        TelethonInfoBox.setMinimumSize(QSize(0, 80))
        TelethonInfoBox.setMaximumSize(QSize(16777215, 80))
        self.verticalLayout = QVBoxLayout(TelethonInfoBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.infoLabel = QLabel(TelethonInfoBox)
        self.infoLabel.setObjectName(u"infoLabel")
        self.infoLabel.setStyleSheet(u"background-color: #EBF5FB;\n"
"color: #3498DB;\n"
"border: 1px solid #BFDBFE;\n"
"border-radius: 6px;\n"
"padding: 15px;\n"
"font-size: 16px;")
        self.infoLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.infoLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.infoLabel)


        self.retranslateUi(TelethonInfoBox)

        QMetaObject.connectSlotsByName(TelethonInfoBox)
    # setupUi

    def retranslateUi(self, TelethonInfoBox):
        self.infoLabel.setText(QCoreApplication.translate("TelethonInfoBox", u"Telethon API cho ph\u00e9p t\u1ea3i l\u00ean c\u00e1c file l\u1edbn h\u01a1n 50MB. \u0110\u1ec3 s\u1eed d\u1ee5ng t\u00ednh n\u0103ng n\u00e0y,\n"
"vui l\u00f2ng ho\u00e0n t\u1ea5t c\u1ea5u h\u00ecnh v\u00e0 x\u00e1c th\u1ef1c OTP cho t\u00e0i kho\u1ea3n Telegram c\u1ee7a b\u1ea1n.", None))
        self.infoLabel.setProperty(u"class", QCoreApplication.translate("TelethonInfoBox", u"infoBox", None))
        pass
    # retranslateUi

