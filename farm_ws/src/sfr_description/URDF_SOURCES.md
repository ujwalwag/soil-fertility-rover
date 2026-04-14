# URDF Sources

## TurtleBot3 with Open Manipulator

**Source**: [URDF Files Dataset](https://github.com/Daniella1/urdf_files_dataset)
**Path**: `oems/xacro_generated/turtlebot3_robotis/turtlebot3_description/urdf/turtlebot3_waffle_for_open_manipulator.urdf`

This is a complete, professional URDF for TurtleBot3 Waffle with Open Manipulator arm integrated.

### Files Copied:
- URDF: `urdf/turtlebot3_om/turtlebot3_waffle_for_open_manipulator.urdf`
- Meshes: `meshes/turtlebot3_om/` (includes base, wheels, sensors, and arm meshes)

### Usage:

To use the TurtleBot3 OM robot instead of the custom arm:

```bash
ros2 launch farm_gazebo farm_world.launch.py use_turtlebot3_om:=true
```

Or modify `spawn_robot.launch.py` to change the default URDF file.

### Custom Arm (Default):

The custom `turtlebot_arm.urdf.xacro` is still available and used by default.
