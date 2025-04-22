# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'config_wizardOZEXBs.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_ConfigWizard(object):
    def setupUi(self, ConfigWizard):
        if not ConfigWizard.objectName():
            ConfigWizard.setObjectName(u"ConfigWizard")
        ConfigWizard.resize(700, 60)
        ConfigWizard.setMinimumSize(QSize(0, 60))
        ConfigWizard.setMaximumSize(QSize(16777215, 60))
        ConfigWizard.setStyleSheet(u"background-color: #F9FAFB;")
        self.wizardLayout = QHBoxLayout(ConfigWizard)
        self.wizardLayout.setObjectName(u"wizardLayout")
        self.wizardLayout.setContentsMargins(20, 5, 20, 5)
        self.stepsLayout = QHBoxLayout()
        self.stepsLayout.setSpacing(15)
        self.stepsLayout.setObjectName(u"stepsLayout")
        self.step1Label = QLabel(ConfigWizard)
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

        self.stepTextLabel1 = QLabel(ConfigWizard)
        self.stepTextLabel1.setObjectName(u"stepTextLabel1")
        self.stepTextLabel1.setStyleSheet(u"color: #3498DB;\n"
"font-size: 14px;\n"
"font-weight: bold;")

        self.stepsLayout.addWidget(self.stepTextLabel1)

        self.stepLine = QLabel(ConfigWizard)
        self.stepLine.setObjectName(u"stepLine")
        self.stepLine.setMinimumSize(QSize(40, 1))
        self.stepLine.setMaximumSize(QSize(40, 1))
        self.stepLine.setStyleSheet(u"background-color: #CBD5E1;")

        self.stepsLayout.addWidget(self.stepLine)

        self.step2Label = QLabel(ConfigWizard)
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

        self.stepTextLabel2 = QLabel(ConfigWizard)
        self.stepTextLabel2.setObjectName(u"stepTextLabel2")
        self.stepTextLabel2.setStyleSheet(u"color: #64748B;\n"
"font-size: 14px;")

        self.stepsLayout.addWidget(self.stepTextLabel2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.stepsLayout.addItem(self.horizontalSpacer)


        self.wizardLayout.addLayout(self.stepsLayout)


        self.retranslateUi(ConfigWizard)

        QMetaObject.connectSlotsByName(ConfigWizard)
    # setupUi

    def retranslateUi(self, ConfigWizard):
        self.step1Label.setText(QCoreApplication.translate("ConfigWizard", u"1", None))
        self.stepTextLabel1.setText(QCoreApplication.translate("ConfigWizard", u"C\u1ea5u h\u00ecnh Telegram Bot API", None))
        self.stepLine.setText("")
        self.step2Label.setText(QCoreApplication.translate("ConfigWizard", u"2", None))
        self.stepTextLabel2.setText(QCoreApplication.translate("ConfigWizard", u"C\u1ea5u h\u00ecnh Telethon API", None))
        pass
    # retranslateUi

