from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='farm_mission',
            executable='mission_state_machine',
            name='mission_state_machine',
            output='screen',
        ),
        Node(
            package='farm_mission',
            executable='waypoint_sampler',
            name='waypoint_sampler',
            output='screen',
        ),
    ])
