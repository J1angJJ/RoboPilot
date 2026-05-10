from pathlib import Path

from typer.testing import CliRunner

from robopilot.generator.project_generator import generate_project
from robopilot.main import app
from robopilot.report.project_report import generate_project_report, write_project_report


TASK = (
    "Create an object detection node subscribing to camera images and publishing "
    "bounding boxes."
)


def test_generates_report_for_valid_project(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    report = generate_project_report(generated.output_dir)

    assert report.startswith("# RoboPilot Project Report\n")
    assert "- Package name: demo_detector" in report
    assert "- Spec valid: true" in report


def test_report_contains_project_summary(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    report = generate_project_report(generated.output_dir)

    assert "## Project Summary" in report
    assert f"- Project path: {generated.output_dir}" in report
    assert "- Selected template: object_detection" in report


def test_report_contains_detected_files(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    report = generate_project_report(generated.output_dir)

    assert "## Detected Files" in report
    assert "- package.xml: true" in report
    assert "- Launch files: launch/demo_detector.launch.py" in report
    assert "- Python node files: demo_detector/detector_node.py" in report


def test_report_contains_repair_suggestions_section(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    report = generate_project_report(generated.output_dir)

    assert "## Repair Suggestions" in report
    assert "- No repair suggestions needed." in report


def test_report_handles_missing_project_path(tmp_path: Path) -> None:
    missing_project = tmp_path / "does_not_exist"

    report = generate_project_report(missing_project)

    assert "- Exists: false" in report
    assert "- project path does not exist" in report
    assert "Check that the project path exists" in report


def test_report_output_is_deterministic(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    first = generate_project_report(generated.output_dir)
    second = generate_project_report(generated.output_dir)

    assert first == second


def test_write_project_report_writes_file(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )
    output_path = tmp_path / "reports" / "demo_report.md"

    report = write_project_report(generated.output_dir, output_path)

    assert output_path.read_text(encoding="utf-8") == report
    assert "## Safety Note" in report


def test_cli_writes_report_to_file(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )
    output_path = tmp_path / "demo_report.md"
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["report", str(generated.output_dir), "--output", str(output_path)],
    )

    assert result.exit_code == 0
    assert output_path.is_file()
    assert "# RoboPilot Project Report" in output_path.read_text(encoding="utf-8")
