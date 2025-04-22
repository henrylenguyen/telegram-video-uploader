# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'python_version_headerklYCvh.ui'
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

class Ui_PythonVersionHeader(object):
    def setupUi(self, PythonVersionHeader):
        if not PythonVersionHeader.objectName():
            PythonVersionHeader.setObjectName(u"PythonVersionHeader")
        PythonVersionHeader.resize(700, 40)
        PythonVersionHeader.setMinimumSize(QSize(0, 40))
        PythonVersionHeader.setMaximumSize(QSize(16777215, 40))
        PythonVersionHeader.setStyleSheet(u"background-color: #FFFFFF;")
        self.horizontalLayout = QHBoxLayout(PythonVersionHeader)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(15, -1, 15, -1)
        self.titleLabel = QLabel(PythonVersionHeader)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setStyleSheet(u"font-size: 14px; font-weight: bold; color: #1E293B;")

        self.horizontalLayout.addWidget(self.titleLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.retranslateUi(PythonVersionHeader)

        QMetaObject.connectSlotsByName(PythonVersionHeader)
    # setupUi

    def retranslateUi(self, PythonVersionHeader):
        self.titleLabel.setText(QCoreApplication.translate("PythonVersionHeader", u"Phi\u00ean b\u1ea3n Python kh\u00f4ng h\u1ed7 tr\u1ee3", None))
        pass
    # retranslateUi

