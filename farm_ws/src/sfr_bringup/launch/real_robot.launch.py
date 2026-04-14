"""Real robot entry point: no Gazebo — hardware interfaces and drivers (stub)."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        LogInfo(
            msg="real_robot.launch.py: stub — add robot_description, ros2_control hardware, "
            "sensors, Nav2, and sfr_gui when hardware is integrated."
        ),
    ])
