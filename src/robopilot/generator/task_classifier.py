"""Offline rule-based task classifier for package generation."""

from __future__ import annotations


CAMERA_SUBSCRIBER = "camera_subscriber"
OBJECT_DETECTION = "object_detection"
VELOCITY_CONTROLLER = "velocity_controller"
PERCEPTION_PIPELINE = "perception_pipeline"
GENERIC_NODE = "generic_node"

# v2.1.0 new templates
SLAM = "slam"
NAVIGATION = "navigation"
SENSOR_FUSION = "sensor_fusion"
IMAGE_PROCESSING = "image_processing"
ROBOT_ARM = "robot_arm"
ROSBAG_TOOLS = "rosbag_tools"
STATE_MACHINE = "state_machine"


def classify_task(task: str) -> str:
    """Classify a natural language task into a generator template type."""
    normalized = _normalize(task)
    if not normalized:
        return GENERIC_NODE

    # Check from most specific patterns to most generic.

    if _contains_any(
        normalized,
        (
            "state machine", "behavior tree", "finite state", "fsm",
            "mission control", "task orchestration", "sequence controller",
            "workflow engine",
        ),
    ):
        return STATE_MACHINE

    if _contains_any(
        normalized,
        (
            "rosbag", "bag record", "bag play", "data logging",
            "log recorder", "replay data", "record topics",
            "ros2 bag",
        ),
    ):
        return ROSBAG_TOOLS

    if _contains_any(
        normalized,
        (
            "slam", "gmapping", "cartographer", "mapping",
            "map building", "localization and mapping",
            "simultaneous localization",
        ),
    ):
        return SLAM

    if _contains_any(
        normalized,
        (
            "robot arm", "manipulator", "joint control", "gripper",
            "pick and place", "moveit", "kinematics",
            "inverse kinematics", "joint trajectory", "arm controller",
        ),
    ):
        return ROBOT_ARM

    if _contains_any(
        normalized,
        (
            "sensor fusion", "ekf", "kalman", "imu gps",
            "multi sensor", "localization filter",
            "robot_localization", "fuse sensor",
        ),
    ):
        return SENSOR_FUSION

    if _contains_any(
        normalized,
        (
            "image processing", "opencv", "edge detection",
            "color detection", "blob", "image filter",
            "canny", "hsv", "threshold", "morphological",
            "image pipeline",
        ),
    ):
        return IMAGE_PROCESSING

    if _contains_any(
        normalized,
        (
            "navigation", "nav2", "path planning", "waypoint",
            "autonomous navigation", "move to goal", "explore",
            "planner controller", "obstacle avoidance",
            "costmap", "path follower",
        ),
    ):
        return NAVIGATION

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
