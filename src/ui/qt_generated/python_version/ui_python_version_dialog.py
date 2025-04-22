# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'python_version_dialogyqVnYi.ui'
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
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_PythonVersionDialog(object):
    def setupUi(self, PythonVersionDialog):
        if not PythonVersionDialog.objectName():
            PythonVersionDialog.setObjectName(u"PythonVersionDialog")
        PythonVersionDialog.resize(700, 400)
        PythonVersionDialog.setMinimumSize(QSize(700, 400))
        PythonVersionDialog.setMaximumSize(QSize(700, 400))
        PythonVersionDialog.setStyleSheet(u"QDialog {\n"
"    background-color: #F9FAFB;\n"
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
"    color: #1E293B;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QLabel.infoLabel {\n"
"    font-size: 14px;\n"
"    color: #64748B;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QLabel.warningLabel {\n"
"    background-color: #FFF5F5;\n"
"    color: #E53E3E;\n"
"    border: 1px solid #FED7D7;\n"
"    border-radius: 6px;\n"
"    padding: 10px 15px;\n"
"    font-size: 15px;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QPushButton.primaryButton {\n"
"    background-color: #3498DB;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 10px 15px;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QPushButt"
                        "on.primaryButton:hover {\n"
"    background-color: #2980B9;\n"
"}\n"
"\n"
"QPushButton.secondaryButton {\n"
"    background-color: #2ECC71;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 10px 15px;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QPushButton.secondaryButton:hover {\n"
"    background-color: #27AE60;\n"
"}\n"
"\n"
"QPushButton.outlineButton {\n"
"    background-color: #FFFFFF;\n"
"    color: #64748B;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 6px;\n"
"    padding: 10px 15px;\n"
"    font-size: 13px;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QPushButton.outlineButton:hover {\n"
"    background-color: #F1F5F9;\n"
"}\n"
"\n"
"QPushButton.linkButton {\n"
"    background-color: #F8F9FA;\n"
"    color: #3498DB;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 6px;\n"
"    padding: 10px 15px;\n"
"    font-size: 13px;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QPushButton.linkButton:hover {\n"
""
                        "    background-color: #EBF5FB;\n"
"}\n"
"\n"
"QFrame.whiteContainer {\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 6px;\n"
"}")
        self.verticalLayout = QVBoxLayout(PythonVersionDialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.headerWidget = QWidget(PythonVersionDialog)
        self.headerWidget.setObjectName(u"headerWidget")
        self.headerWidget.setMinimumSize(QSize(0, 40))
        self.headerWidget.setMaximumSize(QSize(16777215, 40))
        self.headerWidget.setStyleSheet(u"background-color: #FFFFFF;")
        self.horizontalLayout = QHBoxLayout(self.headerWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(15, -1, 15, -1)
        self.titleLabel = QLabel(self.headerWidget)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setStyleSheet(u"font-size: 14px; font-weight: bold; color: #1E293B;")

        self.horizontalLayout.addWidget(self.titleLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.headerWidget)

        self.contentWidget = QWidget(PythonVersionDialog)
        self.contentWidget.setObjectName(u"contentWidget")
        self.verticalLayout_2 = QVBoxLayout(self.contentWidget)
        self.verticalLayout_2.setSpacing(15)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(40, 15, 40, 15)
        self.messageLayout = QHBoxLayout()
        self.messageLayout.setSpacing(15)
        self.messageLayout.setObjectName(u"messageLayout")
        self.warningIconLabel = QLabel(self.contentWidget)
        self.warningIconLabel.setObjectName(u"warningIconLabel")
        self.warningIconLabel.setMinimumSize(QSize(40, 40))
        self.warningIconLabel.setMaximumSize(QSize(40, 40))
        self.warningIconLabel.setStyleSheet(u"background-color: #FFC107;\n"
"color: white;\n"
"border-radius: 20px;\n"
"font-size: 24px;\n"
"font-weight: bold;")
        self.warningIconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.messageLayout.addWidget(self.warningIconLabel)

        self.messageContentLayout = QVBoxLayout()
        self.messageContentLayout.setObjectName(u"messageContentLayout")
        self.mainMessageLabel = QLabel(self.contentWidget)
        self.mainMessageLabel.setObjectName(u"mainMessageLabel")
        self.mainMessageLabel.setStyleSheet(u"font-size: 17px;\n"
"font-weight: 600;\n"
"color: #1E293B;")

        self.messageContentLayout.addWidget(self.mainMessageLabel)

        self.promptLabel = QLabel(self.contentWidget)
        self.promptLabel.setObjectName(u"promptLabel")
        self.promptLabel.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        self.promptLabel.setStyleSheet(u"font-size: 14px;\n"
"color: #64748B;")

        self.messageContentLayout.addWidget(self.promptLabel)


        self.messageLayout.addLayout(self.messageContentLayout)


        self.verticalLayout_2.addLayout(self.messageLayout)

        self.versionLabel = QLabel(self.contentWidget)
        self.versionLabel.setObjectName(u"versionLabel")
        self.versionLabel.setStyleSheet(u"font-size: 14px;\n"
"color: #64748B;")

        self.verticalLayout_2.addWidget(self.versionLabel)

        self.warningAndButtonsGroup = QFrame(self.contentWidget)
        self.warningAndButtonsGroup.setObjectName(u"warningAndButtonsGroup")
        self.warningAndButtonsGroup.setStyleSheet(u"border: 1px solid #FED7D7;\n"
"border-radius: 6px;")
        self.warningAndButtonsGroup.setFrameShape(QFrame.Shape.StyledPanel)
        self.warningAndButtonsGroup.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.warningAndButtonsGroup)
        self.verticalLayout_3.setSpacing(15)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 15)
        self.warningFrame = QFrame(self.warningAndButtonsGroup)
        self.warningFrame.setObjectName(u"warningFrame")
        self.warningFrame.setMinimumSize(QSize(0, 50))
        self.warningFrame.setMaximumSize(QSize(16777215, 50))
        self.warningFrame.setStyleSheet(u"background-color: #FFF5F5;\n"
"border: none;\n"
"border-top-left-radius: 6px;\n"
"border-top-right-radius: 6px;")
        self.warningFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.warningFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.warningFrame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(15, 0, 15, 0)
        self.warningIconSmallLabel = QLabel(self.warningFrame)
        self.warningIconSmallLabel.setObjectName(u"warningIconSmallLabel")
        self.warningIconSmallLabel.setMinimumSize(QSize(30, 30))
        self.warningIconSmallLabel.setMaximumSize(QSize(30, 30))
        self.warningIconSmallLabel.setStyleSheet(u"background-color: #E53E3E;\n"
"color: white;\n"
"border-radius: 15px;\n"
"font-size: 16px;\n"
"font-weight: bold;")
        self.warningIconSmallLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_2.addWidget(self.warningIconSmallLabel)

        self.warningTextLabel = QLabel(self.warningFrame)
        self.warningTextLabel.setObjectName(u"warningTextLabel")
        self.warningTextLabel.setStyleSheet(u"background-color: transparent;\n"
"color: #E53E3E;\n"
"font-size: 15px;\n"
"border: none;")

        self.horizontalLayout_2.addWidget(self.warningTextLabel)


        self.verticalLayout_3.addWidget(self.warningFrame)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(15, -1, 15, -1)
        self.installPythonButton = QPushButton(self.warningAndButtonsGroup)
        self.installPythonButton.setObjectName(u"installPythonButton")
        self.installPythonButton.setMinimumSize(QSize(0, 40))
        self.installPythonButton.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        self.installPythonButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #3498DB;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 10px 15px;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2980B9;\n"
