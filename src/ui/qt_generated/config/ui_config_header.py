# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'config_headernquzvw.ui'
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
    QWidget)

class Ui_ConfigHeader(object):
    def setupUi(self, ConfigHeader):
        if not ConfigHeader.objectName():
            ConfigHeader.setObjectName(u"ConfigHeader")
        ConfigHeader.resize(700, 50)
        ConfigHeader.setMinimumSize(QSize(0, 50))
        ConfigHeader.setMaximumSize(QSize(16777215, 50))
        ConfigHeader.setStyleSheet(u"background-color: #F9FAFB;")
        self.horizontalLayout = QHBoxLayout(ConfigHeader)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(20, 10, 20, 10)
        self.titleLabel = QLabel(ConfigHeader)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setStyleSheet(u"font-size: 18px; font-weight: bold; color: #1E293B;")

        self.horizontalLayout.addWidget(self.titleLabel)


        self.retranslateUi(ConfigHeader)

        QMetaObject.connectSlotsByName(ConfigHeader)
    # setupUi

    def retranslateUi(self, ConfigHeader):
        self.titleLabel.setText(QCoreApplication.translate("ConfigHeader", u"C\u1ea5u h\u00ecnh Telegram", None))
        pass
    # retranslateUi

