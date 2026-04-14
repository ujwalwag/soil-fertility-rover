"""Launch Gazebo with farm world and spawn robot."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_sfr_simulation = get_package_share_directory("sfr_simulation")
    pkg_sfr_description = get_package_share_directory("sfr_description")

    world_file = LaunchConfiguration(
        "world", default=os.path.join(pkg_sfr_simulation, "worlds", "farm_world_light.world")
    )
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    x_pose = LaunchConfiguration("x_pose", default="9.0")
    y_pose = LaunchConfiguration("y_pose", default="9.0")
    z_pose = LaunchConfiguration("z_pose", default="0.01")
    yaw_pose = LaunchConfiguration("yaw_pose", default="0.0")

    env = os.environ.copy()
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"
    meshes_path = os.path.join(pkg_sfr_description, "meshes")
    models_path = os.path.join(pkg_sfr_simulation, "models")
    resource_paths = [meshes_path, models_path]
    gz_resource_path = ":".join(resource_paths)
    if "GZ_SIM_RESOURCE_PATH" in env:
        env["GZ_SIM_RESOURCE_PATH"] = gz_resource_path + ":" + env["GZ_SIM_RESOURCE_PATH"]
    else:
        env["GZ_SIM_RESOURCE_PATH"] = gz_resource_path
    ros_lib_path = "/opt/ros/jazzy/lib"
    if "GZ_SIM_SYSTEM_PLUGIN_PATH" in env:
        env["GZ_SIM_SYSTEM_PLUGIN_PATH"] = ros_lib_path + ":" + env["GZ_SIM_SYSTEM_PLUGIN_PATH"]
    else:
        env["GZ_SIM_SYSTEM_PLUGIN_PATH"] = ros_lib_path
    if "LD_LIBRARY_PATH" in env:
        if ros_lib_path not in env["LD_LIBRARY_PATH"]:
            env["LD_LIBRARY_PATH"] = ros_lib_path + ":" + env["LD_LIBRARY_PATH"]
    else:
        env["LD_LIBRARY_PATH"] = ros_lib_path

    # Ensure spawn (create node) uses same transport partition as gz sim
    set_gz_env = [
        SetEnvironmentVariable("GZ_SIM_RESOURCE_PATH", env["GZ_SIM_RESOURCE_PATH"]),
        SetEnvironmentVariable("GZ_SIM_SYSTEM_PLUGIN_PATH", env["GZ_SIM_SYSTEM_PLUGIN_PATH"]),
    ]

    gazebo_process = ExecuteProcess(
        cmd=["gz", "sim", "-r", world_file],
        output="screen",
        env=env,
        shell=False
    )

    robot_model = LaunchConfiguration("robot_model", default="ugvbeast")

    spawn_robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_sfr_simulation, "launch", "spawn_robot.launch.py")
        ]),
        launch_arguments={
            "robot_model": robot_model,
            "use_sim_time": use_sim_time,
            "x_pose": x_pose,
            "y_pose": y_pose,
            "z_pose": z_pose,
            "yaw_pose": yaw_pose
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument("world", default_value=os.path.join(pkg_sfr_simulation, "worlds", "farm_world_light.world")),
        DeclareLaunchArgument("robot_model", default_value="ugvbeast", description="ugvbeast or turtlebot"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("x_pose", default_value="9.0"),
        DeclareLaunchArgument("y_pose", default_value="9.0"),
        DeclareLaunchArgument("z_pose", default_value="0.01"),
        DeclareLaunchArgument("yaw_pose", default_value="0.0"),
        *set_gz_env,
        gazebo_process,
        spawn_robot_launch,
    ])
