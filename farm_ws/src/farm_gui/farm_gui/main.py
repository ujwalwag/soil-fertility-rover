#!/usr/bin/env python3
"""Farm rover GUI - map, camera, remote control."""

import subprocess
import sys
import os

# Allow running without PyQt5 for environments that might use another backend
try:
    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QPushButton,
        QLabel,
        QComboBox,
        QGroupBox,
        QGridLayout,
        QFrame,
        QStackedWidget,
        QMessageBox,
        QSizePolicy,
    )
    from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPointF
    from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QFont
    HAS_PYQT5 = True
except ImportError:
    HAS_PYQT5 = False

import threading
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.action import ActionClient
from rclpy.qos import qos_profile_sensor_data, QoSProfile, ReliabilityPolicy, DurabilityPolicy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image
from control_msgs.msg import JointTrajectoryControllerState
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import Header
from cv_bridge import CvBridge
import math
import numpy as np

# Default arm positions (hold others when moving subset)
ARM_JOINTS = ["joint1", "joint2", "joint3", "joint4", "gripper_left_joint", "gripper_right_joint"]
DEFAULT_ARM = {j: 0.0 for j in ARM_JOINTS}


class RoverNode(Node):
    """ROS 2 node for rover control and sensor data."""

    def __init__(self):
        super().__init__("farm_gui_node")
        self.declare_parameter("cmd_vel_topic", "/cmd_vel")
        self.declare_parameter("odom_topic", "/odom")
        self.declare_parameter("camera_topic", "/camera/image_raw")
        self.declare_parameter("arm_state_topic", "arm_controller/state")
        self.declare_parameter("arm_action", "arm_controller/follow_joint_trajectory")
        self.declare_parameter("spawn_x", 9.0)
        self.declare_parameter("spawn_y", 9.0)
        self.declare_parameter("sim_included", False)

        cmd_vel = self.get_parameter("cmd_vel_topic").value
        odom = self.get_parameter("odom_topic").value
        camera = self.get_parameter("camera_topic").value
        arm_state = self.get_parameter("arm_state_topic").value
        arm_action = self.get_parameter("arm_action").value
        self.spawn_x = float(self.get_parameter("spawn_x").value)
        self.spawn_y = float(self.get_parameter("spawn_y").value)

        self.cmd_vel_pub = self.create_publisher(Twist, cmd_vel, 10)
        self._arm_action_client = ActionClient(self, FollowJointTrajectory, arm_action)

        # Simple nav: goal + cmd_vel/odom (no Nav2)
        self._nav_goal_x = None
        self._nav_goal_y = None
        self._nav_goal_yaw = 0.0
        self._navigating = False
        self._nav_tolerance = 0.35
        self._nav_linear_gain = 0.4
        self._nav_angular_gain = 2.0

        # odom: reliable QoS to match diff_drive
        qos_reliable = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE, durability=DurabilityPolicy.VOLATILE)
        self.create_subscription(Odometry, odom, self._odom_cb, qos_reliable)
        # Camera: reliable QoS to match ros_gz_bridge (publisher uses default RELIABLE)
        self.create_subscription(Image, camera, self._image_cb, qos_reliable)
        self.create_subscription(
            JointTrajectoryControllerState, arm_state, self._arm_state_cb, 10
        )

        self.odom_x = 0.0
        self.odom_y = 0.0
        self.odom_yaw = 0.0
        self.latest_image = None
        self.bridge = CvBridge()
        self.arm_positions = dict(DEFAULT_ARM)

    def _odom_cb(self, msg):
        self.odom_x = msg.pose.pose.position.x
        self.odom_y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.odom_yaw = math.atan2(siny_cosp, cosy_cosp)

    def _image_cb(self, msg):
        try:
            self.latest_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            if not getattr(self, "_camera_first", False):
                self._camera_first = True
                self.get_logger().info("Camera feed received: %dx%d" % (msg.width, msg.height))
        except Exception as e:
            if not getattr(self, "_camera_warned", False):
                self._camera_warned = True
                self.get_logger().warning("Camera decode failed: %s" % str(e))

    def _arm_state_cb(self, msg):
        for i, name in enumerate(msg.joint_names):
            if i < len(msg.actual.positions):
                self.arm_positions[name] = msg.actual.positions[i]

    def send_cmd_vel(self, linear_x, linear_y, angular_z):
        msg = Twist()
        msg.linear.x = float(linear_x)
        msg.linear.y = float(linear_y)
        msg.angular.z = float(angular_z)
        self.cmd_vel_pub.publish(msg)

    def send_arm_command(self, positions_dict):
        """Send joint positions via FollowJointTrajectory action."""
        pos = dict(self.arm_positions)
        pos.update(positions_dict)
        trajectory = JointTrajectory()
        trajectory.joint_names = ARM_JOINTS
        pt = JointTrajectoryPoint()
        pt.positions = [pos.get(j, 0.0) for j in ARM_JOINTS]
        pt.time_from_start.sec = 0
        pt.time_from_start.nanosec = 500000000
        trajectory.points = [pt]
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = trajectory
        if not self._arm_action_client.wait_for_server(timeout_sec=1.0):
            return
        self._arm_action_client.send_goal_async(goal_msg)

    def send_nav_goal(self, x, y, yaw=0.0):
        """Set navigation goal. Simple proportional controller uses odom + cmd_vel.
        x, y are world coordinates (must match map display)."""
        self._nav_goal_x = float(x)
        self._nav_goal_y = float(y)
        self._nav_goal_yaw = float(yaw)
        self._navigating = True
        return True

    def stop_nav(self):
        """Stop navigation and clear goal."""
        self._navigating = False
        self._nav_goal_x = None
        self._nav_goal_y = None
        self.send_cmd_vel(0.0, 0.0, 0.0)

    def update_simple_nav(self):
        """Run simple proportional nav controller. Call from GUI tick."""
        if not self._navigating or self._nav_goal_x is None:
            return
        # Goal and current in world coords; odom is relative to spawn
        world_x = self.spawn_x + self.odom_x
        world_y = self.spawn_y + self.odom_y
        dx = self._nav_goal_x - world_x
        dy = self._nav_goal_y - world_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < self._nav_tolerance:
            self.get_logger().info(
                "[NAV] Goal reached at world (%.2f, %.2f)" % (self._nav_goal_x, self._nav_goal_y)
            )
            self.send_cmd_vel(0.0, 0.0, 0.0)
            self._navigating = False
            self._nav_goal_x = None
            self._nav_goal_y = None
            return
        theta_goal = math.atan2(dy, dx)
        theta_err = theta_goal - self.odom_yaw
        while theta_err > math.pi:
            theta_err -= 2 * math.pi
        while theta_err < -math.pi:
            theta_err += 2 * math.pi
        if abs(theta_err) > 0.35:
            self.send_cmd_vel(0.0, 0.0, self._nav_angular_gain * theta_err)
        else:
            lin = min(self._nav_linear_gain, self._nav_linear_gain * dist)
            self.send_cmd_vel(lin, 0.0, self._nav_angular_gain * theta_err)


