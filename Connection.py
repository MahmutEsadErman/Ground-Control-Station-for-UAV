import math

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QInputDialog, QMessageBox
from dronekit import Vehicle, connect, LocationGlobalRelative, VehicleMode

from pymavlink import mavutil

from IndicatorsPage import IndicatorsPage
from MapWidget import MapWidget


class ConnectionThread(QThread):
    vehicleConnected = Signal(Vehicle, MapWidget, QPushButton)
    updateData = Signal(Vehicle, MapWidget, IndicatorsPage)
    connectionLost = Signal(QPushButton)

    def __init__(self, ConnectButton, mapwidget, indicators):
        super().__init__()
        self.vehicle = None
        self.connection_string = None
        self.baudrate = None
        self.connectButton = ConnectButton
        self.mapwidget = mapwidget
        self.indicators = indicators

    # This method is called when the thread is started
    def run(self):
        timeout = 7
        # Connect to the Vehicle
        print("Connecting to vehicle on: %s" % self.connection_string)
        self.vehicle = connect(self.connection_string, wait_ready=True, baud=self.baudrate,
                               heartbeat_timeout=timeout + 1)
        print("Connected")
        self.vehicleConnected.emit(self.vehicle, self.mapwidget, self.connectButton)
        # If uav is not reached for timeout second disconnect
        while self.vehicle.last_heartbeat < timeout:
            self.updateData.emit(self.vehicle, self.mapwidget, self.indicators)
            self.msleep(100)

        self.connectionLost.emit(self.connectButton)

    def setBaudRate(self, baud):
        self.baudrate = baud  # 115200 on USB or 57600 on Radio/Telemetry

    def setConnectionString(self, connectionstring):
        if connectionstring == 'USB':
            self.connection_string = '/dev/ttyACM0'
        elif connectionstring == 'SITL (UDP)':
            self.connection_string = '127.0.0.1:14550'
        elif connectionstring == 'SITL (TCP)':
            self.connection_string = '127.0.0.1:5760'
        elif connectionstring == 'UDP':
            text, ok = QInputDialog.getText(None, "Input Dialog", "Enter an IP:")
            if ok and text:
                self.connection_string = text + ":14550"
        elif connectionstring == 'TCP':
            text, ok = QInputDialog.getText(None, "Input Dialog", "Enter an IP:")
            if ok and text:
                self.connection_string = "tcp:" + text + ":5760"
                # msgBox = QMessageBox()
                # msgBox.setText("This is a message.")
                # msgBox.exec()

    def goto_markers_pos(self):
        lat = float(self.mapwidget.map_page.markers_pos[0])
        lon = float(self.mapwidget.map_page.markers_pos[1])
        alt = self.vehicle.location.global_relative_frame.alt
        location = LocationGlobalRelative(lat, lon, alt)
        self.vehicle.simple_goto(location)

    def takeoff(self, target_altitude):
        # Set the vehicle mode to GUIDED
        self.vehicle.mode = VehicleMode("GUIDED")

        # Arm the vehicle
        self.vehicle.armed = True

        # Wait for the vehicle to be armed
        while not self.vehicle.armed:
            self.sleep(1)

        # Take off to target altitude
        self.vehicle.simple_takeoff(target_altitude)

        # Wait until the vehicle reaches the target altitude
        while self.vehicle.location.global_relative_frame.alt < target_altitude * 0.95:
            self.sleep(1)


def handleConnectedVehicle(vehicle, mapwidget, connectbutton):
    # Set connect button disable
    connectbutton.setText('Connected')
    connectbutton.setIcon(QIcon('uifolder/assets/icons/24x24/cil-link.png'))
    connectbutton.setDisabled(True)

    # Fly to UAV's position
    position = [vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon]
    mapwidget.page().runJavaScript(f'console.log("uav position: {position}")')
    mapwidget.page().runJavaScript(f"{mapwidget.map_variable_name}.flyTo({position})")

    # Add uav marker
    mapwidget.page().runJavaScript("""
                var uavMarker = L.marker(
                            %s,
                            {icon: uavIcon,},).addTo(%s);
                """ % (position, mapwidget.map_variable_name)
                                   )


def updateData(vehicle, mapwidget, indicators):
    position = [vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon]

    indicators.setSpeed(vehicle.airspeed)
    indicators.setVerticalSpeed(vehicle.groundspeed)
    indicators.setHeading(vehicle.heading)
    indicators.setAltitude(vehicle.location.global_relative_frame.alt)
    indicators.setAttitude(math.degrees(vehicle.attitude.pitch), math.degrees(vehicle.attitude.roll))
    indicators.xpos_label.setText("X: " + str(position[0]))
    indicators.ypos_label.setText("Y: " + str(position[1]))
    indicators.battery_label.setText("Battery: " + str(vehicle.battery.level))
    indicators.flight_mode_label.setText("Flight Mode: " + str(vehicle.mode.name))

    mapwidget.page().runJavaScript(f"uavMarker.setLatLng({str(position)});")  # to set position of uav marker
    mapwidget.page().runJavaScript(f"uavMarker.setRotationAngle({vehicle.heading - 45});")  # to set rotation of uav


def connectionLost(connectbutton):
    connectbutton.setText('Connect')
    connectbutton.setIcon(QIcon('uifolder/assets/icons/24x24/cil-link-broken.png'))
    connectbutton.setDisabled(False)
