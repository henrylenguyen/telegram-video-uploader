# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'python_version_contentgSiiDX.ui'
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
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_PythonVersionContent(object):
    def setupUi(self, PythonVersionContent):
        if not PythonVersionContent.objectName():
            PythonVersionContent.setObjectName(u"PythonVersionContent")
        PythonVersionContent.resize(700, 320)
        self.verticalLayout = QVBoxLayout(PythonVersionContent)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(40, 15, 40, 15)
        self.messageLayout = QHBoxLayout()
        self.messageLayout.setSpacing(15)
        self.messageLayout.setObjectName(u"messageLayout")
        self.warningIconLabel = QLabel(PythonVersionContent)
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
        self.mainMessageLabel = QLabel(PythonVersionContent)
        self.mainMessageLabel.setObjectName(u"mainMessageLabel")
        self.mainMessageLabel.setStyleSheet(u"font-size: 17px;\n"
"font-weight: 600;\n"
"color: #1E293B;")

        self.messageContentLayout.addWidget(self.mainMessageLabel)

        self.promptLabel = QLabel(PythonVersionContent)
        self.promptLabel.setObjectName(u"promptLabel")
        self.promptLabel.setStyleSheet(u"font-size: 14px;\n"
"color: #64748B;")

        self.messageContentLayout.addWidget(self.promptLabel)


        self.messageLayout.addLayout(self.messageContentLayout)


        self.verticalLayout.addLayout(self.messageLayout)

        self.versionLabel = QLabel(PythonVersionContent)
        self.versionLabel.setObjectName(u"versionLabel")
        self.versionLabel.setStyleSheet(u"font-size: 14px;\n"
"color: #64748B;")

        self.verticalLayout.addWidget(self.versionLabel)

        self.warningAndButtonsGroup = QFrame(PythonVersionContent)
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


        self.verticalLayout.addWidget(self.warningAndButtonsGroup)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(PythonVersionContent)

        QMetaObject.connectSlotsByName(PythonVersionContent)
    # setupUi

    def retranslateUi(self, PythonVersionContent):
        self.warningIconLabel.setText(QCoreApplication.translate("PythonVersionContent", u"!", None))
        self.mainMessageLabel.setText(QCoreApplication.translate("PythonVersionContent", u"\u1ee8ng d\u1ee5ng y\u00eau c\u1ea7u Python 3.7.0 tr\u1edf l\u00ean.", None))
        self.promptLabel.setText(QCoreApplication.translate("PythonVersionContent", u"B\u1ea1n mu\u1ed1n l\u00e0m g\u00ec \u0111\u1ec3 gi\u1ea3i quy\u1ebft v\u1ea5n \u0111\u1ec1 n\u00e0y?", None))
        self.versionLabel.setText(QCoreApplication.translate("PythonVersionContent", u"Phi\u00ean b\u1ea3n hi\u1ec7n t\u1ea1i: Python 3.13.3", None))
        self.warningIconSmallLabel.setText(QCoreApplication.translate("PythonVersionContent", u"i", None))
        self.warningTextLabel.setText(QCoreApplication.translate("PythonVersionContent", u"S\u1eed d\u1ee5ng Python kh\u00f4ng t\u01b0\u01a1ng th\u00edch c\u00f3 th\u1ec3 g\u00e2y l\u1ed7i \u1ee9ng d\u1ee5ng", None))
        self.installPythonButton.setText(QCoreApplication.translate("PythonVersionContent", u"T\u1ea3i Python m\u1edbi", None))
        self.installPythonButton.setProperty(u"class", QCoreApplication.translate("PythonVersionContent", u"primaryButton", None))
        self.createEnvButton.setText(QCoreApplication.translate("PythonVersionContent", u"T\u1ea1o m\u00f4i tr\u01b0\u1eddng \u1ea3o", None))
        self.createEnvButton.setProperty(u"class", QCoreApplication.translate("PythonVersionContent", u"secondaryButton", None))
        pass
    # retranslateUi

