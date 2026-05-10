"""Registry of offline generator template definitions."""

from __future__ import annotations

from dataclasses import dataclass

from robopilot.generator.project_spec import ProjectSpec
from robopilot.generator.task_classifier import (
    CAMERA_SUBSCRIBER,
    GENERIC_NODE,
    OBJECT_DETECTION,
    PERCEPTION_PIPELINE,
    VELOCITY_CONTROLLER,
)


@dataclass(frozen=True)
class TemplateDefinition:
    """Static metadata for one generator template."""

    template_type: str
    node_file_name: str
    executable_name: str
    node_name: str
    class_name: str
    description: str
    notes: tuple[str, ...]


TEMPLATE_REGISTRY: dict[str, TemplateDefinition] = {
    CAMERA_SUBSCRIBER: TemplateDefinition(
        template_type=CAMERA_SUBSCRIBER,
        node_file_name="camera_node.py",
        executable_name="camera_node",
        node_name="camera_subscriber_node",
        class_name="CameraSubscriberNode",
        description="ROS-style camera subscriber node skeleton.",
        notes=(
            "Subscribes to an image-like topic in ROS2-style pseudocode.",
            "Designed for camera, webcam, video, and frame-processing tasks.",
        ),
    ),
    OBJECT_DETECTION: TemplateDefinition(
        template_type=OBJECT_DETECTION,
        node_file_name="detector_node.py",
        executable_name="detector_node",
        node_name="detector_node",
        class_name="DetectorNode",
        description="ROS-style object detection node skeleton.",
        notes=(
            "Uses placeholder bounding box data for offline inspection.",
            "Designed for detect, object, YOLO, bbox, and bounding box tasks.",
        ),
    ),
    VELOCITY_CONTROLLER: TemplateDefinition(
        template_type=VELOCITY_CONTROLLER,
        node_file_name="velocity_controller_node.py",
        executable_name="velocity_controller_node",
        node_name="velocity_controller_node",
        class_name="VelocityControllerNode",
        description="ROS-style velocity controller node skeleton.",
        notes=(
            "Shows cmd_vel-style command publishing in offline pseudocode.",
            "Designed for velocity, controller, control, and motion tasks.",
        ),
    ),
    PERCEPTION_PIPELINE: TemplateDefinition(
        template_type=PERCEPTION_PIPELINE,
        node_file_name="perception_pipeline_node.py",
        executable_name="perception_pipeline_node",
        node_name="perception_pipeline_node",
        class_name="PerceptionPipelineNode",
        description="ROS-style perception pipeline node skeleton.",
        notes=(
            "Represents camera-to-detector-to-tracker workflow stages.",
            "Designed for pipeline, tracker, tracking, and perception workflow tasks.",
        ),
    ),
    GENERIC_NODE: TemplateDefinition(
        template_type=GENERIC_NODE,
        node_file_name="generic_node.py",
        executable_name="generic_node",
        node_name="generic_node",
        class_name="GenericNode",
        description="Generic ROS-style Python node skeleton.",
        notes=(
            "Fallback template for tasks that do not match a specific rule.",
            "Keeps the generated project useful without guessing hardware behavior.",
        ),
    ),
}


def get_template_definition(template_type: str) -> TemplateDefinition:
    """Return template metadata, falling back to the generic template."""
    return TEMPLATE_REGISTRY.get(template_type, TEMPLATE_REGISTRY[GENERIC_NODE])


def build_project_spec(
    *,
    package_name: str,
    task: str,
    selected_template: str,
) -> ProjectSpec:
    """Build a concrete project specification from a selected template."""
    template = get_template_definition(selected_template)
    return ProjectSpec(
        package_name=package_name,
        task=task,
        selected_template=template.template_type,
        node_file_name=template.node_file_name,
        executable_name=template.executable_name,
        node_name=template.node_name,
        class_name=template.class_name,
        description=template.description,
        notes=template.notes,
    )

