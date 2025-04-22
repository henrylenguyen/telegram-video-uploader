# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'otp_headerGzccQO.ui'
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

class Ui_OtpHeader(object):
    def setupUi(self, OtpHeader):
        if not OtpHeader.objectName():
            OtpHeader.setObjectName(u"OtpHeader")
        OtpHeader.resize(500, 60)
        OtpHeader.setMinimumSize(QSize(0, 60))
        OtpHeader.setMaximumSize(QSize(16777215, 60))
        OtpHeader.setStyleSheet(u"background-color: #F9FAFB;")
        self.horizontalLayout = QHBoxLayout(OtpHeader)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(30, -1, 30, -1)
        self.titleLabel = QLabel(OtpHeader)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setStyleSheet(u"font-size: 20px; font-weight: bold; color: #1E293B;")

        self.horizontalLayout.addWidget(self.titleLabel)


        self.retranslateUi(OtpHeader)

        QMetaObject.connectSlotsByName(OtpHeader)
    # setupUi

    def retranslateUi(self, OtpHeader):
        self.titleLabel.setText(QCoreApplication.translate("OtpHeader", u"X\u00e1c th\u1ef1c Telethon", None))
        self.titleLabel.setProperty(u"class", QCoreApplication.translate("OtpHeader", u"titleLabel", None))
        pass
    # retranslateUi

