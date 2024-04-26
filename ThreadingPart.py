from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QInputDialog, QMessageBox
from dronekit import Vehicle, connect

from IndicatorsPage import IndicatorsPage
from MapWidget import MapWidget


class ConnectionThread(QThread):
    vehicleConnected = Signal(Vehicle, MapWidget, QPushButton)
    updateData = Signal(Vehicle, MapWidget, IndicatorsPage)
    connectionLost = Signal(QPushButton)

    def __init__(self, ConnectButton, mapwidget, indicators):
        super().__init__()
        self.connection_string = None
        self.baudrate = None
        self.connectButton = ConnectButton
        self.mapwidget = mapwidget
        self.indicators = indicators

    def run(self):
        timeout = 7
        # Connect to the Vehicle
        print("Connecting to vehicle on: %s" % self.connection_string)
        vehicle = connect(self.connection_string, wait_ready=True, baud=self.baudrate, heartbeat_timeout=timeout + 1)
        print("Connected")
        self.vehicleConnected.emit(vehicle, self.mapwidget, self.connectButton)
        # If uav is not reached for timeout second disconnect
        while vehicle.last_heartbeat < timeout:
            self.updateData.emit(vehicle, self.mapwidget, self.indicators)
            self.sleep(1)

        self.connectionLost.emit(self.connectButton)

    def setBaudRate(self, baud):
        self.baudrate = baud

    def setConnectionString(self, connectionstring):
        if connectionstring == 'USB':
            self.connection_string = '/dev/ttyACM0'
        elif connectionstring == 'SITL (UDP)':
            self.connection_string = '127.0.0.1:14550'
        elif connectionstring == 'SITL (TCP)':
            self.connection_string = 'tcp:127.0.0.1:5760'
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


def handleConnectedVehicle(vehicle, mapwidget, connectbutton):
    # Set connect button disable
    connectbutton.setText('Connected')
    connectbutton.setIcon(QIcon('assets/icons/24x24/cil-link.png'))
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

    mapwidget.page().runJavaScript(f"uavMarker.setLatLng({str(position)});")  # to set position of uav marker
    mapwidget.page().runJavaScript(f"uavMarker.setRotationAngle({vehicle.heading - 45});")  # to set rotation of uav


def connectionLost(connectbutton):
    connectbutton.setText('Connect')
    connectbutton.setIcon(QIcon('assets/icons/24x24/cil-link-broken.png'))
    connectbutton.setDisabled(False)
