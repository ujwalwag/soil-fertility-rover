#!/usr/bin/env python3
"""Placeholder: convert GUI waypoints to Nav2 NavigateToPose / FollowWaypoints actions."""
import rclpy
from rclpy.node import Node


def main(args=None):
    rclpy.init(args=args)
    node = Node("waypoint_planner")
    node.get_logger().info(
        "waypoint_planner: stub — implement Nav2 action clients for your field workflow."
    )
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
