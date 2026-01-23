# Quick Start Guide

## Setting up the environment

From the repository root (`/home/ujwalwag/soil-fertility-rover`):

```bash
# Source ROS 2
source /opt/ros/jazzy/setup.bash

# Source the workspace (from repo root)
source farm_ws/install/setup.bash
```

Or use the provided script:
```bash
./scripts/setup_env.sh
```

## Building the workspace

```bash
# From repo root
cd farm_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
```

Or use the provided script:
```bash
./scripts/build_sim.sh
```

## Launching the simulation

### Option 1: Full simulation (world + robot)
```bash
source /opt/ros/jazzy/setup.bash
source farm_ws/install/setup.bash
ros2 launch farm_bringup sim.launch.py
```

### Option 2: Just the farm world
```bash
source /opt/ros/jazzy/setup.bash
source farm_ws/install/setup.bash
ros2 launch farm_gazebo farm_world.launch.py
```

### Option 3: World + robot spawn
```bash
source /opt/ros/jazzy/setup.bash
source farm_ws/install/setup.bash
ros2 launch farm_gazebo farm_sim.launch.py
```

## Important paths

- **Repository root**: `/home/ujwalwag/soil-fertility-rover`
- **Workspace**: `/home/ujwalwag/soil-fertility-rover/farm_ws`
- **Setup file**: `/home/ujwalwag/soil-fertility-rover/farm_ws/install/setup.bash`

**Note**: Always source from the repository root, not from `farm_ws` directory directly.
