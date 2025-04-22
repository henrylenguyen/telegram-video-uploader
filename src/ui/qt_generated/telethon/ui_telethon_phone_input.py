# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'telethon_phone_inputlsLqtm.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_TelethonPhoneInput(object):
    def setupUi(self, TelethonPhoneInput):
        if not TelethonPhoneInput.objectName():
            TelethonPhoneInput.setObjectName(u"TelethonPhoneInput")
        TelethonPhoneInput.resize(700, 80)
        self.verticalLayout = QVBoxLayout(TelethonPhoneInput)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout = QHBoxLayout()
        self.headerLayout.setSpacing(10)
        self.headerLayout.setObjectName(u"headerLayout")
        self.phoneLabel = QLabel(TelethonPhoneInput)
        self.phoneLabel.setObjectName(u"phoneLabel")
        self.phoneLabel.setStyleSheet(u"font-size: 16px; font-weight: bold; color: #1E293B;")

        self.headerLayout.addWidget(self.phoneLabel)

        self.phoneHintLabel = QLabel(TelethonPhoneInput)
        self.phoneHintLabel.setObjectName(u"phoneHintLabel")
        self.phoneHintLabel.setStyleSheet(u"font-size: 16px; color: #64748B;")

        self.headerLayout.addWidget(self.phoneHintLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.headerLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.headerLayout)

        self.phoneLineEdit = QLineEdit(TelethonPhoneInput)
        self.phoneLineEdit.setObjectName(u"phoneLineEdit")
        self.phoneLineEdit.setMinimumSize(QSize(0, 45))
        self.phoneLineEdit.setMaximumSize(QSize(16777215, 45))

        self.verticalLayout.addWidget(self.phoneLineEdit)


        self.retranslateUi(TelethonPhoneInput)

        QMetaObject.connectSlotsByName(TelethonPhoneInput)
    # setupUi

    def retranslateUi(self, TelethonPhoneInput):
        self.phoneLabel.setText(QCoreApplication.translate("TelethonPhoneInput", u"S\u1ed1 \u0111i\u1ec7n tho\u1ea1i", None))
        self.phoneLabel.setProperty(u"class", QCoreApplication.translate("TelethonPhoneInput", u"fieldLabel", None))
        self.phoneHintLabel.setText(QCoreApplication.translate("TelethonPhoneInput", u"(C\u00f3 \u0111\u1ecbnh d\u1ea1ng: +84123456789)", None))
        self.phoneHintLabel.setProperty(u"class", QCoreApplication.translate("TelethonPhoneInput", u"fieldHint", None))
        self.phoneLineEdit.setText(QCoreApplication.translate("TelethonPhoneInput", u"+84123456789", None))
        pass
    # retranslateUi

