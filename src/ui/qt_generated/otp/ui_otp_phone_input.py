# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'otp_phone_inputMQLWJb.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_OtpPhoneInput(object):
    def setupUi(self, OtpPhoneInput):
        if not OtpPhoneInput.objectName():
            OtpPhoneInput.setObjectName(u"OtpPhoneInput")
        OtpPhoneInput.resize(500, 80)
        self.verticalLayout = QVBoxLayout(OtpPhoneInput)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.phoneLabel = QLabel(OtpPhoneInput)
        self.phoneLabel.setObjectName(u"phoneLabel")
        self.phoneLabel.setStyleSheet(u"font-size: 14px; color: #64748B;")

        self.verticalLayout.addWidget(self.phoneLabel)

        self.phoneLineEdit = QLineEdit(OtpPhoneInput)
        self.phoneLineEdit.setObjectName(u"phoneLineEdit")
        self.phoneLineEdit.setMinimumSize(QSize(0, 50))
        self.phoneLineEdit.setMaximumSize(QSize(16777215, 50))
        self.phoneLineEdit.setStyleSheet(u"background-color: #F9FAFB;")
        self.phoneLineEdit.setReadOnly(True)

        self.verticalLayout.addWidget(self.phoneLineEdit)


        self.retranslateUi(OtpPhoneInput)

        QMetaObject.connectSlotsByName(OtpPhoneInput)
    # setupUi

    def retranslateUi(self, OtpPhoneInput):
        self.phoneLabel.setText(QCoreApplication.translate("OtpPhoneInput", u"S\u1ed1 \u0111i\u1ec7n tho\u1ea1i:", None))
        self.phoneLabel.setProperty(u"class", QCoreApplication.translate("OtpPhoneInput", u"infoLabel", None))
        self.phoneLineEdit.setText(QCoreApplication.translate("OtpPhoneInput", u"+84123456789", None))
        pass
    # retranslateUi

