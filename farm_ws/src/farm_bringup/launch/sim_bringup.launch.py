from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    ld = LaunchDescription()

    try:
        gz = get_package_share_directory('farm_gazebo')
        world = os.path.join(gz, 'worlds', 'farm_world.world')
        if os.path.exists(world):
            ld.add_action(ExecuteProcess(
                cmd=['gz', 'sim', world],
                output='screen',
                shell=True,
            ))
    except Exception:
        pass

    nodes = [
        Node(package='farm_mission', executable='mission_state_machine', name='mission_state_machine', output='screen'),
        Node(package='farm_mission', executable='waypoint_sampler', name='waypoint_sampler', output='screen'),
        Node(package='farm_perception', executable='perception_node', name='perception_node', output='screen'),
        Node(package='farm_sensors', executable='soil_data_publisher', name='soil_data_publisher', output='screen'),
    ]
    for n in nodes:
        ld.add_action(n)

    return ld
