from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get package directories
    pkg_farm_gazebo = get_package_share_directory('farm_gazebo')
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    # Include Gazebo simulation with robot
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_gazebo, 'launch', 'farm_sim.launch.py')
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'x_pose': '0.0',
            'y_pose': '0.0',
            'z_pose': '0.0',
            'yaw_pose': '0.0'
        }.items()
    )

    # Onboard nodes (commented out until executables are implemented)
    # These will be uncommented as the nodes are developed
    onboard_nodes = [
        # Node(package='farm_mission', executable='mission_node', name='mission_node', output='screen'),
        # Node(package='farm_navigation', executable='waypoint_sampler', name='waypoint_sampler', output='screen'),
        # Node(package='farm_arm', executable='sampling_orchestrator', name='sampling_orchestrator', output='screen'),
        # Node(package='farm_perception', executable='opencv_verification', name='opencv_verification', output='screen'),
        # Node(package='farm_sensors', executable='state_estimation', name='state_estimation', output='screen'),
        # Node(package='farm_sensors', executable='soil_data_pipeline', name='soil_data_pipeline', output='screen'),
        # Node(package='farm_sensors', executable='robot_health', name='robot_health', output='screen'),
        # Node(package='farm_base_station', executable='lora_onboard', name='lora_onboard', output='screen'),
    ]

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time if true'
        ),
        gazebo_sim,
        *onboard_nodes,
    ])