"}")

        self.horizontalLayout_3.addWidget(self.installPythonButton)

        self.createEnvButton = QPushButton(self.warningAndButtonsGroup)
        self.createEnvButton.setObjectName(u"createEnvButton")
        self.createEnvButton.setMinimumSize(QSize(0, 40))
        self.createEnvButton.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        self.createEnvButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #2ECC71;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 10px 15px;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #27AE60;\n"
"}")

        self.horizontalLayout_3.addWidget(self.createEnvButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.verticalLayout_2.addWidget(self.warningAndButtonsGroup)

        self.bottomButtonsLayout = QHBoxLayout()
        self.bottomButtonsLayout.setObjectName(u"bottomButtonsLayout")
        self.bottomButtonsLayout.setContentsMargins(-1, 10, -1, -1)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.bottomButtonsLayout.addItem(self.horizontalSpacer_2)

        self.exitButton = QPushButton(self.contentWidget)
        self.exitButton.setObjectName(u"exitButton")
        self.exitButton.setMinimumSize(QSize(150, 35))
        self.exitButton.setMaximumSize(QSize(150, 35))
        self.exitButton.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        self.exitButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #FFFFFF;\n"
"    color: #64748B;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 4px;\n"
"    padding: 10px 15px;\n"
"    font-size: 13px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #F1F5F9;\n"
"}")

        self.bottomButtonsLayout.addWidget(self.exitButton)

        self.continueButton = QPushButton(self.contentWidget)
        self.continueButton.setObjectName(u"continueButton")
        self.continueButton.setMinimumSize(QSize(150, 35))
        self.continueButton.setMaximumSize(QSize(150, 35))
        self.continueButton.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        self.continueButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #F8F9FA;\n"
