from pathlib import Path

import pytest

from robopilot.generator.project_generator import (
    expected_project_files,
    generate_project,
)
from robopilot.generator.task_classifier import OBJECT_DETECTION
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
