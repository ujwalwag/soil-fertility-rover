#!/usr/bin/env python3
"""Perception node: soil contact and depth verification."""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool
from cv_bridge import CvBridge

from .soil_contact_detector import check_soil_contact
from .depth_verification import verify_depth


class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')
        self.bridge = CvBridge()
        self.camera_sub = self.create_subscription(
            Image, '/camera/image_raw', self._image_cb, 10
        )
        self.sample_ok_pub = self.create_publisher(Bool, '/perception/sample_ok', 10)
        self.declare_parameter('contact_threshold', 0.5)
        self.declare_parameter('depth_threshold_mm', 50.0)
        self.get_logger().info('Perception node started')

    def _image_cb(self, msg):
        try:
            img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            thresh = self.get_parameter('contact_threshold').get_parameter_value().double_value
            ok = check_soil_contact(img, thresh)
            out = Bool()
            out.data = ok
            self.sample_ok_pub.publish(out)
        except Exception as e:
            self.get_logger().error('Perception error: %s' % str(e))


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
