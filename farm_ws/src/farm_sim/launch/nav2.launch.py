"""Launch Nav2 for autonomous navigation."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_farm_sim = get_package_share_directory("farm_sim")
    pkg_nav2_bringup = get_package_share_directory("nav2_bringup")

    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    use_nav2 = LaunchConfiguration("use_nav2", default="true")

    map_yaml = os.path.join(pkg_farm_sim, "config", "maps", "farm_map.yaml")
    params_file = os.path.join(pkg_farm_sim, "config", "nav2_params.yaml")

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, "launch", "bringup_launch.py")
        ),
        condition=IfCondition(use_nav2),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "map": map_yaml,
            "params_file": params_file,
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("use_nav2", default_value="true",
                             description="Launch Nav2 for autonomous navigation"),
        nav2_bringup,
    ])
