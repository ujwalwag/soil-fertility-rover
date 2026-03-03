"""Gazebo->ROS bridge for scan, imu, camera (config: gz_bridge.yaml)."""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_farm_sim = get_package_share_directory("farm_sim")
    config_file = os.path.join(pkg_farm_sim, "config", "gz_bridge.yaml")

    bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory("ros_gz_bridge"),
                "launch",
                "ros_gz_bridge.launch.py",
            )
        ]),
        launch_arguments={
            "bridge_name": "farm_sensor_bridge",
            "config_file": config_file,
            "use_composition": "false",
        }.items(),
    )

    return LaunchDescription([bridge])
