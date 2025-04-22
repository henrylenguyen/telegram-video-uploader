# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'splash_screen_contentealOdT.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QProgressBar,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget)

class Ui_SplashScreenContent(object):
    def setupUi(self, SplashScreenContent):
        if not SplashScreenContent.objectName():
            SplashScreenContent.setObjectName(u"SplashScreenContent")
        SplashScreenContent.resize(600, 300)
        self.contentLayout = QVBoxLayout(SplashScreenContent)
        self.contentLayout.setSpacing(20)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.statusScrollArea = QScrollArea(SplashScreenContent)
        self.statusScrollArea.setObjectName(u"statusScrollArea")
        self.statusScrollArea.setMinimumSize(QSize(0, 150))
        self.statusScrollArea.setMaximumSize(QSize(16777215, 150))
        self.statusScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.statusScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.statusScrollArea.setWidgetResizable(True)
        self.scrollAreaContents = QWidget()
        self.scrollAreaContents.setObjectName(u"scrollAreaContents")
        self.scrollAreaContents.setGeometry(QRect(0, 0, 600, 150))
        self.statusItemsLayout = QVBoxLayout(self.scrollAreaContents)
        self.statusItemsLayout.setSpacing(5)
        self.statusItemsLayout.setObjectName(u"statusItemsLayout")
        self.statusItemsLayout.setContentsMargins(0, 0, 0, 0)
        self.statusScrollArea.setWidget(self.scrollAreaContents)

        self.contentLayout.addWidget(self.statusScrollArea)

        self.progressBar = QProgressBar(SplashScreenContent)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(40)

        self.contentLayout.addWidget(self.progressBar)

        self.statusLabel = QLabel(SplashScreenContent)
        self.statusLabel.setObjectName(u"statusLabel")

        self.contentLayout.addWidget(self.statusLabel, 0, Qt.AlignmentFlag.AlignHCenter)


        self.retranslateUi(SplashScreenContent)

        QMetaObject.connectSlotsByName(SplashScreenContent)
    # setupUi

    def retranslateUi(self, SplashScreenContent):
        self.statusLabel.setText(QCoreApplication.translate("SplashScreenContent", u"\u0110ang chu\u1ea9n b\u1ecb b\u1ed9 ph\u00e2n t\u00edch video...", None))
        pass
    # retranslateUi

