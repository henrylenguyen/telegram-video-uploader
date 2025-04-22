# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'config_telethon_tabEfesTc.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_ConfigTelethonTab(object):
    def setupUi(self, ConfigTelethonTab):
        if not ConfigTelethonTab.objectName():
            ConfigTelethonTab.setObjectName(u"ConfigTelethonTab")
        ConfigTelethonTab.resize(650, 479)
        self.verticalLayout = QVBoxLayout(ConfigTelethonTab)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(20, 15, 20, 15)
        self.telethonInfoLabel = QLabel(ConfigTelethonTab)
        self.telethonInfoLabel.setObjectName(u"telethonInfoLabel")
        self.telethonInfoLabel.setMinimumSize(QSize(0, 60))
        self.telethonInfoLabel.setMaximumSize(QSize(16777215, 60))
        self.telethonInfoLabel.setStyleSheet(u"background-color: #EBF5FB;\n"
"color: #3498DB;\n"
"border: 1px solid #BFDBFE;\n"
"border-radius: 6px;\n"
"padding: 8px;\n"
"font-size: 13px;")
        self.telethonInfoLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.telethonInfoLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.telethonInfoLabel)

        self.apiIdContainer = QWidget(ConfigTelethonTab)
        self.apiIdContainer.setObjectName(u"apiIdContainer")
        self.apiIdLayout = QVBoxLayout(self.apiIdContainer)
        self.apiIdLayout.setSpacing(5)
        self.apiIdLayout.setObjectName(u"apiIdLayout")
        self.apiIdLayout.setContentsMargins(0, 0, 0, 0)
        self.apiIdHeaderLayout = QHBoxLayout()
        self.apiIdHeaderLayout.setObjectName(u"apiIdHeaderLayout")
        self.apiIdLabel = QLabel(self.apiIdContainer)
        self.apiIdLabel.setObjectName(u"apiIdLabel")
        self.apiIdLabel.setStyleSheet(u"font-size: 14px; font-weight: bold; color: #1E293B;")

        self.apiIdHeaderLayout.addWidget(self.apiIdLabel)

        self.apiIdHintLabel = QLabel(self.apiIdContainer)
        self.apiIdHintLabel.setObjectName(u"apiIdHintLabel")
        self.apiIdHintLabel.setStyleSheet(u"font-size: 13px; color: #64748B;")

        self.apiIdHeaderLayout.addWidget(self.apiIdHintLabel)

        self.apiIdHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.apiIdHeaderLayout.addItem(self.apiIdHeaderSpacer)


        self.apiIdLayout.addLayout(self.apiIdHeaderLayout)

        self.apiIdLineEdit = QLineEdit(self.apiIdContainer)
        self.apiIdLineEdit.setObjectName(u"apiIdLineEdit")
        self.apiIdLineEdit.setMinimumSize(QSize(0, 45))
        self.apiIdLineEdit.setMaximumSize(QSize(16777215, 45))
        self.apiIdLineEdit.setStyleSheet(u"")

        self.apiIdLayout.addWidget(self.apiIdLineEdit)


        self.verticalLayout.addWidget(self.apiIdContainer)

        self.apiHashContainer = QWidget(ConfigTelethonTab)
        self.apiHashContainer.setObjectName(u"apiHashContainer")
        self.apiHashLayout = QVBoxLayout(self.apiHashContainer)
        self.apiHashLayout.setSpacing(5)
        self.apiHashLayout.setObjectName(u"apiHashLayout")
        self.apiHashLayout.setContentsMargins(0, 0, 0, 0)
        self.apiHashHeaderLayout = QHBoxLayout()
        self.apiHashHeaderLayout.setObjectName(u"apiHashHeaderLayout")
        self.apiHashLabel = QLabel(self.apiHashContainer)
        self.apiHashLabel.setObjectName(u"apiHashLabel")
        self.apiHashLabel.setStyleSheet(u"font-size: 14px; font-weight: bold; color: #1E293B;")

        self.apiHashHeaderLayout.addWidget(self.apiHashLabel)

        self.apiHashHintLabel = QLabel(self.apiHashContainer)
        self.apiHashHintLabel.setObjectName(u"apiHashHintLabel")
        self.apiHashHintLabel.setStyleSheet(u"font-size: 13px; color: #64748B;")

        self.apiHashHeaderLayout.addWidget(self.apiHashHintLabel)

        self.apiHashHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.apiHashHeaderLayout.addItem(self.apiHashHeaderSpacer)


        self.apiHashLayout.addLayout(self.apiHashHeaderLayout)

        self.apiHashInputLayout = QHBoxLayout()
        self.apiHashInputLayout.setSpacing(0)
        self.apiHashInputLayout.setObjectName(u"apiHashInputLayout")
        self.apiHashLineEdit = QLineEdit(self.apiHashContainer)
        self.apiHashLineEdit.setObjectName(u"apiHashLineEdit")
        self.apiHashLineEdit.setMinimumSize(QSize(0, 45))
        self.apiHashLineEdit.setMaximumSize(QSize(16777215, 45))
        self.apiHashLineEdit.setStyleSheet(u"border-top-right-radius: 0px;\n"
"border-bottom-right-radius: 0px;")
        self.apiHashLineEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.apiHashInputLayout.addWidget(self.apiHashLineEdit)

        self.togglePasswordButton = QPushButton(self.apiHashContainer)
        self.togglePasswordButton.setObjectName(u"togglePasswordButton")
        self.togglePasswordButton.setMinimumSize(QSize(40, 45))
        self.togglePasswordButton.setMaximumSize(QSize(40, 45))
        self.togglePasswordButton.setStyleSheet(u"background-color: #F1F5F9;\n"
"border: 1px solid #E4E7EB;\n"
"border-left: none;\n"
"border-top-left-radius: 0px;\n"
"border-bottom-left-radius: 0px;\n"
"border-top-right-radius: 6px;\n"
"border-bottom-right-radius: 6px;")

        self.apiHashInputLayout.addWidget(self.togglePasswordButton)


        self.apiHashLayout.addLayout(self.apiHashInputLayout)


        self.verticalLayout.addWidget(self.apiHashContainer)

        self.phoneContainer = QWidget(ConfigTelethonTab)
        self.phoneContainer.setObjectName(u"phoneContainer")
        self.phoneLayout = QVBoxLayout(self.phoneContainer)
        self.phoneLayout.setSpacing(5)
        self.phoneLayout.setObjectName(u"phoneLayout")
        self.phoneLayout.setContentsMargins(0, 0, 0, 0)
        self.phoneHeaderLayout = QHBoxLayout()
        self.phoneHeaderLayout.setObjectName(u"phoneHeaderLayout")
        self.phoneLabel = QLabel(self.phoneContainer)
        self.phoneLabel.setObjectName(u"phoneLabel")
        self.phoneLabel.setStyleSheet(u"font-size: 14px; font-weight: bold; color: #1E293B;")

        self.phoneHeaderLayout.addWidget(self.phoneLabel)

        self.phoneHintLabel = QLabel(self.phoneContainer)
        self.phoneHintLabel.setObjectName(u"phoneHintLabel")
        self.phoneHintLabel.setStyleSheet(u"font-size: 13px; color: #64748B;")

        self.phoneHeaderLayout.addWidget(self.phoneHintLabel)

        self.phoneHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.phoneHeaderLayout.addItem(self.phoneHeaderSpacer)


        self.phoneLayout.addLayout(self.phoneHeaderLayout)

        self.phoneLineEdit = QLineEdit(self.phoneContainer)
        self.phoneLineEdit.setObjectName(u"phoneLineEdit")
        self.phoneLineEdit.setMinimumSize(QSize(0, 45))
        self.phoneLineEdit.setMaximumSize(QSize(16777215, 45))

        self.phoneLayout.addWidget(self.phoneLineEdit)


        self.verticalLayout.addWidget(self.phoneContainer)

        self.separator = QFrame(ConfigTelethonTab)
        self.separator.setObjectName(u"separator")
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.separator)

        self.otpStatusLayout = QHBoxLayout()
        self.otpStatusLayout.setSpacing(10)
        self.otpStatusLayout.setObjectName(u"otpStatusLayout")
        self.otpStatusLabel = QLabel(ConfigTelethonTab)
        self.otpStatusLabel.setObjectName(u"otpStatusLabel")
        self.otpStatusLabel.setMinimumSize(QSize(0, 36))
        self.otpStatusLabel.setMaximumSize(QSize(16777215, 36))
        self.otpStatusLabel.setStyleSheet(u"background-color: #FFF5F5;\n"
"color: #E53E3E;\n"
"border: 1px solid #FED7D7;\n"
"border-radius: 6px;\n"
"padding: 8px;\n"
"font-size: 13px;")

        self.otpStatusLayout.addWidget(self.otpStatusLabel)

        self.getOtpButton = QPushButton(ConfigTelethonTab)
        self.getOtpButton.setObjectName(u"getOtpButton")
        self.getOtpButton.setMinimumSize(QSize(150, 36))
        self.getOtpButton.setMaximumSize(QSize(150, 36))
        self.getOtpButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #3498DB;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 8px;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2980B9;\n"
