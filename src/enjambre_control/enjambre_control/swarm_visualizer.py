#!/usr/bin/env python3
from functools import partial

import rclpy
from geometry_msgs.msg import Pose, TransformStamped
from rclpy.node import Node
from std_msgs.msg import ColorRGBA, String
from tf2_ros import TransformBroadcaster
from visualization_msgs.msg import Marker, MarkerArray

from .swarm_config import DEFAULT_ALTITUDE, DRONE_MODEL_SCALE, LED_MARKER_SCALE, SWARM_DRONES, TEXT_MARKER_SCALE


class SwarmVisualizer(Node):
    def __init__(self):
        super().__init__('swarm_visualizer')
        self.tf_broadcaster = TransformBroadcaster(self)
        self.marker_pub = self.create_publisher(MarkerArray, '/swarm/markers', 10)

        self.poses = {}
        self.led_colors = {}
        self.formation_labels = {}

        for drone_name, cfg in SWARM_DRONES.items():
            x, y, z = cfg['position']
            pose = Pose()
            pose.position.x = x
            pose.position.y = y
            pose.position.z = z if z else DEFAULT_ALTITUDE
            pose.orientation.w = 1.0
            self.poses[drone_name] = pose
            color = ColorRGBA()
            color.r = 0.0
            color.g = 0.0
            color.b = 1.0
            color.a = 1.0
            self.led_colors[drone_name] = color
            self.formation_labels[drone_name] = ''

            self.create_subscription(Pose, f'/{drone_name}/cmd_pose', partial(self.pose_cb, drone_name), 10)
            self.create_subscription(ColorRGBA, f'/{drone_name}/led_color', partial(self.led_cb, drone_name), 10)
            self.create_subscription(String, f'/{drone_name}/formation_name', partial(self.label_cb, drone_name), 10)

        self.create_timer(0.1, self.publish_visuals)
        self.get_logger().info('Visualizador del enjambre iniciado')

    def pose_cb(self, drone_name: str, msg: Pose):
        self.poses[drone_name] = msg

    def led_cb(self, drone_name: str, msg: ColorRGBA):
        self.led_colors[drone_name] = msg

    def label_cb(self, drone_name: str, msg: String):
        self.formation_labels[drone_name] = msg.data

    def publish_visuals(self):
        now = self.get_clock().now().to_msg()
        marker_array = MarkerArray()

        for idx, drone_name in enumerate(SWARM_DRONES):
            pose = self.poses[drone_name]
            color = self.led_colors[drone_name]

            tf_msg = TransformStamped()
            tf_msg.header.stamp = now
            tf_msg.header.frame_id = 'world'
            tf_msg.child_frame_id = f'{drone_name}_base_link'
            tf_msg.transform.translation.x = pose.position.x
            tf_msg.transform.translation.y = pose.position.y
            tf_msg.transform.translation.z = pose.position.z
            tf_msg.transform.rotation = pose.orientation
            self.tf_broadcaster.sendTransform(tf_msg)

            led = Marker()
            led.header.frame_id = 'world'
            led.header.stamp = now
            led.ns = 'swarm_leds'
            led.id = idx
            led.type = Marker.SPHERE
            led.action = Marker.ADD
            led.pose.position.x = pose.position.x
            led.pose.position.y = pose.position.y
            led.pose.position.z = pose.position.z + 0.10
            led.pose.orientation.w = 1.0
            led.scale.x = LED_MARKER_SCALE
            led.scale.y = LED_MARKER_SCALE
            led.scale.z = LED_MARKER_SCALE
            led.color = color
            marker_array.markers.append(led)

            text = Marker()
            text.header.frame_id = 'world'
            text.header.stamp = now
            text.ns = 'swarm_labels'
            text.id = 100 + idx
            text.type = Marker.TEXT_VIEW_FACING
            text.action = Marker.ADD
            text.pose.position.x = pose.position.x
            text.pose.position.y = pose.position.y
            text.pose.position.z = pose.position.z + 0.20
            text.pose.orientation.w = 1.0
            text.scale.z = TEXT_MARKER_SCALE
            text.color.r = 1.0
            text.color.g = 1.0
            text.color.b = 1.0
            text.color.a = 1.0
            text.text = drone_name
            marker_array.markers.append(text)

        self.marker_pub.publish(marker_array)


def main(args=None):
    rclpy.init(args=args)
    node = SwarmVisualizer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
