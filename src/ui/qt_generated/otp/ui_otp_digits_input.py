# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'otp_digits_inputIoIFox.ui'
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
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_OtpDigitsInput(object):
    def setupUi(self, OtpDigitsInput):
        if not OtpDigitsInput.objectName():
            OtpDigitsInput.setObjectName(u"OtpDigitsInput")
        OtpDigitsInput.resize(500, 91)
        self.verticalLayout = QVBoxLayout(OtpDigitsInput)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.otpLabel = QLabel(OtpDigitsInput)
        self.otpLabel.setObjectName(u"otpLabel")
        self.otpLabel.setStyleSheet(u"font-size: 14px; color: #64748B;")

        self.verticalLayout.addWidget(self.otpLabel)

        self.otpDigitsLayout = QHBoxLayout()
        self.otpDigitsLayout.setSpacing(10)
        self.otpDigitsLayout.setObjectName(u"otpDigitsLayout")
        self.digit1 = QLineEdit(OtpDigitsInput)
        self.digit1.setObjectName(u"digit1")
        self.digit1.setMinimumSize(QSize(60, 60))
        self.digit1.setMaximumSize(QSize(60, 60))
        self.digit1.setStyleSheet(u"border: 1px solid #CBD5E1;\n"
"border-radius: 6px;\n"
"background-color: #F9FAFB;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"color: #1E293B;\n"
"padding: 0px;")
        self.digit1.setMaxLength(1)
        self.digit1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.otpDigitsLayout.addWidget(self.digit1)

        self.digit2 = QLineEdit(OtpDigitsInput)
        self.digit2.setObjectName(u"digit2")
        self.digit2.setMinimumSize(QSize(60, 60))
        self.digit2.setMaximumSize(QSize(60, 60))
        self.digit2.setStyleSheet(u"border: 1px solid #CBD5E1;\n"
"border-radius: 6px;\n"
"background-color: #F9FAFB;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"color: #1E293B;\n"
"padding: 0px;")
        self.digit2.setMaxLength(1)
        self.digit2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.otpDigitsLayout.addWidget(self.digit2)

        self.digit3 = QLineEdit(OtpDigitsInput)
        self.digit3.setObjectName(u"digit3")
        self.digit3.setMinimumSize(QSize(60, 60))
        self.digit3.setMaximumSize(QSize(60, 60))
        self.digit3.setStyleSheet(u"border: 1px solid #CBD5E1;\n"
"border-radius: 6px;\n"
"background-color: #F9FAFB;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"color: #1E293B;\n"
"padding: 0px;")
        self.digit3.setMaxLength(1)
        self.digit3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.otpDigitsLayout.addWidget(self.digit3)

        self.digit4 = QLineEdit(OtpDigitsInput)
        self.digit4.setObjectName(u"digit4")
        self.digit4.setMinimumSize(QSize(60, 60))
        self.digit4.setMaximumSize(QSize(60, 60))
        self.digit4.setStyleSheet(u"border: 1px solid #CBD5E1;\n"
"border-radius: 6px;\n"
"background-color: #F9FAFB;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"color: #1E293B;\n"
"padding: 0px;")
        self.digit4.setMaxLength(1)
        self.digit4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.otpDigitsLayout.addWidget(self.digit4)

        self.digit5 = QLineEdit(OtpDigitsInput)
        self.digit5.setObjectName(u"digit5")
        self.digit5.setMinimumSize(QSize(60, 60))
        self.digit5.setMaximumSize(QSize(60, 60))
        self.digit5.setStyleSheet(u"border: 1px solid #CBD5E1;\n"
"border-radius: 6px;\n"
"background-color: #F9FAFB;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"color: #1E293B;\n"
"padding: 0px;")
        self.digit5.setMaxLength(1)
        self.digit5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.otpDigitsLayout.addWidget(self.digit5)

        self.digit6 = QLineEdit(OtpDigitsInput)
        self.digit6.setObjectName(u"digit6")
        self.digit6.setMinimumSize(QSize(60, 60))
        self.digit6.setMaximumSize(QSize(60, 60))
        self.digit6.setStyleSheet(u"border: 1px solid #CBD5E1;\n"
"border-radius: 6px;\n"
"background-color: #F9FAFB;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"color: #1E293B;\n"
"padding: 0px;")
        self.digit6.setMaxLength(1)
        self.digit6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.otpDigitsLayout.addWidget(self.digit6)


        self.verticalLayout.addLayout(self.otpDigitsLayout)


        self.retranslateUi(OtpDigitsInput)

        QMetaObject.connectSlotsByName(OtpDigitsInput)
    # setupUi

    def retranslateUi(self, OtpDigitsInput):
        self.otpLabel.setText(QCoreApplication.translate("OtpDigitsInput", u"Nh\u1eadp m\u00e3 x\u00e1c th\u1ef1c (6 ch\u1eef s\u1ed1):", None))
        self.otpLabel.setProperty(u"class", QCoreApplication.translate("OtpDigitsInput", u"infoLabel", None))
        self.digit1.setProperty(u"class", QCoreApplication.translate("OtpDigitsInput", u"otpDigit", None))
        self.digit2.setProperty(u"class", QCoreApplication.translate("OtpDigitsInput", u"otpDigit", None))
        self.digit3.setProperty(u"class", QCoreApplication.translate("OtpDigitsInput", u"otpDigit", None))
        self.digit4.setProperty(u"class", QCoreApplication.translate("OtpDigitsInput", u"otpDigit", None))
        self.digit5.setProperty(u"class", QCoreApplication.translate("OtpDigitsInput", u"otpDigit", None))
        self.digit6.setProperty(u"class", QCoreApplication.translate("OtpDigitsInput", u"otpDigit", None))
        pass
    # retranslateUi

