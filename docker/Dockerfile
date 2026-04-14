# Dev container: ROS 2 Jazzy + Gazebo Harmonic (install gz in derived image or host).
FROM ros:jazzy-ros-base

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    python3-rosdep \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ws/farm_ws
COPY farm_ws/src src
RUN rosdep update && rosdep install --from-paths src --ignore-src -r -y || true

CMD ["bash", "-lc", "source /opt/ros/jazzy/setup.bash && colcon build --symlink-install && bash"]
