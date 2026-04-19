# Soil Fertility Detection Rover

ROS 2 **Jazzy** workspace for a soil-sampling rover: **Gazebo Harmonic** simulation, **Nav2**-oriented navigation, **PyQt** GUI, and stubs for field coverage and arm control. Packages use the `sfr_*` prefix (soil fertility rover); the colcon workspace directory remains `farm_ws`.

## Repository layout

```
soil-fertility-rover/
├── farm_ws/src/
│   ├── sfr_description/   # URDF, meshes (no nodes)
│   ├── sfr_simulation/    # Gazebo worlds, spawn, ros_gz bridges, sim controllers
│   ├── sfr_navigation/   # Nav2 YAML, maps, waypoint / coverage planner stubs
│   ├── sfr_arm/           # MoveIt-oriented YAML, arm_controller stub
│   ├── sfr_gui/           # PyQt GUI
│   └── sfr_bringup/       # Top-level launches
├── docker/                # Dockerfile + compose for dev / CI-style builds
├── docs/
├── scripts/               # setup_env.sh, run_sim.sh
└── README.md
```

## Requirements

- ROS 2 Jazzy
- Gazebo Harmonic (`gz sim`)
- For the full stack: `ros_gz_sim`, `ros_gz_bridge`, `ros_gz_control`, `ros_gz_image`, controller packages, `nav2_bringup`, and other deps pulled in via `rosdep` (see [scripts/setup_env.sh](scripts/setup_env.sh))

## Build

```bash
cd farm_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

From the repo root (runs `rosdep` then `colcon build` in `farm_ws`):

```bash
bash scripts/setup_env.sh
```

## Run

| Command | Purpose |
|--------|---------|
| `ros2 launch sfr_bringup sim_with_gui.launch.py` | Gazebo + GUI (good default when you want the camera UI) |
| `ros2 launch sfr_bringup full_sim.launch.py` | Simulation + Nav2 (Nav2 delayed ~32 s) |
| `ros2 launch sfr_bringup full_sim_with_gui.launch.py` | Sim + Nav2 + GUI (Nav2 delayed ~32 s; GUI after ~36 s) |
| `ros2 launch sfr_bringup sim.launch.py` | Simulation only |
| `ros2 launch sfr_gui gui.launch.py` | GUI only (can start sim from the UI) |
| `ros2 launch sfr_bringup real_robot.launch.py` | Hardware bringup stub |

After a successful build:

```bash
bash scripts/run_sim.sh
```

Launches set `RMW_IMPLEMENTATION=rmw_fastrtps_cpp` where relevant.

## Docker

Optional dev shell with the repo mounted at `/ws` and `working_dir` `/ws/farm_ws`:

```bash
docker compose -f docker/compose.yaml run --rm dev
```

Inside the container, source ROS and build as usual (`source /opt/ros/jazzy/setup.bash`, then `colcon build`). The image in [docker/Dockerfile](docker/Dockerfile) is a minimal Jazzy base; install Gazebo Harmonic and extra packages on the host or extend the Dockerfile for a fully self-contained sim image.

## CI

GitHub Actions builds the `sfr_*` packages in a `ros:jazzy-ros-base` container (see [.github/workflows/ci.yml](.github/workflows/ci.yml)).

## Documentation

- [docs/architecture.md](docs/architecture.md) — system overview
- [docs/gui_guide.md](docs/gui_guide.md) — GUI usage
- [docs/simulation_setup.md](docs/simulation_setup.md) — simulation setup
- [docs/hardware_setup.md](docs/hardware_setup.md) — hardware notes
- [docs/gazebo_wsl_troubleshooting.md](docs/gazebo_wsl_troubleshooting.md) — WSL / Gazebo issues
- [docs/experiments.md](docs/experiments.md) — experiment log
- [docs/system_architecture.md](docs/system_architecture.md) — legacy / alternate architecture notes

## Configuration notes

- Default spawn pose: check `x_pose` / `y_pose` in `sfr_bringup` and `sfr_simulation` launch files (often around the map origin).
- Controllers: [farm_ws/src/sfr_simulation/config/all_controllers.yaml](farm_ws/src/sfr_simulation/config/all_controllers.yaml)
- Maps and Nav2: [farm_ws/src/sfr_navigation/config/](farm_ws/src/sfr_navigation/config/)

## License

MIT. See [LICENSE](LICENSE).
