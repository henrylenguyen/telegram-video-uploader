# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'telethon_verification_statusuIstxa.ui'
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

class Ui_TelethonVerificationStatus(object):
    def setupUi(self, TelethonVerificationStatus):
        if not TelethonVerificationStatus.objectName():
            TelethonVerificationStatus.setObjectName(u"TelethonVerificationStatus")
        TelethonVerificationStatus.resize(700, 60)
        TelethonVerificationStatus.setMinimumSize(QSize(0, 60))
        self.verticalLayout = QVBoxLayout(TelethonVerificationStatus)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verificationStatusLabel = QLabel(TelethonVerificationStatus)
        self.verificationStatusLabel.setObjectName(u"verificationStatusLabel")
        self.verificationStatusLabel.setMinimumSize(QSize(0, 60))
        self.verificationStatusLabel.setStyleSheet(u"background-color: #F0FFF4;\n"
"color: #2ECC71;\n"
"border: 1px solid #C6F6D5;\n"
"border-radius: 6px;\n"
"padding: 15px;\n"
"font-size: 16px;")

        self.verticalLayout.addWidget(self.verificationStatusLabel)


        self.retranslateUi(TelethonVerificationStatus)

        QMetaObject.connectSlotsByName(TelethonVerificationStatus)
    # setupUi

    def retranslateUi(self, TelethonVerificationStatus):
        self.verificationStatusLabel.setText(QCoreApplication.translate("TelethonVerificationStatus", u"\u2713 \u0110\u00e3 x\u00e1c th\u1ef1c th\u00e0nh c\u00f4ng! T\u00e0i kho\u1ea3n telegram c\u1ee7a @username", None))
        self.verificationStatusLabel.setProperty(u"class", QCoreApplication.translate("TelethonVerificationStatus", u"statusSuccess", None))
        pass
    # retranslateUi

