"""Offline rule-based task classifier for package generation."""

from __future__ import annotations


CAMERA_SUBSCRIBER = "camera_subscriber"
OBJECT_DETECTION = "object_detection"
VELOCITY_CONTROLLER = "velocity_controller"
PERCEPTION_PIPELINE = "perception_pipeline"
GENERIC_NODE = "generic_node"


def classify_task(task: str) -> str:
    """Classify a natural language task into a generator template type."""
    normalized = _normalize(task)
    if not normalized:
        return GENERIC_NODE

    if _contains_any(
        normalized,
        (
            "pipeline",
            "tracker",
            "tracking",
            "camera -> detector",
            "perception workflow",
        ),
    ):
        return PERCEPTION_PIPELINE

    if _contains_any(
        normalized,
        ("detect", "detection", "object", "yolo", "bbox", "bounding box"),
    ):
        return OBJECT_DETECTION

    if _contains_any(
        normalized,
        ("cmd_vel", "velocity", "controller", "control", "motion"),
    ):
        return VELOCITY_CONTROLLER

    if _contains_any(normalized, ("camera", "image", "frame", "webcam", "video")):
        return CAMERA_SUBSCRIBER

    return GENERIC_NODE


def _normalize(task: str) -> str:
    return " ".join(task.lower().replace("-", " ").split())


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)

