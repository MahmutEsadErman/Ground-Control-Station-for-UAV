from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, Signal
from dronekit import connect, Vehicle, VehicleMode, LocationGlobalRelative

from DisplayInfo import DisplayWindow
from MapWidget import MapWidget

# Connect to the Vehicle.
connection_string = "127.0.0.1:14550"
print("Connecting to vehicle on: %s" % (connection_string,))
vehicle = connect(connection_string, wait_ready=True)
if vehicle is not None:
    print("Connected")


class VehicleThread(QThread):
    def __init__(self, mapwidget):
        super().__init__()
        self.widget = mapwidget

    def run(self):
        while True:
            self.updateData.emit(vehicle, self.widget)
            self.sleep(1)

    updateData = Signal(Vehicle, MapWidget)


def takeoff(height=10):
    print("Pressed Takeoff Button")
    print('Basic pre-arm checks')
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        QThread.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        QThread.sleep(1)

    vehicle.simple_takeoff(height)


def go(coords):
    print("---------------")
    print("Going to: ", coords)
    if not isinstance(coords, LocationGlobalRelative):
        coords = LocationGlobalRelative(float(coords[0]), float(coords[1]), 10)

    if vehicle.mode.name == "GUIDED":
        print("coords: ", coords)
        print("alt: ", coords.alt)
        vehicle.simple_goto(coords)
    else:
        print("Vehicle is not in GUIDED mode")


if __name__ == "__main__":
    app = QApplication([])

    # Set up the main window
    mainwindow = DisplayWindow()
    initial_location = vehicle.location.global_relative_frame
    mainwindow.infoWidget.takeoffButton.clicked.connect(lambda: takeoff(10))
    mainwindow.infoWidget.goButton.clicked.connect(lambda: go(mapwidget.marker_coord))
    mainwindow.infoWidget.returnButton.clicked.connect(lambda: go(initial_location))
    mainwindow.infoWidget.stopButton.clicked.connect(lambda: go(vehicle.location.global_relative_frame))

    # Set up the Map Widget
    mapwidget = MapWidget([vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon])

    # Start the thread
    thread = VehicleThread(mapwidget)
    thread.updateData.connect(mainwindow.updateData)
    thread.start()

    # Show windows
    mapwidget.show()
    mainwindow.show()

    app.exec()
    thread.quit()
    vehicle.close()
