from pathlib import Path

import pytest

from robopilot.generator.project_generator import (
    expected_project_files,
    generate_project,
    generate_project_from_spec,
)
from robopilot.generator.project_spec import ProjectSpec, TopicSpec
from robopilot.generator.task_classifier import (
    IMAGE_PROCESSING,
    NAVIGATION,
    OBJECT_DETECTION,
    ROBOT_ARM,
    ROSBAG_TOOLS,
    SENSOR_FUSION,
    SLAM,
    STATE_MACHINE,
)
from robopilot.generator.template_registry import build_project_spec
from robopilot.spec.io import load_spec, spec_to_yaml, write_spec
from robopilot.spec.validator import validate_spec
from robopilot.utils.file_ops import OutputPathExistsError


TASK = (
    "Create an object detection node subscribing to camera images and publishing "
    "bounding boxes."
)


def test_generator_creates_all_expected_files(tmp_path: Path) -> None:
    project = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    expected_files = expected_project_files("demo_detector")
    assert project.output_dir == tmp_path / "demo_detector"
    assert project.selected_template == OBJECT_DETECTION

    for relative_path in expected_files:
        assert (project.output_dir / relative_path).is_file()

    detector_node = project.output_dir / "demo_detector" / "detector_node.py"
    content = detector_node.read_text(encoding="utf-8")
    assert "class DetectorNode" in content
    assert "rclpy" in content
    assert TASK in content
    compile(content, str(detector_node), "exec")


def test_generator_writes_robopilot_metadata(tmp_path: Path) -> None:
    project = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    metadata = project.output_dir / "robopilot.yaml"
    content = metadata.read_text(encoding="utf-8")
    assert metadata.is_file()
    assert "package_name: demo_detector" in content
    assert "selected_template: object_detection" in content
    assert "generated_by: RoboPilot" in content
    assert "nodes:" in content
    assert "topics:" in content
    assert "  - \"Uses placeholder bounding box data" in content


def test_generator_does_not_overwrite_existing_directory_by_default(
    tmp_path: Path,
) -> None:
    existing_project = tmp_path / "demo_detector"
    existing_project.mkdir()
    marker = existing_project / "keep.txt"
    marker.write_text("do not overwrite", encoding="utf-8")

    with pytest.raises(OutputPathExistsError):
        generate_project(
            name="demo_detector",
            task=TASK,
            output_root=tmp_path,
        )

    assert marker.read_text(encoding="utf-8") == "do not overwrite"


# ---------------------------------------------------------------------------
# v2.1.0 new template generation tests
# ---------------------------------------------------------------------------

NEW_TEMPLATE_TASKS = [
    (SLAM, "my_slam", "Create a SLAM mapping node for lidar data"),
    (NAVIGATION, "my_nav", "Add autonomous navigation with path planning"),
    (SENSOR_FUSION, "my_fusion", "Fuse IMU and GPS data with an EKF filter"),
    (IMAGE_PROCESSING, "my_img", "Process camera images with edge detection and color filtering"),
    (ROBOT_ARM, "my_arm", "Control a 6-DOF robot arm with joint trajectory commands"),
    (ROSBAG_TOOLS, "my_bag", "Record and replay rosbag data for offline analysis"),
    (STATE_MACHINE, "my_fsm", "Build a finite state machine for mission control"),
]


@pytest.mark.parametrize("template_type,package_name,task", NEW_TEMPLATE_TASKS)
def test_new_template_spec_builds_correctly(
    template_type: str, package_name: str, task: str
) -> None:
    """Each new template should produce a valid, non-empty ProjectSpec."""
    spec = build_project_spec(
        package_name=package_name,
        task=task,
        selected_template=template_type,
    )
    assert spec.package_name == package_name
    assert spec.selected_template == template_type
    assert len(spec.nodes) >= 1
    assert spec.nodes[0].file_name.endswith(".py")
    validation = validate_spec(spec)
    assert validation.is_valid, f"Spec not valid: {validation.errors}"


@pytest.mark.parametrize("template_type,package_name,task", NEW_TEMPLATE_TASKS)
def test_new_template_generates_all_files(
    template_type: str, package_name: str, task: str, tmp_path: Path
) -> None:
    """Each new template should generate a complete project with expected files."""
    spec = build_project_spec(
        package_name=package_name,
        task=task,
        selected_template=template_type,
    )
    project = generate_project_from_spec(spec=spec, output_root=tmp_path)
    assert project.output_dir == tmp_path / package_name
    assert project.selected_template == template_type

    # Core files every project must have
    for expected in (
        "package.xml",
        "setup.py",
        "setup.cfg",
        "README.md",
        "robopilot.yaml",
        "config/params.yaml",
    ):
        assert (project.output_dir / expected).is_file(), f"Missing: {expected}"

    # Node file must exist and be valid Python
    node_file = project.output_dir / package_name / spec.nodes[0].file_name
    assert node_file.is_file(), f"Missing node file: {node_file}"
    content = node_file.read_text(encoding="utf-8")
    compile(content, str(node_file), "exec")

    # Launch file must exist
    launch_file = project.output_dir / "launch" / f"{package_name}.launch.py"
    assert launch_file.is_file(), f"Missing launch file: {launch_file}"


@pytest.mark.parametrize("template_type,package_name,task", NEW_TEMPLATE_TASKS)
def test_new_template_spec_roundtrips_through_yaml(
    template_type: str, package_name: str, task: str, tmp_path: Path
) -> None:
    """Spec → YAML → Spec round-trip should preserve key fields."""
    spec = build_project_spec(
        package_name=package_name,
        task=task,
        selected_template=template_type,
    )
    yaml_path = tmp_path / "test.yaml"
    write_spec(spec, yaml_path)
    loaded = load_spec(yaml_path)
    assert loaded.package_name == spec.package_name
    assert loaded.selected_template == spec.selected_template
    assert len(loaded.nodes) == len(spec.nodes)
    assert len(loaded.topics) == len(spec.topics)


def test_configurable_topic_override_flows_to_generated_code(tmp_path: Path) -> None:
    """User-edited topic in robopilot.yaml should appear in generated node files."""
    spec = build_project_spec(
        package_name="custom_topics",
        task="Detect objects",
        selected_template=OBJECT_DETECTION,
    )
    # Simulate user editing the YAML to change topic names
    custom_topics = (
        TopicSpec("/my_camera/color", "subscribe", "sensor_msgs/Image", "Custom camera input"),
        TopicSpec("/my_detections/boxes", "publish", "vision_msgs/Detection2DArray", "Custom detection output"),
    )
    custom_spec = ProjectSpec(
        package_name=spec.package_name,
        task=spec.task,
        selected_template=spec.selected_template,
        nodes=spec.nodes,
        topics=custom_topics,
        config_files=spec.config_files,
        launch_files=spec.launch_files,
        generated_by=spec.generated_by,
        notes=spec.notes,
    )
    project = generate_project_from_spec(spec=custom_spec, output_root=tmp_path)
    node_file = project.output_dir / "custom_topics" / "detector_node.py"
    content = node_file.read_text(encoding="utf-8")
    assert "/my_camera/color" in content
    assert "/my_detections/boxes" in content
