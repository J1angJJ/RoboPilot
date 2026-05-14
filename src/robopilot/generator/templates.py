"""Template rendering for offline ROS-style package generation."""

from __future__ import annotations

from textwrap import dedent

from robopilot.generator.project_spec import ProjectSpec
from robopilot.generator.task_classifier import (
    CAMERA_SUBSCRIBER,
    GENERIC_NODE,
    OBJECT_DETECTION,
    PERCEPTION_PIPELINE,
    VELOCITY_CONTROLLER,
)
from robopilot.spec.io import spec_to_yaml


def package_xml(spec: ProjectSpec) -> str:
    """Render a ROS-style package.xml file."""
    return dedent(
        f"""\
        <?xml version="1.0"?>
        <package format="3">
          <name>{spec.package_name}</name>
    <version>2.0.0</version>
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
    return dedent(
        f"""\
        from setuptools import find_packages, setup


        package_name = "{spec.package_name}"

        setup(
            name=package_name,
    version="2.0.0",
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
        GENERIC_NODE: _generic_params,
    }.get(spec.selected_template, _generic_params)(spec)
    return dedent(body)


def robopilot_yaml(spec: ProjectSpec) -> str:
    """Render RoboPilot generation metadata."""
    return spec_to_yaml(spec)


def node_file(spec: ProjectSpec) -> str:
    """Render the selected ROS-style Python node pseudocode file."""
    if spec.selected_template == OBJECT_DETECTION:
        return _object_detection_node(spec)
    if spec.selected_template == CAMERA_SUBSCRIBER:
        return _camera_subscriber_node(spec)
    if spec.selected_template == VELOCITY_CONTROLLER:
        return _velocity_controller_node(spec)
    if spec.selected_template == PERCEPTION_PIPELINE:
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


def _main_block(class_name: str) -> str:
    return dedent(
        f'''\


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


def _object_detection_node(spec: ProjectSpec) -> str:
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
                self.input_image_topic = "/camera/image_raw"
                self.output_boxes_topic = "/detections/bounding_boxes"
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
                self.input_image_topic = "/camera/image_raw"
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
                self.cmd_vel_topic = "/cmd_vel"
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


def _generic_params(spec: ProjectSpec) -> str:
    return f"""\
    {spec.package_name}:
      {spec.node_name}:
        ros__parameters:
          enabled: true
          update_rate_hz: 10
    """
