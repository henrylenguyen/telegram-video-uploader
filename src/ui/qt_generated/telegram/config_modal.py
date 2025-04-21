# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'config_modalvpwAHt.ui'
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
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_TelegramConfigDialog(object):
    def setupUi(self, TelegramConfigDialog):
        if not TelegramConfigDialog.objectName():
            TelegramConfigDialog.setObjectName(u"TelegramConfigDialog")
        TelegramConfigDialog.resize(700, 600)
        TelegramConfigDialog.setMinimumSize(QSize(700, 600))
        TelegramConfigDialog.setMaximumSize(QSize(800, 650))
        TelegramConfigDialog.setStyleSheet(u"QDialog {\n"
"    background-color: #FFFFFF;\n"
"}\n"
"\n"
"QTabWidget::pane {\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 8px;\n"
"    background-color: #FFFFFF;\n"
"    top: -1px;\n"
"    margin: 0px 20px;\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    background-color: #FFFFFF;\n"
"    color: #64748B;\n"
"    padding: 12px 0px;\n"
"    font-size: 14px;\n"
"    border: none;\n"
"    width: 180px;\n"
"    font-family: Arial;\n"
"    margin-left: 0px; \n"
"}\n"
"\n"
"QTabBar::tab:first {\n"
"    margin-left: 20px; \n"
"}\n"
"\n"
"QTabBar::tab:selected {\n"
"    color: #3498DB;\n"
"    border-bottom: 3px solid #3498DB;\n"
"    background-color: #EBF5FB;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QTabBar::tab:hover:!selected {\n"
"    color: #3498DB;\n"
"    background-color: #F5F9FF;\n"
"}\n"
"\n"
"QScrollArea {\n"
"    border: none;\n"
"    background-color: transparent;\n"
"}\n"
"\n"
"QWidget#scrollContent {\n"
"    background-color: transparent;\n"
"}\n"
"\n"
"QLabel.titleLabel {\n"
"    font-size: 18px;"
                        "\n"
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
"    padding: 8px;\n"
"    font-size: 13px;\n"
"    font-family: Arial;\n"
"    margin-bottom: 15px;\n"
"}\n"
"\n"
"QLabel.fieldLabel {\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"    color: #1E293B;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QLabel.fieldHint {\n"
"    font-size: 13px;\n"
"    color: #64748B;\n"
"    font-family: Arial;\n"
"}\n"
"\n"
"QLineEdit {\n"
"    border: 1px solid #E4E7EB;\n"
"    border-radius: 6px;\n"
"  	padding: 15px;\n"
"    background-color: #FFFFFF;\n"
"    font-size: 14px;\n"
"    color: #1E293B;\n"
"    font-family: Arial;\n"
" \n"
"}\n"
"\n"
"QPushButton.primaryButton {\n"
"    background-color: #3498DB;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 8"
                        "px 15px;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"    font-family: Arial;\n"
"    height: 36px;\n"
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
"    padding: 8px 15px;\n"
"    font-size: 14px;\n"
"    font-family: Arial;\n"
"    height: 36px;\n"
"}\n"
"\n"
"QPushButton.secondaryButton:hover {\n"
"    background-color: #D1E6FA;\n"
"}\n"
"\n"
"QPushButton.outlineButton {\n"
"    background-color: #FFFFFF;\n"
"    color: #64748B;\n"
"    border: 1px solid #E4E7EB;\n"
"    border-radius: 6px;\n"
"    padding: 8px 15px;\n"
"    font-size: 14px;\n"
"    font-family: Arial;\n"
"    height: 36px;\n"
"}\n"
"\n"
"QLabel.statusSuccess {\n"
"    background-color: #F0FFF4;\n"
"    color: #2ECC71;\n"
"    border: 1px solid #C6F6D5;\n"
"    border-radius: 6px;\n"
"    padding: 8px;\n"
"    font-size: 13px;\n"
""
                        "    font-family: Arial;\n"
"    margin-top: 10px;\n"
"    margin-bottom: 10px;\n"
"}\n"
"\n"
"QLabel.statusError {\n"
"    background-color: #FFF5F5;\n"
"    color: #E53E3E;\n"
"    border: 1px solid #FED7D7;\n"
"    border-radius: 6px;\n"
"    padding: 8px;\n"
"    font-size: 13px;\n"
"    font-family: Arial;\n"
"    margin-top: 10px;\n"
"    margin-bottom: 10px;\n"
"}\n"
"")
        self.verticalLayout = QVBoxLayout(TelegramConfigDialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.headerWidget = QWidget(TelegramConfigDialog)
        self.headerWidget.setObjectName(u"headerWidget")
        self.headerWidget.setMinimumSize(QSize(0, 50))
        self.headerWidget.setMaximumSize(QSize(16777215, 50))
        self.headerWidget.setStyleSheet(u"background-color: #F9FAFB;")
        self.horizontalLayout = QHBoxLayout(self.headerWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(20, 10, 20, 10)
        self.titleLabel = QLabel(self.headerWidget)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setStyleSheet(u"font-size: 18px; font-weight: bold; color: #1E293B;")

        self.horizontalLayout.addWidget(self.titleLabel)


        self.verticalLayout.addWidget(self.headerWidget)

        self.wizardWidget = QWidget(TelegramConfigDialog)
        self.wizardWidget.setObjectName(u"wizardWidget")
        self.wizardWidget.setMinimumSize(QSize(0, 60))
        self.wizardWidget.setMaximumSize(QSize(16777215, 60))
        self.wizardWidget.setStyleSheet(u"background-color: #F9FAFB;")
        self.wizardLayout = QHBoxLayout(self.wizardWidget)
        self.wizardLayout.setObjectName(u"wizardLayout")
        self.wizardLayout.setContentsMargins(20, 5, 20, 5)
        self.stepsLayout = QHBoxLayout()
        self.stepsLayout.setSpacing(15)
        self.stepsLayout.setObjectName(u"stepsLayout")
        self.step1Label = QLabel(self.wizardWidget)
        self.step1Label.setObjectName(u"step1Label")
        self.step1Label.setMinimumSize(QSize(32, 32))
        self.step1Label.setMaximumSize(QSize(32, 32))
        self.step1Label.setStyleSheet(u"background-color: #3498DB;\n"
"color: white;\n"
"border-radius: 16px;\n"
"font-size: 14px;\n"
"font-weight: bold;\n"
"")
        self.step1Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stepsLayout.addWidget(self.step1Label)

        self.stepTextLabel1 = QLabel(self.wizardWidget)
        self.stepTextLabel1.setObjectName(u"stepTextLabel1")
        self.stepTextLabel1.setStyleSheet(u"color: #3498DB;\n"
"font-size: 14px;\n"
"font-weight: bold;")

        self.stepsLayout.addWidget(self.stepTextLabel1)

        self.stepLine = QLabel(self.wizardWidget)
        self.stepLine.setObjectName(u"stepLine")
        self.stepLine.setMinimumSize(QSize(40, 1))
        self.stepLine.setMaximumSize(QSize(40, 1))
        self.stepLine.setStyleSheet(u"background-color: #CBD5E1;")

        self.stepsLayout.addWidget(self.stepLine)

        self.step2Label = QLabel(self.wizardWidget)
        self.step2Label.setObjectName(u"step2Label")
        self.step2Label.setMinimumSize(QSize(32, 32))
        self.step2Label.setMaximumSize(QSize(32, 32))
        self.step2Label.setStyleSheet(u"background-color: #CBD5E1;\n"
"color: white;\n"
"border-radius: 16px;\n"
"font-size: 14px;\n"
"font-weight: bold;")
        self.step2Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stepsLayout.addWidget(self.step2Label)

        self.stepTextLabel2 = QLabel(self.wizardWidget)
        self.stepTextLabel2.setObjectName(u"stepTextLabel2")
        self.stepTextLabel2.setStyleSheet(u"color: #64748B;\n"
"font-size: 14px;")

        self.stepsLayout.addWidget(self.stepTextLabel2)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.stepsLayout.addItem(self.horizontalSpacer_2)


        self.wizardLayout.addLayout(self.stepsLayout)


        self.verticalLayout.addWidget(self.wizardWidget)

        self.configTabWidget = QTabWidget(TelegramConfigDialog)
        self.configTabWidget.setObjectName(u"configTabWidget")
        self.configTabWidget.setMinimumSize(QSize(0, 420))
        self.configTabWidget.setMaximumSize(QSize(16777215, 420))
        font = QFont()
        font.setPointSize(9)
        self.configTabWidget.setFont(font)
        self.configTabWidget.setStyleSheet(u"")
        self.botApiTab = QWidget()
        self.botApiTab.setObjectName(u"botApiTab")
        self.botApiTab.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.verticalLayout_2 = QVBoxLayout(self.botApiTab)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.botApiScrollArea = QScrollArea(self.botApiTab)
        self.botApiScrollArea.setObjectName(u"botApiScrollArea")
        self.botApiScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.botApiScrollArea.setWidgetResizable(True)
        self.botApiScrollArea.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.scrollContent = QWidget()
        self.scrollContent.setObjectName(u"scrollContent")
        self.scrollContent.setGeometry(QRect(0, 0, 646, 430))
        self.botApiContentLayout = QVBoxLayout(self.scrollContent)
        self.botApiContentLayout.setSpacing(15)
        self.botApiContentLayout.setObjectName(u"botApiContentLayout")
        self.botApiContentLayout.setContentsMargins(20, 20, 20, 15)
        self.botInfoLabel = QLabel(self.scrollContent)
        self.botInfoLabel.setObjectName(u"botInfoLabel")
        self.botInfoLabel.setMinimumSize(QSize(0, 60))
        self.botInfoLabel.setMaximumSize(QSize(16777215, 60))
        self.botInfoLabel.setStyleSheet(u"background-color: #EBF5FB;\n"
"color: #3498DB;\n"
"border: 1px solid #BFDBFE;\n"
"border-radius: 6px;\n"
"padding: 8px;\n"
"font-size: 13px;")
        self.botInfoLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.botInfoLabel.setWordWrap(True)

        self.botApiContentLayout.addWidget(self.botInfoLabel)

        self.tokenContainer = QWidget(self.scrollContent)
        self.tokenContainer.setObjectName(u"tokenContainer")
        self.tokenLayout = QVBoxLayout(self.tokenContainer)
        self.tokenLayout.setSpacing(5)
        self.tokenLayout.setObjectName(u"tokenLayout")
        self.tokenLayout.setContentsMargins(0, 0, 0, 0)
        self.tokenHeaderLayout = QHBoxLayout()
        self.tokenHeaderLayout.setObjectName(u"tokenHeaderLayout")
        self.tokenLabel = QLabel(self.tokenContainer)
        self.tokenLabel.setObjectName(u"tokenLabel")
        self.tokenLabel.setStyleSheet(u"font-size: 14px; font-weight: bold; color: #1E293B;")

        self.tokenHeaderLayout.addWidget(self.tokenLabel)

        self.tokenHintLabel = QLabel(self.tokenContainer)
        self.tokenHintLabel.setObjectName(u"tokenHintLabel")
        self.tokenHintLabel.setStyleSheet(u"font-size: 13px; color: #64748B;")

        self.tokenHeaderLayout.addWidget(self.tokenHintLabel)

        self.tokenHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.tokenHeaderLayout.addItem(self.tokenHeaderSpacer)


        self.tokenLayout.addLayout(self.tokenHeaderLayout)

        self.tokenLineEdit = QLineEdit(self.tokenContainer)
        self.tokenLineEdit.setObjectName(u"tokenLineEdit")
        self.tokenLineEdit.setMinimumSize(QSize(0, 45))
        self.tokenLineEdit.setMaximumSize(QSize(16777215, 45))

        self.tokenLayout.addWidget(self.tokenLineEdit)


        self.botApiContentLayout.addWidget(self.tokenContainer)

        self.chatIdContainer = QWidget(self.scrollContent)
        self.chatIdContainer.setObjectName(u"chatIdContainer")
        self.chatIdLayout = QVBoxLayout(self.chatIdContainer)
        self.chatIdLayout.setSpacing(5)
        self.chatIdLayout.setObjectName(u"chatIdLayout")
        self.chatIdLayout.setContentsMargins(0, 0, 0, 0)
        self.chatIdHeaderLayout = QHBoxLayout()
        self.chatIdHeaderLayout.setObjectName(u"chatIdHeaderLayout")
        self.chatIdLabel = QLabel(self.chatIdContainer)
        self.chatIdLabel.setObjectName(u"chatIdLabel")
        self.chatIdLabel.setStyleSheet(u"font-size: 14px; font-weight: bold; color: #1E293B;")

        self.chatIdHeaderLayout.addWidget(self.chatIdLabel)

        self.chatIdHintLabel = QLabel(self.chatIdContainer)
        self.chatIdHintLabel.setObjectName(u"chatIdHintLabel")
        self.chatIdHintLabel.setStyleSheet(u"font-size: 13px; color: #64748B;")

        self.chatIdHeaderLayout.addWidget(self.chatIdHintLabel)

        self.chatIdHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.chatIdHeaderLayout.addItem(self.chatIdHeaderSpacer)


        self.chatIdLayout.addLayout(self.chatIdHeaderLayout)

        self.chatIdLineEdit = QLineEdit(self.chatIdContainer)
        self.chatIdLineEdit.setObjectName(u"chatIdLineEdit")
        self.chatIdLineEdit.setMinimumSize(QSize(0, 45))
        self.chatIdLineEdit.setMaximumSize(QSize(16777215, 45))

        self.chatIdLayout.addWidget(self.chatIdLineEdit)


        self.botApiContentLayout.addWidget(self.chatIdContainer)

        self.separator1 = QFrame(self.scrollContent)
        self.separator1.setObjectName(u"separator1")
        self.separator1.setFrameShape(QFrame.Shape.HLine)
        self.separator1.setFrameShadow(QFrame.Shadow.Sunken)

        self.botApiContentLayout.addWidget(self.separator1)

        self.connectionStatusLabel = QLabel(self.scrollContent)
        self.connectionStatusLabel.setObjectName(u"connectionStatusLabel")
        self.connectionStatusLabel.setMinimumSize(QSize(0, 40))
        self.connectionStatusLabel.setMaximumSize(QSize(16777215, 40))
        self.connectionStatusLabel.setStyleSheet(u"background-color: #F0FFF4;\n"
"color: #2ECC71;\n"
"border: 1px solid #C6F6D5;\n"
"border-radius: 6px;\n"
"padding: 8px;\n"
"font-size: 13px;")

        self.botApiContentLayout.addWidget(self.connectionStatusLabel)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setSpacing(15)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.btnCheckConnection = QPushButton(self.scrollContent)
        self.btnCheckConnection.setObjectName(u"btnCheckConnection")
        self.btnCheckConnection.setMinimumSize(QSize(150, 36))
        self.btnCheckConnection.setMaximumSize(QSize(16777215, 36))
        self.btnCheckConnection.setStyleSheet(u"QPushButton {\n"
"    background-color: #EBF5FB;\n"
"    color: #3498DB;\n"
"    border: 1px solid #BFDBFE;\n"
"    border-radius: 6px;\n"
"    padding: 8px;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #D1E6FA;\n"
"}")

        self.horizontalLayout_5.addWidget(self.btnCheckConnection)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_5)


        self.botApiContentLayout.addLayout(self.horizontalLayout_5)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.botApiContentLayout.addItem(self.verticalSpacer)

        self.botApiScrollArea.setWidget(self.scrollContent)

        self.verticalLayout_2.addWidget(self.botApiScrollArea)

        self.configTabWidget.addTab(self.botApiTab, "")
        self.telethonApiTab = QWidget()
        self.telethonApiTab.setObjectName(u"telethonApiTab")
        self.verticalLayout_3 = QVBoxLayout(self.telethonApiTab)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.telethonApiScrollArea = QScrollArea(self.telethonApiTab)
        self.telethonApiScrollArea.setObjectName(u"telethonApiScrollArea")
        self.telethonApiScrollArea.setStyleSheet(u"")
        self.telethonApiScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.telethonApiScrollArea.setWidgetResizable(True)
        self.telethonApiScrollArea.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.scrollContent1 = QWidget()
        self.scrollContent1.setObjectName(u"scrollContent1")
        self.scrollContent1.setGeometry(QRect(0, 0, 646, 492))
        self.telethonApiContentLayout = QVBoxLayout(self.scrollContent1)
        self.telethonApiContentLayout.setSpacing(15)
        self.telethonApiContentLayout.setObjectName(u"telethonApiContentLayout")
        self.telethonApiContentLayout.setContentsMargins(20, 15, 20, 15)
        self.telethonInfoLabel = QLabel(self.scrollContent1)
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

        self.telethonApiContentLayout.addWidget(self.telethonInfoLabel)

        self.apiIdContainer = QWidget(self.scrollContent1)
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

        self.apiIdLayout.addWidget(self.apiIdLineEdit)


        self.telethonApiContentLayout.addWidget(self.apiIdContainer)

        self.apiHashContainer = QWidget(self.scrollContent1)
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


        self.telethonApiContentLayout.addWidget(self.apiHashContainer)

        self.phoneContainer = QWidget(self.scrollContent1)
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


        self.telethonApiContentLayout.addWidget(self.phoneContainer)

        self.separator2 = QFrame(self.scrollContent1)
        self.separator2.setObjectName(u"separator2")
        self.separator2.setFrameShape(QFrame.Shape.HLine)
        self.separator2.setFrameShadow(QFrame.Shadow.Sunken)

        self.telethonApiContentLayout.addWidget(self.separator2)

        self.otpStatusLayout = QHBoxLayout()
        self.otpStatusLayout.setSpacing(10)
        self.otpStatusLayout.setObjectName(u"otpStatusLayout")
        self.otpStatusLabel = QLabel(self.scrollContent1)
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

        self.getOtpButton = QPushButton(self.scrollContent1)
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


        self.telethonApiContentLayout.addLayout(self.otpStatusLayout)

        self.apiHelpLabel = QLabel(self.scrollContent1)
        self.apiHelpLabel.setObjectName(u"apiHelpLabel")
        self.apiHelpLabel.setStyleSheet(u"color: #3498DB; font-size: 13px; text-decoration: underline;")
        self.apiHelpLabel.setTextFormat(Qt.TextFormat.RichText)
        self.apiHelpLabel.setOpenExternalLinks(False)

        self.telethonApiContentLayout.addWidget(self.apiHelpLabel)

        self.verticalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.telethonApiContentLayout.addItem(self.verticalSpacer_2)

        self.telethonApiScrollArea.setWidget(self.scrollContent1)

        self.verticalLayout_3.addWidget(self.telethonApiScrollArea)

        self.configTabWidget.addTab(self.telethonApiTab, "")

        self.verticalLayout.addWidget(self.configTabWidget)

        self.footerWidget = QWidget(TelegramConfigDialog)
        self.footerWidget.setObjectName(u"footerWidget")
        self.footerWidget.setMinimumSize(QSize(0, 60))
        self.footerWidget.setMaximumSize(QSize(16777215, 60))
        self.footerWidget.setStyleSheet(u"background-color: #F9FAFB;")
        self.horizontalLayout_2 = QHBoxLayout(self.footerWidget)
        self.horizontalLayout_2.setSpacing(15)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(20, 10, 20, 10)
        self.draftButton = QPushButton(self.footerWidget)
        self.draftButton.setObjectName(u"draftButton")
        self.draftButton.setMinimumSize(QSize(150, 36))
        self.draftButton.setMaximumSize(QSize(150, 36))
        self.draftButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #FFFFFF;\n"
"    color: #64748B;\n"
"    border: 1px solid #E4E7EB;\n"
"    border-radius: 6px;\n"
"    padding: 8px;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #F5F9FF;\n"
"    color: #3498DB;\n"
"}")

        self.horizontalLayout_2.addWidget(self.draftButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.saveButton = QPushButton(self.footerWidget)
        self.saveButton.setObjectName(u"saveButton")
        self.saveButton.setMinimumSize(QSize(150, 36))
        self.saveButton.setMaximumSize(QSize(150, 36))
        self.saveButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_2.addWidget(self.saveButton)


        self.verticalLayout.addWidget(self.footerWidget)


        self.retranslateUi(TelegramConfigDialog)

        self.configTabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(TelegramConfigDialog)
    # setupUi

    def retranslateUi(self, TelegramConfigDialog):
        TelegramConfigDialog.setWindowTitle(QCoreApplication.translate("TelegramConfigDialog", u"C\u1ea5u h\u00ecnh Telegram", None))
        self.titleLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"C\u1ea5u h\u00ecnh Telegram", None))
        self.step1Label.setText(QCoreApplication.translate("TelegramConfigDialog", u"1", None))
        self.stepTextLabel1.setText(QCoreApplication.translate("TelegramConfigDialog", u"C\u1ea5u h\u00ecnh Telegram Bot API", None))
        self.stepLine.setText("")
        self.step2Label.setText(QCoreApplication.translate("TelegramConfigDialog", u"2", None))
        self.stepTextLabel2.setText(QCoreApplication.translate("TelegramConfigDialog", u"C\u1ea5u h\u00ecnh Telethon API", None))
        self.botInfoLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"\u0110\u1ec3 s\u1eed d\u1ee5ng \u1ee9ng d\u1ee5ng, b\u1ea1n c\u1ea7n c\u1ea5u h\u00ecnh Telegram Bot API b\u1eb1ng c\u00e1ch t\u1ea1o bot v\u1edbi @BotFather\n"
