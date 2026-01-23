# Gazebo GUI Issues in WSL2 - Troubleshooting

## Common Issue: Frozen/Unresponsive Gazebo GUI

If Gazebo opens but you can't interact with it (frozen), try these solutions:

### Solution 1: Check X11 Forwarding

```bash
# Verify DISPLAY is set
echo $DISPLAY  # Should show :0 or similar

# If not set, export it
export DISPLAY=:0

# Test with a simple GUI app
xeyes  # or xclock
```

### Solution 2: Use WSLg (if available)

WSL2 with WSLg has better GUI support. Check if you have it:

```bash
# Check WSL version
wsl --version

# If you have WSLg, DISPLAY should be set automatically
echo $DISPLAY
```

### Solution 3: Hardware Acceleration

Gazebo needs GPU acceleration. In WSL2, you may need:

```bash
# Install WSL2 GPU drivers on Windows host
# Then in WSL:
export LIBGL_ALWAYS_INDIRECT=1
export MESA_GL_VERSION_OVERRIDE=3.3
```

### Solution 4: Use Headless Mode + Remote Viewing

If GUI doesn't work, use headless mode:

```bash
# Launch in headless mode
ros2 launch farm_gazebo farm_world.launch.py headless:=true

# Or use gz web (if available)
gz web -s
```

### Solution 5: Reduce Graphics Quality

Edit the world file to reduce graphics load, or use simpler rendering.

### Solution 6: Check System Resources

Gazebo is resource-intensive. Ensure:
- Enough RAM available
- CPU not maxed out
- No other heavy processes running

### Quick Test

Test if Gazebo GUI works at all:

```bash
gz sim empty.sdf
```

If this also freezes, it's a WSL2/X11 issue, not your launch file.
