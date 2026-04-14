"""Launch farm rover GUI."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

# Use FastDDS to avoid CycloneDDS "Failed to find a free participant index" error
def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    spawn_x = LaunchConfiguration("spawn_x", default="9.0")
    spawn_y = LaunchConfiguration("spawn_y", default="9.0")
    sim_included = LaunchConfiguration("sim_included", default="false")

    gui_node = Node(
        package="sfr_gui",
        executable="sfr_gui",
        name="sfr_gui",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "spawn_x": spawn_x,
            "spawn_y": spawn_y,
            "sim_included": sim_included,
        }],
    )

    return LaunchDescription([
        SetEnvironmentVariable("RMW_IMPLEMENTATION", "rmw_fastrtps_cpp"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("spawn_x", default_value="9.0",
                             description="Robot spawn X (must match sim.launch)"),
        DeclareLaunchArgument("spawn_y", default_value="9.0",
                             description="Robot spawn Y (must match sim.launch)"),
        DeclareLaunchArgument("sim_included", default_value="false",
                             description="True when launched with sim (sim_with_gui.launch)"),
        gui_node,
    ])
