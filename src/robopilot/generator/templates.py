"""Template rendering for offline ROS-style package generation."""

from __future__ import annotations

from textwrap import dedent

from robopilot.generator.project_spec import ProjectSpec
from robopilot.generator.task_classifier import (
    ACKERMANN_DRIVE,
    CAMERA_SUBSCRIBER,
    DEPTH_CAMERA,
    DIAGNOSTIC_AGGREGATOR,
    GENERIC_NODE,
    IMAGE_PROCESSING,
    NAVIGATION,
    OBJECT_DETECTION,
    PERCEPTION_PIPELINE,
    ROBOT_ARM,
    ROSBAG_TOOLS,
    SENSOR_FUSION,
    SLAM,
    STATE_MACHINE,
    TELEOP,
    VELOCITY_CONTROLLER,
)
from robopilot.spec.io import spec_to_yaml


def package_xml(spec: ProjectSpec) -> str:
    """Render a ROS-style package.xml file."""
    from robopilot import __version__ as _ver
    return dedent(
        f"""\
        <?xml version="1.0"?>
        <package format="3">
          <name>{spec.package_name}</name>
          <version>{_ver}</version>
          <description>{spec.description}</description>
          <maintainer email="developer@example.com">RoboPilot User</maintainer>
          <license>MIT</license>

          <buildtool_depend>ament_python</buildtool_depend>

          <exec_depend>rclpy</exec_depend>
          <exec_depend>sensor_msgs</exec_depend>
          <exec_depend>std_msgs</exec_depend>
          <exec_depend>geometry_msgs</exec_depend>

          <export>
            <build_type>ament_python</build_type>
          </export>
        </package>
        """
    )


def setup_py(spec: ProjectSpec) -> str:
    """Render a ROS-style setup.py file."""
    from robopilot import __version__ as _ver
    return dedent(
        f"""\
        from setuptools import find_packages, setup


        package_name = "{spec.package_name}"

        setup(
            name=package_name,
            version="{_ver}",
            packages=find_packages(exclude=["test"]),
            data_files=[
                (f"share/{{package_name}}", ["package.xml", "robopilot.yaml"]),
                (f"share/{{package_name}}/launch", ["launch/{spec.package_name}.launch.py"]),
                (f"share/{{package_name}}/config", ["config/params.yaml"]),
            ],
            install_requires=["setuptools"],
            zip_safe=True,
            maintainer="RoboPilot User",
            maintainer_email="developer@example.com",
            description="{spec.description}",
            license="MIT",
            entry_points={{
                "console_scripts": [
                    "{spec.executable_name} = {spec.package_name}.{spec.module_name}:main",
                ],
            }},
        )
        """
    )


def setup_cfg(spec: ProjectSpec) -> str:
    """Render a ROS-style setup.cfg file."""
    return dedent(
        f"""\
        [develop]
        script_dir=$base/lib/{spec.package_name}

        [install]
        install_scripts=$base/lib/{spec.package_name}
        """
    )


def readme(spec: ProjectSpec) -> str:
    """Render a README for the generated package."""
    notes = "\n".join(f"- {note}" for note in spec.notes)
    return dedent(
        f"""\
        # {spec.package_name}

        {spec.description}

        ## Task

        {spec.task}

        ## Selected Template

        `{spec.selected_template}`

        ## Generated Files

        - `package.xml`
        - `setup.py`
        - `setup.cfg`
        - `robopilot.yaml`
        - `launch/{spec.package_name}.launch.py`
        - `config/params.yaml`
        - `{spec.package_name}/{spec.node_file_name}`

        ## Notes

        {notes}

        This package is intentionally offline-friendly pseudocode. It mirrors common
        ROS2 Python package structure, but RoboPilot does not require a real ROS2
        installation to generate or inspect these files.
        """
    )


def launch_file(spec: ProjectSpec) -> str:
    """Render a ROS-style launch file."""
    return dedent(
        f"""\
        \"\"\"ROS2-style launch pseudocode for {spec.package_name}.\"\"\"

        # This file mirrors a common ROS2 launch structure.
        # It is generated for learning and planning; RoboPilot does not require
        # launch_ros or a ROS2 runtime to be installed.


        def generate_launch_description():
            try:
                from launch import LaunchDescription
                from launch_ros.actions import Node
            except ImportError:
                return {{
                    "package": "{spec.package_name}",
                    "node": "{spec.executable_name}",
                    "selected_template": "{spec.selected_template}",
                    "note": "ROS2 launch modules are not installed; this is pseudocode.",
                }}

            return LaunchDescription(
                [
                    Node(
                        package="{spec.package_name}",
                        executable="{spec.executable_name}",
                        name="{spec.node_name}",
                        output="screen",
                        parameters=["config/params.yaml"],
                    )
                ]
            )
        """
    )


def params_yaml(spec: ProjectSpec) -> str:
    """Render a params.yaml file for the selected template."""
    body = {
        CAMERA_SUBSCRIBER: _camera_params,
        OBJECT_DETECTION: _object_detection_params,
        VELOCITY_CONTROLLER: _velocity_controller_params,
        PERCEPTION_PIPELINE: _perception_pipeline_params,
        SLAM: _slam_params,
        NAVIGATION: _navigation_params,
        SENSOR_FUSION: _sensor_fusion_params,
        IMAGE_PROCESSING: _image_processing_params,
        ROBOT_ARM: _robot_arm_params,
        ROSBAG_TOOLS: _rosbag_tools_params,
        STATE_MACHINE: _state_machine_params,
        GENERIC_NODE: _generic_params,
        DEPTH_CAMERA: _depth_camera_params,
        ACKERMANN_DRIVE: _ackermann_drive_params,
        TELEOP: _teleop_params,
        DIAGNOSTIC_AGGREGATOR: _diagnostic_aggregator_params,
    }.get(spec.selected_template, _generic_params)(spec)
    return dedent(body)


def robopilot_yaml(spec: ProjectSpec) -> str:
    """Render RoboPilot generation metadata."""
    return spec_to_yaml(spec)


def node_file(spec: ProjectSpec) -> str:
    """Render the selected ROS-style Python node pseudocode file."""
    content = _node_file_impl(spec)
    if getattr(spec, "lang", "en") == "zh":
        content = _zh_header(spec) + content
    return content


