#!/usr/bin/env bash
# One-liner: sim + GUI (same DDS domain).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
source "${ROOT}/farm_ws/install/setup.bash"
exec ros2 launch sfr_bringup sim_with_gui.launch.py "$@"
