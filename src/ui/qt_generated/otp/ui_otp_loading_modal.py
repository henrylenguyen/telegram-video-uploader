# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'otp_loading_modaldmUjmO.ui'
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
    QLabel, QLineEdit, QProgressBar, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_OtpLoadingDialog(object):
    def setupUi(self, OtpLoadingDialog):
        if not OtpLoadingDialog.objectName():
            OtpLoadingDialog.setObjectName(u"OtpLoadingDialog")
        OtpLoadingDialog.resize(500, 459)
        OtpLoadingDialog.setStyleSheet(u"QDialog {\n"
"    background-color: #FFFFFF;\n"
"}\n"
"\n"
"QLabel.titleLabel {\n"
"    font-size: 20px;\n"
"    font-weight: bold;\n"
"    color: #1E293B;\n"
"    background-color: transparent;\n"
"}\n"
"\n"
"QLabel.messageLabel {\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"    color: #3498DB;\n"
"}\n"
"\n"
"QLabel.infoLabel {\n"
"    font-size: 14px;\n"
"    color: #64748B;\n"
"}\n"
"\n"
"QLineEdit {\n"
"    border: 1px solid #E4E7EB;\n"
"    border-radius: 6px;\n"
"    padding: 15px;\n"
"    background-color: #FFFFFF;\n"
"    font-size: 16px;\n"
"    color: #1E293B;\n"
"}\n"
"\n"
"QPushButton.primaryButton {\n"
"    background-color: #3498DB;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 15px;\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton.primaryButton:hover {\n"
"    background-color: #2980B9;\n"
"}\n"
"\n"
"QPushButton.secondaryButton {\n"
"    background-color: #EBF5FB;\n"
"    color: #3498DB;\n"
"    border: 1px soli"
                        "d #BFDBFE;\n"
"    border-radius: 6px;\n"
"    padding: 15px;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"QPushButton.secondaryButton:hover {\n"
"    background-color: #D1E6FA;\n"
"}\n"
"\n"
"QPushButton.disabledButton {\n"
"    background-color: #CBD5E1;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 15px;\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QFrame.statusInfo {\n"
"    background-color: #EBF8FF;\n"
"    border: 1px solid #BEE3F8;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"QFrame.otpDigitFrame {\n"
"    background-color: #F9FAFB;\n"
"    border: 1px solid #CBD5E1;\n"
"    border-radius: 4px;\n"
"}")
        self.verticalLayout = QVBoxLayout(OtpLoadingDialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.headerWidget = QWidget(OtpLoadingDialog)
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

        self.contentWidget = QWidget(OtpLoadingDialog)
        self.contentWidget.setObjectName(u"contentWidget")
        self.verticalLayout_2 = QVBoxLayout(self.contentWidget)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(30, 20, 30, 20)
        self.messageLayout = QHBoxLayout()
        self.messageLayout.setSpacing(15)
        self.messageLayout.setObjectName(u"messageLayout")
        self.loadingIconLabel = QLabel(self.contentWidget)
        self.loadingIconLabel.setObjectName(u"loadingIconLabel")
        self.loadingIconLabel.setMinimumSize(QSize(30, 30))
        self.loadingIconLabel.setMaximumSize(QSize(30, 30))
        self.loadingIconLabel.setStyleSheet(u"background-color: #3498DB;\n"
"color: white;\n"
"border-radius: 15px;\n"
"font-size: 14px;\n"
"font-weight: bold;")
        self.loadingIconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.messageLayout.addWidget(self.loadingIconLabel)

        self.messageLabel = QLabel(self.contentWidget)
        self.messageLabel.setObjectName(u"messageLabel")
        self.messageLabel.setStyleSheet(u"font-size: 16px;\n"
"font-weight: bold;\n"
"color: #3498DB;")

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
        self.phoneLineEdit.setMinimumSize(QSize(0, 50))
        self.phoneLineEdit.setMaximumSize(QSize(16777215, 50))
        self.phoneLineEdit.setStyleSheet(u"background-color: #F9FAFB;")
        self.phoneLineEdit.setReadOnly(True)

        self.phoneLayout.addWidget(self.phoneLineEdit)


        self.verticalLayout_2.addLayout(self.phoneLayout)

        self.progressBar = QProgressBar(self.contentWidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
"    border: none;\n"
"    background-color: #E2E8F0;\n"
"    height: 8px;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #3498DB;\n"
"    border-radius: 4px;\n"
"}")
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(-1)
        self.progressBar.setTextVisible(False)
        self.progressBar.setOrientation(Qt.Orientation.Horizontal)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setTextDirection(QProgressBar.Direction.TopToBottom)

        self.verticalLayout_2.addWidget(self.progressBar)

        self.instructionLabel = QLabel(self.contentWidget)
        self.instructionLabel.setObjectName(u"instructionLabel")
        self.instructionLabel.setStyleSheet(u"font-size: 15px; color: #1E293B; margin-top: 10px;")
        self.instructionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instructionLabel.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.instructionLabel)

        self.noteLabel = QLabel(self.contentWidget)
        self.noteLabel.setObjectName(u"noteLabel")
        self.noteLabel.setStyleSheet(u"font-size: 12px; color: #64748B;")
        self.noteLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.noteLabel.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.noteLabel)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.verticalLayout.addWidget(self.contentWidget)

        self.footerFrame = QFrame(OtpLoadingDialog)
        self.footerFrame.setObjectName(u"footerFrame")
        self.footerFrame.setMinimumSize(QSize(0, 60))
        self.footerFrame.setMaximumSize(QSize(16777215, 60))
        self.footerFrame.setStyleSheet(u"background-color: #F9FAFB;")
        self.footerFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.footerFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.footerFrame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(30, 10, 30, 10)
        self.cancelButton = QPushButton(self.footerFrame)
        self.cancelButton.setObjectName(u"cancelButton")
        self.cancelButton.setMinimumSize(QSize(120, 0))
        self.cancelButton.setMaximumSize(QSize(16777215, 45))
        self.cancelButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #EBF5FB;\n"
"    color: #3498DB;\n"
"    border: 1px solid #BFDBFE;\n"
"    border-radius: 6px;\n"
"    padding: 10px;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #D1E6FA;\n"
"}")

        self.horizontalLayout_2.addWidget(self.cancelButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.verifyButton = QPushButton(self.footerFrame)
        self.verifyButton.setObjectName(u"verifyButton")
        self.verifyButton.setEnabled(False)
        self.verifyButton.setMinimumSize(QSize(120, 0))
        self.verifyButton.setMaximumSize(QSize(16777215, 45))
        self.verifyButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #CBD5E1;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 10px;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #CBD5E1;\n"
"}")

        self.horizontalLayout_2.addWidget(self.verifyButton)


        self.verticalLayout.addWidget(self.footerFrame)


        self.retranslateUi(OtpLoadingDialog)

        QMetaObject.connectSlotsByName(OtpLoadingDialog)
    # setupUi

    def retranslateUi(self, OtpLoadingDialog):
        OtpLoadingDialog.setWindowTitle(QCoreApplication.translate("OtpLoadingDialog", u"X\u00e1c th\u1ef1c Telethon", None))
        self.titleLabel.setText(QCoreApplication.translate("OtpLoadingDialog", u"X\u00e1c th\u1ef1c Telethon", None))
        self.titleLabel.setProperty(u"class", QCoreApplication.translate("OtpLoadingDialog", u"titleLabel", None))
        self.loadingIconLabel.setText(QCoreApplication.translate("OtpLoadingDialog", u"\u231b", None))
        self.messageLabel.setText(QCoreApplication.translate("OtpLoadingDialog", u"\u0110ang g\u1eedi m\u00e3 x\u00e1c th\u1ef1c \u0111\u1ebfn Telegram c\u1ee7a b\u1ea1n...", None))
        self.messageLabel.setProperty(u"class", QCoreApplication.translate("OtpLoadingDialog", u"messageLabel", None))
        self.phoneLabel.setText(QCoreApplication.translate("OtpLoadingDialog", u"S\u1ed1 \u0111i\u1ec7n tho\u1ea1i:", None))
        self.phoneLabel.setProperty(u"class", QCoreApplication.translate("OtpLoadingDialog", u"infoLabel", None))
        self.phoneLineEdit.setText(QCoreApplication.translate("OtpLoadingDialog", u"+84123456789", None))
        self.progressBar.setFormat(QCoreApplication.translate("OtpLoadingDialog", u"%v/%m", None))
        self.instructionLabel.setText(QCoreApplication.translate("OtpLoadingDialog", u"Vui l\u00f2ng \u0111\u1ee3i trong khi ch\u00fang t\u00f4i g\u1eedi m\u00e3 x\u00e1c th\u1ef1c \u0111\u1ebfn t\u00e0i kho\u1ea3n Telegram c\u1ee7a b\u1ea1n.", None))
        self.noteLabel.setText(QCoreApplication.translate("OtpLoadingDialog", u"Qu\u00e1 tr\u00ecnh n\u00e0y th\u01b0\u1eddng m\u1ea5t v\u00e0i gi\u00e2y. Sau khi nh\u1eadn \u0111\u01b0\u1ee3c m\u00e3 OTP, vui l\u00f2ng nh\u1eadp v\u00e0o m\u00e0n h\u00ecnh ti\u1ebfp theo \u0111\u1ec3 ho\u00e0n t\u1ea5t x\u00e1c th\u1ef1c.", None))
        self.cancelButton.setText(QCoreApplication.translate("OtpLoadingDialog", u"H\u1ee7y", None))
        self.cancelButton.setProperty(u"class", QCoreApplication.translate("OtpLoadingDialog", u"secondaryButton", None))
        self.verifyButton.setText(QCoreApplication.translate("OtpLoadingDialog", u"\u0110ang x\u1eed l\u00fd...", None))
        self.verifyButton.setProperty(u"class", QCoreApplication.translate("OtpLoadingDialog", u"disabledButton", None))
    # retranslateUi

