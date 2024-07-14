import math
import time

from pymavlink import mavutil
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QInputDialog

from CameraWidget import CameraWidget
from IndicatorsPage import IndicatorsPage
from MapWidget import MapWidget


def handleConnectedVehicle(connection, mapwidget, connectbutton):
    msg = connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    position = [msg.lat / 1e7, msg.lon / 1e7]
    # Set connect button disable
    connectbutton.setText('Connected')
    connectbutton.setIcon(QIcon('../uifolder/assets/icons/24x24/cil-link.png'))
    connectbutton.setDisabled(True)

    # Fly to UAV's position
    mapwidget.page().runJavaScript(f'console.log("uav position: {position}")')
    mapwidget.page().runJavaScript(f"{mapwidget.map_variable_name}.flyTo({position})")

    # Add UAV marker
    mapwidget.page().runJavaScript("""
                    var uavMarker = L.marker(
                                %s,
                                {icon: uavIcon,},).addTo(map);
                    """ % position
                                   )


def updateData(thread, vehicle, mapwidget, indicators, camerawidget):
    type_list = ['ATTITUDE', 'GLOBAL_POSITION_INT', 'VFR_HUD', 'SYS_STATUS', 'HEARTBEAT']

    # Read messages from the vehicle
    msg = vehicle.recv_match(type=type_list)
    if msg is not None:
        # Update indicators
        if msg.get_type() == 'GLOBAL_POSITION_INT':
            position = [msg.lat / 1e7, msg.lon / 1e7]
            indicators.setAltitude(msg.relative_alt / 1000.0)
            indicators.xpos_label.setText(f"X: {position[0]}")
            indicators.ypos_label.setText(f"Y: {position[1]}")
            mapwidget.page().runJavaScript(f"uavMarker.setLatLng({str(position)});")  # to set position of UAV marker
            mapwidget.page().runJavaScript(f"uavMarker.setRotationAngle({(msg.hdg/100) - 45});")  # to set rotation of UAV
            indicators.setHeading(msg.hdg/100)
        if msg.get_type() == 'VFR_HUD':
            indicators.setSpeed(msg.airspeed)
            indicators.setVerticalSpeed(msg.climb)
        if msg.get_type() == 'ATTITUDE':
            indicators.setAttitude(math.degrees(msg.pitch), math.degrees(msg.roll))
            camerawidget.videothread.setHorizon(msg.roll)
        if msg.get_type() == 'SYS_STATUS':
            indicators.battery_label.setText(f"Battery: {msg.battery_remaining}%")
        if msg.get_type() == 'HEARTBEAT':
            thread.last_heartbeat = time.time()
            flight_mode = mavutil.mode_string_v10(msg)
            indicators.flight_mode_label.setText(f"Flight Mode: {flight_mode}")


def connectionLost(connectbutton, mapwidget):
    connectbutton.setText('Connect')
    connectbutton.setIcon(QIcon('../uifolder/assets/icons/24x24/cil-link-broken.png'))
    connectbutton.setDisabled(False)
    # Add UAV marker
    mapwidget.page().runJavaScript("""
                    map.removeLayer(uavMarker);
                    """
                                   )

class ArdupilotConnectionThread(QThread):
    vehicleConnected_signal = Signal(mavutil.mavudp, MapWidget, QPushButton)
    updateData_signal = Signal(QThread,mavutil.mavudp, MapWidget, IndicatorsPage, CameraWidget)
    connectionLost_signal = Signal(QPushButton)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.connection = None
        self.connection_string = None
        self.baudrate = None
        self.connectButton = parent.btn_connect
        self.mapwidget = parent.homepage.mapwidget
        self.indicators = parent.indicatorspage

        self.vehicleConnected_signal.connect(handleConnectedVehicle)
        self.updateData_signal.connect(updateData)
        self.connectionLost_signal.connect(connectionLost)

    # This method is called when the thread is started
    def run(self):
        timeout = 7
        connected = False  # Flag to monitor connection status

        try:
            print(f"Connecting to vehicle on: {self.connection_string}")
            self.connection = mavutil.mavlink_connection(self.connection_string, baud=self.baudrate, autoreconnect=True, timeout=timeout)
            print("Waiting for heartbeat...")
            if self.connection.wait_heartbeat(timeout=timeout):
                print("Connected")
                connected = True
                self.vehicleConnected_signal.emit(self.connection, self.mapwidget, self.connectButton)
            else:
                print("Connection failed")
                connected = False
        except Exception as e:
            print(f"Failed to connect: {e}")
            connected = False

        if connected:
            self.last_heartbeat = time.time()  # Track the last heartbeat time
            while connected:
                current_time = time.time()
                if current_time - self.last_heartbeat > timeout:
                    print("Connection Lost - Heartbeat timeout")
                    connected = False

                try:
                    self.updateData_signal.emit(self, self.connection, self.mapwidget, self.indicators, self.parent.homepage.cameraWidget)
                    self.msleep(20)
                except Exception as e:
                    print(f"Error: {e}")
                    connected = False
            self.connectionLost_signal.emit(self.connectButton)

    def setBaudRate(self, baud):
        self.baudrate = baud  # 115200 on USB or 57600 on Radio/Telemetry

    def setConnectionString(self, connectionstring):
        if connectionstring == 'USB':
            self.connection_string = '/dev/ttyACM0'
        elif connectionstring == 'SITL (UDP)':
            self.connection_string = 'udp:127.0.0.1:14550'
        elif connectionstring == 'SITL (TCP)':
            self.connection_string = 'tcp:127.0.0.1:5760'
        elif connectionstring == 'UDP':
            text, ok = QInputDialog.getText(self.parent, "Input Dialog", "Enter an IP:")
            if ok and text:
                self.connection_string = f'udp:{text}:14550'
        elif connectionstring == 'TCP':
            text, ok = QInputDialog.getText(self.parent, "Input Dialog", "Enter an IP:")
            if ok and text:
                self.connection_string = f'tcp:{text}:5760'

    def goto_markers_pos(self):
        lat = int(int(self.mapwidget.map_page.markers_pos[0]) * 1e7)
        lon = int(int(self.mapwidget.map_page.markers_pos[1]) * 1e7)
        alt = self.connection.location(relative_alt=True).alt
        # Send command to move to the specified latitude, longitude, and current altitude
        self.connection.mav.set_position_target_global_int_send(
            0,  # time_boot_ms (not used)
            self.connection.target_system,  # target system
            self.connection.target_component,  # target component
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,  # frame
            0b0000111111111000,  # type_mask (only positions enabled)
            lat,  # lat_int
            lon,  # lon_int
            alt,  # alt
            0, 0, 0,  # X, Y, Z velocity in m/s (not used)
            0, 0, 0,  # X, Y, Z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)  # yaw, yaw_rate (not used)

    def takeoff(self, target_altitude):
        self.connection.set_mode_apm('GUIDED')
        self.connection.arducopter_arm()

        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0, 0, 0, 0,
            0, 0, target_altitude)
