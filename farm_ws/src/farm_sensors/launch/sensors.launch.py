from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='farm_sensors',
            executable='soil_data_publisher',
            name='soil_data_publisher',
            output='screen',
        ),
    ])
