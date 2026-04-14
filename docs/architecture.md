# Architecture (soil_fertility_rover)

ROS 2 workspace packages:

| Package | Role |
|--------|------|
| **sfr_description** | URDF/xacro, meshes, model-only data. No runtime nodes. |
| **sfr_simulation** | Gazebo worlds, spawn, `ros_gz` bridges, simulation controller YAML. |
| **sfr_navigation** | Nav2 parameters, occupancy maps, waypoint/coverage planner nodes (stubs). |
| **sfr_arm** | MoveIt-oriented YAML and `arm_controller` stub for soil sampling motions. |
| **sfr_gui** | PyQt GUI: modes, map, camera, teleop; thin ROS client layer. |
| **sfr_bringup** | Top-level launches only; composes the packages above. |

Autonomy and arm logic are **ROS nodes without GUI imports** so `real_robot.launch.py` can reuse the same graph without Gazebo.

See repository `README.md` for build and launch commands.
