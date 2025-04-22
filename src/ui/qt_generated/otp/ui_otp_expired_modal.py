# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'otp_expired_modalzSNcup.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_OtpExpiredDialog(object):
    def setupUi(self, OtpExpiredDialog):
        if not OtpExpiredDialog.objectName():
            OtpExpiredDialog.setObjectName(u"OtpExpiredDialog")
        OtpExpiredDialog.resize(500, 558)
        OtpExpiredDialog.setStyleSheet(u"QDialog {\n"
"    background-color: #FFFFFF;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QLabel.titleLabel {\n"
"    font-size: 20px;\n"
"    font-weight: bold;\n"
"    color: #1E293B;\n"
"    background-color: transparent;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QLabel.messageLabel {\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"    color: #E53E3E;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QLabel.infoLabel {\n"
"    font-size: 14px;\n"
"    color: #64748B;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QLineEdit {\n"
"    border: 1px solid #E4E7EB;\n"
"    border-radius: 6px;\n"
"    padding: 10px 15px;\n"
"    background-color: #FFFFFF;\n"
"    font-size: 16px;\n"
"    color: #1E293B;\n"
"    font-family: Arial;\n"
"    height: 50px;\n"
"}\n"
"\n"
"QLineEdit.otpDigit {\n"
"    border: 1px solid #FC8181;\n"
"    border-radius: 6px;\n"
"    background-color: #FFF5F5;\n"
"    font-size: 24px;\n"
"    font-weight: bold;\n"
"    color: #E53E3E;\n"
"    text-align: center;\n"
"    font-family: Arial;\n"
""
                        "}\n"
"\n"
"QPushButton.primaryButton {\n"
"    background-color: #3498DB;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 10px 15px;\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QPushButton.primaryButton:hover {\n"
"    background-color: #2980B9;\n"
"}\n"
"\n"
"QPushButton.secondaryButton {\n"
"    background-color: #EBF5FB;\n"
"    color: #3498DB;\n"
"    border: 1px solid #BFDBFE;\n"
"    border-radius: 6px;\n"
"    padding: 10px 15px;\n"
"    font-size: 16px;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QPushButton.secondaryButton:hover {\n"
"    background-color: #D1E6FA;\n"
"}\n"
"\n"
"QFrame.statusError {\n"
"    background-color: #FFF5F5;\n"
"    border: 1px solid #FED7D7;\n"
"    border-radius: 4px;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QLabel.timerLabel {\n"
"    background-color: transparent;\n"
"    color: #E53E3E;\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"    font-family: Arial;\n"
"}")
        self.verticalLayout = QVBoxLayout(OtpExpiredDialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.headerWidget = QWidget(OtpExpiredDialog)
        self.headerWidget.setObjectName(u"headerWidget")
        self.headerWidget.setMinimumSize(QSize(0, 60))
        self.headerWidget.setMaximumSize(QSize(16777215, 60))
        self.headerWidget.setStyleSheet(u"background-color: #F9FAFB;")
        self.horizontalLayout = QHBoxLayout(self.headerWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(30, -1, 30, -1)
        self.titleLabel = QLabel(self.headerWidget)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setStyleSheet(u"font-size: 20px; font-weight: bold; color: #1E293B;")

        self.horizontalLayout.addWidget(self.titleLabel)


        self.verticalLayout.addWidget(self.headerWidget)

        self.contentWidget = QWidget(OtpExpiredDialog)
        self.contentWidget.setObjectName(u"contentWidget")
        self.verticalLayout_2 = QVBoxLayout(self.contentWidget)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(30, 20, 30, 20)
        self.messageLayout = QHBoxLayout()
        self.messageLayout.setSpacing(15)
        self.messageLayout.setObjectName(u"messageLayout")
        self.iconLabel = QLabel(self.contentWidget)
        self.iconLabel.setObjectName(u"iconLabel")
        self.iconLabel.setMinimumSize(QSize(40, 40))
        self.iconLabel.setMaximumSize(QSize(40, 40))
        self.iconLabel.setStyleSheet(u"background-color: #E53E3E;\n"
"color: white;\n"
"border-radius: 20px;\n"
"font-size: 16px;\n"
"font-weight: bold;")
        self.iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.messageLayout.addWidget(self.iconLabel)

        self.messageLabel = QLabel(self.contentWidget)
        self.messageLabel.setObjectName(u"messageLabel")
        self.messageLabel.setStyleSheet(u"font-size: 16px;\n"
"font-weight: bold;\n"
"color: #E53E3E;")

        self.messageLayout.addWidget(self.messageLabel)


        self.verticalLayout_2.addLayout(self.messageLayout)

        self.phoneLayout = QVBoxLayout()
        self.phoneLayout.setSpacing(10)
        self.phoneLayout.setObjectName(u"phoneLayout")
        self.phoneLabel = QLabel(self.contentWidget)
        self.phoneLabel.setObjectName(u"phoneLabel")
        self.phoneLabel.setStyleSheet(u"font-size: 14px; color: #64748B;")

        self.phoneLayout.addWidget(self.phoneLabel)

        self.phoneLineEdit = QLineEdit(self.contentWidget)
        self.phoneLineEdit.setObjectName(u"phoneLineEdit")
        self.phoneLineEdit.setMinimumSize(QSize(0, 45))
        self.phoneLineEdit.setMaximumSize(QSize(16777215, 45))
        self.phoneLineEdit.setStyleSheet(u"background-color: #F9FAFB;")
        self.phoneLineEdit.setReadOnly(True)

        self.phoneLayout.addWidget(self.phoneLineEdit)


        self.verticalLayout_2.addLayout(self.phoneLayout)

        self.otpLayout = QVBoxLayout()
        self.otpLayout.setSpacing(10)
        self.otpLayout.setObjectName(u"otpLayout")
        self.otpLabel = QLabel(self.contentWidget)
        self.otpLabel.setObjectName(u"otpLabel")
        self.otpLabel.setStyleSheet(u"font-size: 14px; color: #64748B;")

        self.otpLayout.addWidget(self.otpLabel)

        self.otpDigitsLayout = QHBoxLayout()
        self.otpDigitsLayout.setSpacing(10)
        self.otpDigitsLayout.setObjectName(u"otpDigitsLayout")
        self.digit1 = QLineEdit(self.contentWidget)
        self.digit1.setObjectName(u"digit1")
        self.digit1.setMinimumSize(QSize(0, 0))
        self.digit1.setMaximumSize(QSize(16777215, 16777215))
        self.digit1.setStyleSheet(u"border: 1px solid #FC8181;\n"
"border-radius: 6px;\n"
"background-color: #FFF5F5;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"color: #E53E3E;\n"
"padding: 0px;")
        self.digit1.setMaxLength(1)
        self.digit1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.digit1.setReadOnly(True)

        self.otpDigitsLayout.addWidget(self.digit1)

        self.digit2 = QLineEdit(self.contentWidget)
        self.digit2.setObjectName(u"digit2")
        self.digit2.setMinimumSize(QSize(0, 0))
        self.digit2.setMaximumSize(QSize(16777215, 16777215))
        self.digit2.setStyleSheet(u"border: 1px solid #FC8181;\n"
"border-radius: 6px;\n"
"background-color: #FFF5F5;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"color: #E53E3E;\n"
"padding: 0px;")
        self.digit2.setMaxLength(1)
        self.digit2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.digit2.setReadOnly(True)

        self.otpDigitsLayout.addWidget(self.digit2)

        self.digit3 = QLineEdit(self.contentWidget)
        self.digit3.setObjectName(u"digit3")
        self.digit3.setMinimumSize(QSize(0, 0))
        self.digit3.setMaximumSize(QSize(16777215, 16777215))
        self.digit3.setStyleSheet(u"border: 1px solid #FC8181;\n"
"border-radius: 6px;\n"
"background-color: #FFF5F5;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"color: #E53E3E;\n"
"padding: 0px;")
        self.digit3.setMaxLength(1)
        self.digit3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.digit3.setReadOnly(True)

        self.otpDigitsLayout.addWidget(self.digit3)

        self.digit4 = QLineEdit(self.contentWidget)
        self.digit4.setObjectName(u"digit4")
        self.digit4.setMinimumSize(QSize(0, 0))
        self.digit4.setMaximumSize(QSize(16777215, 16777215))
        self.digit4.setStyleSheet(u"border: 1px solid #FC8181;\n"
"border-radius: 6px;\n"
"background-color: #FFF5F5;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"color: #E53E3E;\n"
"padding: 0px;")
        self.digit4.setMaxLength(1)
        self.digit4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.digit4.setReadOnly(True)

        self.otpDigitsLayout.addWidget(self.digit4)

        self.digit5 = QLineEdit(self.contentWidget)
        self.digit5.setObjectName(u"digit5")
        self.digit5.setMinimumSize(QSize(0, 0))
        self.digit5.setMaximumSize(QSize(16777215, 16777215))
        self.digit5.setStyleSheet(u"border: 1px solid #FC8181;\n"
"border-radius: 6px;\n"
"background-color: #FFF5F5;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"color: #E53E3E;\n"
"padding: 0px;")
        self.digit5.setMaxLength(1)
        self.digit5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.digit5.setReadOnly(True)

        self.otpDigitsLayout.addWidget(self.digit5)

        self.digit6 = QLineEdit(self.contentWidget)
        self.digit6.setObjectName(u"digit6")
        self.digit6.setMinimumSize(QSize(0, 0))
        self.digit6.setMaximumSize(QSize(16777215, 16777215))
        self.digit6.setStyleSheet(u"border: 1px solid #FC8181;\n"
"border-radius: 6px;\n"
"background-color: #FFF5F5;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"color: #E53E3E;\n"
"padding: 0px;")
        self.digit6.setMaxLength(1)
        self.digit6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.digit6.setReadOnly(True)

        self.otpDigitsLayout.addWidget(self.digit6)


        self.otpLayout.addLayout(self.otpDigitsLayout)


        self.verticalLayout_2.addLayout(self.otpLayout)

        self.timerFrame = QFrame(self.contentWidget)
        self.timerFrame.setObjectName(u"timerFrame")
        self.timerFrame.setMinimumSize(QSize(0, 36))
        self.timerFrame.setMaximumSize(QSize(16777215, 36))
        self.timerFrame.setStyleSheet(u"background-color: #FFF5F5;\n"
"border: 1px solid #FED7D7;\n"
"border-radius: 4px;")
        self.timerFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.timerFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.timerFrame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(10, 0, 10, 0)
        self.timerIconLabel = QLabel(self.timerFrame)
        self.timerIconLabel.setObjectName(u"timerIconLabel")
        self.timerIconLabel.setMinimumSize(QSize(24, 24))
        self.timerIconLabel.setMaximumSize(QSize(24, 24))
        self.timerIconLabel.setStyleSheet(u"background-color: #E53E3E;\n"
"color: white;\n"
"border-radius: 12px;\n"
"font-size: 14px;\n"
"font-weight: bold;")
        self.timerIconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.timerIconLabel)

        self.timerLabel = QLabel(self.timerFrame)
        self.timerLabel.setObjectName(u"timerLabel")
        self.timerLabel.setStyleSheet(u"background-color: transparent;\n"
"color: #E53E3E;\n"
"font-weight: bold;\n"
"font-size: 16px;\n"
"border: none;")

        self.horizontalLayout_3.addWidget(self.timerLabel)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.timeLeftLabel = QLabel(self.timerFrame)
        self.timeLeftLabel.setObjectName(u"timeLeftLabel")
        self.timeLeftLabel.setStyleSheet(u"background-color: transparent;\n"
"color: #E53E3E;\n"
"font-weight: bold;\n"
"font-size: 16px;\n"
"border: none;")
        self.timeLeftLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.timeLeftLabel)


        self.verticalLayout_2.addWidget(self.timerFrame)

        self.noteLabel = QLabel(self.contentWidget)
        self.noteLabel.setObjectName(u"noteLabel")
        self.noteLabel.setStyleSheet(u"font-size: 13px; color: #64748B;")
        self.noteLabel.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.noteLabel)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.verticalLayout.addWidget(self.contentWidget)

        self.footerFrame = QFrame(OtpExpiredDialog)
        self.footerFrame.setObjectName(u"footerFrame")
        self.footerFrame.setMinimumSize(QSize(0, 70))
        self.footerFrame.setMaximumSize(QSize(16777215, 70))
        self.footerFrame.setStyleSheet(u"background-color: #F9FAFB;")
        self.footerFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.footerFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.footerFrame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(30, 10, 30, 10)
        self.cancelButton = QPushButton(self.footerFrame)
        self.cancelButton.setObjectName(u"cancelButton")
        self.cancelButton.setMinimumSize(QSize(120, 0))
        self.cancelButton.setMaximumSize(QSize(120, 16777215))
        self.cancelButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #EBF5FB;\n"
