# System Architecture

See `block_diagram.png` in this directory for a visual overview (add the image file as needed).

## Overview

The soil fertility rover has two main units:

1. **Base station (RPi5)** – Monitoring, storage, map view, mission status, health, LoRa link.
2. **Onboard computer (Jetson)** – Mission execution, navigation, arm control, sensors, soil pipeline.

They communicate via **LoRa** (ROS 2 messages) and a **data uplink** (logs, soil samples) to the base station.

## Base Station (RPi5)

- **Dashboard + storage + map view** – UI, live charts, CSV/DB, map.
- **Mission status + health** – Robot state and health.
- **LoRa interface** – Commands and status over LoRa.

## Onboard Computer (Jetson)

- **Mission node** – State machine, sample requests.
- **GeoFence + waypoint sampler** – Boundaries, sampling waypoints → NAV2.
- **NAV2** – Planner, controller, BT → `cmd_vel` → ros2_control.
- **MoveIt2** – Arm planning/IK → `joint_traj` → ros2_control.
- **ros2_control** – Wheel/arm → hardware or sim.
- **Sampling orchestrator** – Arm + sensor logic, camera → OpenCV verification.
- **OpenCV verification** – Soil contact/depth → `sample_ok` → soil pipeline.
- **TF + state estimation** – Odom/IMU/GPS → pose.
- **Soil data pipeline** – `sample_ok` + pose + NPK/moisture/env → timestamp, geo-tag, publish samples, uplink.
- **Hardware / sim interface** – Low-level robot interface.

## Data Flow

- **LoRa**: Base station ↔ onboard (commands, status, health).
- **Uplink**: Soil pipeline → base station (samples, logs).

## Packages

See [README](../README.md) and [architecture.md](architecture.md) for the `sfr_*` package list and roles.