"}")

        self.otpStatusLayout.addWidget(self.getOtpButton)


        self.verticalLayout.addLayout(self.otpStatusLayout)

        self.apiHelpLabel = QLabel(ConfigTelethonTab)
        self.apiHelpLabel.setObjectName(u"apiHelpLabel")
        self.apiHelpLabel.setStyleSheet(u"color: #3498DB; font-size: 13px; text-decoration: underline;")
        self.apiHelpLabel.setTextFormat(Qt.TextFormat.RichText)
        self.apiHelpLabel.setOpenExternalLinks(False)

        self.verticalLayout.addWidget(self.apiHelpLabel)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(ConfigTelethonTab)

        QMetaObject.connectSlotsByName(ConfigTelethonTab)
    # setupUi

    def retranslateUi(self, ConfigTelethonTab):
        self.telethonInfoLabel.setText(QCoreApplication.translate("ConfigTelethonTab", u"Telethon API cho ph\u00e9p t\u1ea3i l\u00ean c\u00e1c file l\u1edbn h\u01a1n 50MB. \u0110\u1ec3 s\u1eed d\u1ee5ng t\u00ednh n\u0103ng n\u00e0y,\n"
"vui l\u00f2ng \u0111\u0103ng k\u00fd v\u00e0 nh\u1eadp API ID, API Hash t\u1eeb my.telegram.org.", None))
        self.apiIdLabel.setText(QCoreApplication.translate("ConfigTelethonTab", u"API ID", None))
        self.apiIdHintLabel.setText(QCoreApplication.translate("ConfigTelethonTab", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: 2xxxxxx)", None))
        self.apiIdLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigTelethonTab", u"Nh\u1eadp API ID (v\u00ed d\u1ee5: 2xxxxxx)", None))
        self.apiHashLabel.setText(QCoreApplication.translate("ConfigTelethonTab", u"API Hash", None))
        self.apiHashHintLabel.setText(QCoreApplication.translate("ConfigTelethonTab", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: 7xxxxe)", None))
        self.apiHashLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigTelethonTab", u"Nh\u1eadp API Hash (v\u00ed d\u1ee5: 7xxxxe)", None))
        self.togglePasswordButton.setText(QCoreApplication.translate("ConfigTelethonTab", u"\ud83d\udc41\ufe0f", None))
        self.phoneLabel.setText(QCoreApplication.translate("ConfigTelethonTab", u"S\u1ed1 \u0111i\u1ec7n tho\u1ea1i", None))
        self.phoneHintLabel.setText(QCoreApplication.translate("ConfigTelethonTab", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: +84123456789)", None))
        self.phoneLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigTelethonTab", u"+84123456789", None))
        self.separator.setProperty(u"class", QCoreApplication.translate("ConfigTelethonTab", u"separator", None))
        self.otpStatusLabel.setText(QCoreApplication.translate("ConfigTelethonTab", u"\u26a0 Ch\u01b0a x\u00e1c th\u1ef1c! C\u1ea7n x\u00e1c th\u1ef1c OTP", None))
        self.getOtpButton.setText(QCoreApplication.translate("ConfigTelethonTab", u"L\u1ea5y m\u00e3 x\u00e1c th\u1ef1c", None))
        self.getOtpButton.setProperty(u"class", QCoreApplication.translate("ConfigTelethonTab", u"primaryButton", None))
        self.apiHelpLabel.setText(QCoreApplication.translate("ConfigTelethonTab", u"<a href=\"#\" style=\"color: #3498DB;\">L\u00e0m th\u1ebf n\u00e0o \u0111\u1ec3 l\u1ea5y API ID v\u00e0 Hash?</a>", None))
        pass
    # retranslateUi