def _node_file_impl(spec: ProjectSpec) -> str:
    template = spec.selected_template
    if template == DEPTH_CAMERA:
        return _depth_camera_node(spec)
    if template == ACKERMANN_DRIVE:
        return _ackermann_drive_node(spec)
    if template == TELEOP:
        return _teleop_node(spec)
    if template == DIAGNOSTIC_AGGREGATOR:
        return _diagnostic_aggregator_node(spec)
    if template == SLAM:
        return _slam_node(spec)
    if template == NAVIGATION:
        return _navigation_node(spec)
    if template == SENSOR_FUSION:
        return _sensor_fusion_node(spec)
    if template == IMAGE_PROCESSING:
        return _image_processing_node(spec)
    if template == ROBOT_ARM:
        return _robot_arm_node(spec)
    if template == ROSBAG_TOOLS:
        return _rosbag_tools_node(spec)
    if template == STATE_MACHINE:
        return _state_machine_node(spec)
    if template == OBJECT_DETECTION:
        return _object_detection_node(spec)
    if template == CAMERA_SUBSCRIBER:
        return _camera_subscriber_node(spec)
    if template == VELOCITY_CONTROLLER:
        return _velocity_controller_node(spec)
    if template == PERCEPTION_PIPELINE:
        return _perception_pipeline_node(spec)
    return _generic_node(spec)


def _fallback_node_block() -> str:
    return dedent(
        '''\
        try:
            import rclpy
            from rclpy.node import Node
        except ImportError:
            rclpy = None

            class Node:  # type: ignore[no-redef]
                """Tiny fallback so this pseudocode stays readable offline."""

                def __init__(self, name: str) -> None:
                    self.name = name

                def get_logger(self):
                    return self

                def info(self, message: str) -> None:
                    print(message)
        '''
    )


def _zh_header(spec: ProjectSpec) -> str:
    return f'''# -*- coding: utf-8 -*-
"""{{ '{{' }}spec.description{{ '}}' }}

由 RoboPilot 生成 — 模板: {spec.selected_template}
任务: {spec.task}

本文件为离线伪代码，用于学习和规划。RoboPilot 不需要 ROS/ROS2 运行时。
"""

'''


def _main_block(class_name: str) -> str:
    return dedent(
        f'''


        def main() -> None:
            """Entry point for the ROS2-style node."""
            if rclpy is None:
                node = {class_name}()
                node.run_once()
                return

            rclpy.init()
            node = {class_name}()
            try:
                rclpy.spin(node)
            finally:
                node.destroy_node()
                rclpy.shutdown()


        if __name__ == "__main__":
            main()
        '''
    )


# ---------------------------------------------------------------------------
# v2.0.0 existing template nodes
# ---------------------------------------------------------------------------


def _object_detection_node(spec: ProjectSpec) -> str:
    topics = spec.topics
    sub_topic = _find_topic(topics, "subscribe") or _topic("subscribe", "/camera/image_raw", "sensor_msgs/Image")
    pub_topic = _find_topic(topics, "publish") or _topic("publish", "/detections/bounding_boxes", "std_msgs/String")
    return (
        dedent(
        f'''\
        """ROS2-style object detection node pseudocode generated by RoboPilot.

        Task:
            {spec.task}
        """

        from __future__ import annotations

        from dataclasses import dataclass
        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        @dataclass
        class BoundingBox:
            """Simple placeholder for a detected object bounding box."""

            label: str
            confidence: float
            x: int
            y: int
            width: int
            height: int


        class {spec.class_name}(Node):
            """ROS2-style object detection node skeleton."""

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.input_image_topic = "{sub_topic.name}"
                self.output_boxes_topic = "{pub_topic.name}"
                self.confidence_threshold = 0.50
                self.image_subscription = None
                self.box_publisher = None
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                boxes = self.detect_objects("<offline image placeholder>")
                self.publish_boxes(boxes)

            def detect_objects(self, image_message: Any) -> list[BoundingBox]:
                """Replace this placeholder with a model or classical CV pipeline."""
                _ = image_message
                return [BoundingBox("object", 0.90, 120, 80, 160, 120)]

            def publish_boxes(self, boxes: list[BoundingBox]) -> None:
                """Publish bounding boxes in a real ROS2 node; log them offline."""
                self.get_logger().info(
                    f"Publishing {{len(boxes)}} boxes to {{self.output_boxes_topic}}"
                )
        '''
        )
        + _main_block(spec.class_name)
    )


def _camera_subscriber_node(spec: ProjectSpec) -> str:
    topics = spec.topics
    sub_topic = _find_topic(topics, "subscribe") or _topic("subscribe", "/camera/image_raw", "sensor_msgs/Image")
    return (
        dedent(
        f'''\
        """ROS2-style camera subscriber node pseudocode generated by RoboPilot.

        Task:
            {spec.task}
        """

        from __future__ import annotations

        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        class {spec.class_name}(Node):
            """ROS2-style camera subscriber node skeleton."""

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.input_image_topic = "{sub_topic.name}"
                self.frame_count = 0
                self.image_subscription = None
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                self.on_image("<offline frame placeholder>")

            def on_image(self, image_message: Any) -> None:
                """Handle one camera frame in a real ROS2 subscriber."""
                self.frame_count += 1
                self.get_logger().info(
                    f"Received frame {{self.frame_count}} on {{self.input_image_topic}}: "
                    f"{{image_message!r}}"
                )
        '''
        )
        + _main_block(spec.class_name)
    )


def _velocity_controller_node(spec: ProjectSpec) -> str:
    topics = spec.topics
    pub_topic = _find_topic(topics, "publish") or _topic("publish", "/cmd_vel", "geometry_msgs/Twist")
    return (
        dedent(
        f'''\
        """ROS2-style velocity controller node pseudocode generated by RoboPilot.

        Task:
            {spec.task}
        """

        from __future__ import annotations


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        class {spec.class_name}(Node):
            """ROS2-style velocity controller node skeleton."""

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.cmd_vel_topic = "{pub_topic.name}"
                self.linear_velocity = 0.20
                self.angular_velocity = 0.00
                self.cmd_publisher = None
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                self.publish_velocity_command()

            def publish_velocity_command(self) -> None:
                """Publish a Twist-like command in real ROS2; log it offline."""
                self.get_logger().info(
                    f"Publishing cmd_vel linear={{self.linear_velocity}} "
                    f"angular={{self.angular_velocity}} to {{self.cmd_vel_topic}}"
                )
        '''
        )
        + _main_block(spec.class_name)
    )


def _perception_pipeline_node(spec: ProjectSpec) -> str:
    return (
        dedent(
        f'''\
        """ROS2-style perception pipeline node pseudocode generated by RoboPilot.

        Task:
            {spec.task}
        """

        from __future__ import annotations

        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        class {spec.class_name}(Node):
            """ROS2-style perception workflow node skeleton."""

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.stages = ["camera", "detector", "tracker"]
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                result = self.process_frame("<offline frame placeholder>")
                self.get_logger().info(f"Pipeline result: {{result}}")

            def process_frame(self, frame: Any) -> dict[str, Any]:
                """Represent camera -> detector -> tracker flow in pseudocode."""
                return {{
                    "frame": frame,
                    "detections": ["placeholder_detection"],
                    "tracks": ["placeholder_track"],
                }}
        '''
        )
        + _main_block(spec.class_name)
    )


