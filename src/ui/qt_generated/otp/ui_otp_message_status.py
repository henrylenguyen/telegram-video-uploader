# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'otp_message_statusnYtGLG.ui'
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

class Ui_OtpMessageStatus(object):
    def setupUi(self, OtpMessageStatus):
        if not OtpMessageStatus.objectName():
            OtpMessageStatus.setObjectName(u"OtpMessageStatus")
        OtpMessageStatus.resize(500, 40)
        self.horizontalLayout = QHBoxLayout(OtpMessageStatus)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.iconLabel = QLabel(OtpMessageStatus)
        self.iconLabel.setObjectName(u"iconLabel")
        self.iconLabel.setMinimumSize(QSize(30, 30))
        self.iconLabel.setMaximumSize(QSize(30, 30))
        self.iconLabel.setStyleSheet(u"background-color: #3498DB;\n"
"color: white;\n"
"border-radius: 15px;\n"
"font-size: 14px;\n"
"font-weight: bold;")
        self.iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.iconLabel)

        self.messageLabel = QLabel(OtpMessageStatus)
        self.messageLabel.setObjectName(u"messageLabel")
        self.messageLabel.setStyleSheet(u"font-size: 16px;\n"
"font-weight: bold;\n"
"color: #3498DB;")

        self.horizontalLayout.addWidget(self.messageLabel)


        self.retranslateUi(OtpMessageStatus)

        QMetaObject.connectSlotsByName(OtpMessageStatus)
    # setupUi

    def retranslateUi(self, OtpMessageStatus):
        self.iconLabel.setText(QCoreApplication.translate("OtpMessageStatus", u"\u231b", None))
        self.messageLabel.setText(QCoreApplication.translate("OtpMessageStatus", u"\u0110ang g\u1eedi m\u00e3 x\u00e1c th\u1ef1c \u0111\u1ebfn Telegram c\u1ee7a b\u1ea1n...", None))
        self.messageLabel.setProperty(u"class", QCoreApplication.translate("OtpMessageStatus", u"messageLabel", None))
        pass
    # retranslateUi

