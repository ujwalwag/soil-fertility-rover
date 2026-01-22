#!/usr/bin/env python3
"""Waypoint sampler: generates sampling waypoints within geofence."""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, PolygonStamped
from nav_msgs.msg import Path

from .geofence_manager import GeofenceManager


class WaypointSampler(Node):
    def __init__(self):
        super().__init__('waypoint_sampler')
        self.geofence = GeofenceManager()
        self.waypoints = []
        self.idx = 0

        self.waypoint_pub = self.create_publisher(PoseStamped, '/waypoint_sampler/current_waypoint', 10)
        self.path_pub = self.create_publisher(Path, '/waypoint_sampler/path', 10)
        self.create_subscription(PolygonStamped, '/waypoint_sampler/geofence', self._geofence_cb, 10)

        self.declare_parameter('sampling_spacing', 1.0)
        self.declare_parameter('grid_pattern', 'zigzag')
        self.get_logger().info('Waypoint sampler started')

    def _geofence_cb(self, msg):
        self.geofence.set_geofence(msg)
        self._generate()
        self._publish_path()
        self._publish_current()

    def _generate(self):
        if self.geofence.polygon is None or len(self.geofence.polygon.polygon.points) < 3:
            return
        pts = self.geofence.polygon.polygon.points
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]
        mnx, mxx = min(xs), max(xs)
        mny, mxy = min(ys), max(ys)
        sp = max(0.1, self.get_parameter('sampling_spacing').get_parameter_value().double_value)
        step = max(1, int(sp))
        pat = self.get_parameter('grid_pattern').get_parameter_value().string_value

        self.waypoints = []
        y = mny
        zig = False
        while y <= mxy:
            if pat == 'zigzag':
                xr = range(int(mxx), int(mnx) - 1, -step) if zig else range(int(mnx), int(mxx) + 1, step)
                zig = not zig
            else:
                xr = range(int(mnx), int(mxx) + 1, step)
            for x in xr:
                if self.geofence.contains(x, y):
                    wp = PoseStamped()
                    wp.header.frame_id = 'map'
                    wp.pose.position.x = float(x)
                    wp.pose.position.y = float(y)
                    wp.pose.position.z = 0.0
                    wp.pose.orientation.w = 1.0
                    self.waypoints.append(wp)
            y += sp
        self.idx = 0
        self.get_logger().info('Generated %d waypoints' % len(self.waypoints))

    def _publish_path(self):
        if not self.waypoints:
            return
        path = Path()
        path.header.frame_id = 'map'
        path.header.stamp = self.get_clock().now().to_msg()
        path.poses = self.waypoints
        self.path_pub.publish(path)

    def _publish_current(self):
        if self.waypoints and self.idx < len(self.waypoints):
            wp = self.waypoints[self.idx]
            wp.header.stamp = self.get_clock().now().to_msg()
            self.waypoint_pub.publish(wp)

    def next(self):
        if self.idx < len(self.waypoints) - 1:
            self.idx += 1
            self._publish_current()
            return True
        return False


def main(args=None):
    rclpy.init(args=args)
    node = WaypointSampler()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
