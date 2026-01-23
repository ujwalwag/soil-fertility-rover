from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get package directories
    pkg_farm_gazebo = get_package_share_directory('farm_gazebo')
    pkg_farm_navigation = get_package_share_directory('farm_navigation')
    pkg_farm_control = get_package_share_directory('farm_control')
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-10.0')
    y_pose = LaunchConfiguration('y_pose', default='-10.0')
    z_pose = LaunchConfiguration('z_pose', default='0.1')
    
    # Launch Gazebo simulation with robot
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_gazebo, 'launch', 'farm_world.launch.py')
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'x_pose': x_pose,
            'y_pose': y_pose,
            'z_pose': z_pose,
            'use_turtlebot3_om': 'true',  # Explicitly set to use TurtleBot3 OM
        }.items()
    )
    
    # Launch robot controller (ros2_control) - REQUIRED for robot to move
    pkg_farm_control = get_package_share_directory('farm_control')
    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_control, 'launch', 'control.launch.py')
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
        }.items()
    )
    
    # Launch Gazebo-ROS bridge for sensors (scan, imu, camera)
    pkg_farm_gazebo = get_package_share_directory('farm_gazebo')
    gz_bridge_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_gazebo, 'launch', 'gz_bridge.launch.py')
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
        }.items()
    )
    
    # Launch NAV2 navigation
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_navigation, 'launch', 'nav2.launch.py')
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
        }.items()
    )
    
    # Launch mission controller
    mission_node = Node(
        package='farm_mission',
        executable='soil_sampling_mission',
        name='soil_sampling_mission',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'spawn_x': x_pose,
            'spawn_y': y_pose,
            'num_waypoints': 4,
            'sampling_radius': 10.0,
            'sampling_duration': 5.0,
        }]
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time if true'
        ),
        DeclareLaunchArgument(
            'x_pose',
            default_value='-10.0',
            description='Initial x position of the robot'
        ),
        DeclareLaunchArgument(
            'y_pose',
            default_value='-10.0',
            description='Initial y position of the robot'
        ),
        DeclareLaunchArgument(
            'z_pose',
            default_value='0.1',
            description='Initial z position of the robot'
        ),
        gazebo_sim,
        # Control launch starts controller_manager and spawns controllers
        # Delay to ensure robot_description is published and robot is spawned
        TimerAction(
            period=10.0,  # Wait for robot spawn and robot_description publication
            actions=[control_launch]
        ),
        gz_bridge_launch,
        nav2_launch,
        mission_node,
    ])
