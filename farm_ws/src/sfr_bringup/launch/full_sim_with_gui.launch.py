"""Full simulation + Nav2, then GUI last (shared DDS domain for camera and state)."""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_bringup = get_package_share_directory("sfr_bringup")
    pkg_gui = get_package_share_directory("sfr_gui")

    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    use_nav2 = LaunchConfiguration("use_nav2", default="true")

    stack = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_bringup, "launch", "full_sim.launch.py")
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "use_nav2": use_nav2,
        }.items(),
    )

    gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gui, "launch", "gui.launch.py")),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "spawn_x": "9.0",
            "spawn_y": "9.0",
            "sim_included": "true",
        }.items(),
    )

    # Start GUI after Nav2 / sim graph is up
    gui_delayed = TimerAction(period=36.0, actions=[gui])

    return LaunchDescription([
        SetEnvironmentVariable("RMW_IMPLEMENTATION", "rmw_fastrtps_cpp"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("use_nav2", default_value="true"),
        stack,
        gui_delayed,
    ])
