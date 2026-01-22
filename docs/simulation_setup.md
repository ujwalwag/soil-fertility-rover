# Simulation Setup

## Prerequisites

- Ubuntu 22.04 (or compatible)
- ROS 2 Jazzy
- Gazebo Harmonic
- `colcon`, `vcstool`

## Install Dependencies

```bash
# ROS 2 Jazzy
sudo apt update
sudo apt install -y ros-jazzy-desktop

# Gazebo Harmonic
sudo apt install -y ros-jazzy-ros-gz ros-jazzy-ros-gz-sim ros-jazzy-ros-gz-bridge gz-harmonic

# Navigation
sudo apt install -y ros-jazzy-nav2-bringup ros-jazzy-nav2-common

# Robot description
sudo apt install -y ros-jazzy-robot-state-publisher ros-jazzy-joint-state-publisher \
  ros-jazzy-joint-state-publisher-gui ros-jazzy-xacro

# Build
sudo apt install -y python3-colcon-common-extensions python3-vcstool
pip3 install --user tf-transformations
```

## Setup Script

```bash
./scripts/setup_env.sh
```

Sources ROS 2 and project overlays.

## Build

```bash
./scripts/build_sim.sh
# or
cd farm_ws && colcon build --symlink-install && source install/setup.bash
```

## Run Simulation

```bash
./scripts/run_sim.sh
```

Launches the Gazebo world and required nodes. See `farm_bringup` launch files for details.

## Docker

Build and run the simulation container:

```bash
docker build -f docker/ros2_sim.Dockerfile -t soil-rover-sim .
docker run -it --rm soil-rover-sim
```

See `docker/ros2_sim.Dockerfile` for the image layout.
