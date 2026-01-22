# Experiments

## Running Missions

1. Start base station: `ros2 launch farm_bringup base_station.launch.py`
2. Start onboard stack (or sim): `ros2 launch farm_bringup onboard.launch.py`
3. Send mission (e.g. via service or dashboard) and monitor `/mission/status`, `/robot/health`, `/soil_data/samples`.

## Simulation Experiments

- Use `scripts/run_sim.sh` or `farm_bringup` sim launch.
- Test waypoint sampling, geofence, and sampling orchestration without hardware.
- Tune NAV2, MoveIt2, and OpenCV verification parameters in `farm_navigation`, `farm_arm`, and `farm_perception`.

## Data Collection

- Soil samples are published on `/soil_data/samples` and stored via base station (CSV/DB).
- Use `media/screenshots` and `media/demo_videos` for experiment logs.
- See `farm_sensors` and `farm_base_station` for storage and uplink configuration.

## Adding New Experiments

1. Document goal and procedure in this file.
2. Add any new launch/config under `farm_bringup` or relevant package.
3. Attach screenshots/diagrams under `media/` as needed.