"    color: #3498DB;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 4px;\n"
"    padding: 10px 15px;\n"
"    font-size: 13px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #EBF5FB;\n"
"}")

        self.bottomButtonsLayout.addWidget(self.continueButton)


        self.verticalLayout_2.addLayout(self.bottomButtonsLayout)


        self.verticalLayout.addWidget(self.contentWidget)


        self.retranslateUi(PythonVersionDialog)

        QMetaObject.connectSlotsByName(PythonVersionDialog)
    # setupUi

    def retranslateUi(self, PythonVersionDialog):
        PythonVersionDialog.setWindowTitle(QCoreApplication.translate("PythonVersionDialog", u"Phi\u00ean b\u1ea3n Python kh\u00f4ng h\u1ed7 tr\u1ee3", None))
        self.titleLabel.setText(QCoreApplication.translate("PythonVersionDialog", u"Phi\u00ean b\u1ea3n Python kh\u00f4ng h\u1ed7 tr\u1ee3", None))
        self.warningIconLabel.setText(QCoreApplication.translate("PythonVersionDialog", u"!", None))
        self.mainMessageLabel.setText(QCoreApplication.translate("PythonVersionDialog", u"\u1ee8ng d\u1ee5ng y\u00eau c\u1ea7u Python 3.7.0 tr\u1edf l\u00ean.", None))
        self.promptLabel.setText(QCoreApplication.translate("PythonVersionDialog", u"B\u1ea1n mu\u1ed1n l\u00e0m g\u00ec \u0111\u1ec3 gi\u1ea3i quy\u1ebft v\u1ea5n \u0111\u1ec1 n\u00e0y?", None))
        self.versionLabel.setText(QCoreApplication.translate("PythonVersionDialog", u"Phi\u00ean b\u1ea3n hi\u1ec7n t\u1ea1i: Python 3.13.3", None))
        self.warningIconSmallLabel.setText(QCoreApplication.translate("PythonVersionDialog", u"i", None))
        self.warningTextLabel.setText(QCoreApplication.translate("PythonVersionDialog", u"S\u1eed d\u1ee5ng Python kh\u00f4ng t\u01b0\u01a1ng th\u00edch c\u00f3 th\u1ec3 g\u00e2y l\u1ed7i \u1ee9ng d\u1ee5ng", None))
        self.installPythonButton.setText(QCoreApplication.translate("PythonVersionDialog", u"T\u1ea3i Python m\u1edbi", None))
        self.installPythonButton.setProperty(u"class", QCoreApplication.translate("PythonVersionDialog", u"primaryButton", None))
        self.createEnvButton.setText(QCoreApplication.translate("PythonVersionDialog", u"T\u1ea1o m\u00f4i tr\u01b0\u1eddng \u1ea3o", None))
        self.createEnvButton.setProperty(u"class", QCoreApplication.translate("PythonVersionDialog", u"secondaryButton", None))
        self.exitButton.setText(QCoreApplication.translate("PythonVersionDialog", u"Tho\u00e1t", None))
        self.exitButton.setProperty(u"class", QCoreApplication.translate("PythonVersionDialog", u"outlineButton", None))
        self.continueButton.setText(QCoreApplication.translate("PythonVersionDialog", u"Ti\u1ebfp t\u1ee5c", None))
        self.continueButton.setProperty(u"class", QCoreApplication.translate("PythonVersionDialog", u"linkButton", None))
    # retranslateUi

