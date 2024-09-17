import math
import time

from pymavlink import mavutil
import pymavlink.dialects.v20.all as dialect

from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QInputDialog

from CameraWidget import CameraWidget
from IndicatorsPage import IndicatorsPage
from MapWidget import MapWidget
from Database.users_db import FirebaseUser
from Vehicle.Exploration import exploration

# Some Definitions for testing purpose
ALTITUDE = 50
FOV = 63


class MissionModes:
    EXPLORATION = 0
    WAYPOINTS = 1


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


def updateData(thread, vehicle, mapwidget, indicators, camerawidget, firebase):
    type_list = ['ATTITUDE', 'GLOBAL_POSITION_INT', 'VFR_HUD', 'SYS_STATUS', 'HEARTBEAT']

    # Read messages from the vehicle
    msg = vehicle.recv_match(type=type_list)
    if msg is not None:
        # Update indicators
        if msg.get_type() == 'GLOBAL_POSITION_INT':
            position = [msg.lat / 1e7, msg.lon / 1e7]
            heading = msg.hdg / 100
            altitude = msg.relative_alt / 1000.0

            # Update UAV Data
            thread.latitude = position[0]
            thread.longitude = position[1]
            thread.altitude = altitude

            # Update indicators
            indicators.setAltitude(altitude)
            indicators.xpos_label.setText(f"X: {position[0]}")
            indicators.ypos_label.setText(f"Y: {position[1]}")
            indicators.setHeading(heading)
            # Update UAV marker
            mapwidget.page().runJavaScript(f"uavMarker.setLatLng({str(position)});")  # to set position of UAV marker
            mapwidget.page().runJavaScript(
                f"uavMarker.setRotationAngle({heading - 45});")  # to set rotation of UAV

            # Update Firebase UAV Data
            firebase.marker_latitude = position[0]
            firebase.marker_longitude = position[1]
            firebase.marker_compass = heading

            camerawidget.videothread.lat = position[0]
            camerawidget.videothread.lon = position[1]
            camerawidget.videothread.heading = heading
        if msg.get_type() == 'VFR_HUD':
            indicators.setSpeed(msg.airspeed)
            indicators.setVerticalSpeed(msg.climb)
        if msg.get_type() == 'ATTITUDE':
            indicators.setAttitude(math.degrees(msg.pitch), math.degrees(msg.roll))
            camerawidget.videothread.setHorizon(msg.roll)
        if msg.get_type() == 'SYS_STATUS':
            indicators.battery_label.setText(f"Battery: {msg.voltage_battery/1e3}V")
            thread.parent.label_top_info_1.setText(f"Battery: {msg.battery_remaining}%      {msg.voltage_battery/1e3}V      {msg.current_battery}A")
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
    updateData_signal = Signal(QThread, mavutil.mavudp, MapWidget, IndicatorsPage, CameraWidget, FirebaseUser)
    connectionLost_signal = Signal(QPushButton, MapWidget)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.connection = None
        self.connection_string = None
        self.baudrate = None
        self.connectButton = parent.btn_connect
        self.mapwidget = parent.homepage.mapwidget
        self.indicators = parent.indicatorspage
        self.firebase = parent.targetspage.firebase

        # Telemetry Data
        self.latitude = 0
        self.longitude = 0
        self.altitude = 50

        # Variables
        self.camera_angle = 60
        self.speed_limit = 10
        self.home_position = [0,0]

        self.vehicleConnected_signal.connect(handleConnectedVehicle)
        self.updateData_signal.connect(updateData)
        self.connectionLost_signal.connect(connectionLost)

    # This method is called when the thread is started
    def run(self):
        timeout = 10  # seconds
        connected = False  # Flag to monitor connection status

        try:
            print(f"Connecting to vehicle on: {self.connection_string}")
            self.connection = mavutil.mavlink_connection(self.connection_string, baud=self.baudrate, autoreconnect=True,
                                                         timeout=timeout)
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
            while connected:
                try:
                    self.updateData_signal.emit(self, self.connection, self.mapwidget, self.indicators,
                                                self.parent.homepage.cameraWidget, self.firebase)
                    self.msleep(20)
                except Exception as e:
                    print(f"Error: {e}")
                    connected = False
            self.connectionLost_signal.emit(self.connectButton, self.mapwidget)

    def setBaudRate(self, baud):
        self.baudrate = baud  # 115200 on USB or 57600 on Radio/Telemetry

    def setConnectionString(self, connectionstring):
        if connectionstring == 'Telemetri':
            self.connection_string = '/dev/ttyUSB0'
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

    def goto_markers_pos(self, speed=-1):
        lat = int(float(self.mapwidget.map_page.markers_pos[0]))
        lng = int(float(self.mapwidget.map_page.markers_pos[1]))

        self.connection.set_mode_apm('GUIDED')

        self.move_to(lat, lng)

    def move_to(self, lat, lng, speed=5):
        lat = int(lat * 1e7)
        lng = int(lng * 1e7)
        alt = self.connection.location(relative_alt=True).alt
        # Send command to move to the specified latitude, longitude, and current altitude
        self.connection.mav.command_int_send(
            self.connection.target_system,
            self.connection.target_component,
            dialect.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            # “frame” = 0 or 3 for alt-above-sea-level, 6 for alt-above-home or 11 for alt-above-terrain
            dialect.MAV_CMD_DO_REPOSITION,
            0,  # Current
            0,  # Autocontinue
            speed,
            0, 0, 0,  # Params 2-4 (unused)
            lat,
            lng,
            alt
        )

    def set_roi(self, alt=0):
        lat = int(float(self.mapwidget.map_page.markers_pos[0])*1e7)
        lng = int(float(self.mapwidget.map_page.markers_pos[1])*1e7)
        self.connection.mav.command_int_send(
            self.connection.target_system,
            self.connection.target_component,
            dialect.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            # “frame” = 0 or 3 for alt-above-sea-level, 6 for alt-above-home or 11 for alt-above-terrain
            dialect.MAV_CMD_DO_SET_ROI_LOCATION,
            0,  # Current
            0,  # Autocontinue
            0, 0, 0, 0,  # Params 2-4 (unused)
            lat,
            lng,
            alt  # Altitude
        )

    def cancel_roi_mode(self):
        # Cancel the ROI mode.
        self.connection.mav.command_int_send(
            self.connection.target_system,
            self.connection.target_component,
            0,
            dialect.MAV_CMD_DO_SET_ROI_NONE,
            0, 0,
            0, 0, 0, 0,
            0, 0, 0
        )

    def land(self):
        print("Landing")
        self.connection.set_mode_apm('QLAND')

    def rtl(self):
        def control_if_reached():
            if abs(self.latitude - self.home_position[0]) > 0.0001 or abs(self.longitude - self.home_position[1]) > 0.0001:
                QTimer.singleShot(100, control_if_reached)
            else:
                self.land()
        print("Returning back to home")
        self.move_to(self.home_position[0], self.home_position[1])
        QTimer.singleShot(100, control_if_reached)




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

        self.set_home_position(self.latitude, self.longitude)

    def set_home_position(self, lat, lng):
        self.home_position[0] = lat
        self.home_position[1] = lng

    def start_mission(self):
        self.connection.set_mode_apm('GUIDED')
        self.connection.arducopter_arm()
        self.connection.set_mode('AUTO')

    def set_mission(self, mission_mode, waypoints, altitude):
        if mission_mode == MissionModes.EXPLORATION:
            waypoints = exploration(self, waypoints[0], waypoints[1], ALTITUDE, FOV)
            self.upload_mission(waypoints, int(altitude))
            # Put waypoints
            for wp in waypoints:
                self.mapwidget.page().runJavaScript(f"putWaypoint({wp[0]}, {wp[1]});")

        elif mission_mode == MissionModes.WAYPOINTS:
            self.upload_mission(waypoints,)

    def clear_mission(self):
        self.connection.mav.mission_clear_all_send(
            self.connection.target_system,
            self.connection.target_component,
            mission_type=dialect.MAV_MISSION_TYPE_MISSION
        )

    def upload_mission(self, waypoints, altitude=30):
        self.clear_mission()

        # Verify mission count
        self.connection.mav.mission_count_send(
            self.connection.target_system,
            self.connection.target_component,
            len(waypoints)+2
        )

        # Upload home
        self.connection.mav.mission_item_int_send(
            self.connection.target_system,
            self.connection.target_component,
            0,
            dialect.MAV_FRAME_GLOBAL,
            dialect.MAV_CMD_NAV_WAYPOINT,
            0,  # current
            0,  # auto continue
            0, 0, 0, 0,  # params 1-4
            0, 0, 0)

        self.connection.mav.mission_item_int_send(
            self.connection.target_system,
            self.connection.target_component,
            1,
            dialect.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            dialect.MAV_CMD_NAV_TAKEOFF,
            0,  # current
            0,  # auto continue
            0, 0, 0, 0,  # params 1-4
            0,
            0,
            altitude)

        # Upload waypoints
        for i, item in enumerate(waypoints, start=2):
            print(i, item)
            self.connection.mav.mission_item_int_send(
                self.connection.target_system,
                self.connection.target_component,
                i,
                dialect.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                dialect.MAV_CMD_NAV_WAYPOINT,
                0,  # current
                0,  # auto continue
                0, 0, 0, 0,  # params 1-4
                int(item[0] * 1e7),
                int(item[1] * 1e7),
                altitude)

        self.set_home_position(self.latitude, self.longitude)
        print("Mission uploaded successfully.")
