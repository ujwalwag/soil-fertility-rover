"""Clock bridge only - start early for use_sim_time."""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_sfr_simulation = get_package_share_directory("sfr_simulation")
    config_file = os.path.join(pkg_sfr_simulation, "config", "gz_bridge_clock.yaml")

    bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory("ros_gz_bridge"),
                "launch",
                "ros_gz_bridge.launch.py",
            )
        ]),
        launch_arguments={
            "bridge_name": "farm_clock_bridge",
            "config_file": config_file,
            "use_composition": "false",
        }.items(),
    )

    return LaunchDescription([bridge])