# ---------------------------------------------------------------------------
# v2.1.0 new template nodes
# ---------------------------------------------------------------------------


def _slam_node(spec: ProjectSpec) -> str:
    topics = spec.topics
    scan_topic = _find_topic_by_name(topics, "/scan") or "/scan"
    map_topic = _find_topic_by_name(topics, "/map") or "/map"
    return (
        dedent(
        f'''\
        """ROS2-style SLAM mapping node pseudocode generated by RoboPilot.

        Task:
            {spec.task}

        This node mirrors the structure of slam_toolbox / gmapping without
        requiring ROS2, a real LiDAR, or a simulator runtime.
        """

        from __future__ import annotations

        from dataclasses import dataclass
        from math import cos as _cos, sin as _sin
        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        @dataclass
        class MapCell:
            """A single cell in the occupancy grid map."""

            x: int
            y: int
            occupied: bool
            probability: float


        class {spec.class_name}(Node):
            """ROS2-style SLAM mapping node skeleton.

            Subscribes to laser scan data and builds a 2D occupancy grid map.
            """

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.scan_topic = "{scan_topic}"
                self.map_topic = "{map_topic}"
                self.map_resolution = 0.05
                self.map_width = 200
                self.map_height = 200
                self.max_laser_range = 12.0
                self.scan_subscription = None
                self.map_publisher = None
                self.pose = (0.0, 0.0, 0.0)
                self.map_cells: list[MapCell] = []
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                scan = self.sense_placeholder_scan()
                self.update_map(scan)

            def sense_placeholder_scan(self) -> list[float]:
                """Return a placeholder laser scan for offline inspection."""
                return [1.0] * 360

            def update_map(self, scan_ranges: list[float]) -> None:
                """Update the occupancy grid from laser scan data."""
                for i, rng in enumerate(scan_ranges):
                    if rng < self.max_laser_range:
                        angle = i * 3.14159 / 180.0
                        mx = int(self.pose[0] + rng * _cos(angle) / self.map_resolution)
                        my = int(self.pose[1] + rng * _sin(angle) / self.map_resolution)
                        self.map_cells.append(MapCell(mx, my, True, 0.90))
                self.get_logger().info(
                    f"Updated map: {{len(self.map_cells)}} cells, "
                    f"resolution={{self.map_resolution}}m"
                )

            def save_map(self, path: str) -> None:
                """Save the built map to disk (pgm + yaml)."""
                self.get_logger().info(f"Saving map to {{path}}")
        '''
        )
        + _main_block(spec.class_name)
    )


def _navigation_node(spec: ProjectSpec) -> str:
    topics = spec.topics
    odom_topic = _find_topic_by_name(topics, "/odom") or "/odom"
    goal_topic = _find_topic_by_name(topics, "/goal_pose") or "/goal_pose"
    cmd_topic = _find_topic_by_name(topics, "/cmd_vel") or "/cmd_vel"
    return (
        dedent(
        f'''\
        """ROS2-style autonomous navigation node pseudocode generated by RoboPilot.

        Task:
            {spec.task}

        This node mirrors Nav2 planner/controller structure without requiring
        ROS2, a real robot, or Nav2 to be installed.
        """

        from __future__ import annotations

        from dataclasses import dataclass
        from math import atan2, hypot, pi
        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        @dataclass
        class Pose2D:
            """2D pose representation."""

            x: float
            y: float
            theta: float


        @dataclass
        class PathPoint:
            """A point along a planned path."""

            x: float
            y: float


        class {spec.class_name}(Node):
            """ROS2-style autonomous navigation node skeleton.

            Subscribes to odometry and goal poses, publishes velocity commands
            and planned paths. Mirrors Nav2 planner + controller separation.
            """

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.odom_topic = "{odom_topic}"
                self.goal_topic = "{goal_topic}"
                self.cmd_vel_topic = "{cmd_topic}"
                self.max_linear_speed = 0.50
                self.max_angular_speed = 1.00
                self.goal_tolerance = 0.10
                self.current_pose = Pose2D(0.0, 0.0, 0.0)
                self.goal_pose: Pose2D | None = None
                self.plan: list[PathPoint] = []
                self.odom_subscription = None
                self.goal_subscription = None
                self.cmd_publisher = None
                self.plan_publisher = None
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                self.goal_pose = Pose2D(5.0, 3.0, 0.0)
                self.compute_plan()
                self.execute_plan_step()
                self.check_goal_reached()

            def compute_plan(self) -> None:
                """Compute a simple straight-line path toward the goal."""
                if self.goal_pose is None:
                    return
                steps = max(1, int(hypot(
                    self.goal_pose.x - self.current_pose.x,
                    self.goal_pose.y - self.current_pose.y,
                ) / 0.25))
                self.plan = [
                    PathPoint(
                        self.current_pose.x + (self.goal_pose.x - self.current_pose.x) * t / steps,
                        self.current_pose.y + (self.goal_pose.y - self.current_pose.y) * t / steps,
                    )
                    for t in range(1, steps + 1)
                ]
                self.get_logger().info(f"Computed plan with {{len(self.plan)}} waypoints")

            def execute_plan_step(self) -> None:
                """Execute one step toward the next waypoint."""
                if not self.plan:
                    return
                target = self.plan[0]
                dx = target.x - self.current_pose.x
                dy = target.y - self.current_pose.y
                dist = hypot(dx, dy)
                desired_theta = atan2(dy, dx)
                self.current_pose = Pose2D(target.x, target.y, desired_theta)
                self.plan.pop(0)
                vx = min(self.max_linear_speed, dist)
                self.get_logger().info(
                    f"Publishing cmd_vel: linear={{vx:.2f}} m/s to {{self.cmd_vel_topic}}"
                )

            def check_goal_reached(self) -> None:
                """Check if the robot has reached the goal pose."""
                if self.goal_pose is None:
                    return
                dist = hypot(
                    self.goal_pose.x - self.current_pose.x,
                    self.goal_pose.y - self.current_pose.y,
                )
                if dist < self.goal_tolerance:
                    self.get_logger().info("Goal reached!")
        '''
        )
        + _main_block(spec.class_name)
    )