"    color: #3498DB;\n"
"    border: 1px solid #BFDBFE;\n"
"    border-radius: 6px;\n"
"    padding: 10px;\n"
"    font-size: 16px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #D1E6FA;\n"
"}")

        self.horizontalLayout_2.addWidget(self.cancelButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.getNewCodeButton = QPushButton(self.footerFrame)
        self.getNewCodeButton.setObjectName(u"getNewCodeButton")
        self.getNewCodeButton.setMinimumSize(QSize(120, 0))
        self.getNewCodeButton.setMaximumSize(QSize(120, 16777215))
        self.getNewCodeButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #3498DB;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 10px;\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2980B9;\n"
"}")

        self.horizontalLayout_2.addWidget(self.getNewCodeButton)


        self.verticalLayout.addWidget(self.footerFrame)


        self.retranslateUi(OtpExpiredDialog)

        QMetaObject.connectSlotsByName(OtpExpiredDialog)
    # setupUi

    def retranslateUi(self, OtpExpiredDialog):
        OtpExpiredDialog.setWindowTitle(QCoreApplication.translate("OtpExpiredDialog", u"X\u00e1c th\u1ef1c Telethon", None))
        self.titleLabel.setText(QCoreApplication.translate("OtpExpiredDialog", u"X\u00e1c th\u1ef1c Telethon", None))
        self.titleLabel.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"titleLabel", None))
        self.iconLabel.setText(QCoreApplication.translate("OtpExpiredDialog", u"!", None))
        self.messageLabel.setText(QCoreApplication.translate("OtpExpiredDialog", u"M\u00e3 OTP \u0111\u00e3 h\u1ebft h\u1ea1n ho\u1eb7c kh\u00f4ng h\u1ee3p l\u1ec7", None))
        self.messageLabel.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"messageLabel", None))
        self.phoneLabel.setText(QCoreApplication.translate("OtpExpiredDialog", u"S\u1ed1 \u0111i\u1ec7n tho\u1ea1i:", None))
        self.phoneLabel.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"infoLabel", None))
        self.phoneLineEdit.setText(QCoreApplication.translate("OtpExpiredDialog", u"+84123456789", None))
        self.otpLabel.setText(QCoreApplication.translate("OtpExpiredDialog", u"Nh\u1eadp m\u00e3 x\u00e1c th\u1ef1c (6 ch\u1eef s\u1ed1):", None))
        self.otpLabel.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"infoLabel", None))
        self.digit1.setText(QCoreApplication.translate("OtpExpiredDialog", u"5", None))
        self.digit1.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"otpDigit", None))
        self.digit2.setText(QCoreApplication.translate("OtpExpiredDialog", u"7", None))
        self.digit2.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"otpDigit", None))
        self.digit3.setText(QCoreApplication.translate("OtpExpiredDialog", u"3", None))
        self.digit3.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"otpDigit", None))
        self.digit4.setText(QCoreApplication.translate("OtpExpiredDialog", u"2", None))
        self.digit4.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"otpDigit", None))
        self.digit5.setText(QCoreApplication.translate("OtpExpiredDialog", u"9", None))
        self.digit5.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"otpDigit", None))
        self.digit6.setText(QCoreApplication.translate("OtpExpiredDialog", u"1", None))
        self.digit6.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"otpDigit", None))
        self.timerFrame.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"statusError", None))
        self.timerIconLabel.setText(QCoreApplication.translate("OtpExpiredDialog", u"\u23f1", None))
        self.timerLabel.setText(QCoreApplication.translate("OtpExpiredDialog", u"M\u00e3 \u0111\u00e3 h\u1ebft h\u1ea1n", None))
        self.timerLabel.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"timerLabel", None))
        self.timeLeftLabel.setText(QCoreApplication.translate("OtpExpiredDialog", u"00:00", None))
        self.timeLeftLabel.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"timerLabel", None))
        self.noteLabel.setText(QCoreApplication.translate("OtpExpiredDialog", u"Vui l\u00f2ng nh\u1ea5n \"L\u1ea5y l\u1ea1i m\u00e3\" \u0111\u1ec3 nh\u1eadn m\u00e3 x\u00e1c th\u1ef1c m\u1edbi", None))
        self.cancelButton.setText(QCoreApplication.translate("OtpExpiredDialog", u"H\u1ee7y", None))
        self.cancelButton.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"secondaryButton", None))
        self.getNewCodeButton.setText(QCoreApplication.translate("OtpExpiredDialog", u"L\u1ea5y l\u1ea1i m\u00e3", None))
        self.getNewCodeButton.setProperty(u"class", QCoreApplication.translate("OtpExpiredDialog", u"primaryButton", None))
    # retranslateUi

