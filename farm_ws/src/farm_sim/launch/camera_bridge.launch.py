"""Bridge Gazebo camera to ROS. ros_gz_image (full path) + gz_bridge.yaml both publish /camera/image_raw."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

GZ_CAMERA_TOPIC = "/world/farm_world/model/ugvbeast/link/camera_link/sensor/camera/image_raw"


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        Node(
            package="ros_gz_image",
            executable="image_bridge",
            name="camera_bridge",
            arguments=[GZ_CAMERA_TOPIC],
            parameters=[
                {"use_sim_time": LaunchConfiguration("use_sim_time", default="true")},
                {"qos": "sensor_data"},
            ],
            output="screen",
        ),
    ])
