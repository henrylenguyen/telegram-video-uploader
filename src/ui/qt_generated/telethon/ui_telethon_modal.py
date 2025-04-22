# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'telethon_modalnYCayi.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_TelethonConfigDialog(object):
    def setupUi(self, TelethonConfigDialog):
        if not TelethonConfigDialog.objectName():
            TelethonConfigDialog.setObjectName(u"TelethonConfigDialog")
        TelethonConfigDialog.resize(750, 979)
        TelethonConfigDialog.setStyleSheet(u"QDialog {\n"
"    background-color: #FFFFFF;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QLabel.titleLabel {\n"
"    font-size: 24px;\n"
"    font-weight: bold;\n"
"    color: #1E293B;\n"
"    background-color: transparent;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QLabel.infoBox {\n"
"    background-color: #EBF5FB;\n"
"    color: #3498DB;\n"
"    border: 1px solid #BFDBFE;\n"
"    border-radius: 6px;\n"
"    padding: 15px;\n"
"    font-size: 16px;\n"
"    font-family: Arial;\n"
" \n"
"}\n"
"\n"
"QLabel.stepLabel {\n"
"    font-size: 18px;\n"
"    font-weight: bold;\n"
"    color: #2ECC71;\n"
"    font-family: Arial;\n"
"\n"
"}\n"
"\n"
"QLabel.stepNumber {\n"
"    background-color: #2ECC71;\n"
"    color: white;\n"
"    border-radius: 20px;\n"
"    font-size: 18px;\n"
"    font-weight: bold;\n"
"    padding: 5px;\n"
"    text-align: center;\n"
"    font-family: Arial;\n"
"   \n"
"}\n"
"\n"
"QLabel.fieldLabel {\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"    color: #1E293B;\n"
"    font-family: Aria"
                        "l;\n"
"}\n"
"\n"
"QLabel.fieldHint {\n"
"    font-size: 16px;\n"
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
"    border-top-right-radius: 0px;\n"
" border-bottom-right-radius: 0px;\n"
"}\n"
"\n"
"QPushButton.iconButton {\n"
"    background-color: #F1F5F9;\n"
"    border: 1px solid #E4E7EB;\n"
"    border-left: none;\n"
"    border-top-left-radius: 0px;\n"
"    border-bottom-left-radius: 0px;\n"
"    border-top-right-radius: 6px;\n"
"    border-bottom-right-radius: 6px;\n"
"    font-size: 18px;\n"
"    color: #64748B;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QPushButton.iconButton:hover {\n"
"    background-color: #E2E8F0;\n"
"}\n"
"\n"
"QPushButton.primaryButton {\n"
"    background-color: #3498DB;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
""
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
"QLabel.statusSuccess {\n"
"    background-color: #F0FFF4;\n"
"    color: #2ECC71;\n"
"    border: 1px solid #C6F6D5;\n"
"    border-radius: 6px;\n"
"    padding: 15px;\n"
"    font-size: 16px;\n"
"    font-family: Arial;\n"
"}")
        self.verticalLayout = QVBoxLayout(TelethonConfigDialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.headerWidget = QWidget(TelethonConfigDialog)
        self.headerWidget.setObjectName(u"headerWidget")
        self.headerWidget.setMinimumSize(QSize(0, 70))
        self.headerWidget.setMaximumSize(QSize(16777215, 70))
        self.headerWidget.setStyleSheet(u"background-color: #F9FAFB;")
        self.horizontalLayout = QHBoxLayout(self.headerWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(40, -1, 40, -1)
        self.titleLabel = QLabel(self.headerWidget)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setStyleSheet(u"font-size: 24px; font-weight: bold; color: #1E293B;")

        self.horizontalLayout.addWidget(self.titleLabel)


        self.verticalLayout.addWidget(self.headerWidget)

        self.contentWidget = QWidget(TelethonConfigDialog)
        self.contentWidget.setObjectName(u"contentWidget")
        self.verticalLayout_2 = QVBoxLayout(self.contentWidget)
        self.verticalLayout_2.setSpacing(30)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(40, 30, 40, 30)
        self.infoLabel = QLabel(self.contentWidget)
        self.infoLabel.setObjectName(u"infoLabel")
        self.infoLabel.setMinimumSize(QSize(0, 80))
        self.infoLabel.setStyleSheet(u"background-color: #EBF5FB;\n"
"color: #3498DB;\n"
"border: 1px solid #BFDBFE;\n"
"border-radius: 6px;\n"
"padding: 15px;\n"
"font-size: 16px;")
        self.infoLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.infoLabel.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.infoLabel)

        self.step1Layout = QHBoxLayout()
        self.step1Layout.setSpacing(15)
        self.step1Layout.setObjectName(u"step1Layout")
        self.step1IconLabel = QLabel(self.contentWidget)
        self.step1IconLabel.setObjectName(u"step1IconLabel")
        self.step1IconLabel.setMinimumSize(QSize(40, 40))
        self.step1IconLabel.setMaximumSize(QSize(40, 40))
        self.step1IconLabel.setStyleSheet(u"background-color: #2ECC71;\n"
"color: white;\n"
"border-radius: 20px;\n"
"font-size: 18px;\n"
"font-weight: bold;\n"
"text-align: center;")
        self.step1IconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.step1Layout.addWidget(self.step1IconLabel)

        self.step1Label = QLabel(self.contentWidget)
        self.step1Label.setObjectName(u"step1Label")
        self.step1Label.setStyleSheet(u"font-size: 18px;\n"
"font-weight: bold;\n"
"color: #2ECC71;")

        self.step1Layout.addWidget(self.step1Label)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.step1Layout.addItem(self.horizontalSpacer_3)


        self.verticalLayout_2.addLayout(self.step1Layout)

        self.step1ContentLayout = QVBoxLayout()
        self.step1ContentLayout.setSpacing(20)
        self.step1ContentLayout.setObjectName(u"step1ContentLayout")
        self.step1ContentLayout.setContentsMargins(40, -1, -1, -1)
        self.apiIdLayout = QVBoxLayout()
        self.apiIdLayout.setSpacing(10)
        self.apiIdLayout.setObjectName(u"apiIdLayout")
        self.apiIdLabelLayout = QHBoxLayout()
        self.apiIdLabelLayout.setSpacing(10)
        self.apiIdLabelLayout.setObjectName(u"apiIdLabelLayout")
        self.apiIdLabel = QLabel(self.contentWidget)
        self.apiIdLabel.setObjectName(u"apiIdLabel")
        self.apiIdLabel.setStyleSheet(u"font-size: 16px; font-weight: bold; color: #1E293B;")

        self.apiIdLabelLayout.addWidget(self.apiIdLabel)

        self.apiIdHintLabel = QLabel(self.contentWidget)
        self.apiIdHintLabel.setObjectName(u"apiIdHintLabel")
        self.apiIdHintLabel.setStyleSheet(u"font-size: 16px; color: #64748B;")

        self.apiIdLabelLayout.addWidget(self.apiIdHintLabel)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.apiIdLabelLayout.addItem(self.horizontalSpacer_4)


        self.apiIdLayout.addLayout(self.apiIdLabelLayout)

        self.apiIdInputLayout = QHBoxLayout()
        self.apiIdInputLayout.setSpacing(0)
        self.apiIdInputLayout.setObjectName(u"apiIdInputLayout")
        self.apiIdLineEdit = QLineEdit(self.contentWidget)
        self.apiIdLineEdit.setObjectName(u"apiIdLineEdit")
        self.apiIdLineEdit.setMinimumSize(QSize(0, 45))
        self.apiIdLineEdit.setMaximumSize(QSize(16777215, 45))
        self.apiIdLineEdit.setStyleSheet(u"")

        self.apiIdInputLayout.addWidget(self.apiIdLineEdit)

        self.copyApiIdButton = QPushButton(self.contentWidget)
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

        self.apiIdInputLayout.addWidget(self.copyApiIdButton)


        self.apiIdLayout.addLayout(self.apiIdInputLayout)


        self.step1ContentLayout.addLayout(self.apiIdLayout)

        self.apiHashLayout = QVBoxLayout()
        self.apiHashLayout.setSpacing(10)
        self.apiHashLayout.setObjectName(u"apiHashLayout")
        self.apiHashLabelLayout = QHBoxLayout()
        self.apiHashLabelLayout.setSpacing(10)
        self.apiHashLabelLayout.setObjectName(u"apiHashLabelLayout")
        self.apiHashLabel = QLabel(self.contentWidget)
        self.apiHashLabel.setObjectName(u"apiHashLabel")
        self.apiHashLabel.setStyleSheet(u"font-size: 16px; font-weight: bold; color: #1E293B;")

        self.apiHashLabelLayout.addWidget(self.apiHashLabel)

        self.apiHashHintLabel = QLabel(self.contentWidget)
        self.apiHashHintLabel.setObjectName(u"apiHashHintLabel")
        self.apiHashHintLabel.setStyleSheet(u"font-size: 16px; color: #64748B;")

        self.apiHashLabelLayout.addWidget(self.apiHashHintLabel)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.apiHashLabelLayout.addItem(self.horizontalSpacer_5)


        self.apiHashLayout.addLayout(self.apiHashLabelLayout)

        self.apiHashInputLayout = QHBoxLayout()
        self.apiHashInputLayout.setSpacing(0)
        self.apiHashInputLayout.setObjectName(u"apiHashInputLayout")
        self.apiHashLineEdit = QLineEdit(self.contentWidget)
        self.apiHashLineEdit.setObjectName(u"apiHashLineEdit")
        self.apiHashLineEdit.setMinimumSize(QSize(0, 45))
        self.apiHashLineEdit.setMaximumSize(QSize(16777215, 45))
        self.apiHashLineEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.apiHashInputLayout.addWidget(self.apiHashLineEdit)

        self.togglePasswordButton = QPushButton(self.contentWidget)
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

        self.apiHashInputLayout.addWidget(self.togglePasswordButton)


        self.apiHashLayout.addLayout(self.apiHashInputLayout)


        self.step1ContentLayout.addLayout(self.apiHashLayout)


        self.verticalLayout_2.addLayout(self.step1ContentLayout)

        self.step2Layout = QHBoxLayout()
        self.step2Layout.setSpacing(15)
        self.step2Layout.setObjectName(u"step2Layout")
        self.step2IconLabel = QLabel(self.contentWidget)
        self.step2IconLabel.setObjectName(u"step2IconLabel")
        self.step2IconLabel.setMinimumSize(QSize(40, 40))
        self.step2IconLabel.setMaximumSize(QSize(40, 40))
        self.step2IconLabel.setStyleSheet(u"background-color: #2ECC71;\n"
"color: white;\n"
"font-size: 18px;\n"
"font-weight: bold;\n"
"text-align: center;")
        self.step2IconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.step2Layout.addWidget(self.step2IconLabel)

        self.step2Label = QLabel(self.contentWidget)
        self.step2Label.setObjectName(u"step2Label")
        self.step2Label.setStyleSheet(u"font-size: 18px;\n"
"font-weight: bold;\n"
"color: #2ECC71;")

        self.step2Layout.addWidget(self.step2Label)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.step2Layout.addItem(self.horizontalSpacer_6)


        self.verticalLayout_2.addLayout(self.step2Layout)

        self.step2ContentLayout = QVBoxLayout()
        self.step2ContentLayout.setSpacing(20)
        self.step2ContentLayout.setObjectName(u"step2ContentLayout")
        self.step2ContentLayout.setContentsMargins(40, -1, -1, -1)
        self.phoneLayout = QVBoxLayout()
        self.phoneLayout.setSpacing(10)
        self.phoneLayout.setObjectName(u"phoneLayout")
        self.phoneLabelLayout = QHBoxLayout()
        self.phoneLabelLayout.setSpacing(10)
        self.phoneLabelLayout.setObjectName(u"phoneLabelLayout")
        self.phoneLabel = QLabel(self.contentWidget)
        self.phoneLabel.setObjectName(u"phoneLabel")
        self.phoneLabel.setStyleSheet(u"font-size: 16px; font-weight: bold; color: #1E293B;")

        self.phoneLabelLayout.addWidget(self.phoneLabel)

        self.phoneHintLabel = QLabel(self.contentWidget)
        self.phoneHintLabel.setObjectName(u"phoneHintLabel")
        self.phoneHintLabel.setStyleSheet(u"font-size: 16px; color: #64748B;")

        self.phoneLabelLayout.addWidget(self.phoneHintLabel)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.phoneLabelLayout.addItem(self.horizontalSpacer_7)


        self.phoneLayout.addLayout(self.phoneLabelLayout)

        self.phoneLineEdit = QLineEdit(self.contentWidget)
        self.phoneLineEdit.setObjectName(u"phoneLineEdit")
        self.phoneLineEdit.setMinimumSize(QSize(0, 45))
        self.phoneLineEdit.setMaximumSize(QSize(16777215, 45))

        self.phoneLayout.addWidget(self.phoneLineEdit)


        self.step2ContentLayout.addLayout(self.phoneLayout)

        self.verificationStatusLabel = QLabel(self.contentWidget)
        self.verificationStatusLabel.setObjectName(u"verificationStatusLabel")
        self.verificationStatusLabel.setMinimumSize(QSize(0, 60))
        self.verificationStatusLabel.setStyleSheet(u"background-color: #F0FFF4;\n"
"color: #2ECC71;\n"
"border: 1px solid #C6F6D5;\n"
"border-radius: 6px;\n"
"padding: 15px;\n"
"font-size: 16px;")

        self.step2ContentLayout.addWidget(self.verificationStatusLabel)


        self.verticalLayout_2.addLayout(self.step2ContentLayout)

        self.apiHelpLabel = QLabel(self.contentWidget)
        self.apiHelpLabel.setObjectName(u"apiHelpLabel")
        self.apiHelpLabel.setStyleSheet(u"color: #3498DB; font-size: 14px; text-decoration: underline;")
        self.apiHelpLabel.setTextFormat(Qt.TextFormat.RichText)
        self.apiHelpLabel.setOpenExternalLinks(False)

        self.verticalLayout_2.addWidget(self.apiHelpLabel)


        self.verticalLayout.addWidget(self.contentWidget)

        self.footerWidget = QWidget(TelethonConfigDialog)
        self.footerWidget.setObjectName(u"footerWidget")
        self.footerWidget.setMinimumSize(QSize(0, 70))
        self.footerWidget.setMaximumSize(QSize(16777215, 70))
        self.footerWidget.setStyleSheet(u"background-color: #F9FAFB;")
        self.horizontalLayout_2 = QHBoxLayout(self.footerWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(40, 10, 40, 10)
        self.cancelButton = QPushButton(self.footerWidget)
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

        self.horizontalLayout_2.addWidget(self.cancelButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.saveButton = QPushButton(self.footerWidget)
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

        self.horizontalLayout_2.addWidget(self.saveButton)


        self.verticalLayout.addWidget(self.footerWidget)


        self.retranslateUi(TelethonConfigDialog)

        QMetaObject.connectSlotsByName(TelethonConfigDialog)
    # setupUi

    def retranslateUi(self, TelethonConfigDialog):
        TelethonConfigDialog.setWindowTitle(QCoreApplication.translate("TelethonConfigDialog", u"C\u00e0i \u0111\u1eb7t Telethon API", None))
        self.titleLabel.setText(QCoreApplication.translate("TelethonConfigDialog", u"C\u00e0i \u0111\u1eb7t Telethon API", None))
        self.titleLabel.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"titleLabel", None))
        self.infoLabel.setText(QCoreApplication.translate("TelethonConfigDialog", u"Telethon API cho ph\u00e9p t\u1ea3i l\u00ean c\u00e1c file l\u1edbn h\u01a1n 50MB. \u0110\u1ec3 s\u1eed d\u1ee5ng t\u00ednh n\u0103ng n\u00e0y,\n"
"vui l\u00f2ng ho\u00e0n t\u1ea5t c\u1ea5u h\u00ecnh v\u00e0 x\u00e1c th\u1ef1c OTP cho t\u00e0i kho\u1ea3n Telegram c\u1ee7a b\u1ea1n.", None))
        self.infoLabel.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"infoBox", None))
        self.step1IconLabel.setText(QCoreApplication.translate("TelethonConfigDialog", u"1", None))
        self.step1IconLabel.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"stepNumber", None))
        self.step1Label.setText(QCoreApplication.translate("TelethonConfigDialog", u"Nh\u1eadp th\u00f4ng tin API", None))
        self.step1Label.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"stepLabel", None))
        self.apiIdLabel.setText(QCoreApplication.translate("TelethonConfigDialog", u"API ID", None))
        self.apiIdLabel.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"fieldLabel", None))
        self.apiIdHintLabel.setText(QCoreApplication.translate("TelethonConfigDialog", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: 2xxxxxx)", None))
        self.apiIdHintLabel.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"fieldHint", None))
        self.apiIdLineEdit.setText(QCoreApplication.translate("TelethonConfigDialog", u"23456789", None))
        self.copyApiIdButton.setText(QCoreApplication.translate("TelethonConfigDialog", u"\ud83d\udccb", None))
        self.copyApiIdButton.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"iconButton", None))
        self.apiHashLabel.setText(QCoreApplication.translate("TelethonConfigDialog", u"API Hash", None))
        self.apiHashLabel.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"fieldLabel", None))
        self.apiHashHintLabel.setText(QCoreApplication.translate("TelethonConfigDialog", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: 7xxxxe)", None))
        self.apiHashHintLabel.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"fieldHint", None))
        self.apiHashLineEdit.setText(QCoreApplication.translate("TelethonConfigDialog", u"\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", None))
        self.togglePasswordButton.setText(QCoreApplication.translate("TelethonConfigDialog", u"\ud83d\udc41\ufe0f", None))
        self.togglePasswordButton.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"iconButton", None))
        self.step2IconLabel.setText(QCoreApplication.translate("TelethonConfigDialog", u"2", None))
        self.step2IconLabel.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"stepNumber", None))
        self.step2Label.setText(QCoreApplication.translate("TelethonConfigDialog", u"X\u00e1c th\u1ef1c t\u00e0i kho\u1ea3n", None))
        self.step2Label.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"stepLabel", None))
        self.phoneLabel.setText(QCoreApplication.translate("TelethonConfigDialog", u"S\u1ed1 \u0111i\u1ec7n tho\u1ea1i", None))
        self.phoneLabel.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"fieldLabel", None))
        self.phoneHintLabel.setText(QCoreApplication.translate("TelethonConfigDialog", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: +84123456789)", None))
        self.phoneHintLabel.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"fieldHint", None))
        self.phoneLineEdit.setText(QCoreApplication.translate("TelethonConfigDialog", u"+84123456789", None))
        self.verificationStatusLabel.setText(QCoreApplication.translate("TelethonConfigDialog", u"\u2713 \u0110\u00e3 x\u00e1c th\u1ef1c th\u00e0nh c\u00f4ng! T\u00e0i kho\u1ea3n telegram c\u1ee7a @username", None))
        self.verificationStatusLabel.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"statusSuccess", None))
        self.apiHelpLabel.setText(QCoreApplication.translate("TelethonConfigDialog", u"<a href=\"#\" style=\"color: #3498DB;\">L\u00e0m th\u1ebf n\u00e0o \u0111\u1ec3 l\u1ea5y API ID v\u00e0 Hash?</a>", None))
        self.cancelButton.setText(QCoreApplication.translate("TelethonConfigDialog", u"H\u1ee7y", None))
        self.cancelButton.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"secondaryButton", None))
        self.saveButton.setText(QCoreApplication.translate("TelethonConfigDialog", u"L\u01b0u c\u00e0i \u0111\u1eb7t", None))
        self.saveButton.setProperty(u"class", QCoreApplication.translate("TelethonConfigDialog", u"primaryButton", None))
    # retranslateUi

