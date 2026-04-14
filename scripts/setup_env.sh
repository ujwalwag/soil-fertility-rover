#!/usr/bin/env bash
# Install dependencies and build the workspace (run from repo root).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="${ROOT}/farm_ws"
cd "${WS}/src"
rosdep update
rosdep install --from-paths . --ignore-src -r -y || true
cd "${WS}"
colcon build --symlink-install "$@"
echo "Done. Source: source ${WS}/install/setup.bash"
