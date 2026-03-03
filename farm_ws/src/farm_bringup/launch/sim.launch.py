"""Launch full simulation: Gazebo world + robot + bridge + Nav2."""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory

# Use FastDDS to avoid CycloneDDS "Failed to find a free participant index" error
def generate_launch_description():
    pkg_farm_sim = get_package_share_directory("farm_sim")
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    world = LaunchConfiguration(
        "world",
        default=os.path.join(pkg_farm_sim, "worlds", "farm_world_light.world")
    )

    robot_model = LaunchConfiguration("robot_model", default="ugvbeast")

    farm_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_sim, "launch", "farm_world.launch.py")
        ]),
        launch_arguments={
            "world": world,
            "robot_model": robot_model,
            "use_sim_time": use_sim_time,
            "x_pose": "9.0",
            "y_pose": "9.0",
            "z_pose": "0.01",
            "yaw_pose": "0.0"
        }.items()
    )

    gz_bridge_clock = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_sim, "launch", "gz_bridge_clock.launch.py")
        ]),
    )
    gz_bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_sim, "launch", "gz_bridge.launch.py")
        ]),
    )
    camera_bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_sim, "launch", "camera_bridge.launch.py")
        ]),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )
    # Clock 5s; sensors 25s (after robot spawn 20s). Camera via gz_bridge + ros_gz_image fallback.
    gz_bridge_clock_delayed = TimerAction(period=5.0, actions=[gz_bridge_clock])
    gz_bridge_delayed = TimerAction(period=25.0, actions=[gz_bridge, camera_bridge])

    spawn_controllers = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_farm_sim, "launch", "spawn_controllers.launch.py")
        ]),
        launch_arguments={"use_sim_time": use_sim_time}.items()
    )

    return LaunchDescription([
        SetEnvironmentVariable("RMW_IMPLEMENTATION", "rmw_fastrtps_cpp"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("robot_model", default_value="ugvbeast",
                             description="Robot model: ugvbeast or turtlebot"),
        DeclareLaunchArgument(
            "world",
            default_value=os.path.join(pkg_farm_sim, "worlds", "farm_world_light.world"),
            description="World file (farm_world_light.world = stable, farm_world.world = full)",
        ),
        farm_world,
        gz_bridge_clock_delayed,
        gz_bridge_delayed,
        spawn_controllers,
    ])
