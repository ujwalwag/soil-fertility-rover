#!/usr/bin/env python3
"""Simple arm controller for Open Manipulator - publishes joint commands."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
import math


class SimpleArmController(Node):
    def __init__(self):
        super().__init__('simple_arm_controller')
        
        # Joint names for Open Manipulator
        self.joint_names = ['joint1', 'joint2', 'joint3', 'joint4', 'gripper_left_joint', 'gripper_right_joint']
        
        # Current joint positions
        self.current_positions = [0.0] * len(self.joint_names)
        
        # Publishers - publish to individual joint controllers or joint_trajectory_controller
        self.joint_pubs = {}
        for joint in self.joint_names:
            self.joint_pubs[joint] = self.create_publisher(
                Float64MultiArray,
                f'/{joint}_controller/commands',
                10
            )
        
        # Alternative: publish to joint_trajectory_controller if available
        self.joint_cmd_pub = self.create_publisher(
            Float64MultiArray,
            '/arm_controller/commands',
            10
        )
        
        # Subscribe to joint states to know current positions
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self._joint_state_cb,
            10
        )
        
        self.get_logger().info('Simple arm controller started')
    
    def _joint_state_cb(self, msg):
        """Update current joint positions."""
        for i, name in enumerate(msg.name):
            if name in self.joint_names:
                idx = self.joint_names.index(name)
                self.current_positions[idx] = msg.position[i]
    
    def move_arm_down(self):
        """Move arm to sampling position (down)."""
        # Joint positions: [joint1, joint2, joint3, joint4, gripper_left, gripper_right]
        # Adjust these to lower the end effector
        positions = [
            0.0,      # joint1: base rotation (keep centered)
            -1.2,     # joint2: shoulder down
            1.0,      # joint3: elbow up
            -0.5,     # joint4: wrist down
            0.0,      # gripper_left: closed
            0.0       # gripper_right: closed
        ]
        self._send_joint_commands(positions)
        self.get_logger().info('Arm moving down to sampling position')
    
    def move_arm_up(self):
        """Move arm to stowed position (up)."""
        positions = [
            0.0,      # joint1: base rotation
            0.5,      # joint2: shoulder up
            -0.5,     # joint3: elbow down
            0.0,      # joint4: wrist neutral
            0.0,      # gripper_left: closed
            0.0       # gripper_right: closed
        ]
        self._send_joint_commands(positions)
        self.get_logger().info('Arm moving up to stowed position')
    
    def _send_joint_commands(self, positions):
        """Send joint position commands."""
        if len(positions) != len(self.joint_names):
            self.get_logger().error(f'Position array length mismatch: {len(positions)} != {len(self.joint_names)}')
            return
        
        # Try joint_trajectory_controller first
        cmd = Float64MultiArray()
        cmd.data = positions
        self.joint_cmd_pub.publish(cmd)
        
        # Also try individual joint controllers
        for i, joint in enumerate(self.joint_names):
            joint_cmd = Float64MultiArray()
            joint_cmd.data = [positions[i]]
            self.joint_pubs[joint].publish(joint_cmd)


def main(args=None):
    rclpy.init(args=args)
    node = SimpleArmController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