def _sensor_fusion_node(spec: ProjectSpec) -> str:
    return (
        dedent(
        f'''\
        """ROS2-style sensor fusion node pseudocode generated by RoboPilot.

        Task:
            {spec.task}

        This node mirrors robot_localization EKF/UKF patterns without
        requiring ROS2, real sensors, or filter libraries.
        """

        from __future__ import annotations

        from dataclasses import dataclass
        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        @dataclass
        class FusedOdometry:
            """Fused odometry estimate from multiple sensor sources."""

            x: float
            y: float
            z: float
            roll: float
            pitch: float
            yaw: float
            covariance: list[float]


        class {spec.class_name}(Node):
            """ROS2-style sensor fusion node skeleton (EKF/UKF pattern).

            Subscribes to IMU, GPS, and wheel odometry, fuses them into a
            filtered odometry estimate. Mirrors robot_localization patterns.
            """

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.use_imu = True
                self.use_gps = True
                self.use_odom = True
                self.filter_type = "ekf"
                self.publish_rate = 50.0
                self.imu_subscription = None
                self.gps_subscription = None
                self.odom_subscription = None
                self.filtered_publisher = None
                self.latest_imu: dict[str, Any] = {{}}
                self.latest_gps: dict[str, Any] = {{}}
                self.latest_odom: dict[str, Any] = {{}}
                self.state = FusedOdometry(
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    [0.01] * 36,
                )
                self.get_logger().info(
                    "Initialized {spec.selected_template} template "
                    f"(filter={{self.filter_type}})"
                )

            def run_once(self) -> None:
                self.latest_imu = {{
                    "angular_velocity_z": 0.01,
                    "linear_acceleration_x": 0.05,
                    "orientation_w": 1.0,
                }}
                self.latest_gps = {{"latitude": 40.0, "longitude": -105.0, "altitude": 1600.0}}
                self.latest_odom = {{"twist_linear_x": 0.20, "twist_angular_z": 0.01}}
                self.predict_step(0.02)
                self.update_step()
                self.publish_fused_odometry()

            def predict_step(self, dt: float) -> None:
                """EKF prediction step using IMU and odometry."""
                self.state.x += self.latest_odom.get("twist_linear_x", 0.0) * dt
                self.state.yaw += self.latest_imu.get("angular_velocity_z", 0.0) * dt
                self.get_logger().info(f"Predicted: x={{self.state.x:.3f}}, yaw={{self.state.yaw:.3f}}")

            def update_step(self) -> None:
                """EKF update step using GPS measurements."""
                self.get_logger().info("Correction applied from GPS measurement")

            def publish_fused_odometry(self) -> None:
                """Publish the fused and filtered odometry estimate."""
                self.get_logger().info(
                    f"Publishing fused odometry: "
                    f"x={{self.state.x:.3f}}, y={{self.state.y:.3f}}, yaw={{self.state.yaw:.3f}}"
                )
        '''
        )
        + _main_block(spec.class_name)
    )


def _image_processing_node(spec: ProjectSpec) -> str:
    topics = spec.topics
    raw_topic = _find_topic_by_name(topics, "/camera/image_raw") or "/camera/image_raw"
    out_topic = _find_topic_by_name(topics, "/processed/image") or "/processed/image"
    return (
        dedent(
        f'''\
        """ROS2-style image processing node pseudocode generated by RoboPilot.

        Task:
            {spec.task}

        This node mirrors OpenCV + cv_bridge processing pipelines without
        requiring ROS2, OpenCV, or a real camera.
        """

        from __future__ import annotations

        from dataclasses import dataclass
        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        @dataclass
        class ProcessingResult:
            """Result of one image processing step."""

            mode: str
            input_shape: tuple[int, int]
            output_shape: tuple[int, int]
            features_detected: int


        class {spec.class_name}(Node):
            """ROS2-style image processing node skeleton.

            Subscribes to a raw camera image, applies configurable processing
            (blur, edge detection, color filtering), and publishes the
            processed result. Mirrors cv_bridge + OpenCV pipelines.
            """

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.input_topic = "{raw_topic}"
                self.output_topic = "{out_topic}"
                self.processing_mode = "canny"
                self.blur_kernel = 5
                self.canny_threshold_low = 50
                self.canny_threshold_high = 150
                self.image_subscription = None
                self.processed_publisher = None
                self.get_logger().info(
                    "Initialized {spec.selected_template} template "
                    f"(mode={{self.processing_mode}})"
                )

            def run_once(self) -> None:
                frame = self.capture_placeholder_frame()
                result = self.process_frame(frame)
                self.publish_result(result)

            def capture_placeholder_frame(self) -> Any:
                """Return placeholder image data for offline development."""
                return {{
                    "width": 640,
                    "height": 480,
                    "encoding": "bgr8",
                    "data": "<placeholder image bytes>",
                }}

            def process_frame(self, frame: dict[str, Any]) -> ProcessingResult:
                """Apply the selected image processing pipeline."""
                w, h = frame.get("width", 640), frame.get("height", 480)
                if self.processing_mode == "canny":
                    self.get_logger().info(
                        f"Applying Canny edge detection "
                        f"(low={{self.canny_threshold_low}}, high={{self.canny_threshold_high}})"
                    )
                elif self.processing_mode == "blur":
                    self.get_logger().info(
                        f"Applying Gaussian blur (kernel={{self.blur_kernel}})"
                    )
                else:
                    self.get_logger().info(f"Applying {{self.processing_mode}} filter")
                return ProcessingResult(self.processing_mode, (w, h), (w, h), 12)

            def publish_result(self, result: ProcessingResult) -> None:
                """Publish the processed image result."""
                self.get_logger().info(
                    f"Publishing processed frame to {{self.output_topic}}: "
                    f"{{result.features_detected}} features detected"
                )
        '''
        )
        + _main_block(spec.class_name)
    )


