#!/bin/bash
# Clean launch script - resets environment and launches Gazebo

# Clear any problematic environment variables
unset LIBGL_ALWAYS_SOFTWARE
unset GALLIUM_DRIVER
unset LIBGL_ALWAYS_INDIRECT

# Source ROS 2
source /opt/ros/jazzy/setup.bash

# Source workspace
cd /home/ujwalwag/soil-fertility-rover
source farm_ws/install/setup.bash

# Launch with clean environment
echo "Launching Gazebo with clean environment..."
ros2 launch farm_gazebo farm_world.launch.py "$@"
