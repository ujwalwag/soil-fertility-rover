# Soil Fertility Rover

Automated soil sampling robot system for farm fertility mapping. Base station (RPi5) and onboard computer (Jetson) communicate via LoRa; the rover navigates waypoints, collects geo-tagged soil samples, and streams data to the base station.

## Structure

```
soil-fertility-rover/
├── README.md
├── docs/
│   ├── system_architecture.md
│   ├── block_diagram.png      # (add diagram here)
│   ├── simulation_setup.md
│   ├── hardware_setup.md
│   └── experiments.md
├── media/
│   ├── screenshots/
│   ├── demo_videos/
│   └── diagrams/
├── farm_ws/
│   ├── src/
│   ├── install/               # (gitignored)
│   ├── build/                 # (gitignored)
│   └── log/                   # (gitignored)
├── scripts/
│   ├── setup_env.sh
│   ├── build_sim.sh
│   └── run_sim.sh
├── docker/
│   └── ros2_sim.Dockerfile
├── .gitignore
└── LICENSE
```

## Quick Start

```bash
# Setup environment
./scripts/setup_env.sh

# Build workspace
./scripts/build_sim.sh

# Run simulation
./scripts/run_sim.sh
```

## Packages (`farm_ws/src`)

| Package | Description |
|--------|-------------|
| `farm_description` | Robot URDF / meshes |
| `farm_gazebo` | Gazebo world and sim launch |
| `farm_control` | ros2_control config and controllers |
| `farm_navigation` | NAV2, waypoint sampler, geofence |
| `farm_arm` | Arm control, sampling orchestrator |
| `farm_perception` | OpenCV soil verification |
| `farm_sensors` | Soil pipeline, state estimation, health |
| `farm_mission` | Mission state machine |
| `farm_base_station` | Dashboard, storage, LoRa |
| `farm_bringup` | Launch files and bringup |

## Requirements

- ROS 2 Jazzy
- Gazebo Harmonic
- See [docs/simulation_setup.md](docs/simulation_setup.md) and [docs/hardware_setup.md](docs/hardware_setup.md)

## License

See [LICENSE](LICENSE).
