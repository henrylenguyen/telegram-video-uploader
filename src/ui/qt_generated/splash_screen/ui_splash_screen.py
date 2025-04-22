# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'splash_screenJPDzXj.ui'
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
    QProgressBar, QScrollArea, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_SplashScreen(object):
    def setupUi(self, SplashScreen):
        if not SplashScreen.objectName():
            SplashScreen.setObjectName(u"SplashScreen")
        SplashScreen.resize(600, 454)
        SplashScreen.setStyleSheet(u"QWidget#SplashScreen {\n"
"  background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8f9fa, stop:1 #e9ecef);\n"
"  border-radius: 15px;\n"
"}\n"
"\n"
"QLabel#titleLabel {\n"
"  font-family: Arial, sans-serif;\n"
"  font-size: 24px;\n"
"  font-weight: bold;\n"
"  color: #2c3e50;\n"
"}\n"
"\n"
"QLabel#statusLabel {\n"
"  font-family: Arial, sans-serif;\n"
"  font-size: 12px;\n"
"  color: #7f8c8d;\n"
"}\n"
"\n"
"QScrollArea {\n"
"  background-color: transparent;\n"
"  border: none;\n"
"}\n"
"\n"
"QScrollArea#statusScrollArea > QWidget {\n"
"  background-color: transparent;\n"
"}\n"
"\n"
"QWidget#scrollAreaContents {\n"
"  background-color: white;\n"
"  border-radius: 8px;\n"
"}\n"
"\n"
"QScrollBar:vertical {\n"
"  background: #E2E8F0;\n"
"  width: 6px;\n"
"  border-radius: 3px;\n"
"  margin: 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"  background: #CBD5E1;\n"
"  border-radius: 3px;\n"
"  min-height: 30px;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {\n"
"  height: 0"
                        "px;\n"
"}\n"
"\n"
"QProgressBar {\n"
"  background-color: #e0e0e0;\n"
"  border: none;\n"
"  height: 10px;\n"
"  border-radius: 5px;\n"
"  text-align: center;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"  background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498DB, stop:1 #2ECC71);\n"
"  border-radius: 5px;\n"
"}\n"
"\n"
"QLabel.statusItem {\n"
"  font-family: Arial, sans-serif;\n"
"  font-size: 14px;\n"
"  color: #2c3e50;\n"
"}\n"
"\n"
"QLabel.statusItemPending {\n"
"  font-family: Arial, sans-serif;\n"
"  font-size: 14px;\n"
"  color: #7f8c8d;\n"
"}\n"
"\n"
"QFrame.statusItemFrame {\n"
"  background-color: white;\n"
"}\n"
"\n"
"QDialog {\n"
"    background-color: #FFFFFF;\n"
"}\n"
"\n"
"QTabWidget::pane {\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 8px;\n"
"    background-color: #FFFFFF;\n"
"    top: -1px;\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    background-color: #FFFFFF;\n"
"    color: #64748B;\n"
"    padding: 25px 20px;\n"
"    font-size: 16px;\n"
"    border: none;\n"
"    width: 200px;\n"
""
                        "    font-family: Arial;\n"
"}\n"
"\n"
"QTabBar::tab:selected {\n"
"    color: #3498DB;\n"
"    border-bottom: 3px solid #3498DB;\n"
"    background-color: #EBF5FB;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QTabBar::tab:hover:!selected {\n"
"    color: #3498DB;\n"
"    background-color: #F5F9FF;\n"
"}\n"
"")
        self.verticalLayout = QVBoxLayout(SplashScreen)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(30, 30, 30, 30)
        self.logoLayout = QVBoxLayout()
        self.logoLayout.setSpacing(15)
        self.logoLayout.setObjectName(u"logoLayout")
        self.logoLabel = QLabel(SplashScreen)
        self.logoLabel.setObjectName(u"logoLabel")
        self.logoLabel.setMinimumSize(QSize(70, 70))
        self.logoLabel.setMaximumSize(QSize(70, 70))
        self.logoLabel.setScaledContents(True)

        self.logoLayout.addWidget(self.logoLabel, 0, Qt.AlignmentFlag.AlignHCenter)

        self.titleLabel = QLabel(SplashScreen)
        self.titleLabel.setObjectName(u"titleLabel")

        self.logoLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout.addLayout(self.logoLayout)

        self.contentLayout = QVBoxLayout()
        self.contentLayout.setSpacing(20)
        self.contentLayout.setObjectName(u"contentLayout")
        self.statusScrollArea = QScrollArea(SplashScreen)
        self.statusScrollArea.setObjectName(u"statusScrollArea")
        self.statusScrollArea.setMinimumSize(QSize(0, 150))
        self.statusScrollArea.setMaximumSize(QSize(16777215, 150))
        self.statusScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.statusScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.statusScrollArea.setWidgetResizable(True)
        self.scrollAreaContents = QWidget()
        self.scrollAreaContents.setObjectName(u"scrollAreaContents")
        self.scrollAreaContents.setGeometry(QRect(0, 0, 532, 392))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.statusItem1 = QFrame(self.scrollAreaContents)
        self.statusItem1.setObjectName(u"statusItem1")
        self.statusItem1.setFrameShape(QFrame.Shape.StyledPanel)
        self.statusItem1.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.statusItem1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 5, 10, 5)
        self.indicator1 = QLabel(self.statusItem1)
        self.indicator1.setObjectName(u"indicator1")
        self.indicator1.setMinimumSize(QSize(20, 20))
        self.indicator1.setMaximumSize(QSize(20, 20))

        self.horizontalLayout.addWidget(self.indicator1)

        self.label1 = QLabel(self.statusItem1)
        self.label1.setObjectName(u"label1")

        self.horizontalLayout.addWidget(self.label1)


        self.verticalLayout_2.addWidget(self.statusItem1)

        self.statusItem2 = QFrame(self.scrollAreaContents)
        self.statusItem2.setObjectName(u"statusItem2")
        self.statusItem2.setFrameShape(QFrame.Shape.StyledPanel)
        self.statusItem2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.statusItem2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(10, 5, 10, 5)
        self.indicator2 = QLabel(self.statusItem2)
        self.indicator2.setObjectName(u"indicator2")
        self.indicator2.setMinimumSize(QSize(20, 20))
        self.indicator2.setMaximumSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.indicator2)

        self.label2 = QLabel(self.statusItem2)
        self.label2.setObjectName(u"label2")

        self.horizontalLayout_2.addWidget(self.label2)


        self.verticalLayout_2.addWidget(self.statusItem2)

        self.statusItem3 = QFrame(self.scrollAreaContents)
        self.statusItem3.setObjectName(u"statusItem3")
        self.statusItem3.setFrameShape(QFrame.Shape.StyledPanel)
        self.statusItem3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.statusItem3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(10, 5, 10, 5)
        self.indicator3 = QLabel(self.statusItem3)
        self.indicator3.setObjectName(u"indicator3")
        self.indicator3.setMinimumSize(QSize(20, 20))
        self.indicator3.setMaximumSize(QSize(20, 20))

        self.horizontalLayout_3.addWidget(self.indicator3)

        self.label3 = QLabel(self.statusItem3)
        self.label3.setObjectName(u"label3")

        self.horizontalLayout_3.addWidget(self.label3)


        self.verticalLayout_2.addWidget(self.statusItem3)

        self.statusItem4 = QFrame(self.scrollAreaContents)
        self.statusItem4.setObjectName(u"statusItem4")
        self.statusItem4.setFrameShape(QFrame.Shape.StyledPanel)
        self.statusItem4.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.statusItem4)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(10, 5, 10, 5)
        self.indicator4 = QLabel(self.statusItem4)
        self.indicator4.setObjectName(u"indicator4")
        self.indicator4.setMinimumSize(QSize(20, 20))
        self.indicator4.setMaximumSize(QSize(20, 20))

        self.horizontalLayout_4.addWidget(self.indicator4)

        self.label4 = QLabel(self.statusItem4)
        self.label4.setObjectName(u"label4")

        self.horizontalLayout_4.addWidget(self.label4)


        self.verticalLayout_2.addWidget(self.statusItem4)

        self.statusItem5 = QFrame(self.scrollAreaContents)
        self.statusItem5.setObjectName(u"statusItem5")
        self.statusItem5.setFrameShape(QFrame.Shape.StyledPanel)
        self.statusItem5.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.statusItem5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(10, 5, 10, 5)
        self.indicator5 = QLabel(self.statusItem5)
        self.indicator5.setObjectName(u"indicator5")
        self.indicator5.setMinimumSize(QSize(20, 20))
        self.indicator5.setMaximumSize(QSize(20, 20))

        self.horizontalLayout_5.addWidget(self.indicator5)

        self.label5 = QLabel(self.statusItem5)
        self.label5.setObjectName(u"label5")

        self.horizontalLayout_5.addWidget(self.label5)


        self.verticalLayout_2.addWidget(self.statusItem5)

        self.statusItem6 = QFrame(self.scrollAreaContents)
        self.statusItem6.setObjectName(u"statusItem6")
        self.statusItem6.setFrameShape(QFrame.Shape.StyledPanel)
        self.statusItem6.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.statusItem6)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(10, 5, 10, 5)
        self.indicator6 = QLabel(self.statusItem6)
        self.indicator6.setObjectName(u"indicator6")
        self.indicator6.setMinimumSize(QSize(20, 20))
        self.indicator6.setMaximumSize(QSize(20, 20))

        self.horizontalLayout_6.addWidget(self.indicator6)

        self.label6 = QLabel(self.statusItem6)
        self.label6.setObjectName(u"label6")

        self.horizontalLayout_6.addWidget(self.label6)


        self.verticalLayout_2.addWidget(self.statusItem6)

        self.statusItem7 = QFrame(self.scrollAreaContents)
        self.statusItem7.setObjectName(u"statusItem7")
        self.statusItem7.setFrameShape(QFrame.Shape.StyledPanel)
        self.statusItem7.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.statusItem7)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(10, 5, 10, 5)
        self.indicator7 = QLabel(self.statusItem7)
        self.indicator7.setObjectName(u"indicator7")
        self.indicator7.setMinimumSize(QSize(20, 20))
        self.indicator7.setMaximumSize(QSize(20, 20))

        self.horizontalLayout_7.addWidget(self.indicator7)

        self.label7 = QLabel(self.statusItem7)
        self.label7.setObjectName(u"label7")

        self.horizontalLayout_7.addWidget(self.label7)


        self.verticalLayout_2.addWidget(self.statusItem7)

        self.statusItem8 = QFrame(self.scrollAreaContents)
        self.statusItem8.setObjectName(u"statusItem8")
        self.statusItem8.setFrameShape(QFrame.Shape.StyledPanel)
        self.statusItem8.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.statusItem8)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(10, 5, 10, 5)
        self.indicator8 = QLabel(self.statusItem8)
        self.indicator8.setObjectName(u"indicator8")
        self.indicator8.setMinimumSize(QSize(20, 20))
        self.indicator8.setMaximumSize(QSize(20, 20))

        self.horizontalLayout_8.addWidget(self.indicator8)

        self.label8 = QLabel(self.statusItem8)
        self.label8.setObjectName(u"label8")

        self.horizontalLayout_8.addWidget(self.label8)


        self.verticalLayout_2.addWidget(self.statusItem8)

        self.statusItem9 = QFrame(self.scrollAreaContents)
        self.statusItem9.setObjectName(u"statusItem9")
        self.statusItem9.setFrameShape(QFrame.Shape.StyledPanel)
        self.statusItem9.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.statusItem9)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(10, 5, 10, 5)
        self.indicator9 = QLabel(self.statusItem9)
        self.indicator9.setObjectName(u"indicator9")
        self.indicator9.setMinimumSize(QSize(20, 20))
        self.indicator9.setMaximumSize(QSize(20, 20))

        self.horizontalLayout_9.addWidget(self.indicator9)

        self.label9 = QLabel(self.statusItem9)
        self.label9.setObjectName(u"label9")

        self.horizontalLayout_9.addWidget(self.label9)


        self.verticalLayout_2.addWidget(self.statusItem9)

        self.statusItem10 = QFrame(self.scrollAreaContents)
        self.statusItem10.setObjectName(u"statusItem10")
        self.statusItem10.setFrameShape(QFrame.Shape.StyledPanel)
        self.statusItem10.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.statusItem10)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(10, 5, 10, 5)
        self.indicator10 = QLabel(self.statusItem10)
        self.indicator10.setObjectName(u"indicator10")
        self.indicator10.setMinimumSize(QSize(20, 20))
        self.indicator10.setMaximumSize(QSize(20, 20))

        self.horizontalLayout_10.addWidget(self.indicator10)

        self.label10 = QLabel(self.statusItem10)
        self.label10.setObjectName(u"label10")

        self.horizontalLayout_10.addWidget(self.label10)


        self.verticalLayout_2.addWidget(self.statusItem10)

        self.statusScrollArea.setWidget(self.scrollAreaContents)

        self.contentLayout.addWidget(self.statusScrollArea)

        self.progressBar = QProgressBar(SplashScreen)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(40)

        self.contentLayout.addWidget(self.progressBar)

        self.statusLabel = QLabel(SplashScreen)
        self.statusLabel.setObjectName(u"statusLabel")

        self.contentLayout.addWidget(self.statusLabel, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout.addLayout(self.contentLayout)


        self.retranslateUi(SplashScreen)

        QMetaObject.connectSlotsByName(SplashScreen)
    # setupUi

    def retranslateUi(self, SplashScreen):
        SplashScreen.setWindowTitle(QCoreApplication.translate("SplashScreen", u"\u0110ang kh\u1edfi \u0111\u1ed9ng...", None))
        self.logoLabel.setText("")
        self.titleLabel.setText(QCoreApplication.translate("SplashScreen", u"Telegram Video Uploader", None))
        self.statusItem1.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemFrame", None))
        self.indicator1.setText("")
        self.label1.setText(QCoreApplication.translate("SplashScreen", u"Ki\u1ec3m tra k\u1ebft n\u1ed1i Internet", None))
        self.label1.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItem", None))
        self.statusItem2.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemFrame", None))
        self.indicator2.setText("")
        self.label2.setText(QCoreApplication.translate("SplashScreen", u"Ki\u1ec3m tra c\u1ea5u h\u00ecnh h\u1ec7 th\u1ed1ng", None))
        self.label2.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItem", None))
        self.statusItem3.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemFrame", None))
        self.indicator3.setText("")
        self.label3.setText(QCoreApplication.translate("SplashScreen", u"Thi\u1ebft l\u1eadp SSL cho Telethon", None))
        self.label3.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItem", None))
        self.statusItem4.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemFrame", None))
        self.indicator4.setText("")
        self.label4.setText(QCoreApplication.translate("SplashScreen", u"Kh\u1edfi t\u1ea1o t\u00e0i nguy\u00ean \u1ee9ng d\u1ee5ng", None))
        self.label4.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemPending", None))
        self.statusItem5.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemFrame", None))
        self.indicator5.setText("")
        self.label5.setText(QCoreApplication.translate("SplashScreen", u"Chu\u1ea9n b\u1ecb b\u1ed9 ph\u00e2n t\u00edch video", None))
        self.label5.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemPending", None))
        self.statusItem6.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemFrame", None))
        self.indicator6.setText("")
        self.label6.setText(QCoreApplication.translate("SplashScreen", u"Ki\u1ec3m tra k\u1ebft n\u1ed1i Telegram", None))
        self.label6.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemPending", None))
        self.statusItem7.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemFrame", None))
        self.indicator7.setText("")
        self.label7.setText(QCoreApplication.translate("SplashScreen", u"T\u1ea3i c\u00e1c th\u00e0nh ph\u1ea7n giao di\u1ec7n", None))
        self.label7.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemPending", None))
        self.statusItem8.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemFrame", None))
        self.indicator8.setText("")
        self.label8.setText(QCoreApplication.translate("SplashScreen", u"Ki\u1ec3m tra kh\u00f4ng gian l\u01b0u tr\u1eef", None))
        self.label8.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemPending", None))
        self.statusItem9.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemFrame", None))
        self.indicator9.setText("")
        self.label9.setText(QCoreApplication.translate("SplashScreen", u"T\u00ecm ki\u1ebfm c\u1eadp nh\u1eadt", None))
        self.label9.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemPending", None))
        self.statusItem10.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemFrame", None))
        self.indicator10.setText("")
        self.label10.setText(QCoreApplication.translate("SplashScreen", u"T\u1ed1i \u01b0u h\u00f3a hi\u1ec7u su\u1ea5t", None))
        self.label10.setProperty(u"class", QCoreApplication.translate("SplashScreen", u"statusItemPending", None))
        self.statusLabel.setText(QCoreApplication.translate("SplashScreen", u"\u0110ang chu\u1ea9n b\u1ecb b\u1ed9 ph\u00e2n t\u00edch video...", None))
    # retranslateUi

