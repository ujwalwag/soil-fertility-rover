from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get package directory
    pkg_farm_gazebo = get_package_share_directory('farm_gazebo')
    
    # Launch arguments
    world_file = LaunchConfiguration('world', default=os.path.join(pkg_farm_gazebo, 'worlds', 'farm_world.world'))
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-10.0')
    y_pose = LaunchConfiguration('y_pose', default='-10.0')
    z_pose = LaunchConfiguration('z_pose', default='0.1')
    yaw_pose = LaunchConfiguration('yaw_pose', default='0.0')
    use_turtlebot3_om = LaunchConfiguration('use_turtlebot3_om', default='true')
    auto_start = LaunchConfiguration('auto_start', default='false')
    
    # Launch Gazebo with the farm world (running by default)
    # -r flag runs simulation immediately
    # Use paused:=true to start simulation paused
    paused = LaunchConfiguration('paused', default='false')
    
    # Launch Gazebo with GUI - simple configuration (was working earlier)
    # Set environment for mesh resource path
    env = os.environ.copy()
    # Only set DISPLAY if not already set
    if 'DISPLAY' not in env:
        env['DISPLAY'] = ':0'
    
    # Add mesh directory to Gazebo resource path
    pkg_farm_description = get_package_share_directory('farm_description')
    meshes_path = os.path.join(pkg_farm_description, 'meshes')
    if 'GZ_SIM_RESOURCE_PATH' in env:
        env['GZ_SIM_RESOURCE_PATH'] = meshes_path + ':' + env['GZ_SIM_RESOURCE_PATH']
    else:
        env['GZ_SIM_RESOURCE_PATH'] = meshes_path
    
    # Add ros2_control plugin library path for Gazebo Harmonic
    # This allows Gazebo to find the gz_ros2_control-system plugin
    ros_lib_path = '/opt/ros/jazzy/lib'
    # Set system plugin path (for system plugins)
    if 'GZ_SIM_SYSTEM_PLUGIN_PATH' in env:
        env['GZ_SIM_SYSTEM_PLUGIN_PATH'] = ros_lib_path + ':' + env['GZ_SIM_SYSTEM_PLUGIN_PATH']
    else:
        env['GZ_SIM_SYSTEM_PLUGIN_PATH'] = ros_lib_path
    # Also add to LD_LIBRARY_PATH as fallback for model plugins
    if 'LD_LIBRARY_PATH' in env:
        if ros_lib_path not in env['LD_LIBRARY_PATH']:
            env['LD_LIBRARY_PATH'] = ros_lib_path + ':' + env['LD_LIBRARY_PATH']
    else:
        env['LD_LIBRARY_PATH'] = ros_lib_path
    
    gazebo_process = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],  # -r runs simulation
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
            default_value='true',
            description='Use TurtleBot3 with Open Manipulator from dataset if true (default: true)'
        ),
        DeclareLaunchArgument(
            'paused',
            default_value='false',
            description='Start simulation paused if true. Default: running'
        ),
        gazebo_process,
        spawn_robot_launch,
    ])
