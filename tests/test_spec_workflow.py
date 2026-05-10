from dataclasses import replace
from pathlib import Path

from robopilot.generator.project_generator import (
    create_project_spec,
    generate_project,
    generate_project_from_spec,
)
from robopilot.generator.task_classifier import OBJECT_DETECTION
from robopilot.spec.io import load_spec, write_spec
from robopilot.spec.validator import validate_spec


TASK = (
    "Create an object detection node subscribing to camera images and publishing "
    "bounding boxes."
)


def test_creates_project_spec_from_task() -> None:
    spec = create_project_spec(name="demo_detector", task=TASK)

    assert spec.package_name == "demo_detector"
    assert spec.task == TASK
    assert spec.selected_template == OBJECT_DETECTION
    assert spec.nodes[0].file_name == "detector_node.py"
    assert "config/params.yaml" in spec.config_files
    assert "launch/demo_detector.launch.py" in spec.launch_files


def test_saves_and_loads_project_spec(tmp_path: Path) -> None:
    spec = create_project_spec(name="demo_detector", task=TASK)
    spec_path = tmp_path / "robopilot.yaml"

    write_spec(spec, spec_path)
    loaded = load_spec(spec_path)

    assert loaded == spec


def test_validates_valid_project_spec() -> None:
    spec = create_project_spec(name="demo_detector", task=TASK)

    result = validate_spec(spec)

    assert result.is_valid
    assert result.errors == ()


def test_rejects_invalid_spec_missing_package_name() -> None:
    spec = create_project_spec(name="demo_detector", task=TASK)
    invalid_spec = replace(spec, package_name="")

    result = validate_spec(invalid_spec)

    assert not result.is_valid
    assert "package_name is required." in result.errors


def test_generates_project_from_spec(tmp_path: Path) -> None:
    spec = create_project_spec(name="demo_detector", task=TASK)

    project = generate_project_from_spec(spec=spec, output_root=tmp_path)

    assert project.output_dir == tmp_path / "demo_detector"
    assert (project.output_dir / "robopilot.yaml").is_file()
    assert (project.output_dir / "demo_detector" / "detector_node.py").is_file()


def test_preserves_prompt_driven_generate_behavior(tmp_path: Path) -> None:
    project = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    assert project.selected_template == OBJECT_DETECTION
    assert (project.output_dir / "demo_detector" / "detector_node.py").is_file()

