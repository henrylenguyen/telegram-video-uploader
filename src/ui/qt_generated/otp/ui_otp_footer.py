# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'otp_footerELyXfk.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_OtpFooter(object):
    def setupUi(self, OtpFooter):
        if not OtpFooter.objectName():
            OtpFooter.setObjectName(u"OtpFooter")
        OtpFooter.resize(500, 70)
        OtpFooter.setMinimumSize(QSize(0, 70))
        OtpFooter.setMaximumSize(QSize(16777215, 70))
        OtpFooter.setStyleSheet(u"background-color: #F9FAFB;")
        OtpFooter.setFrameShape(QFrame.Shape.StyledPanel)
        OtpFooter.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(OtpFooter)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(30, 10, 30, 10)
        self.cancelButton = QPushButton(OtpFooter)
        self.cancelButton.setObjectName(u"cancelButton")
        self.cancelButton.setMinimumSize(QSize(120, 50))
        self.cancelButton.setMaximumSize(QSize(120, 50))
        self.cancelButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #EBF5FB;\n"
"    color: #3498DB;\n"
"    border: 1px solid #BFDBFE;\n"
"    border-radius: 6px;\n"
"    padding: 10px;\n"
"    font-size: 16px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #D1E6FA;\n"
"}")

        self.horizontalLayout.addWidget(self.cancelButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.actionButton = QPushButton(OtpFooter)
        self.actionButton.setObjectName(u"actionButton")
        self.actionButton.setMinimumSize(QSize(120, 50))
        self.actionButton.setMaximumSize(QSize(120, 50))
        self.actionButton.setStyleSheet(u"QPushButton {\n"
"    background-color: #3498DB;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 10px;\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2980B9;\n"
"}")

        self.horizontalLayout.addWidget(self.actionButton)


        self.retranslateUi(OtpFooter)

        QMetaObject.connectSlotsByName(OtpFooter)
    # setupUi

    def retranslateUi(self, OtpFooter):
        self.cancelButton.setText(QCoreApplication.translate("OtpFooter", u"H\u1ee7y", None))
        self.cancelButton.setProperty(u"class", QCoreApplication.translate("OtpFooter", u"secondaryButton", None))
        self.actionButton.setText(QCoreApplication.translate("OtpFooter", u"X\u00e1c th\u1ef1c", None))
        self.actionButton.setProperty(u"class", QCoreApplication.translate("OtpFooter", u"primaryButton", None))
        pass
    # retranslateUi

