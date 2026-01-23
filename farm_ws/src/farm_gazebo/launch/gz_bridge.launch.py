from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    # Note: cmd_vel is handled by ros2_control, no bridge needed
    # Bridge for cmd_vel removed - ros2_control handles it directly
    
    # Bridge for scan (laser): Gazebo -> ROS
    scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='scan_bridge',
        arguments=[
            '/model/turtlebot3_om/link/base_scan/sensor/scan/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan'
        ],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Bridge for IMU: Gazebo -> ROS
    imu_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='imu_bridge',
        arguments=[
            '/model/turtlebot3_om/link/imu_link/sensor/imu/imu@sensor_msgs/msg/Imu@gz.msgs.IMU'
        ],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Bridge for camera: Gazebo -> ROS
    camera_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='camera_bridge',
        arguments=[
            '/model/turtlebot3_om/link/camera_rgb_frame/sensor/camera/image@sensor_msgs/msg/Image@gz.msgs.Image'
        ],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    return LaunchDescription([
        scan_bridge,
        imu_bridge,
        camera_bridge,
    ])
