from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, ExecuteProcess, LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg = get_package_share_directory('farm_control')
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    
    # ROOT FIX: The Gazebo plugin creates its own controller_manager node
    # We need to load controller parameters AFTER the plugin creates the node
    # Then spawn controllers with their individual parameter files
    
    # Load controller_manager parameters after plugin creates the node
    load_params = ExecuteProcess(
        cmd=['ros2', 'param', 'load', '/controller_manager', os.path.join(pkg, 'config', 'all_controllers.yaml')],
        output='screen',
    )
    
    # Spawn controllers after parameters are loaded
    spawn_diff_drive = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diff_drive_controller',
            '-c', 'controller_manager',
            '-p', os.path.join(pkg, 'config', 'diff_drive_controller.yaml'),
            '--activate'
        ],
        output='screen',
    )
    
    spawn_joint_state = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '-c', 'controller_manager',
            '-p', os.path.join(pkg, 'config', 'joint_state_broadcaster.yaml'),
            '--activate'
        ],
        output='screen',
    )
    
    spawn_arm = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'arm_controller',
            '-c', 'controller_manager',
            '-p', os.path.join(pkg, 'config', 'arm_controller.yaml'),
            '--activate'
        ],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        LogInfo(msg='Waiting for Gazebo plugin to create controller_manager node...'),
        # Wait for Gazebo plugin to create controller_manager node and load hardware
        # Then load controller parameters and spawn controllers
        TimerAction(
            period=20.0,  # Wait for robot spawn, plugin to create controller_manager, and hardware to load
            actions=[
                LogInfo(msg='Loading controller_manager parameters...'),
                load_params,
                TimerAction(
                    period=3.0,  # Wait for params to load
                    actions=[
                        LogInfo(msg='Spawning controllers...'),
                        # Spawn joint_state_broadcaster first - diff_drive_controller needs joint states
                        spawn_joint_state,
                        TimerAction(
                            period=2.0,  # Wait for joint_state_broadcaster to start publishing
                            actions=[
                                spawn_diff_drive,
                                spawn_arm,
                            ]
                        ),
                    ]
                )
            ]
        ),
    ])
