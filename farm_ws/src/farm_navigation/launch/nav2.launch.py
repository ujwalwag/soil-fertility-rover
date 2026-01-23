from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg = get_package_share_directory('farm_navigation')
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    params_file = LaunchConfiguration('params_file', default=os.path.join(pkg, 'config', 'nav2_params.yaml'))
    costmap_file = os.path.join(pkg, 'config', 'costmap.yaml')
    controller_config = os.path.join(pkg, 'config', 'controller.yaml')
    bt_xml = os.path.join(pkg, 'config', 'bt_tree.xml')
    map_file = os.path.join(pkg, 'maps', 'farm_map.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('params_file', default_value=params_file),
        
        # Map server
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}, {'yaml_filename': map_file}],
        ),
        
        # AMCL for localization
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
        ),
        
        # NAV2 controller
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[controller_config, costmap_file, {'use_sim_time': use_sim_time}],
        ),
        
        # NAV2 planner
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[params_file, costmap_file, {'use_sim_time': use_sim_time}],
        ),
        
        # NAV2 BT navigator
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}, {'default_nav_to_pose_bt_xml': bt_xml}],
        ),
        
        # Lifecycle manager for NAV2 nodes
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}, {'autostart': True}, {'node_names': ['map_server', 'amcl', 'controller_server', 'planner_server', 'bt_navigator']}],
        ),
    ])
