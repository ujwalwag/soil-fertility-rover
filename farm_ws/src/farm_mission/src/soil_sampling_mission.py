#!/usr/bin/env python3
"""Soil sampling mission controller - navigates to 4 random waypoints and samples."""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import Float64MultiArray
import random
import math
from enum import Enum


class MissionState(Enum):
    IDLE = 'idle'
    INITIALIZING = 'initializing'
    NAVIGATING = 'navigating'
    ARM_DOWN = 'arm_down'
    SAMPLING = 'sampling'
    ARM_UP = 'arm_up'
    RETURNING = 'returning'
    COMPLETED = 'completed'
    ERROR = 'error'


class SoilSamplingMission(Node):
    def __init__(self):
        super().__init__('soil_sampling_mission')
        
        # Mission parameters
        self.declare_parameter('num_waypoints', 4)
        self.declare_parameter('sampling_radius', 10.0)  # meters from spawn
        self.declare_parameter('sampling_duration', 5.0)  # seconds
        
        # State
        self.state = MissionState.IDLE
        self.spawn_pose = None
        self.waypoints = []
        self.current_waypoint_idx = 0
        self.arm_down_time = None
        
        # Subscribers
        # Get initial pose from robot_state_publisher or set manually
        # For now, we'll get it from the spawn position parameter
        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/amcl_pose',
            self._pose_cb,
            10
        )
        
        # Get spawn position from launch parameters or use default
        self.declare_parameter('spawn_x', -10.0)
        self.declare_parameter('spawn_y', -10.0)
        spawn_x = self.get_parameter('spawn_x').get_parameter_value().double_value
        spawn_y = self.get_parameter('spawn_y').get_parameter_value().double_value
        
        # Set spawn pose from parameters
        self.spawn_pose = PoseStamped()
        self.spawn_pose.header.frame_id = 'map'
        self.spawn_pose.pose.position.x = spawn_x
        self.spawn_pose.pose.position.y = spawn_y
        self.spawn_pose.pose.position.z = 0.1
        self.spawn_pose.pose.orientation.w = 1.0
        
        self._generate_waypoints()
        if self.waypoints:
            self.state = MissionState.INITIALIZING
            self.get_logger().info(f'Mission initialized from spawn ({spawn_x:.2f}, {spawn_y:.2f})')
        
        # Publishers for arm control
        self.arm_joint_pub = self.create_publisher(
            Float64MultiArray,
            '/arm_controller/commands',
            10
        )
        
        # Action clients
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Wait for navigation server
        self.get_logger().info('Waiting for navigation server...')
        if not self.nav_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().warn('Navigation server not available, will retry...')
        
        # Timers
        self.create_timer(0.1, self._mission_loop)
        self.create_timer(1.0, self._status_log)
        
        self.get_logger().info('Soil sampling mission controller started')
        self.get_logger().info('Mission initialized, starting navigation...')
        
    
    def _pose_cb(self, msg):
        """Update current pose from AMCL."""
        self.current_pose = msg
    
    def _generate_waypoints(self):
        """Generate 4 random waypoints around spawn position."""
        if self.spawn_pose is None:
            return
            
        num_wp = self.get_parameter('num_waypoints').get_parameter_value().integer_value
        radius = self.get_parameter('sampling_radius').get_parameter_value().double_value
        spawn_x = self.spawn_pose.pose.position.x
        spawn_y = self.spawn_pose.pose.position.y
        
        self.waypoints = []
        for i in range(num_wp):
            # Generate random angle and distance
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(radius * 0.3, radius)
            
            wp = PoseStamped()
            wp.header.frame_id = 'map'
            wp.pose.position.x = spawn_x + distance * math.cos(angle)
            wp.pose.position.y = spawn_y + distance * math.sin(angle)
            wp.pose.position.z = 0.0
            # Face towards waypoint
            yaw = math.atan2(distance * math.sin(angle), distance * math.cos(angle))
            wp.pose.orientation.z = math.sin(yaw / 2.0)
            wp.pose.orientation.w = math.cos(yaw / 2.0)
            
            self.waypoints.append(wp)
            self.get_logger().info(f'Waypoint {i+1}: ({wp.pose.position.x:.2f}, {wp.pose.position.y:.2f})')
    
    def _arm_down(self):
        """Move arm to sampling position (down)."""
        # Joint positions: [joint1, joint2, joint3, joint4, gripper_left, gripper_right]
        cmd = Float64MultiArray()
        cmd.data = [0.0, -1.2, 1.0, -0.5, 0.0, 0.0]  # Arm down position
        self.arm_joint_pub.publish(cmd)
        self.get_logger().info('Arm moving down to sampling position...')
    
    def _arm_up(self):
        """Move arm to stowed position (up)."""
        cmd = Float64MultiArray()
        cmd.data = [0.0, 0.5, -0.5, 0.0, 0.0, 0.0]  # Arm up/stowed position
        self.arm_joint_pub.publish(cmd)
        self.get_logger().info('Arm moving up to stowed position...')
    
    def _navigate_to_waypoint(self, waypoint):
        """Navigate to a waypoint using NAV2."""
        if not self.nav_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Navigation server not available, retrying...')
            return False
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = waypoint
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.header.frame_id = 'map'
        
        self.get_logger().info(f'Navigating to waypoint {self.current_waypoint_idx + 1} at ({waypoint.pose.position.x:.2f}, {waypoint.pose.position.y:.2f})...')
        self._nav_future = self.nav_client.send_goal_async(goal_msg)
        self._nav_future.add_done_callback(self._nav_response_cb)
        return True
    
    def _nav_response_cb(self, future):
        """Handle navigation goal response."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Navigation goal rejected')
            self.state = MissionState.ERROR
            return
        
        self.get_logger().info('Navigation goal accepted')
        self._nav_result_future = goal_handle.get_result_async()
        self._nav_result_future.add_done_callback(self._nav_result_cb)
    
    def _nav_result_cb(self, future):
        """Handle navigation result."""
        result = future.result()
        if result.status == 4:  # SUCCEEDED
            self.get_logger().info('Reached waypoint!')
            if self.state == MissionState.RETURNING:
                self.state = MissionState.COMPLETED
                self.get_logger().info('Mission completed! Returned to spawn.')
            else:
                self.state = MissionState.ARM_DOWN
        else:
            self.get_logger().warn(f'Navigation failed with status {result.status}, retrying...')
            # Retry navigation
            if self.state == MissionState.RETURNING:
                if self.spawn_pose:
                    self._navigate_to_waypoint(self.spawn_pose)
            elif self.current_waypoint_idx < len(self.waypoints):
                self._navigate_to_waypoint(self.waypoints[self.current_waypoint_idx])
    
    def _mission_loop(self):
        """Main mission state machine loop."""
        if self.state == MissionState.IDLE:
            return
        
        elif self.state == MissionState.INITIALIZING:
            if self.waypoints:
                self.current_waypoint_idx = 0
                self.state = MissionState.NAVIGATING
                self._navigate_to_waypoint(self.waypoints[0])
        
        elif self.state == MissionState.NAVIGATING:
            # Navigation is handled by async callbacks
            pass
        
        elif self.state == MissionState.ARM_DOWN:
            self._arm_down()
            self.arm_down_time = self.get_clock().now()
            self.state = MissionState.SAMPLING
        
        elif self.state == MissionState.SAMPLING:
            duration = self.get_parameter('sampling_duration').get_parameter_value().double_value
            if (self.get_clock().now() - self.arm_down_time).nanoseconds / 1e9 >= duration:
                self.get_logger().info('Sampling complete, raising arm...')
                self.state = MissionState.ARM_UP
                self._arm_up()
        
        elif self.state == MissionState.ARM_UP:
            # Wait a bit for arm to move up (2 seconds after sampling)
            if self.arm_down_time and (self.get_clock().now() - self.arm_down_time).nanoseconds / 1e9 >= 7.0:
                # Move to next waypoint or return home
                self.current_waypoint_idx += 1
                if self.current_waypoint_idx < len(self.waypoints):
                    self.state = MissionState.NAVIGATING
                    self._navigate_to_waypoint(self.waypoints[self.current_waypoint_idx])
                else:
                    # All waypoints done, return to spawn
                    self.get_logger().info('All waypoints completed, returning to spawn...')
                    self.state = MissionState.RETURNING
                    if self.spawn_pose:
                        self._navigate_to_waypoint(self.spawn_pose)
        
        elif self.state == MissionState.RETURNING:
            # Navigation handled by async callbacks
            pass
        
        elif self.state == MissionState.COMPLETED:
            self.get_logger().info('Mission completed!')
        
        elif self.state == MissionState.ERROR:
            self.get_logger().error('Mission error state')
    
    def _status_log(self):
        """Periodic status logging."""
        if self.state != MissionState.IDLE:
            self.get_logger().info(f'State: {self.state.value}, Waypoint: {self.current_waypoint_idx}/{len(self.waypoints)}')


def main(args=None):
    rclpy.init(args=args)
    node = SoilSamplingMission()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
