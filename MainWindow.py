import sys

from PySide6 import QtGui
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QSizePolicy, QSizeGrip, QComboBox, QFrame, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QEvent, QSize, QPropertyAnimation, QEasingCurve, QTimer

from TargetsPage import TargetsPage
from Connection import ConnectionThread
from HomePage import HomePage
from IndicatorsPage import IndicatorsPage
from uifolder import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Frameless Window
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set initial windows size
        self.state = 0 # maximized or not
        self.screenSize = QApplication.primaryScreen().size()
        # self.resize(1280, 800)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        # Move Window to Center
        self.move(self.screenSize.width() / 2 - self.width() / 2, self.screenSize.height() / 2 - self.height() / 2)

        # Set Font
        QtGui.QFontDatabase.addApplicationFont('uifolder/assets/fonts/segoeui.ttf')
        QtGui.QFontDatabase.addApplicationFont('uifolder/assets/fonts/segoeuib.ttf')

        # Sizegrip (To Resize Window)
        self.sizegrip = QSizeGrip(self.frame_size_grip)
        self.sizegrip.setStyleSheet("background-image: url(uifolder/assets/icons/16x16/cil-size-grip.png);width: 20px; height: 20px; margin 0px; padding: 0px;")

        # Set Initial Baud Rate to Combobox
        self.combobox_baudrate.setCurrentText('115200')

        # Setting Pages
        self.homepage = HomePage()
        self.indicatorspage = IndicatorsPage()
        self.targetspage = TargetsPage()
        self.indicatorswidget = QWidget(layout=QVBoxLayout())
        self.indicatorswidget.layout().addWidget(self.indicatorspage)
        self.stackedWidget.addWidget(self.homepage)
        self.stackedWidget.addWidget(self.targetspage)
        self.stackedWidget.addWidget(self.indicatorswidget)
        self.stackedWidget.setCurrentWidget(self.homepage)

        # Connection Thread
        self.connectionThread = ConnectionThread(self)

        #  SET BUTTONS
        #  Main Window buttons
        self.btn_close.setIcon(QtGui.QIcon('uifolder/assets/icons/16x16/cil-x.png'))
        self.btn_close.clicked.connect(lambda: sys.exit())
        self.btn_maximize_restore.setIcon(QtGui.QIcon('uifolder/assets/icons/16x16/cil-window-maximize.png'))
        self.btn_maximize_restore.clicked.connect(self.maximize_restore)
        self.btn_minimize.setIcon(QtGui.QIcon('uifolder/assets/icons/16x16/cil-window-minimize.png'))
        self.btn_minimize.clicked.connect(lambda: self.showMinimized())

        self.btn_home_page.setDisabled(True)
        self.disabledbutton = self.btn_home_page
        self.setButton(self.btn_toggle_menu, 'uifolder/assets/icons/24x24/cil-menu.png')
        self.setButton(self.btn_home_page, 'uifolder/assets/icons/24x24/cil-home.png')
        self.setButton(self.btn_indicators_page, 'uifolder/assets/icons/24x24/cil-speedometer.png')
        self.setButton(self.btn_targets_page, 'uifolder/assets/icons/24x24/cil-user.png')
        self.btn_connect.setIcon(QtGui.QIcon('uifolder/assets/icons/24x24/cil-link-broken.png'))

        # Buttons to give orders to vehicle
        self.btn_connect.clicked.connect(self.connectToVehicle)
        self.homepage.btn_move.clicked.connect(self.connectionThread.goto_markers_pos)
        self.homepage.btn_takeoff.clicked.connect(lambda: self.connectionThread.takeoff(10))

        # Button to Allocate Windows
        self.indicatorspage.btn_AllocateWidget.clicked.connect(lambda: self.AllocateWidget(self.indicatorswidget, self.indicatorspage))

        # To move the window only from top frame
        self.label_title_bar_top.installEventFilter(self)


    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    # To take events from child widgets
    def eventFilter(self, obj, event):
        if obj == self.label_title_bar_top:
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
            self.btn_maximize_restore.setToolTip("Maximize")
            self.btn_maximize_restore.setIcon(QtGui.QIcon(u"uifolder/assets/icons/16x16/cil-window-maximize.png"))
            self.showNormal()
            self.state = 0
        else:
            self.btn_maximize_restore.setToolTip("Restore")
            self.btn_maximize_restore.setIcon(QtGui.QIcon(u"uifolder/assets/icons/16x16/cil-window-restore.png"))
            self.showMaximized()
            self.state = 1

    def buttonFunctions(self):
        button = self.sender()
        # Toggle Button
        if button.objectName() == "btn_toggle_menu":
            width = self.frame_left_menu.width()
            maxWidth = 220
            standard = 70
            # SET MAX WIDTH
            if width == standard:
                widthExtended = maxWidth
                self.btn_home_page.setText("    Home")
                self.btn_indicators_page.setText("   Indicators")
                self.btn_targets_page.setText("     Targets")
            else:
                widthExtended = standard
                self.btn_home_page.setText("")
                self.btn_indicators_page.setText("")
                self.btn_targets_page.setText("")

            # ANIMATION
            self.animation = QPropertyAnimation(self.frame_left_menu, b"minimumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()

            animation = QPropertyAnimation(button, b"geometry")
            animation.setDuration(2000)
            animation.setStartValue(button.geometry())
            animation.setEndValue(button.geometry())
            animation.setEasingCurve(QEasingCurve.InOutQuad)

            # Start the animation
            animation.start()
        else:
            self.disabledbutton.setDisabled(False)
            self.disabledbutton = button
            self.disabledbutton.setDisabled(True)

        # PAGE HOME
        if button.objectName() == "btn_home_page":
            self.stackedWidget.setCurrentWidget(self.homepage)
            self.label_top_info_2.setText("| HOME")

        # PAGE NEW USER
        if button.objectName() == "btn_indicators_page":
            self.stackedWidget.setCurrentWidget(self.indicatorswidget)
            self.label_top_info_2.setText("| Indicators")

        # PAGE WIDGETS
        if button.objectName() == "btn_targets_page":
            self.stackedWidget.setCurrentWidget(self.targetspage)
            self.label_top_info_2.setText("| Targets")

    def connectToVehicle(self):
        self.connectionThread.setBaudRate(int(self.combobox_baudrate.currentText()))
        self.connectionThread.setConnectionString(self.combobox_connectionstring.currentText())
        self.connectionThread.start()

    def AllocateWidget(self, parent, child):
        if child.isAttached:
            self.stackedWidget.setCurrentWidget(self.homepage)
            parent.layout().removeWidget(child)
            self.new_window = QMainWindow(styleSheet="background-color: rgb(44, 49, 60);" )
            self.new_window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
            child.btn_AllocateWidget.setIcon(QIcon("uifolder/assets/icons/16x16/cil-arrow-bottom.png"))
            self.new_window.setCentralWidget(child)
            self.new_window.show()
            child.isAttached = False
        else:
            parent.layout().addWidget(child)
            self.new_window.setCentralWidget(None)
            self.new_window.close()
            child.btn_AllocateWidget.setIcon(QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png"))
            child.isAttached = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