def _robot_arm_node(spec: ProjectSpec) -> str:
    return (
        dedent(
        f'''\
        """ROS2-style robot arm controller node pseudocode generated by RoboPilot.

        Task:
            {spec.task}

        This node mirrors ros2_control / MoveIt2 joint trajectory patterns
        without requiring ROS2, a real arm, or simulation.
        """

        from __future__ import annotations

        from dataclasses import dataclass
        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        @dataclass
        class JointState:
            """State of a single robot joint."""

            name: str
            position: float
            velocity: float
            effort: float


        @dataclass
        class JointTrajectory:
            """A trajectory for one or more joints."""

            joint_names: list[str]
            points: list[list[float]]
            durations: list[float]


        class {spec.class_name}(Node):
            """ROS2-style robot arm controller node skeleton.

            Subscribes to joint states, publishes joint trajectory commands.
            Mirrors ros2_control JointTrajectoryController patterns.
            """

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.num_joints = 6
                self.joint_names = [
                    "joint_1", "joint_2", "joint_3",
                    "joint_4", "joint_5", "joint_6",
                ]
                self.home_position = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                self.gripper_enabled = True
                self.current_joints: list[JointState] = []
                self.joint_subscription = None
                self.command_publisher = None
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                self.read_joint_states()
                self.go_to_home()
                waypoint = [0.5, -0.3, 0.2, 1.2, 0.0, 0.0]
                self.send_joint_trajectory([waypoint], [2.0])
                if self.gripper_enabled:
                    self.actuate_gripper("close")

            def read_joint_states(self) -> None:
                """Read current joint positions from the robot."""
                self.current_joints = [
                    JointState(name, 0.0, 0.0, 0.0)
                    for name in self.joint_names
                ]
                self.get_logger().info(
                    f"Read {{len(self.current_joints)}} joint states"
                )

            def go_to_home(self) -> None:
                """Move the arm to the home position."""
                traj = JointTrajectory(
                    self.joint_names,
                    [list(self.home_position)],
                    [1.5],
                )
                self.get_logger().info("Moving arm to home position")

            def send_joint_trajectory(
                self,
                points: list[list[float]],
                durations: list[float],
            ) -> None:
                """Send a joint trajectory command."""
                self.get_logger().info(
                    f"Publishing joint trajectory: "
                    f"{{len(points)}} waypoints, {{len(points[0]) if points else 0}} joints"
                )
                for i, (point, dur) in enumerate(zip(points, durations)):
                    self.get_logger().info(
                        f"  Waypoint {{i + 1}}: joints={{point}}, duration={{dur}}s"
                    )

            def actuate_gripper(self, action: str) -> None:
                """Open or close the end-effector gripper."""
                self.get_logger().info(f"Gripper action: {{action}}")
        '''
        )
        + _main_block(spec.class_name)
    )


def _rosbag_tools_node(spec: ProjectSpec) -> str:
    return (
        dedent(
        f'''\
        """ROS2-style rosbag management node pseudocode generated by RoboPilot.

        Task:
            {spec.task}

        This node mirrors rosbag2 record/playback/info patterns without
        requiring ROS2 or rosbag2 to be installed.
        """

        from __future__ import annotations

        from dataclasses import dataclass
        from time import strftime as time_strftime
        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        @dataclass
        class BagMetadata:
            """Metadata for a recorded rosbag."""

            path: str
            topics: list[str]
            message_count: int
            duration_seconds: float
            size_bytes: int


        class {spec.class_name}(Node):
            """ROS2-style rosbag recording and playback utility node.

            Manages bag recording, playback control, and bag info queries.
            Mirrors rosbag2 patterns for logging and replay workflows.
            """

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.output_dir = "bags/"
                self.max_bag_size_mb = 500
                self.compression_enabled = True
                self.auto_record_topics = True
                self.recording = False
                self.playing = False
                self.recorded_bags: list[BagMetadata] = []
                self.trigger_subscription = None
                self.status_publisher = None
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                self.start_recording(["/camera/image_raw", "/scan", "/odom"])
                self.get_logger().info("Recording for 3 seconds (placeholder)...")
                self.stop_recording()
                self.list_recorded_bags()
                if self.recorded_bags:
                    self.get_bag_info(self.recorded_bags[-1].path)

            def start_recording(self, topics: list[str]) -> None:
                """Start recording specified topics to a bag file."""
                self.recording = True
                timestamp = time_strftime("%Y%m%d_%H%M%S")
                bag_path = f"{{self.output_dir}}recording_{{timestamp}}"
                self.get_logger().info(
                    f"Recording {{len(topics)}} topics to {{bag_path}} "
                    f"(max size={{self.max_bag_size_mb}}MB)"
                )

            def stop_recording(self) -> None:
                """Stop the current recording session."""
                if self.recording:
                    self.recording = False
                    metadata = BagMetadata(
                        "bags/recording_20240101_120000",
                        ["/camera/image_raw", "/scan", "/odom"],
                        1500,
                        30.0,
                        5000000,
                    )
                    self.recorded_bags.append(metadata)
                    self.get_logger().info(
                        f"Recording stopped: {{metadata.message_count}} messages, "
                        f"{{metadata.duration_seconds}}s, {{metadata.size_bytes}} bytes"
                    )

            def start_playback(self, bag_path: str) -> None:
                """Start playing back a recorded bag file."""
                self.playing = True
                self.get_logger().info(f"Playing bag: {{bag_path}}")

            def stop_playback(self) -> None:
                """Stop the current playback session."""
                self.playing = False
                self.get_logger().info("Playback stopped")

            def get_bag_info(self, bag_path: str) -> BagMetadata | None:
                """Get metadata for a recorded bag file."""
                for bag in self.recorded_bags:
                    if bag.path == bag_path:
                        self.get_logger().info(
                            f"Bag info: {{bag.path}} - "
                            f"{{len(bag.topics)}} topics, "
                            f"{{bag.message_count}} messages, "
                            f"{{bag.duration_seconds}}s"
                        )
                        return bag
                self.get_logger().info(f"Bag not found: {{bag_path}}")
                return None

            def list_recorded_bags(self) -> None:
                """List all recorded bag files."""
                self.get_logger().info(
                    f"Recorded bags: {{len(self.recorded_bags)}}"
                )
                for bag in self.recorded_bags:
                    self.get_logger().info(f"  - {{bag.path}}")
        '''
        )
        + _main_block(spec.class_name)
    )


