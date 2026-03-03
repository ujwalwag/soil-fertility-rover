"""Spawn robot in Gazebo. Uses -file for reliability (avoids param string issues)."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import os
import tempfile
from ament_index_python.packages import get_package_share_directory


def get_robot_description(context):
    pkg_farm_description = get_package_share_directory("farm_description")
    pkg_farm_sim = get_package_share_directory("farm_sim")
    robot_model = context.launch_configurations.get("robot_model", "ugvbeast")

    _launch_dir = os.path.dirname(os.path.abspath(__file__))
    _src_farm_desc = os.path.abspath(os.path.join(_launch_dir, "..", "..", "farm_description"))
    _src_urdf = os.path.join(_src_farm_desc, "urdf", "ugvbeast_arm.urdf")

    urdf_path = os.path.join(pkg_farm_description, "urdf", "ugvbeast_arm.urdf")
    use_ugv = robot_model.lower() in ("ugvbeast", "ugv", "beast")

    if use_ugv:
        # Prefer source path when it exists (development); else use install
        if os.path.exists(_src_urdf):
            urdf_path = _src_urdf
            pkg_farm_description = _src_farm_desc
        elif not os.path.exists(urdf_path):
            use_ugv = False

    if not use_ugv:
        urdf_path = os.path.join(
            pkg_farm_description, "urdf", "turtlebot3_om",
            "turtlebot3_waffle_for_open_manipulator.urdf"
        )
    controller_config_path = os.path.join(pkg_farm_sim, "config", "all_controllers.yaml")

    with open(urdf_path, "r") as f:
        robot_desc = f.read()

    meshes_ugv = os.path.abspath(os.path.join(pkg_farm_description, "meshes", "ugv_beast"))
    meshes_arm = os.path.abspath(os.path.join(pkg_farm_description, "meshes", "turtlebot3_om"))
    robot_desc = robot_desc.replace("../../meshes/ugv_beast/", "file://" + meshes_ugv + "/")
    robot_desc = robot_desc.replace("../../meshes/turtlebot3_om/", "file://" + meshes_arm + "/")
    robot_desc = robot_desc.replace("file://file://", "file://")
    robot_desc = robot_desc.replace(
        "$(find farm_control)/config/all_controllers.yaml", controller_config_path
    )

    use_sim_time_str = context.launch_configurations.get("use_sim_time", "true")
    use_sim_time_bool = use_sim_time_str.lower() in ("true", "1", "yes")
    x_pose = context.launch_configurations.get("x_pose", "9.0")
    y_pose = context.launch_configurations.get("y_pose", "9.0")
    z_pose = context.launch_configurations.get("z_pose", "0.05")
    yaw_pose = context.launch_configurations.get("yaw_pose", "0.0")

    # Write URDF to file - more reliable than -param for large models
    tmp_dir = tempfile.gettempdir()
    urdf_file = os.path.join(tmp_dir, "ugvbeast_spawn.urdf")
    with open(urdf_file, "w") as f:
        f.write(robot_desc)

    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-world", "farm_world",
            "-name", "ugvbeast",
            "-file", urdf_file,
            "-x", x_pose, "-y", y_pose, "-z", z_pose, "-Y", yaw_pose,
        ],
        output="screen",
        parameters=[{"use_sim_time": use_sim_time_bool}],
    )

    return [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{
                "use_sim_time": use_sim_time_bool,
                "robot_description": ParameterValue(robot_desc, value_type=str),
                "publish_frequency": 50.0
            }]
        ),
        TimerAction(period=20.0, actions=[spawn_entity]),  # 20s for world + maize to fully load
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("robot_model", default_value="ugvbeast",
                             description="Robot model: ugvbeast or turtlebot"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("x_pose", default_value="9.0"),
        DeclareLaunchArgument("y_pose", default_value="9.0"),
        DeclareLaunchArgument("z_pose", default_value="0.05"),
        DeclareLaunchArgument("yaw_pose", default_value="0.0"),
        OpaqueFunction(function=get_robot_description),
    ])
