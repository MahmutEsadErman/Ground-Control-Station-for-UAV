import sys
import time

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QInputDialog
from PySide6.QtCore import Qt, QTimer

from CameraWidget import CameraWidget
from MapWidget import MapWidget
from uifolder import Ui_HomePage
from Vehicle.ArdupilotConnection import MissionModes

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
        self.btn_antenna.hide()

        # --- Follow Parameters & Control UI ---
        from PySide6.QtWidgets import QGroupBox, QFormLayout, QSpinBox, QHBoxLayout, QLabel, QPushButton
        self.follow_groupbox = QGroupBox("Drone Takip Parametreleri")
        self.follow_layout = QFormLayout()
        
        # Follow Distance
        self.spin_follow_distance = QSpinBox()
        self.spin_follow_distance.setRange(1, 100)
        self.spin_follow_distance.setValue(5)
        self.spin_follow_distance.setSuffix(" m")
        self.follow_layout.addRow("Takip Mesafesi:", self.spin_follow_distance)
        
        # Follow Height
        self.spin_follow_height = QSpinBox()
        self.spin_follow_height.setRange(1, 100)
        self.spin_follow_height.setValue(3)
        self.spin_follow_height.setSuffix(" m")
        self.follow_layout.addRow("Takip Yüksekliği:", self.spin_follow_height)

        # Timeout
        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(1, 300)
        self.spin_timeout.setValue(10)
        self.spin_timeout.setSuffix(" sn")
        self.follow_layout.addRow("Zaman Aşımı (Timeout):", self.spin_timeout)
        
        # Buttons
        self.btn_set_follow_params = QPushButton("Parametreleri Güncelle")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_set_follow_params)
        
        self.follow_groupbox.setLayout(self.follow_layout)
        self.verticalLayout_6.insertWidget(1, self.follow_groupbox)
        self.verticalLayout_6.insertLayout(2, btn_layout)

        # Connect new buttons
        self.btn_set_follow_params.clicked.connect(self.update_follow_params)
        # --------------------------------------

    def update_follow_params(self):
        dist = self.spin_follow_distance.value()
        height = self.spin_follow_height.value()
        timeout = self.spin_timeout.value()
        print(f"Takip Parametreleri Güncellendi - Mesafe: {dist}m, Yükseklik: {height}m, Timeout: {timeout}sn")
        # Ensure connectionThread exists and send params via ROS service
        if hasattr(self.parent, 'connectionThread') and self.parent.connectionThread:
            self.parent.connectionThread.set_follow_parameters(dist, height, timeout)

    def buttonFunctions(self):
        button = self.sender()

        if button.objectName() == "btn_chooseMode":
            if self.modes_comboBox.currentText() == "İşaretçi Modu":
                self.mapwidget.page().runJavaScript(f"map.on('click', moveMarkerByClick);")
                self.mapwidget.page().runJavaScript(f"map.off('click', drawRectangle);")
                self.mapwidget.page().runJavaScript(f"map.off('click', putWaypointEvent);")
                self.mapwidget.page().runJavaScript(f"if(!map.hasLayer(mymarker)) mymarker.addTo(map);")
            if self.modes_comboBox.currentText() == "Alan Seçimi Modu":
                self.mapwidget.page().runJavaScript(f"map.off('click', putWaypointEvent);")
                self.mapwidget.page().runJavaScript(f"map.off('click', moveMarkerByClick);")
                self.mapwidget.page().runJavaScript(f"map.on('click', drawRectangle);")
                self.mapwidget.page().runJavaScript(f"if(map.hasLayer(mymarker)) map.removeLayer(mymarker);")
            if self.modes_comboBox.currentText() == "Waypoint Modu":
                self.mapwidget.page().runJavaScript(f"map.off('click', moveMarkerByClick);")
                self.mapwidget.page().runJavaScript(f"map.off('click', drawRectangle);")
                self.mapwidget.page().runJavaScript(f"map.on('click', putWaypointEvent);")
                self.mapwidget.page().runJavaScript(f"if(map.hasLayer(mymarker)) map.removeLayer(mymarker);")
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
