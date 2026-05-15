#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger, SetBool
import subprocess
import signal
import os
import psutil
import json
import shutil

topic2record=['/camera/image/compressed', '/mavros/imu/data', '/mavros/global_position/global',
 '/mavros/global_position/rel_alt']

class OnboardSystemController(Node):
    def __init__(self):
        super().__init__('onboard_system_controller')
        
        # 1. Standart ROS 2 Servis Sunucuları
        self.srv_start_record = self.create_service(Trigger, '/drone/start_record', self.start_record_cb)
        self.srv_stop_record = self.create_service(Trigger, '/drone/stop_record', self.stop_record_cb)
        self.srv_toggle_detection = self.create_service(SetBool, '/drone/toggle_detection', self.toggle_detection_cb)
        
        # 2. Heartbeat Yayıncısı (Sistem Durumu)
        self.heartbeat_pub = self.create_publisher(String, '/drone/heartbeat', 10)
        self.heartbeat_timer = self.create_timer(1.0, self.publish_heartbeat)

        # Durum Değişkenleri
        self.bag_process = None
        self.is_recording = False
        self.is_detecting = False # Canlı tespiti aktif mi?
        
        self.get_logger().info('Yerleşik Sistem Kontrolcüsü (Onboard System Controller) AKTİF.')

    def start_record_cb(self, request, response):
        free_space_gb = shutil.disk_usage("/home")[2] / (1024**3)
        if free_space_gb < 5.0:
            response.success = False
            response.message = f"Hata: Yetersiz disk alanı ({free_space_gb:.1f} GB)."
            return response

        if not self.is_recording:
            try:
                record_path = '/home/orin/flight_records/mission_data'
                cmd = [
                    'ros2', 'bag', 'record', '-o', record_path,
                    *topic2record
                ]
                self.bag_process = subprocess.Popen(
                    cmd, preexec_fn=os.setsid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                self.is_recording = True
                response.success = True
                response.message = "Sensör kaydı başarıyla başlatıldı."
            except Exception as e:
                response.success = False
                response.message = f"Kayıt hatası: {str(e)}"
        else:
            response.success = False
            response.message = "Kayıt zaten devam ediyor."
        return response

    def stop_record_cb(self, request, response):
        if self.is_recording and self.bag_process:
            os.killpg(os.getpgid(self.bag_process.pid), signal.SIGINT)
            self.bag_process.wait(timeout=10)
            self.bag_process = None
            self.is_recording = False
            response.success = True
            response.message = "Kayıt güvenli şekilde durduruldu."
        else:
            response.success = False
            response.message = "Aktif kayıt bulunamadı."
        return response

    def toggle_detection_cb(self, request, response):
        # Canlı tespiti algoritmasını (örneğin YOLO) açıp kapatan servis
        self.is_detecting = request.data
        durum = "AKTİF" if self.is_detecting else "PASİF"
        response.success = True
        response.message = f"Canlı tespiti {durum} hale getirildi."
        self.get_logger().info(response.message)
        return response

    def publish_heartbeat(self):
        # Sıcaklık kontrolü (Termal Throttling önlemi)
        temp_data = psutil.sensors_temperatures()
        cpu_temp = 0.0
        if 'thermal_zone0' in temp_data:
            cpu_temp = temp_data['thermal_zone0'][0].current

        ram_usage = psutil.virtual_memory().percent
        disk_free_gb = shutil.disk_usage("/home")[2] / (1024**3)

        heartbeat_payload = {
            "timestamp": self.get_clock().now().nanoseconds / 1e9,
            "status": "OK" if cpu_temp < 85.0 else "WARNING_HIGH_TEMP",
            "cpu_temp_c": round(cpu_temp, 1),
            "ram_usage_percent": ram_usage,
            "disk_free_gb": round(disk_free_gb, 1),
            "is_recording": self.is_recording,
            "is_detecting": self.is_detecting
        }

        msg = String()
        msg.data = json.dumps(heartbeat_payload)
        self.heartbeat_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    system_controller = OnboardSystemController()
    try:
        rclpy.spin(system_controller)
    except KeyboardInterrupt:
        pass
    finally:
        if system_controller.is_recording and system_controller.bag_process:
            os.killpg(os.getpgid(system_controller.bag_process.pid), signal.SIGINT)
        system_controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()