from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton
from dronekit import Vehicle, connect

from MapWidget import MapWidget


class ConnectionThread(QThread):
    vehicleConnected = Signal(Vehicle, MapWidget, QPushButton)
    updateData = Signal(Vehicle, MapWidget)
    connectionLost = Signal(QPushButton)

    def __init__(self, connection_string, baudrate, ConnectButton, mapwidget):
        super().__init__()
        self.connection_string = connection_string
        self.baudrate = baudrate
        self.connectButton = ConnectButton
        self.mapwidget = mapwidget

    def run(self):
        timeout = 7
        # Connect to the Vehicle
        print("Connecting to vehicle on: %s" % self.connection_string)
        vehicle = connect(self.connection_string, wait_ready=True, baud=self.baudrate, heartbeat_timeout=timeout + 1)
        print("Connected")

        self.vehicleConnected.emit(vehicle, self.mapwidget, self.connectButton)

        while vehicle.last_heartbeat < timeout:
            self.updateData.emit(vehicle, self.mapwidget)
            self.sleep(1)

        self.connectionLost.emit(self.connectButton)


def handleConnectedVehicle(vehicle, mapwidget, connectbutton):
    # Set connect button disable
    connectbutton.setText('Connected')
    connectbutton.setIcon(QIcon('icons/24x24/cil-link.png'))
    connectbutton.setDisabled(True)

    # Fly to UAV's position
    position = [vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon]
    mapwidget.page().runJavaScript(f'console.log("uav position: {position}")')
    mapwidget.page().runJavaScript(f"{mapwidget.map_variable_name}.flyTo({position})")

    # Add uav marker
    mapwidget.page().runJavaScript("""
                var uavMarker = L.marker(
                            %s,
                            {icon: uavIcon,
                            },

                        ).addTo(%s);
                """ % (position, mapwidget.map_variable_name)
                                   )


def updateData(vehicle, mapwidget):
    position = [vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon]
    # self.infoWidget.armable.setText(str(vehicle.is_armable))
    # self.infoWidget.mode.setText(vehicle.mode.name)
    # self.infoWidget.positionLabel.setText(str(position))
    # self.infoWidget.velocity.setText(str(vehicle.velocity))
    # self.infoWidget.altitude.setText(str(vehicle.location.global_relative_frame.alt))
    mapwidget.page().runJavaScript(f"uavMarker.setLatLng({str(position)});")  # to set position of uav marker
    mapwidget.page().runJavaScript(f"uavMarker.setRotationAngle({vehicle.heading - 45});")  # to set rotation of uav


def connectionLost(connectbutton):
    connectbutton.setText('Connect')
    connectbutton.setIcon(QIcon('icons/24x24/cil-link-broken.png'))
    connectbutton.setDisabled(False)
