from robopilot.generator.task_classifier import (
    CAMERA_SUBSCRIBER,
    GENERIC_NODE,
    OBJECT_DETECTION,
    PERCEPTION_PIPELINE,
    VELOCITY_CONTROLLER,
    classify_task,
)


def test_classifies_object_detection_task() -> None:
    assert classify_task("Create a YOLO object detection node with bbox output") == (
        OBJECT_DETECTION
    )


def test_classifies_camera_subscriber_task() -> None:
    assert classify_task("Subscribe to a webcam frame stream") == CAMERA_SUBSCRIBER


def test_classifies_velocity_controller_task() -> None:
    assert classify_task("Publish cmd_vel velocity commands for robot motion") == (
        VELOCITY_CONTROLLER
    )


def test_classifies_perception_pipeline_task() -> None:
    assert classify_task("camera -> detector -> tracker perception workflow") == (
        PERCEPTION_PIPELINE
    )


def test_classifies_unknown_task_as_generic() -> None:
    assert classify_task("Make a simple heartbeat node") == GENERIC_NODE

