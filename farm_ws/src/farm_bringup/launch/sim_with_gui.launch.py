"""Launch simulation AND GUI together - ensures same DDS domain for camera feed."""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_farm_bringup = get_package_share_directory("farm_bringup")
    pkg_farm_gui = get_package_share_directory("farm_gui")

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_bringup, "launch", "sim.launch.py")
        ]),
        launch_arguments={"use_sim_time": "true"}.items(),
    )

    gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_gui, "launch", "gui.launch.py")
        ]),
        launch_arguments={
            "use_sim_time": "true",
            "spawn_x": "9.0",
            "spawn_y": "9.0",
            "sim_included": "true",
        }.items(),
    )

    return LaunchDescription([
        SetEnvironmentVariable("RMW_IMPLEMENTATION", "rmw_fastrtps_cpp"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        sim,
        gui,
    ])
