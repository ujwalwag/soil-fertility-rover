#!/usr/bin/env python3
"""Placeholder: soil sampling motions via joint trajectory / MoveIt when integrated."""
import rclpy
from rclpy.node import Node


def main(args=None):
    rclpy.init(args=args)
    node = Node("arm_controller")
    node.get_logger().info(
        "arm_controller: stub — wire to FollowJointTrajectory / MoveIt for probe insertion."
    )
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
