from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """Launch file optimized for interactive Gazebo GUI."""
    # Get package directory
    pkg_farm_gazebo = get_package_share_directory('farm_gazebo')
    
    # Launch arguments
    world_file = LaunchConfiguration('world', default=os.path.join(pkg_farm_gazebo, 'worlds', 'farm_world.world'))
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-10.0')
    y_pose = LaunchConfiguration('y_pose', default='-10.0')
    z_pose = LaunchConfiguration('z_pose', default='0.1')
    yaw_pose = LaunchConfiguration('yaw_pose', default='0.0')
    use_turtlebot3_om = LaunchConfiguration('use_turtlebot3_om', default='false')
    
    # Launch Gazebo with explicit GUI settings for interactivity
    # Set environment variables to ensure GUI works properly
    env = os.environ.copy()
    env['LIBGL_ALWAYS_INDIRECT'] = '1'  # For X11 forwarding
    env['QT_QPA_PLATFORM'] = 'xcb'  # Use X11 platform
    
    gazebo_process = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen',
        env=env,
        shell=False
    )
    
    # Spawn robot
    spawn_robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_gazebo, 'launch', 'spawn_robot.launch.py')
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'x_pose': x_pose,
            'y_pose': y_pose,
            'z_pose': z_pose,
            'yaw_pose': yaw_pose,
            'use_turtlebot3_om': use_turtlebot3_om
        }.items()
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(pkg_farm_gazebo, 'worlds', 'farm_world.world'),
            description='Path to the Gazebo world file'
        ),
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
        DeclareLaunchArgument(
            'yaw_pose',
            default_value='0.0',
            description='Initial yaw orientation of the robot'
        ),
        DeclareLaunchArgument(
            'use_turtlebot3_om',
            default_value='false',
            description='Use TurtleBot3 with Open Manipulator from dataset if true'
        ),
        gazebo_process,
        spawn_robot_launch,
    ])
