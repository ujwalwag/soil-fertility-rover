#!/usr/bin/env python3
"""Mission state machine."""

from enum import Enum
import uuid
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from farm_interfaces.msg import MissionStatus
from farm_interfaces.action import DoSample
from geometry_msgs.msg import PoseStamped


class MissionState(Enum):
    IDLE = 'idle'
    INITIALIZING = 'initializing'
    NAVIGATING = 'navigating'
    SAMPLING = 'sampling'
    RETURNING = 'returning'
    COMPLETED = 'completed'
    ERROR = 'error'


class MissionStateMachine(Node):
    def __init__(self):
        super().__init__('mission_state_machine')
        self.state = MissionState.IDLE
        self.mission_id = str(uuid.uuid4())
        self.waypoints_done = 0
        self.waypoints_total = 0
        self.current_pose = PoseStamped()
        self.current_pose.header.frame_id = 'map'

        self.status_pub = self.create_publisher(MissionStatus, '/mission/status', 10)
        self.pose_sub = self.create_subscription(
            PoseStamped, '/state_estimation/pose', self._pose_cb, 10
        )
        self.sample_client = ActionClient(self, DoSample, '/do_sample')
        self.create_timer(1.0, self._tick)
        self.create_timer(0.5, self._publish_status)
        self.get_logger().info('Mission state machine started')

    def _pose_cb(self, msg):
        self.current_pose = msg

    def _tick(self):
        if self.state == MissionState.INITIALIZING:
            self.state = MissionState.NAVIGATING

    def _publish_status(self):
        msg = MissionStatus()
        msg.timestamp = self.get_clock().now().to_msg()
        msg.mission_id = self.mission_id
        msg.state = self.state.value
        msg.status_code = 0
        msg.status_message = 'Mission in %s' % self.state.value
        msg.current_pose = self.current_pose
        msg.waypoints_completed = self.waypoints_done
        msg.waypoints_total = self.waypoints_total
        msg.progress_percent = (self.waypoints_done / self.waypoints_total * 100.0) if self.waypoints_total else 0.0
        self.status_pub.publish(msg)

    def request_sample(self, pose: PoseStamped, depth: float = 0.1):
        if not self.sample_client.wait_for_server(timeout_sec=1.0):
            return False
        goal = DoSample.Goal()
        goal.target_pose = pose
        goal.depth = depth
        self.sample_client.send_goal_async(goal)
        return True


def main(args=None):
    rclpy.init(args=args)
    node = MissionStateMachine()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
