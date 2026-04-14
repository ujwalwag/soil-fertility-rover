# Hardware Setup

## Base Station (RPi5)

- **Raspberry Pi 5** with Raspberry Pi OS
- **LoRa radio** (e.g. SX1276-based module) for link to rover
- **Display** for dashboard (optional)
- **Storage** for CSV/DB (local SSD or USB)

## Onboard Computer (Jetson)

- **NVIDIA Jetson** (e.g. Orin Nano / Xavier NX) with JetPack
- **LoRa radio** (matching base station)
- **IMU** (e.g. ICM-20948, BNO055)
- **GPS** (optional, for global geo-tagging)
- **Wheel encoders** for odometry
- **Camera** for soil verification (OpenCV)
- **NPK / moisture / env sensors** for soil pipeline

## Robot Platform

- **Differential or omnidirectional base** with ros2_control-compatible drivers
- **Robotic arm** (e.g. small manipulator) for sampling, MoveIt2-compatible
- **Power** – battery, voltage monitoring for `farm_sensors` health node

## Wiring and Drivers

- Connect LoRa, IMU, GPS, encoders, camera, and sensors to the Jetson.
- Provide ROS 2 drivers or `ros2_control` hardware interfaces for:
  - Base (e.g. `diff_drive_controller`)
  - Arm (e.g. `joint_trajectory_controller`)

## Configuration

- LoRa topics: `farm_base_station` (base) and onboard LoRa node.
- Sensor topics: used by `farm_sensors` (soil pipeline, state estimation, health).
- Controller config: `sfr_simulation` and `sfr_bringup` launch parameters.

See package `README` files and launch args for topic remapping and frame IDs.
