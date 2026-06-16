"""Registry of offline generator template definitions."""

from __future__ import annotations

from dataclasses import dataclass

from robopilot.generator.project_spec import NodeSpec, ProjectSpec, TopicSpec
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
    topics: tuple[TopicSpec, ...]
    notes: tuple[str, ...]


TEMPLATE_REGISTRY: dict[str, TemplateDefinition] = {
    # --- v2.0.0 existing templates ---
    CAMERA_SUBSCRIBER: TemplateDefinition(
        template_type=CAMERA_SUBSCRIBER,
        node_file_name="camera_node.py",
        executable_name="camera_node",
        node_name="camera_subscriber_node",
        class_name="CameraSubscriberNode",
        description="ROS-style camera subscriber node skeleton.",
        topics=(
            TopicSpec(
                name="/camera/image_raw",
                direction="subscribe",
                message_type="sensor_msgs/Image",
                description="Input camera image stream.",
            ),
        ),
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
        topics=(
            TopicSpec(
                name="/camera/image_raw",
                direction="subscribe",
                message_type="sensor_msgs/Image",
                description="Input image stream for detection.",
            ),
            TopicSpec(
                name="/detections/bounding_boxes",
                direction="publish",
                message_type="std_msgs/String",
                description="Placeholder bounding box detections.",
            ),
        ),
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
        topics=(
            TopicSpec(
                name="/cmd_vel",
                direction="publish",
                message_type="geometry_msgs/Twist",
                description="Velocity command output.",
            ),
        ),
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
        topics=(
            TopicSpec(
                name="/camera/image_raw",
                direction="subscribe",
                message_type="sensor_msgs/Image",
                description="Input camera stream.",
            ),
            TopicSpec(
                name="/detections/bounding_boxes",
                direction="publish",
                message_type="std_msgs/String",
                description="Intermediate detector output.",
            ),
            TopicSpec(
                name="/tracks",
                direction="publish",
                message_type="std_msgs/String",
                description="Placeholder tracking output.",
            ),
        ),
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
        topics=(),
        notes=(
            "Fallback template for tasks that do not match a specific rule.",
            "Keeps the generated project useful without guessing hardware behavior.",
        ),
    ),
    # --- v2.1.0 new templates ---
    SLAM: TemplateDefinition(
        template_type=SLAM,
        node_file_name="slam_node.py",
        executable_name="slam_node",
        node_name="slam_node",
        class_name="SlamNode",
        description="ROS-style SLAM mapping node skeleton.",
        topics=(
            TopicSpec(
                name="/scan",
                direction="subscribe",
                message_type="sensor_msgs/LaserScan",
                description="LiDAR laser scan input for map building.",
            ),
            TopicSpec(
                name="/map",
                direction="publish",
                message_type="nav_msgs/OccupancyGrid",
                description="Generated occupancy grid map.",
            ),
            TopicSpec(
                name="/map_metadata",
                direction="publish",
                message_type="nav_msgs/MapMetaData",
                description="Map metadata including resolution and origin.",
            ),
        ),
        notes=(
            "Mirrors slam_toolbox / gmapping node structure in pseudocode.",
            "Designed for SLAM, mapping, gmapping, and cartographer tasks.",
        ),
    ),
    NAVIGATION: TemplateDefinition(
        template_type=NAVIGATION,
        node_file_name="navigator_node.py",
        executable_name="navigator_node",
        node_name="navigator_node",
        class_name="NavigatorNode",
        description="ROS-style autonomous navigation node skeleton.",
        topics=(
            TopicSpec(
                name="/odom",
                direction="subscribe",
                message_type="nav_msgs/Odometry",
                description="Robot odometry for localization.",
            ),
            TopicSpec(
                name="/goal_pose",
                direction="subscribe",
                message_type="geometry_msgs/PoseStamped",
                description="Target navigation goal pose.",
            ),
            TopicSpec(
                name="/cmd_vel",
                direction="publish",
                message_type="geometry_msgs/Twist",
                description="Velocity commands to the robot base.",
            ),
            TopicSpec(
                name="/plan",
                direction="publish",
                message_type="nav_msgs/Path",
                description="Planned path from current pose to goal.",
            ),
        ),
        notes=(
            "Mirrors Nav2 planner/controller structure in pseudocode.",
            "Designed for navigation, nav2, path planning, and waypoint tasks.",
        ),
    ),
    SENSOR_FUSION: TemplateDefinition(
        template_type=SENSOR_FUSION,
        node_file_name="fusion_node.py",
        executable_name="fusion_node",
        node_name="fusion_node",
        class_name="FusionNode",
        description="ROS-style sensor fusion node skeleton (EKF/UKF).",
        topics=(
            TopicSpec(
                name="/imu/data",
                direction="subscribe",
                message_type="sensor_msgs/Imu",
                description="IMU sensor data for orientation estimation.",
            ),
            TopicSpec(
                name="/gps/fix",
                direction="subscribe",
                message_type="sensor_msgs/NavSatFix",
                description="GPS position data for global localization.",
            ),
            TopicSpec(
                name="/odom",
                direction="subscribe",
                message_type="nav_msgs/Odometry",
                description="Wheel odometry input for fusion.",
            ),
            TopicSpec(
                name="/filtered_odom",
                direction="publish",
                message_type="nav_msgs/Odometry",
                description="Fused and filtered odometry output.",
            ),
        ),
        notes=(
            "Mirrors robot_localization EKF/UKF node structure in pseudocode.",
            "Designed for sensor fusion, EKF, Kalman filter, IMU+GPS tasks.",
        ),
    ),
    IMAGE_PROCESSING: TemplateDefinition(
        template_type=IMAGE_PROCESSING,
        node_file_name="image_processor_node.py",
        executable_name="image_processor_node",
        node_name="image_processor_node",
        class_name="ImageProcessorNode",
        description="ROS-style image processing pipeline node skeleton.",
        topics=(
            TopicSpec(
                name="/camera/image_raw",
                direction="subscribe",
                message_type="sensor_msgs/Image",
                description="Raw camera image input.",
            ),
            TopicSpec(
                name="/processed/image",
                direction="publish",
                message_type="sensor_msgs/Image",
                description="Processed image output (filtered, edge, etc.).",
            ),
        ),
        notes=(
            "Mirrors OpenCV + cv_bridge processing patterns in pseudocode.",
            "Designed for image processing, OpenCV, edge detection, and vision filter tasks.",
        ),
    ),
    ROBOT_ARM: TemplateDefinition(
        template_type=ROBOT_ARM,
        node_file_name="arm_controller_node.py",
        executable_name="arm_controller_node",
        node_name="arm_controller_node",
        class_name="ArmControllerNode",
        description="ROS-style robot arm / manipulator control node skeleton.",
        topics=(
            TopicSpec(
                name="/joint_states",
                direction="subscribe",
                message_type="sensor_msgs/JointState",
                description="Current joint positions, velocities, and efforts.",
            ),
            TopicSpec(
                name="/joint_commands",
                direction="publish",
                message_type="trajectory_msgs/JointTrajectory",
                description="Joint trajectory commands for arm motion.",
            ),
        ),
        notes=(
            "Mirrors ros2_control / MoveIt2 joint trajectory patterns in pseudocode.",
            "Designed for robot arm, manipulator, joint control, and pick-and-place tasks.",
        ),
    ),
    ROSBAG_TOOLS: TemplateDefinition(
        template_type=ROSBAG_TOOLS,
        node_file_name="bag_manager_node.py",
        executable_name="bag_manager_node",
        node_name="bag_manager_node",
        class_name="BagManagerNode",
        description="ROS-style rosbag recording and playback utility node skeleton.",
        topics=(
            TopicSpec(
                name="/record_trigger",
                direction="subscribe",
                message_type="std_msgs/String",
                description="Trigger signal to start/stop recording.",
            ),
            TopicSpec(
                name="/bag_status",
                direction="publish",
                message_type="std_msgs/String",
                description="Status updates for bag recording/playback.",
            ),
        ),
        notes=(
            "Mirrors rosbag2 / rosbag recorder and player patterns in pseudocode.",
            "Designed for rosbag, data logging, and replay tasks.",
        ),
    ),
    STATE_MACHINE: TemplateDefinition(
        template_type=STATE_MACHINE,
        node_file_name="state_machine_node.py",
        executable_name="state_machine_node",
        node_name="state_machine_node",
        class_name="StateMachineNode",
        description="ROS-style state machine / behavior tree orchestration node skeleton.",
        topics=(
            TopicSpec(
                name="/state",
                direction="publish",
                message_type="std_msgs/String",
                description="Current state machine state.",
            ),
            TopicSpec(
                name="/task_command",
                direction="publish",
                message_type="std_msgs/String",
                description="Task command sent to subordinate nodes.",
            ),
            TopicSpec(
                name="/task_result",
                direction="subscribe",
                message_type="std_msgs/String",
                description="Task result received from subordinate nodes.",
            ),
        ),
        notes=(
            "Mirrors BehaviorTree.CPP / SMACH / YASMIN orchestration patterns in pseudocode.",
            "Designed for state machine, behavior tree, mission control, and workflow tasks.",
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
    node = NodeSpec(
        name=template.node_name,
        executable=template.executable_name,
        module=template.node_file_name.removesuffix(".py"),
        class_name=template.class_name,
        file_name=template.node_file_name,
        description=template.description,
    )
    return ProjectSpec(
        package_name=package_name,
        task=task,
        selected_template=template.template_type,
        nodes=(node,),
        topics=template.topics,
        config_files=("config/params.yaml",),
        launch_files=(f"launch/{package_name}.launch.py",),
        generated_by="RoboPilot",
        notes=template.notes,
    )
