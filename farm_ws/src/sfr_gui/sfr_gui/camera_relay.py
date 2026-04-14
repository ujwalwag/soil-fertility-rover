#!/usr/bin/env python3
"""Optional relay: normalize camera topic for the GUI (subscribe /camera/image_raw -> /camera/image_display)."""

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image

CAMERA_SOURCE_TOPIC = "/camera/image_raw"
CAMERA_OUT_TOPIC = "/camera/image_display"


class CameraRelayNode(Node):
    def __init__(self):
        super().__init__("camera_relay")
        self.pub = self.create_publisher(Image, CAMERA_OUT_TOPIC, qos_profile_sensor_data)
        self.create_subscription(Image, CAMERA_SOURCE_TOPIC, self._cb, qos_profile_sensor_data)
        self.get_logger().info(
            "Relay: %s -> %s" % (CAMERA_SOURCE_TOPIC, CAMERA_OUT_TOPIC)
        )

    def _cb(self, msg):
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CameraRelayNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
