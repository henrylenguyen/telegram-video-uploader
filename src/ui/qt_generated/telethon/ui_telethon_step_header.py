# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'telethon_step_headerWQturd.ui'
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

class Ui_TelethonStepHeader(object):
    def setupUi(self, TelethonStepHeader):
        if not TelethonStepHeader.objectName():
            TelethonStepHeader.setObjectName(u"TelethonStepHeader")
        TelethonStepHeader.resize(700, 40)
        self.horizontalLayout = QHBoxLayout(TelethonStepHeader)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.stepIconLabel = QLabel(TelethonStepHeader)
        self.stepIconLabel.setObjectName(u"stepIconLabel")
        self.stepIconLabel.setMinimumSize(QSize(35, 35))
        self.stepIconLabel.setMaximumSize(QSize(35, 35))
        self.stepIconLabel.setStyleSheet(u"background-color: #2ECC71;\n"
"color: white;\n"
"border-radius: 20px;\n"
"font-size: 18px;\n"
"font-weight: bold;\n"
"text-align: center;")
        self.stepIconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.stepIconLabel)

        self.stepLabel = QLabel(TelethonStepHeader)
        self.stepLabel.setObjectName(u"stepLabel")
        self.stepLabel.setStyleSheet(u"font-size: 18px;\n"
"font-weight: bold;\n"
"color: #2ECC71;")

        self.horizontalLayout.addWidget(self.stepLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.retranslateUi(TelethonStepHeader)

        QMetaObject.connectSlotsByName(TelethonStepHeader)
    # setupUi

    def retranslateUi(self, TelethonStepHeader):
        self.stepIconLabel.setText(QCoreApplication.translate("TelethonStepHeader", u"1", None))
        self.stepIconLabel.setProperty(u"class", QCoreApplication.translate("TelethonStepHeader", u"stepNumber", None))
        self.stepLabel.setText(QCoreApplication.translate("TelethonStepHeader", u"Nh\u1eadp th\u00f4ng tin API", None))
        self.stepLabel.setProperty(u"class", QCoreApplication.translate("TelethonStepHeader", u"stepLabel", None))
        pass
    # retranslateUi

