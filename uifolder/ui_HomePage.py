# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'HomePage.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
        HomePage.resize(1097, 620)
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
        self.mission = QWidget()
        self.mission.setObjectName(u"mission")
        self.verticalLayout_3 = QVBoxLayout(self.mission)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.frame = QFrame(self.mission)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.widget = QWidget(self.frame)
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

        self.verticalLayout_4.addWidget(self.widget)

        self.btn_setMission = QPushButton(self.frame)
        self.btn_setMission.setObjectName(u"btn_setMission")

        self.verticalLayout_4.addWidget(self.btn_setMission)

        self.btn_undo = QPushButton(self.frame)
        self.btn_undo.setObjectName(u"btn_undo")

        self.verticalLayout_4.addWidget(self.btn_undo)

        self.btn_clearAll = QPushButton(self.frame)
        self.btn_clearAll.setObjectName(u"btn_clearAll")

        self.verticalLayout_4.addWidget(self.btn_clearAll)


        self.verticalLayout_3.addWidget(self.frame)

        self.btn_antenna = QPushButton(self.mission)
        self.btn_antenna.setObjectName(u"btn_antenna")
        self.btn_antenna.setStyleSheet(u"QPushButton{\n"
"	border-radius: 4px;\n"
"	\n"
"	background-color: qlineargradient(spread:pad, x1:0.139, y1:0.862773, x2:1, y2:0.017, stop:0.159204 rgba(99, 18, 24, 255), stop:1 rgba(165, 29, 45, 252));\n"
"}\n"
"QPushButton:hover{ \n"
"	background-color:qlineargradient(spread:pad, x1:0.139, y1:0.862773, x2:1, y2:0.017, stop:0.0646766 rgba(89, 22, 27, 255), stop:0.527363 rgba(165, 29, 45, 252))\n"
"}\n"
"QPushButton:pressed{\n"
"  padding-left: 5px;\n"
"	padding-top: 5px;\n"
"	background-color: qlineargradient(spread:pad, x1:0.139, y1:0.862773, x2:1, y2:0.017, stop:0.159204 rgba(99, 18, 24, 200), stop:1 rgba(165, 29, 45, 200));\n"
"}\n"
"QPushButton:disabled{ \n"
"	background-color: qlineargradient(spread:pad, x1:0.139, y1:0.862773, x2:1, y2:0.017, stop:0.159204 rgba(14, 74, 89, 255), stop:1 rgba(77, 149, 47, 255));\n"
"}")

        self.verticalLayout_3.addWidget(self.btn_antenna)

        self.frame_3 = QFrame(self.mission)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.btn_startMission = QPushButton(self.frame_3)
        self.btn_startMission.setObjectName(u"btn_startMission")

        self.verticalLayout_5.addWidget(self.btn_startMission)

        self.btn_abort = QPushButton(self.frame_3)
        self.btn_abort.setObjectName(u"btn_abort")

        self.verticalLayout_5.addWidget(self.btn_abort)

        self.btn_rtl = QPushButton(self.frame_3)
        self.btn_rtl.setObjectName(u"btn_rtl")

        self.verticalLayout_5.addWidget(self.btn_rtl)


        self.verticalLayout_3.addWidget(self.frame_3)

        self.tabWidget.addTab(self.mission, "")
        self.guided = QWidget()
        self.guided.setObjectName(u"guided")
        self.verticalLayout_6 = QVBoxLayout(self.guided)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.btn_takeoff = QPushButton(self.guided)
        self.btn_takeoff.setObjectName(u"btn_takeoff")

        self.verticalLayout_6.addWidget(self.btn_takeoff)

        self.btn_move = QPushButton(self.guided)
        self.btn_move.setObjectName(u"btn_move")

        self.verticalLayout_6.addWidget(self.btn_move)

        self.btn_track_all = QPushButton(self.guided)
        self.btn_track_all.setObjectName(u"btn_track_all")

        self.verticalLayout_6.addWidget(self.btn_track_all)

        self.btn_land = QPushButton(self.guided)
        self.btn_land.setObjectName(u"btn_land")

        self.verticalLayout_6.addWidget(self.btn_land)

        self.btn_rtl_2 = QPushButton(self.guided)
        self.btn_rtl_2.setObjectName(u"btn_rtl_2")

        self.verticalLayout_6.addWidget(self.btn_rtl_2)

        self.tabWidget.addTab(self.guided, "")
        self.Console = QWidget()
        self.Console.setObjectName(u"Console")
        self.verticalLayout_7 = QVBoxLayout(self.Console)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.textBrowser = QTextBrowser(self.Console)
        self.textBrowser.setObjectName(u"textBrowser")

        self.verticalLayout_7.addWidget(self.textBrowser)

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

        self.tabWidget.setCurrentIndex(1)


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
        self.btn_antenna.setText(QCoreApplication.translate("HomePage", u"Anten Takibi", None))
        self.btn_startMission.setText(QCoreApplication.translate("HomePage", u"G\u00f6reve Ba\u015fla", None))
        self.btn_abort.setText(QCoreApplication.translate("HomePage", u"Takibi B\u0131rak", None))
        self.btn_rtl.setText(QCoreApplication.translate("HomePage", u"Eve D\u00f6n", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.mission), QCoreApplication.translate("HomePage", u"Mission", None))
        self.btn_takeoff.setText(QCoreApplication.translate("HomePage", u"Kalk", None))
        self.btn_move.setText(QCoreApplication.translate("HomePage", u"Noktaya Git", None))
        self.btn_track_all.setText(QCoreApplication.translate("HomePage", u"G\u00f6rd\u00fc\u011f\u00fcn\u00fc Takip Et", None))
        self.btn_land.setText(QCoreApplication.translate("HomePage", u"\u0130ni\u015f Yap", None))
        self.btn_rtl_2.setText(QCoreApplication.translate("HomePage", u"Eve D\u00f6n", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.guided), QCoreApplication.translate("HomePage", u"Guided", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Console), QCoreApplication.translate("HomePage", u"Konsol", None))
    # retranslateUi

