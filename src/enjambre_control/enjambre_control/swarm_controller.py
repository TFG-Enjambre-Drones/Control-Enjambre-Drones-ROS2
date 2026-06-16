#!/usr/bin/env python3
import math

import rclpy
from geometry_msgs.msg import Pose
from rclpy.node import Node
from std_msgs.msg import ColorRGBA, String

from .formations import FORMATIONS
from .swarm_config import COLOR_MAP, DEFAULT_ALTITUDE, DEFAULT_CENTER, DEFAULT_FORMATION, DEFAULT_YAW_DEG, PUBLISH_RATE_HZ, SWARM_DRONES


class DroneSwarmController(Node):
    def __init__(self):
        super().__init__('swarm_controller')

        self.declare_parameter('formation', DEFAULT_FORMATION)
        self.declare_parameter('center_x', DEFAULT_CENTER[0])
        self.declare_parameter('center_y', DEFAULT_CENTER[1])
        self.declare_parameter('altitude', DEFAULT_ALTITUDE)
        self.declare_parameter('yaw_deg', DEFAULT_YAW_DEG)

        self.active_formation = self.get_parameter('formation').get_parameter_value().string_value
        self.center_x = self.get_parameter('center_x').get_parameter_value().double_value
        self.center_y = self.get_parameter('center_y').get_parameter_value().double_value
        self.altitude = self.get_parameter('altitude').get_parameter_value().double_value
        self.yaw_deg = self.get_parameter('yaw_deg').get_parameter_value().double_value

        if self.active_formation not in FORMATIONS:
            self.get_logger().warn(f'Formación {self.active_formation} no válida. Uso: {DEFAULT_FORMATION}')
            self.active_formation = DEFAULT_FORMATION

        self.pose_publishers = {}
        self.led_publishers = {}
        self.status_publishers = {}

        for drone_name in SWARM_DRONES:
            self.pose_publishers[drone_name] = self.create_publisher(Pose, f'/{drone_name}/cmd_pose', 10)
            self.led_publishers[drone_name] = self.create_publisher(ColorRGBA, f'/{drone_name}/led_color', 10)
            self.status_publishers[drone_name] = self.create_publisher(String, f'/{drone_name}/formation_name', 10)

        period = 1.0 / PUBLISH_RATE_HZ
        self.create_timer(period, self.publish_swarm_state)
        self.get_logger().info(f'Controlador iniciado. Formación activa: {self.active_formation}')

    def set_formation(self, formation_name: str):
        if formation_name not in FORMATIONS:
            self.get_logger().error(f'Formación desconocida: {formation_name}')
            return
        self.active_formation = formation_name
        self.get_logger().info(f'Nueva formación: {formation_name}')

    def move_swarm(self, dx: float, dy: float):
        self.center_x += dx
        self.center_y += dy

    def set_led(self, drone_name: str, color_name: str):
        if drone_name not in SWARM_DRONES or color_name not in COLOR_MAP:
            return
        SWARM_DRONES[drone_name]['led_color'] = color_name

    def get_color_msg(self, color_name: str) -> ColorRGBA:
        rgba = COLOR_MAP.get(color_name, COLOR_MAP['blue'])
        msg = ColorRGBA()
        msg.r, msg.g, msg.b, msg.a = rgba
        return msg

    def compute_pose(self, rel_x: float, rel_y: float) -> Pose:
        angle = math.radians(self.yaw_deg)
        rot_x = rel_x * math.cos(angle) - rel_y * math.sin(angle)
        rot_y = rel_x * math.sin(angle) + rel_y * math.cos(angle)

        pose = Pose()
        pose.position.x = self.center_x + rot_x
        pose.position.y = self.center_y + rot_y
        pose.position.z = self.altitude
        pose.orientation.w = 1.0
        return pose

    def publish_swarm_state(self):
        offsets = FORMATIONS[self.active_formation]
        for drone_name, config in SWARM_DRONES.items():
            rel_x, rel_y = offsets[drone_name]
            pose = self.compute_pose(rel_x, rel_y)
            self.pose_publishers[drone_name].publish(pose)
            self.led_publishers[drone_name].publish(self.get_color_msg(config['led_color']))
            label = String()
            label.data = self.active_formation
            self.status_publishers[drone_name].publish(label)


def main(args=None):
    rclpy.init(args=args)
    node = DroneSwarmController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