def _state_machine_node(spec: ProjectSpec) -> str:
    return (
        dedent(
        f'''\
        """ROS2-style state machine node pseudocode generated by RoboPilot.

        Task:
            {spec.task}

        This node mirrors BehaviorTree.CPP / SMACH / YASMIN orchestration
        patterns without requiring ROS2 or behavior tree libraries.
        """

        from __future__ import annotations

        from dataclasses import dataclass
        from enum import Enum
        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        class TaskStatus(Enum):
            """Status of a state machine task."""

            IDLE = "idle"
            RUNNING = "running"
            SUCCESS = "success"
            FAILURE = "failure"


        @dataclass
        class State:
            """A named state in the state machine."""

            name: str
            entry_action: str
            exit_action: str
            transitions: dict[str, str]


        class {spec.class_name}(Node):
            """ROS2-style state machine / behavior tree orchestration node.

            Manages a finite state machine (FSM) that sequences high-level
            robot tasks. Mirrors BehaviorTree.CPP and SMACH patterns.
            """

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.initial_state = "IDLE"
                self.states: dict[str, State] = {{}}
                self.current_state: str | None = None
                self.transition_timeout = 10.0
                self.auto_start = True
                self.state_publisher = None
                self.command_publisher = None
                self.result_subscription = None
                self._setup_states()
                self.get_logger().info(
                    "Initialized {spec.selected_template} template "
                    f"(initial={{self.initial_state}})"
                )

            def _setup_states(self) -> None:
                """Define the default state machine structure."""
                self.states = {{
                    "IDLE": State("IDLE", "wait_for_command", "log_idle_exit", {{
                        "start": "INIT",
                    }}),
                    "INIT": State("INIT", "initialize_sensors", "log_init_exit", {{
                        "done": "NAVIGATE",
                        "error": "ERROR",
                    }}),
                    "NAVIGATE": State("NAVIGATE", "start_navigation", "stop_navigation", {{
                        "arrived": "PERCEIVE",
                        "stuck": "RECOVER",
                    }}),
                    "PERCEIVE": State("PERCEIVE", "capture_and_detect", "log_results", {{
                        "done": "ACTUATE",
                    }}),
                    "ACTUATE": State("ACTUATE", "execute_manipulation", "retract_arm", {{
                        "done": "IDLE",
                        "failure": "ERROR",
                    }}),
                    "RECOVER": State("RECOVER", "clear_costmaps", "log_recovery", {{
                        "recovered": "NAVIGATE",
                        "failed": "ERROR",
                    }}),
                    "ERROR": State("ERROR", "log_error", "safe_stop", {{
                        "reset": "IDLE",
                    }}),
                }}

            def run_once(self) -> None:
                if self.current_state is None:
                    self.transition_to(self.initial_state)
                self.execute_current_state()
                self.transition_to("INIT")
                self.execute_current_state()
                self.transition_to("NAVIGATE")
                self.get_logger().info(
                    f"State machine running. Current state: {{self.current_state}}"
                )

            def transition_to(self, target: str) -> bool:
                """Transition to a target state if allowed."""
                if self.current_state is None:
                    self.current_state = target
                    self._on_enter(target)
                    return True
                state = self.states.get(self.current_state)
                if state is None:
                    return False
                if target in state.transitions:
                    self._on_exit(self.current_state)
                    self.current_state = target
                    self._on_enter(target)
                    self.get_logger().info(
                        f"Transition: {{state.name}} -> {{target}}"
                    )
                    return True
                self.get_logger().info(
                    f"Transition denied: {{state.name}} -/-> {{target}}"
                )
                return False

            def _on_enter(self, state_name: str) -> None:
                state = self.states.get(state_name)
                if state:
                    self.get_logger().info(
                        f"Entering '{{state_name}}': {{state.entry_action}}"
                    )

            def _on_exit(self, state_name: str) -> None:
                state = self.states.get(state_name)
                if state:
                    self.get_logger().info(
                        f"Exiting '{{state_name}}': {{state.exit_action}}"
                    )

            def execute_current_state(self) -> None:
                """Execute the action associated with the current state."""
                if self.current_state:
                    self.get_logger().info(
                        f"Executing state '{{self.current_state}}'"
                    )
        '''
        )
        + _main_block(spec.class_name)
    )


# ---------------------------------------------------------------------------
# v2.2.0 M11 new template nodes
# ---------------------------------------------------------------------------


def _depth_camera_node(spec: ProjectSpec) -> str:
    return (
        dedent(
        f'''\
        """ROS2-style depth camera driver node pseudocode generated by RoboPilot.

        Task:
            {spec.task}

        This node mirrors RGB-D sensor drivers (RealSense / Kinect) without
        requiring ROS2, actual hardware, or camera SDKs.
        """

        from __future__ import annotations

        from dataclasses import dataclass
        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        @dataclass
        class DepthFrame:
            """Simulated depth frame with per-pixel distance values."""

            width: int
            height: int
            depth_scale: float
            data: list[int]


        @dataclass
        class Point3D:
            """A single 3D point in the camera frame."""

            x: float
            y: float
            z: float


        class {spec.class_name}(Node):
            """ROS2-style RGB-D depth camera node skeleton.

            Publishes rectified depth images and registered point clouds.
            Mirrors RealSense ROS2 driver / image_pipeline patterns.
            """

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.depth_width = 640
                self.depth_height = 480
                self.depth_fps = 30
                self.depth_scale = 0.001
                self.point_cloud_enabled = True
                self.depth_publisher = None
                self.pointcloud_publisher = None
                self.camera_info_publisher = None
                self.frame_id = "camera_depth_optical_frame"
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                depth = self.capture_depth_frame()
                self.publish_depth_image(depth)
                if self.point_cloud_enabled:
                    cloud = self.depth_to_pointcloud(depth)
                    self.publish_pointcloud(cloud)

            def capture_depth_frame(self) -> DepthFrame:
                """Capture a simulated depth frame for offline testing."""
                return DepthFrame(
                    self.depth_width, self.depth_height, self.depth_scale,
                    [1500] * (self.depth_width * self.depth_height),
                )

            def publish_depth_image(self, frame: DepthFrame) -> None:
                """Publish a depth image (16-bit mono, mm values)."""
                self.get_logger().info(
                    f"Publishing depth image: {{frame.width}}x{{frame.height}}, "
                    f"scale={{frame.depth_scale}}m"
                )

            def depth_to_pointcloud(self, frame: DepthFrame) -> list[Point3D]:
                """Convert depth image to a 3D point cloud (pinhole model)."""
                cx, cy = frame.width / 2.0, frame.height / 2.0
                fx = fy = float(frame.width)
                points: list[Point3D] = []
                for i, d_mm in enumerate(frame.data):
                    z = d_mm * frame.depth_scale
                    if z <= 0:
                        continue
                    u = i % frame.width
                    v = i // frame.width
                    x = (u - cx) * z / fx
                    y = (v - cy) * z / fy
                    points.append(Point3D(x, y, z))
                self.get_logger().info(
                    f"Generated {{len(points)}} 3D points from depth frame"
                )
                return points

            def publish_pointcloud(self, points: list[Point3D]) -> None:
                """Publish a PointCloud2 message from unstructured points."""
                self.get_logger().info(
                    f"Publishing point cloud with {{len(points)}} points"
                )
        '''
        )
        + _main_block(spec.class_name)
    )


