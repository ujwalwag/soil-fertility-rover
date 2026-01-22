from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get package directories
    pkg_farm_description = get_package_share_directory('farm_description')
    pkg_farm_gazebo = get_package_share_directory('farm_gazebo')
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    z_pose = LaunchConfiguration('z_pose', default='0.0')
    yaw_pose = LaunchConfiguration('yaw_pose', default='0.0')
    
    # URDF file path
    urdf_file = os.path.join(pkg_farm_description, 'urdf', 'turtlebot_arm.urdf.xacro')
    
    # Process URDF with xacro
    robot_description = Command(['xacro ', urdf_file])
    
    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_description
        }]
    )
    
    # Spawn robot in Gazebo using ros_gz_sim
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-entity', 'turtlebot_arm',
            '-topic', 'robot_description',
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose,
            '-Y', yaw_pose
        ],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time if true'
        ),
        DeclareLaunchArgument(
            'x_pose',
            default_value='0.0',
            description='Initial x position of the robot'
        ),
        DeclareLaunchArgument(
            'y_pose',
            default_value='0.0',
            description='Initial y position of the robot'
        ),
        DeclareLaunchArgument(
            'z_pose',
            default_value='0.0',
            description='Initial z position of the robot'
        ),
        DeclareLaunchArgument(
            'yaw_pose',
            default_value='0.0',
            description='Initial yaw orientation of the robot'
        ),
        robot_state_publisher,
        spawn_entity,
    ])
