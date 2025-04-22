# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'otp_expired_timer_framejNUwCD.ui'
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
    QSizePolicy, QSpacerItem, QWidget)

class Ui_OtpExpiredTimerFrame(object):
    def setupUi(self, OtpExpiredTimerFrame):
        if not OtpExpiredTimerFrame.objectName():
            OtpExpiredTimerFrame.setObjectName(u"OtpExpiredTimerFrame")
        OtpExpiredTimerFrame.resize(500, 36)
        OtpExpiredTimerFrame.setMinimumSize(QSize(0, 36))
        OtpExpiredTimerFrame.setMaximumSize(QSize(16777215, 36))
        OtpExpiredTimerFrame.setStyleSheet(u"background-color: #FFF5F5;\n"
"border: 1px solid #FED7D7;\n"
"border-radius: 4px;")
        OtpExpiredTimerFrame.setFrameShape(QFrame.Shape.StyledPanel)
        OtpExpiredTimerFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(OtpExpiredTimerFrame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 0, 10, 0)
        self.timerIconLabel = QLabel(OtpExpiredTimerFrame)
        self.timerIconLabel.setObjectName(u"timerIconLabel")
        self.timerIconLabel.setMinimumSize(QSize(24, 24))
        self.timerIconLabel.setMaximumSize(QSize(24, 24))
        self.timerIconLabel.setStyleSheet(u"background-color: #E53E3E;\n"
"color: white;\n"
"border-radius: 12px;\n"
"font-size: 14px;\n"
"font-weight: bold;")
        self.timerIconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.timerIconLabel)

        self.timerLabel = QLabel(OtpExpiredTimerFrame)
        self.timerLabel.setObjectName(u"timerLabel")
        self.timerLabel.setStyleSheet(u"background-color: transparent;\n"
"color: #E53E3E;\n"
"font-weight: bold;\n"
"font-size: 16px;\n"
"border: none;")

        self.horizontalLayout.addWidget(self.timerLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.timeLeftLabel = QLabel(OtpExpiredTimerFrame)
        self.timeLeftLabel.setObjectName(u"timeLeftLabel")
        self.timeLeftLabel.setStyleSheet(u"background-color: transparent;\n"
"color: #E53E3E;\n"
"font-weight: bold;\n"
"font-size: 16px;\n"
"border: none;")
        self.timeLeftLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout.addWidget(self.timeLeftLabel)


        self.retranslateUi(OtpExpiredTimerFrame)

        QMetaObject.connectSlotsByName(OtpExpiredTimerFrame)
    # setupUi

    def retranslateUi(self, OtpExpiredTimerFrame):
        OtpExpiredTimerFrame.setProperty(u"class", QCoreApplication.translate("OtpExpiredTimerFrame", u"statusError", None))
        self.timerIconLabel.setText(QCoreApplication.translate("OtpExpiredTimerFrame", u"\u23f1", None))
        self.timerLabel.setText(QCoreApplication.translate("OtpExpiredTimerFrame", u"M\u00e3 \u0111\u00e3 h\u1ebft h\u1ea1n", None))
        self.timerLabel.setProperty(u"class", QCoreApplication.translate("OtpExpiredTimerFrame", u"timerLabel", None))
        self.timeLeftLabel.setText(QCoreApplication.translate("OtpExpiredTimerFrame", u"00:00", None))
        self.timeLeftLabel.setProperty(u"class", QCoreApplication.translate("OtpExpiredTimerFrame", u"timerLabel", None))
    # retranslateUi

