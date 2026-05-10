from dataclasses import replace
from pathlib import Path

from robopilot.generator.project_generator import create_project_spec, generate_project
from robopilot.inspector.project_inspector import inspect_project
from robopilot.spec.io import write_spec


TASK = (
    "Create an object detection node subscribing to camera images and publishing "
    "bounding boxes."
)


def test_inspects_valid_generated_project(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    report = inspect_project(generated.output_dir)

    assert report.exists
    assert not report.is_empty
    assert report.package_name == "demo_detector"
    assert report.spec.exists
    assert report.spec.valid
    assert report.spec.selected_template == "object_detection"
    assert report.files.package_xml
    assert report.files.setup_py
    assert report.files.setup_cfg
    assert report.files.readme
    assert report.files.launch_files == ("launch/demo_detector.launch.py",)
    assert report.files.config_files == ("config/params.yaml",)
    assert report.files.python_node_files == ("demo_detector/detector_node.py",)
    assert report.issues == ()


def test_detects_missing_package_xml(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )
    (generated.output_dir / "package.xml").unlink()

    report = inspect_project(generated.output_dir)

    assert not report.files.package_xml
    assert "missing package.xml" in report.issues


def test_detects_missing_robopilot_yaml(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )
    (generated.output_dir / "robopilot.yaml").unlink()

    report = inspect_project(generated.output_dir)

    assert not report.spec.exists
    assert "missing robopilot.yaml" in report.issues


def test_handles_nonexistent_project_path(tmp_path: Path) -> None:
    report = inspect_project(tmp_path / "does_not_exist")

    assert not report.exists
    assert "project path does not exist" in report.issues
    assert report.files.launch_files == ()


def test_detects_empty_project_directory(tmp_path: Path) -> None:
    empty_project = tmp_path / "empty_project"
    empty_project.mkdir()

    report = inspect_project(empty_project)

    assert report.exists
    assert report.is_empty
    assert "empty project directory" in report.issues
    assert "missing package.xml" in report.issues


def test_json_output_structure(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    data = inspect_project(generated.output_dir).to_dict()

    assert set(data) == {
        "project_path",
        "exists",
        "is_empty",
        "package_name",
        "spec",
        "files",
        "issues",
        "suggested_next_steps",
    }
    assert data["spec"]["selected_template"] == "object_detection"
    assert data["files"]["python_node_files"] == ["demo_detector/detector_node.py"]


def test_invalid_robopilot_yaml_uses_existing_validator(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )
    spec = create_project_spec(name="demo_detector", task=TASK)
    invalid_spec = replace(spec, package_name="")
    write_spec(invalid_spec, generated.output_dir / "robopilot.yaml")

    report = inspect_project(generated.output_dir)

    assert report.spec.exists
    assert not report.spec.valid
    assert "package_name is required." in report.spec.errors
    assert "robopilot.yaml exists but fails validation" in report.issues