class MapWidget(QFrame):
    """Map panel showing farm layout, rover position, click to drop red pin.
    Map matches farm_world_light.world top-down: 100x100m, maize rows, trees, fence."""

    def __init__(self, rover_node, parent=None):
        super().__init__(parent)
        self.rover_node = rover_node
        self.setMinimumSize(400, 400)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setStyleSheet("background-color: #1a1a2e; border: 1px solid #4a4a6a; border-radius: 4px;")
        # Map parameters - must match farm_map.yaml
        self.map_origin_x = -50.0
        self.map_origin_y = -50.0
        self.map_resolution = 0.1  # m/pixel
        self.map_width_m = 100.0
        self.map_height_m = 100.0
        self.map_pix = None  # QPixmap of loaded map
        self.pin_position = None
        self.pin_enabled = True

        # Load map from farm_sim package (config/maps/ installed to share/farm_sim/config/maps/)
        try:
            from ament_index_python.packages import get_package_share_directory
            pkg = get_package_share_directory("farm_sim")
            map_path = os.path.join(pkg, "config", "maps", "farm_map.pgm")
            if os.path.exists(map_path):
                self._load_map(map_path)
            else:
                # Fallback: source path when running from workspace (farm_gui/farm_gui -> ../../farm_sim)
                base = os.path.dirname(os.path.abspath(__file__))
                fallback = os.path.normpath(os.path.join(base, "..", "..", "farm_sim", "config", "maps", "farm_map.pgm"))
                if os.path.exists(fallback):
                    self._load_map(fallback)
        except Exception:
            self.map_pix = None

    def _load_map(self, path: str):
        """Load PGM and convert to top-down farm map. Origin (-50,-50), center (0,0).
        PGM: col=x, row=flipped y. North=top, East=right."""
        try:
            with open(path, "rb") as f:
                header = f.readline().decode().strip()
                if header != "P2":
                    return
                while True:
                    line = f.readline().decode().strip()
                    if not line.startswith("#"):
                        break
                parts = line.split()
                w, h = int(parts[0]), int(parts[1])
                maxval = int(f.readline().decode().strip())
                data = []
                for _ in range(h):
                    row = [int(x) for x in f.readline().decode().split()]
                    data.extend(row)
            # Clean palette: green field, grid, obstacles
            img = QImage(w, h, QImage.Format_RGB32)
            for yy in range(h):
                for xx in range(w):
                    v = data[yy * w + xx]
                    if v <= 10:
                        r, g, b = 80, 65, 50  # Obstacles (fence, trees)
                    elif v >= 230:
                        r, g, b = 130, 165, 95  # Crop row strips
                    elif v >= 220:
                        r, g, b = 100, 130, 75  # Grid lines
                    else:
                        r, g, b = 115, 150, 88  # Open grass
                    img.setPixel(xx, yy, (255 << 24) | (r << 16) | (g << 8) | b)
            self.map_pix = QPixmap.fromImage(img)
        except Exception:
            self.map_pix = None

    def _display_to_world(self, px: int, py: int) -> tuple[float, float]:
        """Convert display pixel to world (x, y). Map centered, 100m span."""
        w, h = self.width(), self.height()
        scale = min(w, h) / self.map_width_m
        x = (px - w / 2) / scale
        y = (h / 2 - py) / scale
        return (x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and getattr(self, "pin_enabled", True):
            self.pin_position = self._display_to_world(event.x(), event.y())
            if hasattr(self.rover_node, "get_logger"):
                self.rover_node.get_logger().info(
                    "[CLICK] Map: dropped goal pin at world (%.2f, %.2f)" % self.pin_position
                )
            self.update()

    def get_pin_position(self):
        return self.pin_position

    def clear_pin(self):
        self.pin_position = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        w, h = self.width(), self.height()
        scale = min(w, h) / self.map_width_m

        # Draw map background (1000x1000 px = 100x100m, scale to fit)
        size = min(w, h)
        scale = size / self.map_width_m
        map_left = int((w - size) / 2)
        map_top = int((h - size) / 2)
        if self.map_pix is not None:
            scaled = self.map_pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            dx = (w - scaled.width()) / 2
            dy = (h - scaled.height()) / 2
            painter.drawPixmap(int(dx), int(dy), scaled)
        else:
            painter.fillRect(0, 0, w, h, QColor(40, 55, 40))

        # Grid overlay: every 10m
        cx, cy = w / 2, h / 2
        painter.setPen(QPen(QColor(70, 95, 65), 1))
        for i in range(-50, 51, 10):
            px = int(cx + i * scale)
            py = int(cy - i * scale)
            if map_left <= px <= map_left + size:
                painter.drawLine(px, map_top, px, map_top + size)
            if map_top <= py <= map_top + size:
                painter.drawLine(map_left, py, map_left + size, py)

        # Map center = world (0,0). Scale: pixels per meter
        cx, cy = w / 2, h / 2

        # Coordinate frame label (use QPointF to avoid int/float overload issues)
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(QPointF(10, 20), "N")
        painter.drawText(QPointF(w - 25, cy + 5), "E")

        # Draw rover position: odom is relative to spawn; world = spawn + odom
        x = self.rover_node.spawn_x + self.rover_node.odom_x
        y = self.rover_node.spawn_y + self.rover_node.odom_y
        px = int(cx + x * scale)
        py = int(cy - y * scale)

        painter.setPen(QPen(QColor(33, 150, 243), 2))
        painter.setBrush(QColor(33, 150, 243))
        painter.drawEllipse(px - 10, py - 10, 20, 20)
        yaw = self.rover_node.odom_yaw
        dx = 25 * math.cos(yaw)
        dy = -25 * math.sin(yaw)
        painter.setPen(QPen(QColor(25, 118, 210), 2))
        painter.drawLine(px, py, int(px + dx), int(py + dy))

        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 9))
        painter.drawText(QPointF(px + 14, py - 5), f"({x:.1f}, {y:.1f})")

        # Draw red pin if dropped
        if self.pin_position is not None:
            pin_x, pin_y = self.pin_position
            pin_px = int(cx + pin_x * scale)
            pin_py = int(cy - pin_y * scale)
            painter.setPen(QPen(QColor(239, 83, 80), 3))
            painter.setBrush(QColor(239, 83, 80))
            painter.drawEllipse(pin_px - 12, pin_py - 12, 24, 24)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(QPointF(pin_px + 14, pin_py + 4), f"Goal ({pin_x:.1f}, {pin_y:.1f})")


