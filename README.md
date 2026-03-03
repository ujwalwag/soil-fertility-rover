# Soil Fertility Rover

ROS 2 simulation and GUI for a farm rover with differential drive, arm, and sensors. Built for Gazebo Harmonic (gz-sim).

## Overview

- **Simulation:** Gazebo world, UGV Beast–style base with Open Manipulator arm, lidar, IMU, camera.
- **Control:** `diff_drive_controller` (cmd_vel / odom), joint trajectory controller for the arm.
- **GUI:** Map view, camera feed placeholder, remote drive and arm controls, simple goal-based navigation.

## Requirements

- ROS 2 Jazzy (or compatible)
- Gazebo Harmonic (`gz sim`)
- Packages: `ros_gz_sim`, `ros_gz_bridge`, `ros_gz_control`, `ros_gz_image`, `diff_drive_controller`, `joint_trajectory_controller`, etc.

## Workspace layout

```
soil-fertility-rover/
├── farm_ws/                    # ROS 2 workspace
│   └── src/
│       ├── farm_bringup/       # Launch files (sim, sim_with_gui)
│       ├── farm_description/  # URDF (ugvbeast_arm), meshes
│       ├── farm_gui/          # PyQt5 GUI (map, controls, camera)
│       ├── farm_sim/          # Gazebo world, spawn, bridges, controllers
│       └── virtual_maize_field/  # Maize models (optional)
├── docs/
├── scripts/
├── LICENSE
└── README.md
```

## Build

```bash
cd farm_ws
colcon build --symlink-install
source install/setup.bash
```

To build only core packages:

```bash
colcon build --packages-select farm_description farm_sim farm_bringup farm_gui
source install/setup.bash
```

## Run

**Simulation + GUI (recommended):**

```bash
source farm_ws/install/setup.bash
ros2 launch farm_bringup sim_with_gui.launch.py
```

- Wait ~25–30 s for the world to load and controllers to start.
- Use the GUI: drive buttons for remote control, or set a goal on the map and use “Navigate to dropped point” for simple autonomous nav.

**Simulation only:**

```bash
ros2 launch farm_bringup sim.launch.py
```

**GUI only** (e.g. if sim is already running elsewhere):

```bash
ros2 launch farm_gui gui.launch.py
```

Then click “Start Simulation” in the GUI to launch the sim in the background.

## Topics (main)

| Topic        | Type              | Description        |
|-------------|-------------------|--------------------|
| `/cmd_vel`  | `geometry_msgs/Twist` | Velocity commands  |
| `/odom`     | `nav_msgs/Odometry`   | Odometry           |
| `/scan`     | `sensor_msgs/LaserScan` | Lidar             |
| `/imu`      | `sensor_msgs/Imu`     | IMU               |
| `/camera/image_raw` | `sensor_msgs/Image` | Camera (bridged)   |

## Configuration

- **Spawn pose:** `sim.launch.py` and `farm_world.launch.py` use `x_pose`, `y_pose`, `z_pose`, `yaw_pose` (defaults: 9, 9, 0.01, 0).
- **Diff drive:** `farm_sim/config/all_controllers.yaml` (wheel separation, radius, odom, cmd_vel).
- **RMW:** Launches set `RMW_IMPLEMENTATION=rmw_fastrtps_cpp` to avoid CycloneDDS participant issues.

## License

MIT. See [LICENSE](LICENSE).
