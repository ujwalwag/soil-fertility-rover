#!/bin/bash
# Run Gazebo simulation and bringup

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
WS="$REPO_ROOT/farm_ws"

source /opt/ros/jazzy/setup.bash
[ -f "$WS/install/setup.bash" ] && source "$WS/install/setup.bash"

# Launch sim via farm_bringup (adjust launch file name as needed)
ros2 launch farm_bringup sim.launch.py
