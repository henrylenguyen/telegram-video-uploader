# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'otp_timer_framemiFlxH.ui'
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

class Ui_OtpTimerFrame(object):
    def setupUi(self, OtpTimerFrame):
        if not OtpTimerFrame.objectName():
            OtpTimerFrame.setObjectName(u"OtpTimerFrame")
        OtpTimerFrame.resize(500, 36)
        OtpTimerFrame.setMinimumSize(QSize(0, 36))
        OtpTimerFrame.setMaximumSize(QSize(16777215, 36))
        OtpTimerFrame.setStyleSheet(u"background-color: #EBF8FF;\n"
"border: 1px solid #BEE3F8;\n"
"border-radius: 4px;")
        OtpTimerFrame.setFrameShape(QFrame.Shape.StyledPanel)
        OtpTimerFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(OtpTimerFrame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 0, 10, 0)
        self.timerIconLabel = QLabel(OtpTimerFrame)
        self.timerIconLabel.setObjectName(u"timerIconLabel")
        self.timerIconLabel.setMinimumSize(QSize(24, 24))
        self.timerIconLabel.setMaximumSize(QSize(24, 24))
        self.timerIconLabel.setStyleSheet(u"background-color: #3498DB;\n"
"color: white;\n"
"border-radius: 12px;\n"
"font-size: 14px;\n"
"font-weight: bold;")
        self.timerIconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.timerIconLabel)

        self.timerLabel = QLabel(OtpTimerFrame)
        self.timerLabel.setObjectName(u"timerLabel")
        self.timerLabel.setStyleSheet(u"background-color: transparent;\n"
"color: #3498DB;\n"
"font-weight: bold;\n"
"font-size: 16px;\n"
"border: none;")

        self.horizontalLayout.addWidget(self.timerLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.timeLeftLabel = QLabel(OtpTimerFrame)
        self.timeLeftLabel.setObjectName(u"timeLeftLabel")
        self.timeLeftLabel.setStyleSheet(u"background-color: transparent;\n"
"color: #3498DB;\n"
"font-weight: bold;\n"
"font-size: 16px;\n"
"border: none;")
        self.timeLeftLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout.addWidget(self.timeLeftLabel)


        self.retranslateUi(OtpTimerFrame)

        QMetaObject.connectSlotsByName(OtpTimerFrame)
    # setupUi

    def retranslateUi(self, OtpTimerFrame):
        OtpTimerFrame.setProperty(u"class", QCoreApplication.translate("OtpTimerFrame", u"statusInfo", None))
        self.timerIconLabel.setText(QCoreApplication.translate("OtpTimerFrame", u"\u23f1", None))
        self.timerLabel.setText(QCoreApplication.translate("OtpTimerFrame", u"M\u00e3 c\u00f3 hi\u1ec7u l\u1ef1c trong:", None))
        self.timerLabel.setProperty(u"class", QCoreApplication.translate("OtpTimerFrame", u"timerLabel", None))
        self.timeLeftLabel.setText(QCoreApplication.translate("OtpTimerFrame", u"04:31", None))
        self.timeLeftLabel.setProperty(u"class", QCoreApplication.translate("OtpTimerFrame", u"timerLabel", None))
    # retranslateUi

