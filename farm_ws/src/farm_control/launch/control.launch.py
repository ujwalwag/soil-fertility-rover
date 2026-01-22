from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg = get_package_share_directory('farm_control')
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            name='controller_manager',
            parameters=[
                {'use_sim_time': use_sim_time},
                os.path.join(pkg, 'config', 'ros2_control.yaml'),
                os.path.join(pkg, 'config', 'diff_drive.yaml'),
                os.path.join(pkg, 'config', 'arm_controllers.yaml'),
            ],
            output='screen',
        ),
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['diff_drive_controller', '-c', 'controller_manager'],
            output='screen',
        ),
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_state_broadcaster', '-c', 'controller_manager'],
            output='screen',
        ),
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['arm_controller', '-c', 'controller_manager'],
            output='screen',
        ),
    ])
