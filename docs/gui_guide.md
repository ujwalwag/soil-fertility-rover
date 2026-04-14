# GUI guide (sfr_gui)

- **Launch with simulation:** `ros2 launch sfr_bringup sim_with_gui.launch.py` — Gazebo and GUI start together (good for camera DDS).
- **Full stack (sim + Nav2 + GUI last):** `ros2 launch sfr_bringup full_sim_with_gui.launch.py` — wait ~40 s for GUI node.
- **GUI only:** `ros2 launch sfr_gui gui.launch.py` — use “Start Simulation” if the sim is not already running.

The Gazebo window is separate from the Qt window; the GUI does not embed the 3D view.
