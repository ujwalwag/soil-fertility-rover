"""Full simulation stack: Gazebo + bridges + controllers, then Nav2 (after world is ready)."""

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    TimerAction,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_bringup = get_package_share_directory("sfr_bringup")
    pkg_nav = get_package_share_directory("sfr_navigation")

    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    use_nav2 = LaunchConfiguration("use_nav2", default="true")

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_bringup, "launch", "sim.launch.py")
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav, "launch", "navigation.launch.py")
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "use_nav2": use_nav2,
        }.items(),
    )

    # After robot spawn (~20s) and bridges (~25s), start Nav2
    navigation_delayed = TimerAction(period=32.0, actions=[navigation])

    return LaunchDescription([
        SetEnvironmentVariable("RMW_IMPLEMENTATION", "rmw_fastrtps_cpp"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument(
            "use_nav2",
            default_value="true",
            description="If true, start Nav2 stack after simulation is up",
        ),
        sim,
        navigation_delayed,
    ])
