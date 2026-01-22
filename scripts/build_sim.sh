#!/bin/bash
# Build farm_ws for simulation

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
WS="$REPO_ROOT/farm_ws"

if [ ! -f /opt/ros/jazzy/setup.bash ]; then
  echo "ROS 2 Jazzy not found. Install it first." >&2
  exit 1
fi
source /opt/ros/jazzy/setup.bash

mkdir -p "$WS/src"
cd "$WS"
colcon build --symlink-install

echo "Build done. Source: source $WS/install/setup.bash"
