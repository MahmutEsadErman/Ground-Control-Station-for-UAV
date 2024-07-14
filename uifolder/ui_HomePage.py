# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'HomePage.ui'
##
## Created by: Qt User Interface Compiler version 6.5.3
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QPushButton, QSizePolicy, QTabWidget,
    QTextBrowser, QVBoxLayout, QWidget)

class Ui_HomePage(object):
    def setupUi(self, HomePage):
        if not HomePage.objectName():
            HomePage.setObjectName(u"HomePage")
        HomePage.resize(1085, 578)
        HomePage.setStyleSheet(u"")
        self.gridLayout_2 = QGridLayout(HomePage)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.frame_right = QFrame(HomePage)
        self.frame_right.setObjectName(u"frame_right")
        self.frame_right.setStyleSheet(u"QFrame{border: None;}")
        self.frame_right.setFrameShape(QFrame.StyledPanel)
        self.frame_right.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_right)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.cameraFrame = QWidget(self.frame_right)
        self.cameraFrame.setObjectName(u"cameraFrame")
        self.cameraFrame.setStyleSheet(u"")
        self.horizontalLayout_3 = QHBoxLayout(self.cameraFrame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")

        self.verticalLayout.addWidget(self.cameraFrame)

        self.frame_2 = QFrame(self.frame_right)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setStyleSheet(u"")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.frame_2)
        self.tabWidget.setObjectName(u"tabWidget")
        self.Buttons = QWidget()
        self.Buttons.setObjectName(u"Buttons")
        self.verticalLayout_3 = QVBoxLayout(self.Buttons)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.widget = QWidget(self.Buttons)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.modes_comboBox = QComboBox(self.widget)
        self.modes_comboBox.addItem("")
        self.modes_comboBox.addItem("")
        self.modes_comboBox.addItem("")
        self.modes_comboBox.addItem("")
        self.modes_comboBox.setObjectName(u"modes_comboBox")

        self.horizontalLayout.addWidget(self.modes_comboBox)

        self.btn_chooseMode = QPushButton(self.widget)
        self.btn_chooseMode.setObjectName(u"btn_chooseMode")

        self.horizontalLayout.addWidget(self.btn_chooseMode)

        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 1)

        self.verticalLayout_3.addWidget(self.widget)

        self.btn_setMission = QPushButton(self.Buttons)
        self.btn_setMission.setObjectName(u"btn_setMission")

        self.verticalLayout_3.addWidget(self.btn_setMission)

        self.btn_undo = QPushButton(self.Buttons)
        self.btn_undo.setObjectName(u"btn_undo")

        self.verticalLayout_3.addWidget(self.btn_undo)

        self.btn_clearAll = QPushButton(self.Buttons)
        self.btn_clearAll.setObjectName(u"btn_clearAll")

        self.verticalLayout_3.addWidget(self.btn_clearAll)

        self.btn_takeoff = QPushButton(self.Buttons)
        self.btn_takeoff.setObjectName(u"btn_takeoff")

        self.verticalLayout_3.addWidget(self.btn_takeoff)

        self.btn_move = QPushButton(self.Buttons)
        self.btn_move.setObjectName(u"btn_move")

        self.verticalLayout_3.addWidget(self.btn_move)

        self.tabWidget.addTab(self.Buttons, "")
        self.Console = QWidget()
        self.Console.setObjectName(u"Console")
        self.textBrowser = QTextBrowser(self.Console)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(60, 20, 256, 192))
        self.tabWidget.addTab(self.Console, "")

        self.verticalLayout_2.addWidget(self.tabWidget)


        self.verticalLayout.addWidget(self.frame_2)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)

        self.gridLayout_2.addWidget(self.frame_right, 0, 1, 1, 1)

        self.mapFrame = QWidget(HomePage)
        self.mapFrame.setObjectName(u"mapFrame")
        self.mapFrame.setMinimumSize(QSize(650, 0))
        self.mapFrame.setStyleSheet(u"")
        self.horizontalLayout_2 = QHBoxLayout(self.mapFrame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.gridLayout_2.addWidget(self.mapFrame, 0, 0, 1, 1)


        self.retranslateUi(HomePage)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(HomePage)
    # setupUi

    def retranslateUi(self, HomePage):
        HomePage.setWindowTitle(QCoreApplication.translate("HomePage", u"Form", None))
        self.modes_comboBox.setItemText(0, QCoreApplication.translate("HomePage", u"Harita Modu Se\u00e7", None))
        self.modes_comboBox.setItemText(1, QCoreApplication.translate("HomePage", u"\u0130\u015faret\u00e7i Modu", None))
        self.modes_comboBox.setItemText(2, QCoreApplication.translate("HomePage", u"Alan Se\u00e7imi Modu", None))
        self.modes_comboBox.setItemText(3, QCoreApplication.translate("HomePage", u"Waypoint Modu", None))

        self.btn_chooseMode.setText(QCoreApplication.translate("HomePage", u"Modu Se\u00e7", None))
        self.btn_setMission.setText(QCoreApplication.translate("HomePage", u"G\u00f6revi Tan\u0131mla", None))
        self.btn_undo.setText(QCoreApplication.translate("HomePage", u"Geri Al", None))
        self.btn_clearAll.setText(QCoreApplication.translate("HomePage", u"Hepsini Temizle", None))
        self.btn_takeoff.setText(QCoreApplication.translate("HomePage", u"Kalk", None))
        self.btn_move.setText(QCoreApplication.translate("HomePage", u"Noktaya Git", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Buttons), QCoreApplication.translate("HomePage", u"Butonlar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Console), QCoreApplication.translate("HomePage", u"Konsol", None))
    # retranslateUi

