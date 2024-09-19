import sys
import time

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QInputDialog
from PySide6.QtCore import Qt, QTimer

from CameraWidget import CameraWidget
from MapWidget import MapWidget
from Vehicle.ArdupilotConnection import MissionModes
from uifolder import Ui_HomePage

class HomePage(QWidget, Ui_HomePage):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        # Set Map Widget
        istanbulhavalimani = [41.27442, 28.727317]
        self.mapwidget = MapWidget(istanbulhavalimani)
        self.mapFrame.layout().addWidget(self.mapwidget)

        # Set Camera Widget
        self.cameraWidget = CameraWidget(self)
        self.cameraFrame.layout().addWidget(self.cameraWidget)

        # Show in another window buttons
        self.mapwidget.btn_AllocateWidget.clicked.connect(lambda: self.AllocateWidget(self.mapFrame, self.mapwidget))
        self.cameraWidget.btn_AllocateWidget.clicked.connect(lambda: self.AllocateWidget(self.cameraFrame, self.cameraWidget))

        # Buttons
        self.btn_chooseMode.clicked.connect(self.buttonFunctions)
        self.btn_undo.clicked.connect(self.buttonFunctions)
        self.btn_clearAll.clicked.connect(self.buttonFunctions)
        self.btn_setMission.clicked.connect(self.set_mission)

    def buttonFunctions(self):
        button = self.sender()

        if button.objectName() == "btn_chooseMode":
            if self.modes_comboBox.currentText() == "İşaretçi Modu":
                self.mapwidget.page().runJavaScript(f"map.on('click', moveMarkerByClick);")
                self.mapwidget.page().runJavaScript(f"map.off('click', drawRectangle);")
                self.mapwidget.page().runJavaScript(f"map.off('click', putWaypointEvent);")
            if self.modes_comboBox.currentText() == "Alan Seçimi Modu":
                self.mapwidget.page().runJavaScript(f"map.off('click', putWaypointEvent);")
                self.mapwidget.page().runJavaScript(f"map.off('click', moveMarkerByClick);")
                self.mapwidget.page().runJavaScript(f"map.on('click', drawRectangle);")
            if self.modes_comboBox.currentText() == "Waypoint Modu":
                self.mapwidget.page().runJavaScript(f"map.off('click', moveMarkerByClick);")
                self.mapwidget.page().runJavaScript(f"map.off('click', drawRectangle);")
                self.mapwidget.page().runJavaScript(f"map.on('click', putWaypointEvent);")
        if button.objectName() == "btn_clearAll":
            self.mapwidget.page().runJavaScript(f"clearAll();")
        if button.objectName() == "btn_undo":
            self.mapwidget.page().runJavaScript("undoWaypoint();")
        if button.objectName() == "btn_chooseField":
            print("Drawing Rectangle Mode")
            self.mapwidget.page().runJavaScript(f"map.off('click', putWaypoint);")
            self.mapwidget.page().runJavaScript(f"map.on('click', drawRectangle);")

    def set_mission(self):
        altitude, okPressed = QInputDialog.getText(self, "Enter Altitude", "Altitude:", text="10")
        altitude = int(altitude)
        if okPressed:
            if self.modes_comboBox.currentText() == 'Waypoint Modu':
                self.mapwidget.page().runJavaScript("setMission(1);")
                QTimer().singleShot(1000, lambda: self.parent.connectionThread.set_mission(MissionModes.WAYPOINTS, self.mapwidget.mission, altitude))
            else:
                self.mapwidget.page().runJavaScript("setMission(0);")
                QTimer().singleShot(1000, lambda: self.parent.connectionThread.set_mission(MissionModes.EXPLORATION, self.mapwidget.mission, altitude))

    def AllocateWidget(self, parent, child):
        if child.isAttached:
            parent.layout().removeWidget(child)
            self.new_window = QMainWindow()
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
    window = HomePage()
    window.show()
    sys.exit(app.exec())
