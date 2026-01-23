#!/usr/bin/env python3
"""Parameter server node to publish controller_manager parameters for Gazebo plugin"""
import rclpy
from rclpy.node import Node
import yaml
import sys
import os


class ControllerParamServer(Node):
    def __init__(self, param_file):
        super().__init__('controller_param_server')
        self.get_logger().info(f'Loading controller parameters from {param_file}')
        
        # Load YAML file
        with open(param_file, 'r') as f:
            params = yaml.safe_load(f)
        
        # Set parameters on controller_manager node
        # The Gazebo plugin will create this node and read these parameters
        if 'controller_manager' in params and 'ros__parameters' in params['controller_manager']:
            cm_params = params['controller_manager']['ros__parameters']
            for key, value in cm_params.items():
                self.declare_parameter(f'controller_manager.{key}', value)
                self.get_logger().info(f'Set parameter: controller_manager.{key}')
        
        self.get_logger().info('Controller parameters published. Plugin can now read them.')


def main():
    if len(sys.argv) < 2:
        print('Usage: param_server.py <param_file>')
        return
    
    param_file = sys.argv[1]
    if not os.path.exists(param_file):
        print(f'Error: Parameter file not found: {param_file}')
        return
    
    rclpy.init()
    node = ControllerParamServer(param_file)
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