def _ackermann_drive_node(spec: ProjectSpec) -> str:
    return (
        dedent(
        f'''\
        """ROS2-style Ackermann steering controller node pseudocode generated by RoboPilot.

        Task:
            {spec.task}

        This node mirrors Ackermann drive kinematics for car-like robots
        without requiring ROS2 or real vehicle hardware.
        """

        from __future__ import annotations

        from math import atan2, hypot, tan as _tan
        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        class {spec.class_name}(Node):
            """ROS2-style Ackermann steering controller node skeleton.

            Converts Twist velocity commands to steering angle + wheel speed
            using the bicycle model / Ackermann geometry.
            """

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.wheelbase = 0.33
                self.max_steering_angle = 0.60
                self.max_speed = 2.0
                self.min_turning_radius = self.wheelbase / _tan(self.max_steering_angle)
                self.cmd_subscription = None
                self.steering_publisher = None
                self.speed_publisher = None
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                vx, wz = 0.50, 0.20
                steering, wheel_speed = self.twist_to_ackermann(vx, wz)
                self.publish_commands(steering, wheel_speed)

            def twist_to_ackermann(
                self, linear_x: float, angular_z: float,
            ) -> tuple[float, float]:
                """Convert Twist (vx, wz) to (steering_angle, wheel_speed)."""
                if abs(angular_z) < 1e-6:
                    steering = 0.0
                    wheel_speed = linear_x
                else:
                    radius = linear_x / angular_z
                    if abs(radius) < self.min_turning_radius:
                        radius = self.min_turning_radius * (1 if radius > 0 else -1)
                    steering = _tan(self.wheelbase / radius)
                    wheel_speed = angular_z * radius
                steering = max(-self.max_steering_angle, min(self.max_steering_angle, steering))
                wheel_speed = max(-self.max_speed, min(self.max_speed, wheel_speed))
                self.get_logger().info(
                    f"Twist vx={{linear_x:.2f}} wz={{angular_z:.2f}} "
                    f"-> steering={{steering:.3f}}rad speed={{wheel_speed:.2f}}m/s"
                )
                return steering, wheel_speed

            def publish_commands(self, steering: float, speed: float) -> None:
                """Publish steering angle and wheel speed commands."""
                self.get_logger().info(
                    f"Publishing steering={{steering:.3f}}rad speed={{speed:.2f}}m/s"
                )
        '''
        )
        + _main_block(spec.class_name)
    )


def _teleop_node(spec: ProjectSpec) -> str:
    return (
        dedent(
        f'''\
        """ROS2-style teleoperation node pseudocode generated by RoboPilot.

        Task:
            {spec.task}

        This node mirrors teleop_twist_joy / teleop_twist_keyboard patterns
        without requiring ROS2, a joystick, or real hardware.
        """

        from __future__ import annotations

        from dataclasses import dataclass
        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        @dataclass
        class JoyState:
            """Simulated joystick/gamepad state."""

            axes: list[float]
            buttons: list[int]


        class {spec.class_name}(Node):
            """ROS2-style teleoperation node skeleton.

            Subscribes to joystick input, publishes Twist velocity commands.
            Supports configurable axis mapping and speed scaling.
            Mirrors teleop_twist_joy patterns.
            """

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.linear_scale = 0.50
                self.angular_scale = 1.00
                self.linear_axis = 1
                self.angular_axis = 2
                self.enable_button = 0
                self.deadman_button = 4
                self.enabled = True
                self.joy_subscription = None
                self.cmd_publisher = None
                self.last_joy: JoyState | None = None
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                joy = JoyState([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [1, 0, 0, 0, 0, 0, 0, 0])
                twist = self.joy_to_twist(joy)
                if self.enabled:
                    self.publish_cmd_vel(twist)

            def joy_to_twist(self, joy: JoyState) -> tuple[float, float]:
                """Map joystick axes to linear and angular velocity."""
                linear = 0.0
                angular = 0.0
                if len(joy.axes) > self.linear_axis:
                    linear = -joy.axes[self.linear_axis] * self.linear_scale
                if len(joy.axes) > self.angular_axis:
                    angular = joy.axes[self.angular_axis] * self.angular_scale
                dead_zone = 0.05
                if abs(linear) < dead_zone:
                    linear = 0.0
                if abs(angular) < dead_zone:
                    angular = 0.0
                return linear, angular

            def publish_cmd_vel(self, twist: tuple[float, float]) -> None:
                """Publish Twist velocity command."""
                self.get_logger().info(
                    f"cmd_vel: linear={{twist[0]:.2f}} angular={{twist[1]:.2f}}"
                )

            def set_enabled(self, state: bool) -> None:
                """Enable or disable teleop output."""
                self.enabled = state
                self.get_logger().info(f"Teleop {{'enabled' if state else 'disabled'}}")
        '''
        )
        + _main_block(spec.class_name)
    )


def _diagnostic_aggregator_node(spec: ProjectSpec) -> str:
    return (
        dedent(
        f'''\
        """ROS2-style diagnostic aggregator node pseudocode generated by RoboPilot.

        Task:
            {spec.task}

        This node mirrors diagnostic_aggregator / hardware status monitoring
        patterns without requiring ROS2 or real hardware drivers.
        """

        from __future__ import annotations

        from dataclasses import dataclass
        from enum import Enum
        from typing import Any


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        class DiagnosticLevel(Enum):
            """ROS diagnostic status levels."""

            OK = 0
            WARN = 1
            ERROR = 2
            STALE = 3


        @dataclass
        class DiagnosticStatus:
            """A single diagnostic item from a hardware driver or node."""

            name: str
            hardware_id: str
            level: int
            message: str
            values: list[dict[str, Any]]


        class {spec.class_name}(Node):
            """ROS2-style diagnostic aggregation node skeleton.

            Subscribes to raw diagnostics from all nodes/drivers, analyzes
            them against configured rules, and publishes an aggregated summary.
            Mirrors diagnostic_aggregator patterns.
            """

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.warning_timeout = 5.0
                self.error_timeout = 10.0
                self.aggregation_period = 1.0
                self.diag_subscription = None
                self.agg_publisher = None
                self.status_history: dict[str, list[DiagnosticStatus]] = {{}}
                self.analysis_rules: list[str] = [
                    "motor_temp_high",
                    "battery_low",
                    "sensor_timeout",
                    "cpu_usage_high",
                ]
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                statuses = self.simulate_diagnostics()
                aggregated = self.analyze(statuses)
                self.status_history["latest"] = aggregated
                self.publish_aggregated(aggregated)

            def simulate_diagnostics(self) -> list[DiagnosticStatus]:
                """Generate simulated diagnostic data for offline testing."""
                return [
                    DiagnosticStatus("motor_driver", "motor_1", DiagnosticLevel.OK.value,
                                     "Motor operating normally", []),
                    DiagnosticStatus("battery_monitor", "battery_1", DiagnosticLevel.WARN.value,
                                     "Battery at 25%", [{{"key": "voltage", "value": "11.2V"}}]),
                    DiagnosticStatus("lidar_sensor", "lidar_1", DiagnosticLevel.OK.value,
                                     "Lidar scanning at 10Hz", []),
                    DiagnosticStatus("cpu_monitor", "cpu_0", DiagnosticLevel.WARN.value,
                                     "CPU usage at 87%", [{{"key": "usage", "value": "87%"}}]),
                ]

            def analyze(
                self, statuses: list[DiagnosticStatus],
            ) -> list[DiagnosticStatus]:
                """Analyze and filter diagnostic statuses against rules."""
                errors = [s for s in statuses if s.level == DiagnosticLevel.ERROR.value]
                warns = [s for s in statuses if s.level == DiagnosticLevel.WARN.value]
                self.get_logger().info(
                    f"Diagnostics: {{len(statuses)}} total, "
                    f"{{len(errors)}} errors, {{len(warns)}} warnings"
                )
                for s in statuses:
                    self.get_logger().info(
                        f"  [{{'OK' if s.level == 0 else 'WARN' if s.level == 1 else 'ERROR'}}] "
                        f"{{s.name}}: {{s.message}}"
                    )
                return statuses

            def publish_aggregated(self, aggregated: list[DiagnosticStatus]) -> None:
                """Publish the aggregated diagnostic summary."""
                self.get_logger().info(
                    f"Publishing aggregated diagnostics: {{len(aggregated)}} items"
                )

            def get_summary(self) -> dict[str, int]:
                """Return a count summary by diagnostic level."""
                latest = self.status_history.get("latest", [])
                return {{
                    "ok": sum(1 for s in latest if s.level == DiagnosticLevel.OK.value),
                    "warn": sum(1 for s in latest if s.level == DiagnosticLevel.WARN.value),
                    "error": sum(1 for s in latest if s.level == DiagnosticLevel.ERROR.value),
                }}
        '''
        )
        + _main_block(spec.class_name)
    )