class CameraWidget(QLabel):
    """Camera feed display."""

    def __init__(self, rover_node, parent=None):
        super().__init__(parent)
        self.rover_node = rover_node
        self.setMinimumSize(640, 480)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #263238; color: #78909c;")
        self.setText("Waiting for camera...")

    def update_frame(self):
        if self.rover_node.latest_image is not None:
            img = np.ascontiguousarray(self.rover_node.latest_image)
            h, w = img.shape[:2]
            bytes_per_line = 3 * w
            qimg = QImage(
                img.data, w, h, bytes_per_line, QImage.Format_RGB888
            ).rgbSwapped()
            self.setPixmap(QPixmap.fromImage(qimg).scaled(640, 480, Qt.KeepAspectRatio))
            self.setText("")
        else:
            self.setText("No camera feed")


def create_control_panel(rover_node, send_cb):
    """Create drive and arm control buttons."""
    log = rover_node.get_logger()
    panel = QGroupBox("Rover Controls")
    layout = QGridLayout()

    def drive_cb(lx, ly, az, label):
        log.info("[CLICK] Drive: %s (linear_x=%.2f, linear_y=%.2f, angular_z=%.2f)" % (label, lx, ly, az))
        send_cb(lx, ly, az)

    # Drive buttons
    btn_up = QPushButton("▲\nUp")
    btn_up.setMinimumHeight(50)
    btn_up.pressed.connect(lambda: drive_cb(0.3, 0, 0, "Up PRESSED"))
    btn_up.released.connect(lambda: drive_cb(0, 0, 0, "Up RELEASED"))

    btn_down = QPushButton("▼\nDown")
    btn_down.setMinimumHeight(50)
    btn_down.pressed.connect(lambda: drive_cb(-0.3, 0, 0, "Down PRESSED"))
    btn_down.released.connect(lambda: drive_cb(0, 0, 0, "Down RELEASED"))

    btn_left = QPushButton("◀ Left")
    btn_left.setMinimumHeight(50)
    btn_left.pressed.connect(lambda: drive_cb(0, 0, 0.5, "Left PRESSED"))
    btn_left.released.connect(lambda: drive_cb(0, 0, 0, "Left RELEASED"))

    btn_right = QPushButton("Right ▶")
    btn_right.setMinimumHeight(50)
    btn_right.pressed.connect(lambda: drive_cb(0, 0, -0.5, "Right PRESSED"))
    btn_right.released.connect(lambda: drive_cb(0, 0, 0, "Right RELEASED"))

    btn_stop = QPushButton("STOP")
    btn_stop.setMinimumHeight(50)
    btn_stop.setStyleSheet("background-color: #e53935; color: white; font-weight: bold;")
    btn_stop.pressed.connect(lambda: drive_cb(0, 0, 0, "STOP"))

    layout.addWidget(btn_up, 0, 1)
    layout.addWidget(btn_left, 1, 0)
    layout.addWidget(btn_stop, 1, 1)
    layout.addWidget(btn_right, 1, 2)
    layout.addWidget(btn_down, 2, 1)

    # Arm controls
    arm_grp = QGroupBox("Arm")
    arm_layout = QVBoxLayout()

    def arm_up():
        log.info("[CLICK] Arm: Arm Up")
        rover_node.send_arm_command(
            {"joint2": 0.5, "joint3": 0.5, "joint4": 0.0}
        )

    def arm_down():
        log.info("[CLICK] Arm: Arm Down")
        rover_node.send_arm_command(
            {"joint2": -0.5, "joint3": -0.5, "joint4": 0.0}
        )

    btn_arm_up = QPushButton("Arm Up")
    btn_arm_up.clicked.connect(arm_down)  # swapped: up button moves arm down
    btn_arm_down = QPushButton("Arm Down")
    btn_arm_down.clicked.connect(arm_up)  # swapped: down button moves arm up
    btn_return_normal = QPushButton("Return to Normal")
    btn_return_normal.clicked.connect(lambda: rover_node.send_arm_command(DEFAULT_ARM))

    arm_layout.addWidget(btn_arm_up)
    arm_layout.addWidget(btn_arm_down)
    arm_layout.addWidget(btn_return_normal)
    arm_grp.setLayout(arm_layout)

    layout.addWidget(arm_grp, 3, 0, 1, 3)
    panel.setLayout(layout)
    return panel


