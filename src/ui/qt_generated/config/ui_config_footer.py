# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'config_footercMWtVa.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QPushButton, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_ConfigFooter(object):
    def setupUi(self, ConfigFooter):
        if not ConfigFooter.objectName():
            ConfigFooter.setObjectName(u"ConfigFooter")
        ConfigFooter.resize(700, 60)
        ConfigFooter.setMinimumSize(QSize(0, 60))
        ConfigFooter.setMaximumSize(QSize(16777215, 60))
        ConfigFooter.setStyleSheet(u"background-color: #F9FAFB;")
        self.horizontalLayout = QHBoxLayout(ConfigFooter)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(20, 10, 20, 10)
        self.draftButton = QPushButton(ConfigFooter)
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

        self.horizontalLayout.addWidget(self.draftButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.saveButton = QPushButton(ConfigFooter)
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

        self.horizontalLayout.addWidget(self.saveButton)


        self.retranslateUi(ConfigFooter)

        QMetaObject.connectSlotsByName(ConfigFooter)
    # setupUi

    def retranslateUi(self, ConfigFooter):
        self.draftButton.setText(QCoreApplication.translate("ConfigFooter", u"L\u01b0u d\u1ea1ng b\u1ea3n nh\u00e1p", None))
        self.draftButton.setProperty(u"class", QCoreApplication.translate("ConfigFooter", u"outlineButton", None))
        self.saveButton.setText(QCoreApplication.translate("ConfigFooter", u"L\u01b0u c\u00e0i \u0111\u1eb7t", None))
        self.saveButton.setProperty(u"class", QCoreApplication.translate("ConfigFooter", u"primaryButton", None))
        pass
    # retranslateUi