"v\u00e0 cung c\u1ea5p token c\u00f9ng v\u1edbi chat ID c\u1ee7a nh\u00f3m n\u01a1i b\u1ea1n mu\u1ed1n t\u1ea3i video l\u00ean.", None))
        self.tokenLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"Token Telegram", None))
        self.tokenHintLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"(T\u00ecm trong @BotFather)", None))
        self.tokenLineEdit.setPlaceholderText(QCoreApplication.translate("TelegramConfigDialog", u"110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw", None))
        self.chatIdLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"Chat ID", None))
        self.chatIdHintLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: -100xxxxxxxxx)", None))
        self.chatIdLineEdit.setPlaceholderText(QCoreApplication.translate("TelegramConfigDialog", u"-1001234567890", None))
        self.separator1.setProperty(u"class", QCoreApplication.translate("TelegramConfigDialog", u"separator", None))
        self.connectionStatusLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"\u2713 \u0110\u00e3 k\u1ebft n\u1ed1i th\u00e0nh c\u00f4ng! K\u1ebft n\u1ed1i t\u1edbi bot @myTelegramBot", None))
        self.btnCheckConnection.setText(QCoreApplication.translate("TelegramConfigDialog", u"Ki\u1ec3m tra k\u1ebft n\u1ed1i", None))
        self.btnCheckConnection.setProperty(u"class", QCoreApplication.translate("TelegramConfigDialog", u"secondaryButton", None))
        self.configTabWidget.setTabText(self.configTabWidget.indexOf(self.botApiTab), QCoreApplication.translate("TelegramConfigDialog", u"Telegram Bot API", None))
        self.telethonInfoLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"Telethon API cho ph\u00e9p t\u1ea3i l\u00ean c\u00e1c file l\u1edbn h\u01a1n 50MB. \u0110\u1ec3 s\u1eed d\u1ee5ng t\u00ednh n\u0103ng n\u00e0y,\n"
