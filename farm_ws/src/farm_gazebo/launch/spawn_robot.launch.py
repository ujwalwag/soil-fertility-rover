from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, OpaqueFunction
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.conditions import IfCondition, UnlessCondition
import os
from ament_index_python.packages import get_package_share_directory


def get_robot_description(context):
    """Get robot description based on launch argument using OpaqueFunction."""
    use_turtlebot3_om = context.launch_configurations.get('use_turtlebot3_om', 'true')
    pkg_farm_description = get_package_share_directory('farm_description')
    pkg_farm_control = get_package_share_directory('farm_control')
    
    if use_turtlebot3_om == 'true':
        # Use TurtleBot3 OM (plain URDF)
        urdf_file = os.path.join(pkg_farm_description, 'urdf', 'turtlebot3_om', 'turtlebot3_waffle_for_open_manipulator.urdf')
        meshes_dir = os.path.join(pkg_farm_description, 'meshes', 'turtlebot3_om')
        
        # Check if file exists
        if not os.path.exists(urdf_file):
            raise FileNotFoundError(f"URDF file not found: {urdf_file}")
        
        # Read URDF file and fix mesh paths to absolute
        with open(urdf_file, 'r') as f:
            robot_desc = f.read()
        
        # Replace relative mesh paths with absolute paths
        # Use absolute path - Gazebo should resolve it
        meshes_dir_abs = os.path.abspath(meshes_dir)
        
        # Replace relative mesh paths with absolute file:// paths
        # This ensures Gazebo can find the meshes
        robot_desc = robot_desc.replace(
            '../../meshes/turtlebot3_om/',
            'file://' + meshes_dir_abs + '/'
        )
        # Clean up any double file://
        robot_desc = robot_desc.replace('file://file://', 'file://')
        
        # Replace $(find farm_control) with actual package path for plugin parameters
        # This allows the gz_ros2_control plugin to find the controller configuration file
        controller_config_path = os.path.join(pkg_farm_control, 'config', 'all_controllers.yaml')
        robot_desc = robot_desc.replace(
            '$(find farm_control)/config/all_controllers.yaml',
            controller_config_path
        )
    else:
        # Use custom arm (xacro)
        urdf_file = os.path.join(pkg_farm_description, 'urdf', 'turtlebot_arm.urdf.xacro')
        # Process with xacro
        from subprocess import check_output
        robot_desc = check_output(['xacro', urdf_file]).decode('utf-8')
    
    # Return nodes with the robot description
    # Convert string to boolean for use_sim_time
    use_sim_time_str = context.launch_configurations.get('use_sim_time', 'true')
    use_sim_time_bool = use_sim_time_str.lower() in ('true', '1', 'yes')
    
    return [
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time_bool,  # Pass as boolean, not string
                'robot_description': ParameterValue(robot_desc, value_type=str),
                'publish_frequency': 50.0  # Ensure it publishes regularly
            }]
        )
    ]


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
    use_turtlebot3_om = LaunchConfiguration('use_turtlebot3_om', default='true')
    
    # Use OpaqueFunction to get robot description and create robot_state_publisher node
    robot_state_publisher_action = OpaqueFunction(function=get_robot_description)
    
    # Spawn robot in Gazebo using ros_gz_sim
    # Use a unique entity name to avoid conflicts
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-entity', 'turtlebot3_om',
            '-topic', 'robot_description',
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose,
            '-Y', yaw_pose
            # Note: -world parameter not needed, uses active world
        ],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # Add delay to spawn entity to ensure Gazebo is ready and robot_description is published
    # Wait longer to ensure everything is initialized
    delayed_spawn = TimerAction(
        period=7.0,  # Increased delay to ensure Gazebo is fully ready
        actions=[spawn_entity]
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_turtlebot3_om',
            default_value='true',
            description='Use TurtleBot3 with Open Manipulator from dataset if true'
        ),
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
        robot_state_publisher_action,
        delayed_spawn,
    ])
