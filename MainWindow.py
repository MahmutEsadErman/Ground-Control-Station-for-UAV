import sys

from PySide6 import QtGui
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow, QSizePolicy, QSizeGrip, QComboBox
from PySide6.QtCore import QFile, Qt, QEvent, QSize, QPropertyAnimation, QEasingCurve

from TargetsPage import TargetsPage
from Connection import *
from HomePage import HomePage
from IndicatorsPage import IndicatorsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Frameless Window
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Load the ui file
        ui_file_name = "uifolder/BaseGUI.ui"
        ui_file = QFile(ui_file_name)
        self.ui = QUiLoader().load(ui_file)
        ui_file.close()
        self.setCentralWidget(self.ui)

        # Set Window Title
        self.setWindowTitle("Nebula GCS")

        # Set initial windows size
        self.state = 0 # maximized or not
        self.screenSize = QApplication.primaryScreen().size()
        windowRatio = 3/4
        self.startSize = QSize(self.screenSize.width() * windowRatio, self.screenSize.height() * windowRatio)
        self.resize(self.startSize)
        self.setMinimumSize(self.startSize)
        self.setMaximumSize(self.screenSize)
        self.ui.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        # Move Window to Center
        self.move(self.screenSize.width() / 2 - self.startSize.width() / 2, self.screenSize.height() / 2 - self.startSize.height() / 2)

        # Set Font
        QtGui.QFontDatabase.addApplicationFont('assets/fonts/segoeui.ttf')
        QtGui.QFontDatabase.addApplicationFont('assets/fonts/segoeuib.ttf')

        # Sizegrip (To Resize Window)
        self.sizegrip = QSizeGrip(self.ui.frame_size_grip)
        self.sizegrip.setStyleSheet("background-image: url(assets/icons/16x16/cil-size-grip.png);width: 20px; height: 20px; margin 0px; padding: 0px;")

        # Set Initial Baud Rate to Combobox
        self.ui.combobox_baudrate.setCurrentText('115200')

        # Setting Pages
        self.homepage = HomePage()
        self.indicatorspage = IndicatorsPage()
        self.targetspage = TargetsPage()
        self.ui.stackedWidget.addWidget(self.homepage)
        self.ui.stackedWidget.addWidget(self.targetspage)
        self.ui.stackedWidget.addWidget(self.homepage)
        self.ui.stackedWidget.addWidget(self.indicatorspage)
        self.ui.stackedWidget.setCurrentWidget(self.homepage)

        # Connection Thread
        self.connectionThread = ConnectionThread(self.ui.btn_connect, self.homepage.mapwidget, self.indicatorspage)
        self.connectionThread.vehicleConnected.connect(handleConnectedVehicle)
        self.connectionThread.updateData.connect(updateData)
        self.connectionThread.connectionLost.connect(connectionLost)

        #  SET BUTTONS
        #  Main Window buttons
        self.ui.btn_close.setIcon(QtGui.QIcon('assets/icons/16x16/cil-x.png'))
        self.ui.btn_close.clicked.connect(lambda: sys.exit())
        self.ui.btn_maximize_restore.setIcon(QtGui.QIcon('assets/icons/16x16/cil-window-maximize.png'))
        self.ui.btn_maximize_restore.clicked.connect(self.maximize_restore)
        self.ui.btn_minimize.setIcon(QtGui.QIcon('assets/icons/16x16/cil-window-minimize.png'))
        self.ui.btn_minimize.clicked.connect(lambda: self.showMinimized())

        self.ui.btn_home_page.setDisabled(True)
        self.disabledbutton = self.ui.btn_home_page
        self.setButton(self.ui.btn_toggle_menu, 'assets/icons/24x24/cil-menu.png')
        self.setButton(self.ui.btn_home_page, 'assets/icons/24x24/cil-home.png')
        self.setButton(self.ui.btn_indicators_page, 'assets/icons/24x24/cil-speedometer.png')
        self.setButton(self.ui.btn_targets_page, 'assets/icons/24x24/cil-user.png')
        self.ui.btn_connect.setIcon(QtGui.QIcon('assets/icons/24x24/cil-link-broken.png'))

        # Buttons to give orders to vehicle
        self.ui.btn_connect.clicked.connect(self.connectToVehicle)
        self.homepage.ui.btn_move.clicked.connect(self.connectionThread.goto_markers_pos)
        self.homepage.ui.btn_takeoff.clicked.connect(lambda: self.connectionThread.takeoff(10))

        # To move the window only from top frame
        self.ui.label_title_bar_top.installEventFilter(self)


    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    # To take events from child widgets
    def eventFilter(self, obj, event):
        if obj == self.ui.label_title_bar_top:
            # Maximize and restore when double click
            if event.type() == QEvent.MouseButtonDblClick:
                self.maximize_restore()
            # Drag move window
            if event.type() == QEvent.MouseMove:
                if event.buttons() == Qt.LeftButton:
                    self.setCursor(Qt.SizeAllCursor)
                    self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                    self.dragPos = event.globalPosition().toPoint()
                    return True
            if event.type() == QEvent.MouseButtonRelease:
                self.setCursor(Qt.ArrowCursor)
        return super().eventFilter(obj, event)

    def setButton(self, button, icon):
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy3)
        button.setMinimumSize(QSize(0, 70))
        button.setLayoutDirection(Qt.LeftToRight)
        button.setIcon(QtGui.QIcon(icon))
        button.clicked.connect(self.buttonFunctions)

    def maximize_restore(self):
        if self.state == 1:
            self.ui.btn_maximize_restore.setToolTip("Maximize")
            self.ui.btn_maximize_restore.setIcon(QtGui.QIcon(u"assets/icons/16x16/cil-window-maximize.png"))
            self.showNormal()
            self.state = 0
        else:
            self.ui.btn_maximize_restore.setToolTip("Restore")
            self.ui.btn_maximize_restore.setIcon(QtGui.QIcon(u"assets/icons/16x16/cil-window-restore.png"))
            self.showMaximized()
            self.state = 1

    def buttonFunctions(self):
        button = self.sender()
        # Toggle Button
        if button.objectName() == "btn_toggle_menu":
            width = self.ui.frame_left_menu.width()
            maxWidth = 220
            standard = 70
            # SET MAX WIDTH
            if width == standard:
                widthExtended = maxWidth
                self.ui.btn_home_page.setText("    Home")
                self.ui.btn_indicators_page.setText("   Indicators")
                self.ui.btn_targets_page.setText("     Targets")
            else:
                widthExtended = standard
                self.ui.btn_home_page.setText("")
                self.ui.btn_indicators_page.setText("")
                self.ui.btn_targets_page.setText("")

            # ANIMATION
            self.animation = QPropertyAnimation(self.ui.frame_left_menu, b"minimumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()
        else:
            self.disabledbutton.setDisabled(False)
            self.disabledbutton = button
            self.disabledbutton.setDisabled(True)

        # PAGE HOME
        if button.objectName() == "btn_home_page":
            self.ui.stackedWidget.setCurrentWidget(self.homepage)
            self.ui.label_top_info_2.setText("| HOME")

        # PAGE NEW USER
        if button.objectName() == "btn_indicators_page":
            self.ui.stackedWidget.setCurrentWidget(self.indicatorspage)
            self.ui.label_top_info_2.setText("| Indicators")

        # PAGE WIDGETS
        if button.objectName() == "btn_targets_page":
            self.ui.stackedWidget.setCurrentWidget(self.targetspage)
            self.ui.label_top_info_2.setText("| Targets")

    def connectToVehicle(self):
        self.connectionThread.setBaudRate(int(self.ui.combobox_baudrate.currentText()))
        self.connectionThread.setConnectionString(self.ui.combobox_connectionstring.currentText())
        self.connectionThread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
