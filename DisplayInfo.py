import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import QFile, QIODevice


class DisplayWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Load the ui file
        ui_file_name = "uifolder/displayinfo.ui"
        ui_file = QFile(ui_file_name)
        # Control if file exists
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)
        self.infoWidget = QUiLoader().load(ui_file)
        ui_file.close()
        layout = QVBoxLayout()
        layout.addWidget(self.infoWidget)
        self.setLayout(layout)
        self.setWindowTitle("Display Info")

        # Set window size
        self.setFixedSize(450, 430)

    def updateData(self, vehicle, mapwidget):
        position = [vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon]
        self.infoWidget.armable.setText(str(vehicle.is_armable))
        self.infoWidget.mode.setText(vehicle.mode.name)
        self.infoWidget.positionLabel.setText(str(position))
        self.infoWidget.velocity.setText(str(vehicle.velocity))
        self.infoWidget.altitude.setText(str(vehicle.location.global_relative_frame.alt))
        mapwidget.page().runJavaScript(f"uavMarker.setLatLng({str(position)});") # to set position of uav marker in the map
        mapwidget.page().runJavaScript(f"uavMarker.setRotationAngle({vehicle.heading-45});")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DisplayWindow()
    # window.updateData(True, "GUIDED", 10, 10)
    window.show()
    sys.exit(app.exec())
