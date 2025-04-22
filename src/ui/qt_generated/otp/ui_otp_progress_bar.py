# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'otp_progress_barOGTtvx.ui'
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
from PySide6.QtWidgets import (QApplication, QProgressBar, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_OtpProgressBar(object):
    def setupUi(self, OtpProgressBar):
        if not OtpProgressBar.objectName():
            OtpProgressBar.setObjectName(u"OtpProgressBar")
        OtpProgressBar.resize(500, 18)
        self.verticalLayout = QVBoxLayout(OtpProgressBar)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.progressBar = QProgressBar(OtpProgressBar)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
"    border: none;\n"
"    background-color: #E2E8F0;\n"
"    height: 8px;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #3498DB;\n"
"    border-radius: 4px;\n"
"}")
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(-1)
        self.progressBar.setTextVisible(False)

        self.verticalLayout.addWidget(self.progressBar)


        self.retranslateUi(OtpProgressBar)

        QMetaObject.connectSlotsByName(OtpProgressBar)
    # setupUi

    def retranslateUi(self, OtpProgressBar):
        pass
    # retranslateUi

