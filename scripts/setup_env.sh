#!/bin/bash
# Source ROS 2 and workspace overlay for soil-fertility-rover

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
WS="$REPO_ROOT/farm_ws"

# ROS 2
if [ -f /opt/ros/jazzy/setup.bash ]; then
  source /opt/ros/jazzy/setup.bash
else
  echo "ROS 2 Jazzy not found. Install it first." >&2
  exit 1
fi

# Workspace overlay
if [ -f "$WS/install/setup.bash" ]; then
  source "$WS/install/setup.bash"
  echo "Sourced farm_ws overlay."
else
  echo "farm_ws not built yet. Run ./scripts/build_sim.sh"
fi

export SOIL_ROVER_ROOT="$REPO_ROOT"
