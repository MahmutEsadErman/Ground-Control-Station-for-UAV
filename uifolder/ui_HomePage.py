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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_HomePage(object):
    def setupUi(self, HomePage):
        if not HomePage.objectName():
            HomePage.setObjectName(u"HomePage")
        HomePage.resize(1085, 578)
        self.gridLayout_2 = QGridLayout(HomePage)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.mapFrame = QWidget(HomePage)
        self.mapFrame.setObjectName(u"mapFrame")
        self.mapFrame.setMinimumSize(QSize(650, 0))
        self.mapFrame.setStyleSheet(u"")
        self.horizontalLayout_2 = QHBoxLayout(self.mapFrame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.gridLayout_2.addWidget(self.mapFrame, 0, 0, 1, 1)

        self.frame_right = QFrame(HomePage)
        self.frame_right.setObjectName(u"frame_right")
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
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.frame_2)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.frame_3 = QFrame(self.frame_2)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.frame_3)
        self.gridLayout.setObjectName(u"gridLayout")
        self.btn_undo = QPushButton(self.frame_3)
        self.btn_undo.setObjectName(u"btn_undo")

        self.gridLayout.addWidget(self.btn_undo, 6, 0, 1, 1)

        self.btn_move = QPushButton(self.frame_3)
        self.btn_move.setObjectName(u"btn_move")

        self.gridLayout.addWidget(self.btn_move, 4, 0, 1, 1)

        self.btn_waypoints = QPushButton(self.frame_3)
        self.btn_waypoints.setObjectName(u"btn_waypoints")

        self.gridLayout.addWidget(self.btn_waypoints, 5, 0, 1, 1)

        self.btn_setMission = QPushButton(self.frame_3)
        self.btn_setMission.setObjectName(u"btn_setMission")

        self.gridLayout.addWidget(self.btn_setMission, 6, 1, 1, 1)

        self.btn_movemarker = QPushButton(self.frame_3)
        self.btn_movemarker.setObjectName(u"btn_movemarker")

        self.gridLayout.addWidget(self.btn_movemarker, 5, 1, 1, 1)

        self.btn_takeoff = QPushButton(self.frame_3)
        self.btn_takeoff.setObjectName(u"btn_takeoff")

        self.gridLayout.addWidget(self.btn_takeoff, 4, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.frame_3)


        self.verticalLayout.addWidget(self.frame_2)


        self.gridLayout_2.addWidget(self.frame_right, 0, 1, 1, 1)


        self.retranslateUi(HomePage)

        QMetaObject.connectSlotsByName(HomePage)
    # setupUi

    def retranslateUi(self, HomePage):
        HomePage.setWindowTitle(QCoreApplication.translate("HomePage", u"Form", None))
        self.label.setText(QCoreApplication.translate("HomePage", u"butonlar label", None))
        self.btn_undo.setText(QCoreApplication.translate("HomePage", u"Undo", None))
        self.btn_move.setText(QCoreApplication.translate("HomePage", u"Move", None))
        self.btn_waypoints.setText(QCoreApplication.translate("HomePage", u"Put Waypoints", None))
        self.btn_setMission.setText(QCoreApplication.translate("HomePage", u"Set Mission", None))
        self.btn_movemarker.setText(QCoreApplication.translate("HomePage", u"Move Marker", None))
        self.btn_takeoff.setText(QCoreApplication.translate("HomePage", u"Takeoff", None))
    # retranslateUi

