# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'config_bot_tabklWBaD.ui'
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

class Ui_ConfigBotTab(object):
    def setupUi(self, ConfigBotTab):
        if not ConfigBotTab.objectName():
            ConfigBotTab.setObjectName(u"ConfigBotTab")
        ConfigBotTab.resize(650, 430)
        self.verticalLayout = QVBoxLayout(ConfigBotTab)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(20, 20, 20, 15)
        self.botInfoLabel = QLabel(ConfigBotTab)
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

        self.verticalLayout.addWidget(self.botInfoLabel)

        self.tokenContainer = QWidget(ConfigBotTab)
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


        self.verticalLayout.addWidget(self.tokenContainer)

        self.chatIdContainer = QWidget(ConfigBotTab)
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


        self.verticalLayout.addWidget(self.chatIdContainer)

        self.separator = QFrame(ConfigBotTab)
        self.separator.setObjectName(u"separator")
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.separator)

        self.connectionStatusLabel = QLabel(ConfigBotTab)
        self.connectionStatusLabel.setObjectName(u"connectionStatusLabel")
        self.connectionStatusLabel.setMinimumSize(QSize(0, 40))
        self.connectionStatusLabel.setMaximumSize(QSize(16777215, 40))
        self.connectionStatusLabel.setStyleSheet(u"background-color: #F0FFF4;\n"
"color: #2ECC71;\n"
"border: 1px solid #C6F6D5;\n"
"border-radius: 6px;\n"
"padding: 8px;\n"
"font-size: 13px;")

        self.verticalLayout.addWidget(self.connectionStatusLabel)

        self.connectionCheckLayout = QHBoxLayout()
        self.connectionCheckLayout.setSpacing(15)
        self.connectionCheckLayout.setObjectName(u"connectionCheckLayout")
        self.btnCheckConnection = QPushButton(ConfigBotTab)
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

        self.connectionCheckLayout.addWidget(self.btnCheckConnection)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.connectionCheckLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.connectionCheckLayout)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(ConfigBotTab)

        QMetaObject.connectSlotsByName(ConfigBotTab)
    # setupUi

    def retranslateUi(self, ConfigBotTab):
        self.botInfoLabel.setText(QCoreApplication.translate("ConfigBotTab", u"\u0110\u1ec3 s\u1eed d\u1ee5ng \u1ee9ng d\u1ee5ng, b\u1ea1n c\u1ea7n c\u1ea5u h\u00ecnh Telegram Bot API b\u1eb1ng c\u00e1ch t\u1ea1o bot v\u1edbi @BotFather\n"
"v\u00e0 cung c\u1ea5p token c\u00f9ng v\u1edbi chat ID c\u1ee7a nh\u00f3m n\u01a1i b\u1ea1n mu\u1ed1n t\u1ea3i video l\u00ean.", None))
        self.tokenLabel.setText(QCoreApplication.translate("ConfigBotTab", u"Token Telegram", None))
        self.tokenHintLabel.setText(QCoreApplication.translate("ConfigBotTab", u"(T\u00ecm trong @BotFather)", None))
        self.tokenLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigBotTab", u"110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw", None))
        self.chatIdLabel.setText(QCoreApplication.translate("ConfigBotTab", u"Chat ID", None))
        self.chatIdHintLabel.setText(QCoreApplication.translate("ConfigBotTab", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: -100xxxxxxxxx)", None))
        self.chatIdLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigBotTab", u"-1001234567890", None))
        self.separator.setProperty(u"class", QCoreApplication.translate("ConfigBotTab", u"separator", None))
        self.connectionStatusLabel.setText(QCoreApplication.translate("ConfigBotTab", u"\u2713 \u0110\u00e3 k\u1ebft n\u1ed1i th\u00e0nh c\u00f4ng! K\u1ebft n\u1ed1i t\u1edbi bot @myTelegramBot", None))
        self.btnCheckConnection.setText(QCoreApplication.translate("ConfigBotTab", u"Ki\u1ec3m tra k\u1ebft n\u1ed1i", None))
        self.btnCheckConnection.setProperty(u"class", QCoreApplication.translate("ConfigBotTab", u"secondaryButton", None))
        pass
    # retranslateUi

