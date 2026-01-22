from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg = get_package_share_directory('farm_arm')
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        Node(
            package='moveit_ros_move_group',
            executable='move_group',
            name='move_group',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time},
                os.path.join(pkg, 'config', 'kinematics.yaml'),
                os.path.join(pkg, 'config', 'controllers.yaml'),
                os.path.join(pkg, 'config', 'joint_limits.yaml'),
            ],
        ),
    ])