def _generic_node(spec: ProjectSpec) -> str:
    return (
        dedent(
        f'''\
        """Generic ROS2-style node pseudocode generated by RoboPilot.

        Task:
            {spec.task}
        """

        from __future__ import annotations


        '''
        )
        + _fallback_node_block()
        + "\n\n"
        + dedent(
            f'''\
        class {spec.class_name}(Node):
            """Generic ROS2-style node skeleton."""

            def __init__(self) -> None:
                super().__init__("{spec.node_name}")
                self.get_logger().info("Initialized {spec.selected_template} template.")

            def run_once(self) -> None:
                self.get_logger().info("Run one offline placeholder step.")
        '''
        )
        + _main_block(spec.class_name)
    )


# ---------------------------------------------------------------------------
# Parameter YAML renderers
# ---------------------------------------------------------------------------


def _camera_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          input_image_topic: /camera/image_raw
          queue_size: 10
          log_every_n_frames: 30
    """


def _object_detection_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          input_image_topic: /camera/image_raw
          output_boxes_topic: /detections/bounding_boxes
          confidence_threshold: 0.50
          publish_debug_image: false
    """


def _velocity_controller_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          cmd_vel_topic: /cmd_vel
          linear_velocity: 0.20
          angular_velocity: 0.00
          publish_rate_hz: 10
    """


def _perception_pipeline_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          input_image_topic: /camera/image_raw
          detections_topic: /detections/bounding_boxes
          tracks_topic: /tracks
          enable_tracking: true
    """


def _slam_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          map_resolution: 0.05
          map_update_interval: 1.0
          max_laser_range: 12.0
          map_frame_id: "map"
          base_frame_id: "base_link"
          odom_frame_id: "odom"
    """


def _navigation_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          max_linear_speed: 0.50
          max_angular_speed: 1.00
          goal_tolerance: 0.10
          planner_type: "navfn"
          controller_type: "dwb"
          obstacle_check_distance: 2.0
    """


def _sensor_fusion_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          use_imu: true
          use_gps: true
          use_odom: true
          filter_type: "ekf"
          publish_rate: 50.0
          sensor_timeout: 0.10
          two_d_mode: true
    """


def _image_processing_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          processing_mode: "canny"
          blur_kernel: 5
          canny_threshold_low: 50
          canny_threshold_high: 150
          hsv_lower: [0, 50, 50]
          hsv_upper: [10, 255, 255]
    """


def _robot_arm_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          num_joints: 6
          joint_names:
            - joint_1
            - joint_2
            - joint_3
            - joint_4
            - joint_5
            - joint_6
          home_position: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
          gripper_enabled: true
          max_velocity_scaling: 0.50
    """


def _rosbag_tools_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          output_dir: "bags/"
          max_bag_size_mb: 500
          compression_enabled: true
          auto_record_topics: true
          storage_format: "mcap"
    """


def _state_machine_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          initial_state: "IDLE"
          states:
            - IDLE
            - INIT
            - NAVIGATE
            - PERCEIVE
            - ACTUATE
            - RECOVER
            - ERROR
          transition_timeout: 10.0
          auto_start: true
    """


def _depth_camera_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          depth_width: 640
          depth_height: 480
          depth_fps: 30
          depth_scale: 0.001
          point_cloud_enabled: true
          color_width: 640
          color_height: 480
          color_fps: 30
          enable_color: true
    """


def _ackermann_drive_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          wheelbase: 0.33
          max_steering_angle: 0.60
          max_speed: 2.0
          steering_control_gain: 1.0
          speed_control_gain: 1.0
          use_speed_control: true
    """


def _teleop_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          linear_scale: 0.50
          angular_scale: 1.00
          linear_axis: 1
          angular_axis: 2
          enable_button: 0
          deadman_button: 4
          require_deadman: true
          publish_rate: 20.0
    """


def _diagnostic_aggregator_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          warning_timeout: 5.0
          error_timeout: 10.0
          aggregation_period: 1.0
          analysis_rules:
            - motor_temp_high
            - battery_low
            - sensor_timeout
            - cpu_usage_high
          publish_summary: true
    """


def _generic_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          enabled: true
          update_rate_hz: 10
    """


# ---------------------------------------------------------------------------
# Topic helpers
# ---------------------------------------------------------------------------


def _find_topic(
    topics: tuple["TopicSpec", ...],
    direction: str,
) -> "TopicSpec | None":
    """Return the first topic matching the given direction."""
    for t in topics:
        if t.direction == direction:
            return t
    return None


def _find_topic_by_name(
    topics: tuple["TopicSpec", ...],
    name: str,
) -> "str | None":
    """Return the topic name if it exists in the topic list, else None."""
    for t in topics:
        if t.name == name:
            return t.name
    return None


def _topic(direction: str, name: str, message_type: str) -> "TopicSpec":
    # Import here to avoid circular imports at module scope.
    from robopilot.generator.project_spec import TopicSpec

    return TopicSpec(name, direction, message_type, "")
