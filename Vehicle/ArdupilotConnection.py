import math
import time

import rclpy
from rclpy.node import Node
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.qos import qos_profile_sensor_data

from std_msgs.msg import String
from std_srvs.srv import Trigger, SetBool

from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QInputDialog

from sensor_msgs.msg import NavSatFix, Imu, BatteryState
from mavros_msgs.msg import State, VfrHud, GlobalPositionTarget, Waypoint
from mavros_msgs.srv import CommandBool, SetMode, CommandTOL, WaypointPush, WaypointClear, CommandLong, CommandInt

import json
from datetime import datetime

from CameraWidget import CameraWidget
from IndicatorsPage import IndicatorsPage
from MapWidget import MapWidget
from Vehicle.Exploration import exploration

FOV = 110


class MissionModes:
    EXPLORATION = 0
    WAYPOINTS = 1


def euler_from_quaternion(q):
    x, y, z, w = q.x, q.y, q.z, q.w
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch = math.asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(t3, t4)
    return roll, pitch, yaw


class ArdupilotConnectionThread(QThread):
    vehicleConnected_signal = Signal()
    connectionLost_signal = Signal()

    # GUI signals to ensure thread-safety
    update_uav_marker_signal = Signal(float, float, float)
    update_indicators_signal = Signal(float, float, float, float, float, float, float, float, str, float)
    heartbeat_signal = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.connectButton = parent.btn_connect
        self.mapwidget = parent.homepage.mapwidget
        self.indicators = parent.indicatorspage
        self.camerawidget = parent.homepage.cameraWidget

        # Telemetry Data
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 15.0
        self.heading = 0.0
        self.speed = 0.0
        self.vertical_speed = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.flight_mode = "UNKNOWN"
        self.battery_volt = 0.0

        self.home_position = [0.0, 0.0]
        self.camera_angle = 45

        self.node = None
        self.connected_state = False

        # Onboard system control clients (initialized in run())
        self.start_record_client = None
        self.stop_record_client = None
        self.toggle_detection_client = None

        self.vehicleConnected_signal.connect(self.handleConnectedVehicle)
        self.connectionLost_signal.connect(self.handleConnectionLost)
        self.update_uav_marker_signal.connect(self.update_uav_marker)
        self.update_indicators_signal.connect(self.update_indicators)

    def run(self):
        self.context = Context()
        rclpy.init(context=self.context)

        self.node = rclpy.create_node('gcs_mavros_node', context=self.context)

        # Subscribers
        self.node.create_subscription(State, '/mavros/state', self.state_cb, qos_profile_sensor_data)
        self.node.create_subscription(NavSatFix, '/mavros/global_position/global', self.global_pos_cb, qos_profile_sensor_data)
        self.node.create_subscription(VfrHud, '/mavros/vfr_hud', self.vfr_hud_cb, qos_profile_sensor_data)
        self.node.create_subscription(Imu, '/mavros/imu/data', self.imu_cb, qos_profile_sensor_data)
        self.node.create_subscription(BatteryState, '/mavros/battery', self.battery_cb, qos_profile_sensor_data)

        # Service Clients
        self.arm_client = self.node.create_client(CommandBool, '/mavros/cmd/arming')
        self.set_mode_client = self.node.create_client(SetMode, '/mavros/set_mode')
        self.takeoff_client = self.node.create_client(CommandTOL, '/mavros/cmd/takeoff')
        self.land_client = self.node.create_client(CommandTOL, '/mavros/cmd/land')
        self.wp_push_client = self.node.create_client(WaypointPush, '/mavros/mission/push')
        self.wp_clear_client = self.node.create_client(WaypointClear, '/mavros/mission/clear')
        self.cmd_long_client = self.node.create_client(CommandLong, '/mavros/cmd/command')
        self.cmd_int_client = self.node.create_client(CommandInt, '/mavros/cmd/command_int')

        # Publishers
        self.setpoint_global_pub = self.node.create_publisher(GlobalPositionTarget, '/mavros/setpoint_position/global', 10)

        # Onboard System Control - Service Clients
        self.start_record_client = self.node.create_client(Trigger, '/drone/start_record')
        self.stop_record_client = self.node.create_client(Trigger, '/drone/stop_record')
        self.toggle_detection_client = self.node.create_client(SetBool, '/drone/toggle_detection')

        # Heartbeat Subscription
        self.node.create_subscription(String, '/drone/heartbeat', self.heartbeat_cb, 10)

        print("Waiting for MAVROS nodes...")

        self.executor = SingleThreadedExecutor(context=self.context)
        self.executor.add_node(self.node)

        try:
            self.executor.spin()
        except Exception as e:
            print(f"Exception in ROS 2 node thread: {e}")
        finally:
            self.executor.remove_node(self.node)
            if self.node:
                self.node.destroy_node()
            if self.context:
                rclpy.shutdown(context=self.context)

    def state_cb(self, msg):
        self.flight_mode = msg.mode
        if msg.connected and not self.connected_state:
            self.connected_state = True
            self.vehicleConnected_signal.emit()
        elif not msg.connected and self.connected_state:
            self.connected_state = False
            self.connectionLost_signal.emit()
            
        self.trigger_ui_update()

    def global_pos_cb(self, msg):
        self.latitude = msg.latitude
        self.longitude = msg.longitude
        self.altitude = msg.altitude

        self.camerawidget.videothread.lat = self.latitude
        self.camerawidget.videothread.lon = self.longitude
        self.trigger_ui_update()

    def vfr_hud_cb(self, msg):
        self.speed = msg.airspeed
        self.vertical_speed = msg.climb
        self.heading = msg.heading
        self.camerawidget.videothread.heading = self.heading
        self.trigger_ui_update()

    def imu_cb(self, msg):
        roll, pitch, _ = euler_from_quaternion(msg.orientation)
        self.roll = math.degrees(roll)
        self.pitch = math.degrees(pitch)
        self.trigger_ui_update()

    def battery_cb(self, msg):
        self.battery_volt = msg.voltage
        self.trigger_ui_update()

    def trigger_ui_update(self):
        # Update markers
        self.update_uav_marker_signal.emit(self.latitude, self.longitude, self.heading)
        # Update indicators
        self.update_indicators_signal.emit(
            self.latitude, self.longitude, self.altitude, self.heading,
            self.speed, self.vertical_speed, self.pitch, self.roll, self.flight_mode, self.battery_volt
        )

    def handleConnectedVehicle(self):
        self.connectButton.setText('Connected')
        self.connectButton.setIcon(QIcon('uifolder/assets/icons/24x24/cil-link.png'))
        self.connectButton.setDisabled(True)

        position = [self.latitude, self.longitude]
        self.mapwidget.page().runJavaScript(f'console.log("uav position: {position}")')
        self.mapwidget.page().runJavaScript(f"{self.mapwidget.map_variable_name}.flyTo({position})")
        self.mapwidget.page().runJavaScript(f"var uavMarker = L.marker({position}, {{icon: uavIcon,}}).addTo(map);")

    def handleConnectionLost(self):
        self.connectButton.setText('Connect')
        self.connectButton.setIcon(QIcon('uifolder/assets/icons/24x24/cil-link-broken.png'))
        self.connectButton.setDisabled(False)
        self.mapwidget.page().runJavaScript("map.removeLayer(uavMarker);")

    def update_uav_marker(self, lat, lon, heading):
        if self.connected_state:
            position = [lat, lon]
            self.mapwidget.page().runJavaScript(f"if (typeof uavMarker !== 'undefined') {{ uavMarker.setLatLng({str(position)}); uavMarker.setRotationAngle({heading - 45}); }}")

    def update_indicators(self, lat, lon, alt, heading, spd, vspd, ptc, rll, mode, batt):
        self.indicators.setAltitude(alt)
        self.indicators.xpos_label.setText(f"X: {lat:.6f}")
        self.indicators.ypos_label.setText(f"Y: {lon:.6f}")
        self.indicators.setHeading(heading)
        self.indicators.setSpeed(spd)
        self.indicators.setVerticalSpeed(vspd)
        self.indicators.setAttitude(ptc, rll)
        self.indicators.flight_mode_label.setText(f"Flight Mode: {mode}")
        self.indicators.battery_label.setText(f"Battery: {batt:.2f}V")
        self.parent.label_top_info_1.setText(f"Battery: {batt:.2f}V")

    # The parameters are no longer needed for MAVROS configuration,
    # as connection parameters are given through launch files or ROS nodes.
    # We leave dummy functions so the UI doesn't crash if they are still called.
    def setBaudRate(self, baud):
        pass

    def setConnectionString(self, connectionstring):
        pass

    def set_mode(self, custom_mode):
        req = SetMode.Request()
        req.custom_mode = custom_mode
        if self.set_mode_client.wait_for_service(timeout_sec=1.0):
            self.set_mode_client.call_async(req)

    def arm(self):
        req = CommandBool.Request()
        req.value = True
        if self.arm_client.wait_for_service(timeout_sec=1.0):
            self.arm_client.call_async(req)

    def goto_markers_pos(self, speed=-1):
        if len(self.mapwidget.map_page.markers_pos) >= 2:
            lat = float(self.mapwidget.map_page.markers_pos[0])
            lng = float(self.mapwidget.map_page.markers_pos[1])
            self.set_mode('GUIDED')
            self.move_to(lat, lng)

    def move_to(self, lat, lng, altitude=None):
        if altitude is None:
            altitude = self.altitude
        msg = GlobalPositionTarget()
        msg.coordinate_frame = GlobalPositionTarget.FRAME_GLOBAL_REL_ALT
        msg.type_mask = 4088 # ignore everything except position
        msg.latitude = lat
        msg.longitude = lng
        msg.altitude = altitude
        if self.setpoint_global_pub:
            self.setpoint_global_pub.publish(msg)

    def set_roi(self, alt=0):
        if len(self.mapwidget.map_page.markers_pos) >= 2:
            lat = float(self.mapwidget.map_page.markers_pos[0])
            lng = float(self.mapwidget.map_page.markers_pos[1])
            req = CommandInt.Request()
            req.command = 195  # MAV_CMD_DO_SET_ROI_LOCATION
            req.frame = 3      # MAV_FRAME_GLOBAL_RELATIVE_ALT
            req.x = int(lat * 1e7)
            req.y = int(lng * 1e7)
            req.z = float(alt)
            if self.cmd_int_client.wait_for_service(timeout_sec=1.0):
                self.cmd_int_client.call_async(req)

    def cancel_roi_mode(self):
        req = CommandLong.Request()
        req.command = 197 # MAV_CMD_DO_SET_ROI_NONE
        if self.cmd_long_client.wait_for_service(timeout_sec=1.0):
            self.cmd_long_client.call_async(req)

    # ── Onboard System Control Methods ──────────────────────────────
    def start_record(self):
        """Send start_record service call to remote Jetson Orin."""
        if self.start_record_client is None:
            self.heartbeat_signal.emit("[HATA] ROS 2 bağlantısı henüz kurulmadı.")
            return
        if self.start_record_client.wait_for_service(timeout_sec=2.0):
            req = Trigger.Request()
            future = self.start_record_client.call_async(req)
            future.add_done_callback(self._record_response_cb)
        else:
            self.heartbeat_signal.emit(f"[HATA] /drone/start_record servisi bulunamadı.")

    def stop_record(self):
        """Send stop_record service call to remote Jetson Orin."""
        if self.stop_record_client is None:
            self.heartbeat_signal.emit("[HATA] ROS 2 bağlantısı henüz kurulmadı.")
            return
        if self.stop_record_client.wait_for_service(timeout_sec=2.0):
            req = Trigger.Request()
            future = self.stop_record_client.call_async(req)
            future.add_done_callback(self._record_response_cb)
        else:
            self.heartbeat_signal.emit(f"[HATA] /drone/stop_record servisi bulunamadı.")

    def toggle_detection(self, enable):
        """Send toggle_detection service call to remote Jetson Orin."""
        if self.toggle_detection_client is None:
            self.heartbeat_signal.emit("[HATA] ROS 2 bağlantısı henüz kurulmadı.")
            return
        if self.toggle_detection_client.wait_for_service(timeout_sec=2.0):
            req = SetBool.Request()
            req.data = enable
            future = self.toggle_detection_client.call_async(req)
            future.add_done_callback(self._record_response_cb)
        else:
            self.heartbeat_signal.emit(f"[HATA] /drone/toggle_detection servisi bulunamadı.")

    def _record_response_cb(self, future):
        """Callback for service response - emit result to console."""
        try:
            result = future.result()
            status = "✓" if result.success else "✗"
            self.heartbeat_signal.emit(f"[SERVİS {status}] {result.message}")
        except Exception as e:
            self.heartbeat_signal.emit(f"[HATA] Servis çağrısı başarısız: {e}")

    def heartbeat_cb(self, msg):
        """Process heartbeat messages from the onboard system controller."""
        try:
            data = json.loads(msg.data)
            ts = datetime.fromtimestamp(data.get('timestamp', 0)).strftime('%H:%M:%S')
            status = data.get('status', 'N/A')
            cpu_temp = data.get('cpu_temp_c', 0)
            ram = data.get('ram_usage_percent', 0)
            disk = data.get('disk_free_gb', 0)
            recording = "●REC" if data.get('is_recording', False) else "○REC"
            detecting = "●DET" if data.get('is_detecting', False) else "○DET"

            heartbeat_text = (
                f"[{ts}] {status} | CPU: {cpu_temp}°C | "
                f"RAM: {ram}% | Disk: {disk}GB | {recording} | {detecting}"
            )
            self.heartbeat_signal.emit(heartbeat_text)
        except Exception as e:
            self.heartbeat_signal.emit(f"[HEARTBEAT HATA] {e}")

    def land(self):
        print("Landing")
        self.set_mode('LAND')

    def rtl(self):
        print("Returning back to home")
        self.set_mode('RTL')

    def takeoff(self, target_altitude):
        self.set_mode('GUIDED')
        self.arm()
        time.sleep(0.5)
        req = CommandTOL.Request()
        req.altitude = float(target_altitude)
        if self.takeoff_client.wait_for_service(timeout_sec=1.0):
            self.takeoff_client.call_async(req)
        self.set_home_position(self.latitude, self.longitude)

    def set_home_position(self, lat, lng):
        self.home_position[0] = lat
        self.home_position[1] = lng

    def start_mission(self):
        self.set_mode('GUIDED')
        self.arm()
        time.sleep(0.5)
        self.set_mode('AUTO')

    def set_mission(self, mission_mode, waypoints, altitude):
        print("Altitude: ", altitude)
        if mission_mode == MissionModes.EXPLORATION:
            waypoints = exploration(self, waypoints[0], waypoints[1], altitude, FOV)
            self.upload_mission(waypoints, altitude)
            # Put waypoints
            for wp in waypoints:
                self.mapwidget.page().runJavaScript(f"putWaypoint({wp[0]}, {wp[1]});")
        elif mission_mode == MissionModes.WAYPOINTS:
            self.upload_mission(waypoints, altitude)

    def clear_mission(self):
        if self.wp_clear_client.wait_for_service(timeout_sec=1.0):
            req = WaypointClear.Request()
            self.wp_clear_client.call_async(req)

    def upload_mission(self, waypoints, altitude=15.0):
        self.clear_mission()
        time.sleep(0.5)

        req = WaypointPush.Request()

        # Add Home Waypoint
        wp_home = Waypoint()
        wp_home.frame = Waypoint.FRAME_GLOBAL_REL_ALT
        wp_home.command = 16 # MAV_CMD_NAV_WAYPOINT
        wp_home.is_current = True
        wp_home.autocontinue = True
        wp_home.x_lat = self.latitude
        wp_home.y_long = self.longitude
        wp_home.z_alt = 0.0
        req.waypoints.append(wp_home)

        # Add Takeoff
        wp_takeoff = Waypoint()
        wp_takeoff.frame = Waypoint.FRAME_GLOBAL_REL_ALT
        wp_takeoff.command = 22 # MAV_CMD_NAV_TAKEOFF
        wp_takeoff.is_current = False
        wp_takeoff.autocontinue = True
        wp_takeoff.x_lat = self.latitude
        wp_takeoff.y_long = self.longitude
        wp_takeoff.z_alt = float(altitude)
        req.waypoints.append(wp_takeoff)

        # Upload waypoints
        for item in waypoints:
            wp = Waypoint()
            wp.frame = Waypoint.FRAME_GLOBAL_REL_ALT
            wp.command = 16 # MAV_CMD_NAV_WAYPOINT
            wp.is_current = False
            wp.autocontinue = True
            wp.x_lat = float(item[0])
            wp.y_long = float(item[1])
            wp.z_alt = float(altitude)
            req.waypoints.append(wp)

        if self.wp_push_client.wait_for_service(timeout_sec=1.0):
            self.wp_push_client.call_async(req)
            print("Mission uploaded successfully.")

