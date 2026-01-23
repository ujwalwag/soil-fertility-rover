#!/bin/bash
# Setup script for Gazebo in WSL2 - fixes OpenGL/GUI issues

echo "Setting up Gazebo for WSL2..."

# Set environment variables for software rendering (works in WSL2)
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
export QT_QPA_PLATFORM=xcb

# Ensure DISPLAY is set
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
    echo "Set DISPLAY to :0"
fi

echo "Environment variables set:"
echo "  LIBGL_ALWAYS_SOFTWARE=$LIBGL_ALWAYS_SOFTWARE"
echo "  GALLIUM_DRIVER=$GALLIUM_DRIVER"
echo "  DISPLAY=$DISPLAY"

echo ""
echo "To use these settings, source this script before launching:"
echo "  source scripts/setup_gazebo_wsl.sh"
echo "  ros2 launch farm_gazebo farm_world.launch.py"
