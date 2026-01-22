#!/usr/bin/env python3
"""Soil data publisher: aggregates NPK, moisture, pose; publishes SoilSample."""

import uuid
import rclpy
from rclpy.node import Node
from farm_interfaces.msg import SoilSample
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Bool

from .npk_driver import read_npk
from .moisture_driver import read_moisture


class SoilDataPublisher(Node):
    def __init__(self):
        super().__init__('soil_data_publisher')
        self.sample_ok_sub = self.create_subscription(
            Bool, '/perception/sample_ok', self._sample_ok_cb, 10
        )
        self.pose_sub = self.create_subscription(
            PoseStamped, '/state_estimation/pose', self._pose_cb, 10
        )
        self.pub = self.create_publisher(SoilSample, '/soil_data/samples', 10)
        self.pose = None
        self.sample_ok = False
        self.create_timer(1.0, self._read_sensors)
        self.get_logger().info('Soil data publisher started')

    def _pose_cb(self, msg):
        self.pose = msg

    def _sample_ok_cb(self, msg):
        if msg.data and not self.sample_ok:
            self.sample_ok = True
            self._publish_sample()
        else:
            self.sample_ok = msg.data

    def _read_sensors(self):
        pass

    def _publish_sample(self):
        if self.pose is None:
            return
        n, p, k = read_npk()
        m = read_moisture()
        msg = SoilSample()
        msg.timestamp = self.get_clock().now().to_msg()
        msg.sample_id = str(uuid.uuid4())
        msg.pose = self.pose
        msg.npk_nitrogen = n
        msg.npk_phosphorus = p
        msg.npk_potassium = k
        msg.moisture = m
        msg.temperature = 25.0
        msg.humidity = 50.0
        msg.ph = 7.0
        self.pub.publish(msg)
        self.get_logger().info('Published sample %s' % msg.sample_id)


def main(args=None):
    rclpy.init(args=args)
    node = SoilDataPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
