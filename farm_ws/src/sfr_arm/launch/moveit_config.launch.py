"""Optional: load MoveIt parameters from sfr_arm/config (when MoveIt is fully integrated)."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        LogInfo(msg="moveit_config.launch.py: add moveit_setup_assistant / move_group when SRDF is ready."),
    ])
