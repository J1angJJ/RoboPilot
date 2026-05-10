from pathlib import Path

from typer.testing import CliRunner

from robopilot.apply_preview.preview import preview_apply
from robopilot.generator.project_generator import generate_project_from_spec
from robopilot.main import app
from robopilot.planner.rule_based_planner import RuleBasedPlanner
from robopilot.refiner.spec_refiner import refine_spec
from robopilot.spec.io import write_spec


TASK = "Create an object detection node publishing bounding boxes"


def _base_spec():
    return RuleBasedPlanner().plan(package_name="demo_detector", task=TASK)


def test_preview_on_matching_generated_project_shows_files_to_keep(tmp_path: Path) -> None:
    spec = _base_spec()
    spec_path = tmp_path / "robopilot.yaml"
    write_spec(spec, spec_path)
    project = generate_project_from_spec(spec=spec, output_root=tmp_path / "generated")

    result = preview_apply(spec_path, project.output_dir)

    assert result.files_to_create == ()
    assert result.files_to_update == ()
    assert "package.xml" in result.files_to_keep
    assert "demo_detector/detector_node.py" in result.files_to_keep


def test_preview_after_refined_spec_shows_tracker_file_to_create(tmp_path: Path) -> None:
    base = _base_spec()
    refined = refine_spec(base, "Add a tracker node after the detector")
    spec_path = tmp_path / "refined.yaml"
    write_spec(refined, spec_path)
    project = generate_project_from_spec(spec=base, output_root=tmp_path / "generated")

    result = preview_apply(spec_path, project.output_dir)

    assert "demo_detector/tracker_node.py" in result.files_to_create
    assert "robopilot.yaml" in result.files_to_update


def test_preview_detects_files_to_create_for_empty_project_directory(tmp_path: Path) -> None:
    spec = _base_spec()
    spec_path = tmp_path / "robopilot.yaml"
    project_path = tmp_path / "empty_project"
    project_path.mkdir()
    write_spec(spec, spec_path)

    result = preview_apply(spec_path, project_path)

    assert "package.xml" in result.files_to_create
    assert "setup.py" in result.files_to_create
    assert result.files_to_keep == ()
    assert not result.missing_project


def test_preview_handles_non_existent_project_path(tmp_path: Path) -> None:
    spec = _base_spec()
    spec_path = tmp_path / "robopilot.yaml"
    project_path = tmp_path / "missing_project"
    write_spec(spec, spec_path)

    result = preview_apply(spec_path, project_path)

    assert result.missing_project
    assert "package.xml" in result.files_to_create
    assert result.conflicts == ()


def test_preview_json_output_has_stable_keys(tmp_path: Path) -> None:
    spec = _base_spec()
    spec_path = tmp_path / "robopilot.yaml"
    write_spec(spec, spec_path)

    result = preview_apply(spec_path, tmp_path / "missing").to_dict()

    assert list(result.keys()) == [
        "spec_path",
        "project_path",
        "package_name",
        "selected_template",
        "files_to_create",
        "files_to_update",
        "files_to_keep",
        "conflicts",
        "missing_project",
        "safety_note",
        "suggested_next_steps",
    ]


def test_preview_does_not_modify_project_files(tmp_path: Path) -> None:
    spec = _base_spec()
    spec_path = tmp_path / "robopilot.yaml"
    project = generate_project_from_spec(spec=spec, output_root=tmp_path / "generated")
    package_xml = project.output_dir / "package.xml"
    before = package_xml.read_text(encoding="utf-8")
    write_spec(refine_spec(spec, "Add a tracker node"), spec_path)

    preview_apply(spec_path, project.output_dir)

    assert package_xml.read_text(encoding="utf-8") == before
    assert not (project.output_dir / "demo_detector" / "tracker_node.py").exists()


def test_cli_apply_preview_json_output_works(tmp_path: Path) -> None:
    spec = _base_spec()
    spec_path = tmp_path / "robopilot.yaml"
    write_spec(spec, spec_path)
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "apply-preview",
            "--spec",
            str(spec_path),
            "--project",
            str(tmp_path / "missing"),
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"files_to_create"' in result.output
    assert '"missing_project": true' in result.output


def test_existing_generate_command_still_works(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "generate",
            "--name",
            "demo_detector",
            "--task",
            TASK,
            "--output-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert (tmp_path / "demo_detector" / "package.xml").is_file()


def test_existing_report_and_inspect_commands_still_work(tmp_path: Path) -> None:
    spec = _base_spec()
    project = generate_project_from_spec(spec=spec, output_root=tmp_path)
    runner = CliRunner()

    inspect_result = runner.invoke(app, ["inspect", str(project.output_dir), "--json"])
    report_result = runner.invoke(app, ["report", str(project.output_dir)])

    assert inspect_result.exit_code == 0
    assert '"package_name": "demo_detector"' in inspect_result.output
    assert report_result.exit_code == 0
    assert "# RoboPilot Project Report" in report_result.output
