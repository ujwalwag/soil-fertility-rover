"""Spawn ros2_control controllers after robot is loaded in Gazebo.
The gz_ros2_control plugin creates controller_manager when the model loads.
Robot spawns at 20s; spawn drive at 22s, arm at 24s so drive works even if arm fails.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")

    # Drive controllers - must load first for cmd_vel/odom to work
    # --controller-manager-timeout: wait for controller_manager (created when robot spawns)
    spawner_drive = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "diff_drive_controller",
            "--controller-manager",
            "/controller_manager",
            "--controller-manager-timeout",
            "30",
        ],
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
    )

    # Arm controller - separate spawn so drive works even if arm fails
    spawner_arm = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "arm_controller",
            "--controller-manager",
            "/controller_manager",
            "--controller-manager-timeout",
            "30",
        ],
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
    )

    spawner_drive_delayed = TimerAction(period=22.0, actions=[spawner_drive])
    spawner_arm_delayed = TimerAction(period=24.0, actions=[spawner_arm])

    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        spawner_drive_delayed,
        spawner_arm_delayed,
    ])
