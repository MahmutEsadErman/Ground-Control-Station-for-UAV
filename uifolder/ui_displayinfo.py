# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'displayinfo.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QLabel,
    QProgressBar, QPushButton, QSizePolicy, QWidget)

class Ui_DisplayInfoWidget(object):
    def setupUi(self, DisplayInfoWidget):
        if not DisplayInfoWidget.objectName():
            DisplayInfoWidget.setObjectName(u"DisplayInfoWidget")
        DisplayInfoWidget.resize(444, 444)
        self.groupBox = QGroupBox(DisplayInfoWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(20, 10, 381, 271))
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.velocity = QLabel(self.groupBox)
        self.velocity.setObjectName(u"velocity")

        self.gridLayout.addWidget(self.velocity, 3, 1, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)

        self.armable = QLabel(self.groupBox)
        self.armable.setObjectName(u"armable")
        self.armable.setStyleSheet(u"border-left-color: rgb(0, 118, 201);")

        self.gridLayout.addWidget(self.armable, 0, 1, 1, 1)

        self.mode = QLabel(self.groupBox)
        self.mode.setObjectName(u"mode")

        self.gridLayout.addWidget(self.mode, 1, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)

        self.altitude = QLabel(self.groupBox)
        self.altitude.setObjectName(u"altitude")

        self.gridLayout.addWidget(self.altitude, 4, 1, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)

        self.positionLabel = QLabel(self.groupBox)
        self.positionLabel.setObjectName(u"positionLabel")

        self.gridLayout.addWidget(self.positionLabel, 2, 1, 1, 1)

        self.progressBar = QProgressBar(DisplayInfoWidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(20, 310, 291, 23))
        self.progressBar.setValue(24)
        self.takeoffButton = QPushButton(DisplayInfoWidget)
        self.takeoffButton.setObjectName(u"takeoffButton")
        self.takeoffButton.setGeometry(QRect(320, 310, 89, 25))
        self.takeoffButton.setStyleSheet(u"color: rgb(246, 245, 244);\n"
"background-color: rgb(94, 92, 100);\n"
"")
        self.goButton = QPushButton(DisplayInfoWidget)
        self.goButton.setObjectName(u"goButton")
        self.goButton.setGeometry(QRect(30, 350, 89, 25))
        self.goButton.setStyleSheet(u"color: rgb(246, 245, 244);\n"
"background-color: rgb(94, 92, 100);\n"
"")
        self.returnButton = QPushButton(DisplayInfoWidget)
        self.returnButton.setObjectName(u"returnButton")
        self.returnButton.setGeometry(QRect(300, 350, 89, 25))
        self.returnButton.setStyleSheet(u"color: rgb(246, 245, 244);\n"
"background-color: rgb(94, 92, 100);\n"
"")
        self.stopButton = QPushButton(DisplayInfoWidget)
        self.stopButton.setObjectName(u"stopButton")
        self.stopButton.setGeometry(QRect(170, 350, 89, 25))
        self.stopButton.setStyleSheet(u"color: rgb(246, 245, 244);\n"
"background-color: rgb(94, 92, 100);\n"
"")

        self.retranslateUi(DisplayInfoWidget)

        QMetaObject.connectSlotsByName(DisplayInfoWidget)
    # setupUi

    def retranslateUi(self, DisplayInfoWidget):
        DisplayInfoWidget.setWindowTitle(QCoreApplication.translate("DisplayInfoWidget", u"Ground Station", None))
        self.groupBox.setTitle(QCoreApplication.translate("DisplayInfoWidget", u"Info", None))
        self.velocity.setText(QCoreApplication.translate("DisplayInfoWidget", u"-", None))
        self.label_4.setText(QCoreApplication.translate("DisplayInfoWidget", u"armable:", None))
        self.label_3.setText(QCoreApplication.translate("DisplayInfoWidget", u"altitude", None))
        self.armable.setText(QCoreApplication.translate("DisplayInfoWidget", u"-", None))
        self.mode.setText(QCoreApplication.translate("DisplayInfoWidget", u"-", None))
        self.label_2.setText(QCoreApplication.translate("DisplayInfoWidget", u"velocity:", None))
        self.altitude.setText(QCoreApplication.translate("DisplayInfoWidget", u"-", None))
        self.label.setText(QCoreApplication.translate("DisplayInfoWidget", u"mode: ", None))
        self.label_5.setText(QCoreApplication.translate("DisplayInfoWidget", u"position", None))
        self.positionLabel.setText(QCoreApplication.translate("DisplayInfoWidget", u"-", None))
        self.takeoffButton.setText(QCoreApplication.translate("DisplayInfoWidget", u"Take Off", None))
        self.goButton.setText(QCoreApplication.translate("DisplayInfoWidget", u"go", None))
        self.returnButton.setText(QCoreApplication.translate("DisplayInfoWidget", u"return back", None))
        self.stopButton.setText(QCoreApplication.translate("DisplayInfoWidget", u"stop", None))
    # retranslateUi