"vui l\u00f2ng \u0111\u0103ng k\u00fd v\u00e0 nh\u1eadp API ID, API Hash t\u1eeb my.telegram.org.", None))
        self.apiIdLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"API ID", None))
        self.apiIdHintLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: 2xxxxxx)", None))
        self.apiIdLineEdit.setPlaceholderText(QCoreApplication.translate("TelegramConfigDialog", u"Nh\u1eadp API ID (v\u00ed d\u1ee5: 2xxxxxx)", None))
        self.apiHashLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"API Hash", None))
        self.apiHashHintLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: 7xxxxe)", None))
        self.apiHashLineEdit.setPlaceholderText(QCoreApplication.translate("TelegramConfigDialog", u"Nh\u1eadp API Hash (v\u00ed d\u1ee5: 7xxxxe)", None))
        self.togglePasswordButton.setText(QCoreApplication.translate("TelegramConfigDialog", u"\ud83d\udc41\ufe0f", None))
        self.phoneLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"S\u1ed1 \u0111i\u1ec7n tho\u1ea1i", None))
        self.phoneHintLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: +84123456789)", None))
        self.phoneLineEdit.setPlaceholderText(QCoreApplication.translate("TelegramConfigDialog", u"+84123456789", None))
        self.separator2.setProperty(u"class", QCoreApplication.translate("TelegramConfigDialog", u"separator", None))
        self.otpStatusLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"\u26a0 Ch\u01b0a x\u00e1c th\u1ef1c! C\u1ea7n x\u00e1c th\u1ef1c OTP", None))
        self.getOtpButton.setText(QCoreApplication.translate("TelegramConfigDialog", u"L\u1ea5y m\u00e3 x\u00e1c th\u1ef1c", None))
        self.getOtpButton.setProperty(u"class", QCoreApplication.translate("TelegramConfigDialog", u"primaryButton", None))
        self.apiHelpLabel.setText(QCoreApplication.translate("TelegramConfigDialog", u"<a href=\"#\" style=\"color: #3498DB;\">L\u00e0m th\u1ebf n\u00e0o \u0111\u1ec3 l\u1ea5y API ID v\u00e0 Hash?</a>", None))
        self.configTabWidget.setTabText(self.configTabWidget.indexOf(self.telethonApiTab), QCoreApplication.translate("TelegramConfigDialog", u"Telethon API", None))
        self.draftButton.setText(QCoreApplication.translate("TelegramConfigDialog", u"L\u01b0u d\u1ea1ng b\u1ea3n nh\u00e1p", None))
        self.draftButton.setProperty(u"class", QCoreApplication.translate("TelegramConfigDialog", u"outlineButton", None))
        self.saveButton.setText(QCoreApplication.translate("TelegramConfigDialog", u"L\u01b0u c\u00e0i \u0111\u1eb7t", None))
        self.saveButton.setProperty(u"class", QCoreApplication.translate("TelegramConfigDialog", u"primaryButton", None))
    # retranslateUi

