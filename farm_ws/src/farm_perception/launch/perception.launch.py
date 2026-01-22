from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg = get_package_share_directory('farm_perception')
    params = os.path.join(pkg, 'config', 'perception_params.yaml')

    return LaunchDescription([
        Node(
            package='farm_perception',
            executable='perception_node',
            name='perception_node',
            parameters=[params],
            output='screen',
        ),
    ])
