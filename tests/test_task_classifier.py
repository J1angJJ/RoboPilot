from robopilot.generator.task_classifier import (
    CAMERA_SUBSCRIBER,
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
    VELOCITY_CONTROLLER,
    classify_task,
)


# v2.0.0 existing
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


# v2.1.0 new
def test_classifies_slam_task() -> None:
    assert classify_task("Create a SLAM mapping node for lidar data") == SLAM
    assert classify_task("Build a gmapping-based map for the lab") == SLAM
    assert classify_task("Simultaneous localization and mapping with cartographer") == SLAM


def test_classifies_navigation_task() -> None:
    assert classify_task("Add autonomous navigation with path planning") == NAVIGATION
    assert classify_task("Use Nav2 for waypoint following") == NAVIGATION
    assert classify_task("Implement obstacle avoidance and costmap-based planner") == NAVIGATION


def test_classifies_sensor_fusion_task() -> None:
    assert classify_task("Fuse IMU and GPS data with an EKF filter") == SENSOR_FUSION
    assert classify_task("Apply Kalman filter for multi-sensor localization") == SENSOR_FUSION
    assert classify_task("Use robot_localization for sensor fusion") == SENSOR_FUSION


def test_classifies_image_processing_task() -> None:
    assert classify_task("Process camera images with edge detection and color filtering") == IMAGE_PROCESSING
    assert classify_task("Apply OpenCV Canny and HSV threshold on input frames") == IMAGE_PROCESSING
    assert classify_task("Build an image processing pipeline with morphological filters") == IMAGE_PROCESSING


def test_classifies_robot_arm_task() -> None:
    assert classify_task("Control a 6-DOF robot arm with joint trajectory commands") == ROBOT_ARM
    assert classify_task("Implement pick and place with MoveIt and inverse kinematics") == ROBOT_ARM
    assert classify_task("Create a manipulator controller with gripper support") == ROBOT_ARM


def test_classifies_rosbag_tools_task() -> None:
    assert classify_task("Record and replay rosbag data for offline analysis") == ROSBAG_TOOLS
    assert classify_task("Set up data logging with ros2 bag record") == ROSBAG_TOOLS
    assert classify_task("Create a bag recorder for sensor data") == ROSBAG_TOOLS


def test_classifies_state_machine_task() -> None:
    assert classify_task("Build a finite state machine for mission control") == STATE_MACHINE
    assert classify_task("Create a behavior tree for task orchestration") == STATE_MACHINE
    assert classify_task("Implement an FSM-based workflow engine") == STATE_MACHINE


def test_state_machine_before_navigation() -> None:
    """state_machine keywords should match before navigation/generic patterns."""
    assert classify_task("State machine for robot mission") == STATE_MACHINE
    assert classify_task("FSM for task orchestration") == STATE_MACHINE


def test_slam_before_navigation() -> None:
    """SLAM with 'mapping' keyword should not be misclassified as navigation."""
    assert classify_task("Create a SLAM node for mapping") == SLAM

