# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'telethon_headerXWhlMB.ui'
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

class Ui_TelethonHeader(object):
    def setupUi(self, TelethonHeader):
        if not TelethonHeader.objectName():
            TelethonHeader.setObjectName(u"TelethonHeader")
        TelethonHeader.resize(750, 70)
        TelethonHeader.setMinimumSize(QSize(0, 70))
        TelethonHeader.setMaximumSize(QSize(16777215, 70))
        TelethonHeader.setStyleSheet(u"background-color: #F9FAFB;")
        self.horizontalLayout = QHBoxLayout(TelethonHeader)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(40, -1, 40, -1)
        self.titleLabel = QLabel(TelethonHeader)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setStyleSheet(u"font-size: 24px; font-weight: bold; color: #1E293B;")

        self.horizontalLayout.addWidget(self.titleLabel)


        self.retranslateUi(TelethonHeader)

        QMetaObject.connectSlotsByName(TelethonHeader)
    # setupUi

    def retranslateUi(self, TelethonHeader):
        self.titleLabel.setText(QCoreApplication.translate("TelethonHeader", u"C\u00e0i \u0111\u1eb7t Telethon API", None))
        self.titleLabel.setProperty(u"class", QCoreApplication.translate("TelethonHeader", u"titleLabel", None))
        pass
    # retranslateUi