def main():
    if not HAS_PYQT5:
        print("PyQt5 is required. Install with: pip3 install PyQt5")
        sys.exit(1)

    rclpy.init()
    app = QApplication(sys.argv)

    rover_node = RoverNode()
    executor = MultiThreadedExecutor()
    executor.add_node(rover_node)

    def spin_thread():
        try:
            executor.spin()
        except Exception:
            pass

    ros_thread = threading.Thread(target=spin_thread, daemon=True)
    ros_thread.start()

    # Main window
    window = QMainWindow()
    window.setWindowTitle("Farm Rover Control")
    window.setMinimumSize(1100, 700)

    central = QWidget()
    central.setLayout(QVBoxLayout())

    # Top bar: Start simulation (or "Sim running" when launched with sim_with_gui) + mode
    top_bar = QHBoxLayout()
    sim_included = rover_node.get_parameter("sim_included").value
    btn_start = QPushButton("Start Simulation" if not sim_included else "Simulation running")
    btn_start.setStyleSheet(
        "background-color: #43a047; color: white; font-weight: bold; padding: 10px 20px;"
    )
    if sim_included:
        btn_start.setEnabled(False)

    def start_sim():
        rover_node.get_logger().info("[CLICK] Start Simulation")
        try:
            env = dict(os.environ)
            env.setdefault("RMW_IMPLEMENTATION", "rmw_fastrtps_cpp")
            subprocess.Popen(
                ["ros2", "launch", "farm_bringup", "sim.launch.py"],
                cwd=os.path.expanduser("~"),
                env=env,
            )
            rover_node.get_logger().info("[CLICK] Start Simulation: launched successfully")
            QMessageBox.information(
                window, "Simulation", "Launching simulation in background. Wait ~15s for it to be ready."
            )
        except FileNotFoundError:
            rover_node.get_logger().error("[CLICK] Start Simulation: FAILED - ros2 not found")
            QMessageBox.warning(
                window, "Error",
                "ros2 not found. Source ROS 2 and farm_ws install/setup.bash first."
            )

    btn_start.clicked.connect(start_sim)
    top_bar.addWidget(btn_start)

    mode_combo = QComboBox()
    mode_combo.addItems(["Autonomous Mode", "Remote Control Mode"])
    top_bar.addWidget(QLabel("Mode:"))
    top_bar.addWidget(mode_combo)
    top_bar.addStretch()
    central.layout().addLayout(top_bar)

    # Shared map and camera (always visible)
    map_widget = MapWidget(rover_node)
    camera_widget = CameraWidget(rover_node)
    map_instruction = QLabel("Click on map to drop a red goal pin")
    map_instruction.setStyleSheet("color: #666; font-style: italic;")

    # Left column: map + camera
    left_col = QVBoxLayout()
    left_col.addWidget(map_instruction)
    left_col.addWidget(map_widget)
    left_col.addWidget(camera_widget)

    # Right column: stacked - autonomous vs remote controls
    stacked_right = QStackedWidget()

    # Autonomous mode: navigate button
    autonomous_page = QWidget()
    auto_layout = QVBoxLayout()
    auto_grp = QGroupBox("Autonomous")
    auto_grp_layout = QVBoxLayout()
    btn_navigate = QPushButton("Navigate to dropped point")
    btn_navigate.setMinimumHeight(50)
    btn_navigate.setStyleSheet("background-color: #1976d2; color: white; font-weight: bold;")
    btn_clear_pin = QPushButton("Clear pin")
    btn_clear_pin.setMinimumHeight(40)

    def do_navigate():
        rover_node.get_logger().info("[CLICK] Navigate to dropped point")
        pos = map_widget.get_pin_position()
        if pos is None:
            rover_node.get_logger().warning("[CLICK] Navigate: FAILED - no pin dropped")
            QMessageBox.warning(window, "No pin", "Click on the map first to drop a red pin.")
            return
        x, y = pos
        if rover_node.send_nav_goal(x, y):
            rover_node.get_logger().info("[CLICK] Navigate: started -> (%.2f, %.2f)" % (x, y))
            QMessageBox.information(window, "Navigation", f"Navigating to ({x:.1f}, {y:.1f})")
        else:
            rover_node.get_logger().warning("[CLICK] Navigate: FAILED - could not start")
            QMessageBox.warning(window, "Navigation", "Could not start navigation.")

    btn_navigate.clicked.connect(do_navigate)
    def do_clear_pin():
        rover_node.get_logger().info("[CLICK] Clear pin")
        map_widget.clear_pin()

    btn_clear_pin.clicked.connect(do_clear_pin)
    auto_grp_layout.addWidget(btn_navigate)
    auto_grp_layout.addWidget(btn_clear_pin)
    auto_grp_layout.addStretch()
    auto_grp.setLayout(auto_grp_layout)
    auto_layout.addWidget(auto_grp)
    auto_layout.addStretch()
    autonomous_page.setLayout(auto_layout)
    stacked_right.addWidget(autonomous_page)

    # Remote control mode: manual drive + arm
    remote_page = QWidget()
    remote_layout = QVBoxLayout()
    control_panel = create_control_panel(
        rover_node, lambda lx, ly, az: rover_node.send_cmd_vel(lx, ly, az)
    )
    remote_layout.addWidget(control_panel)
    remote_layout.addStretch()
    remote_page.setLayout(remote_layout)
    stacked_right.addWidget(remote_page)

    def on_mode_change(i):
        mode_name = "Autonomous Mode" if i == 0 else "Remote Control Mode"
        rover_node.get_logger().info("[CLICK] Mode: switched to %s" % mode_name)
        stacked_right.setCurrentIndex(i)
        if i == 0:  # Autonomous
            map_instruction.setText("Click on map to drop a red goal pin")
            map_widget.pin_enabled = True
        else:  # Remote
            map_instruction.setText("Remote control: use buttons to drive")
            map_widget.pin_enabled = False

    mode_combo.currentIndexChanged.connect(on_mode_change)
    map_widget.pin_enabled = True
    stacked_right.setCurrentIndex(0)
    rover_node.get_logger().info("[GUI] Started - initial mode: Autonomous Mode")

    # Main content: left (map+camera) + right (mode-specific controls)
    content = QHBoxLayout()
    content.addLayout(left_col, 2)
    content.addWidget(stacked_right, 1)
    central.layout().addLayout(content)
    window.setCentralWidget(central)

    # Update timer (ROS callbacks run in executor thread)
    def tick():
        try:
            rover_node.update_simple_nav()
        except Exception as e:
            err_str = str(e).lower()
            if "context is not valid" in err_str or "rcl_shutdown" in err_str or "rclerror" in type(e).__name__.lower():
                update_timer.stop()
                return
            raise
        map_widget.update()
        camera_widget.update_frame()

    update_timer = QTimer()
    update_timer.timeout.connect(tick)
    update_timer.start(50)

    window.show()
    result = app.exec_()
    update_timer.stop()
    executor.shutdown()
    try:
        rclpy.shutdown()
    except Exception:
        pass  # may already be shut down (e.g. SIGINT from launch)
    sys.exit(result)
