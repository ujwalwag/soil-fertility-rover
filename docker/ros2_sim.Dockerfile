# ROS 2 Jazzy + Gazebo Harmonic simulation image for soil-fertility-rover

FROM osrf/ros:jazzy-desktop

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    gz-harmonic \
    ros-jazzy-nav2-bringup \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-joint-state-publisher \
    ros-jazzy-xacro \
    python3-colcon-common-extensions \
    python3-pip \
    python3-psutil \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir tf-transformations

WORKDIR /app
COPY farm_ws /app/farm_ws

RUN . /opt/ros/jazzy/setup.sh && \
    cd /app/farm_ws && \
    colcon build --symlink-install

RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc && \
    echo "source /app/farm_ws/install/setup.bash" >> /root/.bashrc

ENTRYPOINT ["/bin/bash", "-c", ". /opt/ros/jazzy/setup.bash && . /app/farm_ws/install/setup.bash && exec \"$@\"", "--"]
CMD ["ros2", "launch", "farm_bringup", "sim.launch.py"]
