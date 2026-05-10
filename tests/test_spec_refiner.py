from pathlib import Path

from typer.testing import CliRunner

from robopilot.generator.project_spec import ProjectSpec
from robopilot.generator.task_classifier import OBJECT_DETECTION, PERCEPTION_PIPELINE
from robopilot.main import app
from robopilot.planner.rule_based_planner import RuleBasedPlanner
from robopilot.refiner.spec_refiner import refine_spec
from robopilot.spec.io import load_spec, write_spec
from robopilot.spec.validator import validate_spec


TASK = "Create an object detection node publishing bounding boxes"


def _base_spec() -> ProjectSpec:
    return RuleBasedPlanner().plan(package_name="demo_detector", task=TASK)


def test_loads_and_refines_existing_valid_spec() -> None:
    refined = refine_spec(_base_spec(), "Add a tracker node after the detector")

    assert validate_spec(refined).is_valid
    assert any(node.name == "tracker_node" for node in refined.nodes)


def test_adds_tracker_node() -> None:
    refined = refine_spec(_base_spec(), "Add a tracker node after the detector")

    node_names = [node.name for node in refined.nodes]
    assert "tracker_node" in node_names
    assert node_names.index("tracker_node") == node_names.index("detector_node") + 1
    assert refined.selected_template == PERCEPTION_PIPELINE
    assert "tracker_node was added by refinement." in refined.notes


def test_avoids_duplicate_tracker_node() -> None:
    once = refine_spec(_base_spec(), "Add a tracker node after the detector")
    twice = refine_spec(once, "Add a tracker node after the detector")

    assert [node.name for node in twice.nodes].count("tracker_node") == 1
    assert (
        "tracker_node already exists; refinement did not add a duplicate."
        in twice.notes
    )


def test_adds_camera_node() -> None:
    refined = refine_spec(_base_spec(), "Add a camera node")

    assert any(node.name == "camera_node" for node in refined.nodes)
    assert "camera_node was added by refinement." in refined.notes


def test_adds_controller_node() -> None:
    refined = refine_spec(_base_spec(), "Add a controller node")

    assert any(node.name == "controller_node" for node in refined.nodes)
    assert "controller_node was added by refinement." in refined.notes


def test_preserves_existing_package_name_and_task() -> None:
    spec = _base_spec()

    refined = refine_spec(spec, "Add a tracker node after the detector")

    assert refined.package_name == spec.package_name
    assert refined.task == spec.task
    assert refined.config_files == spec.config_files
    assert refined.launch_files == spec.launch_files


def test_validates_refined_spec_before_saving() -> None:
    refined = refine_spec(_base_spec(), "Add a controller node")

    result = validate_spec(refined)

    assert result.is_valid
    assert result.errors == ()


def test_adds_topic_when_instruction_contains_topic_name() -> None:
    refined = refine_spec(_base_spec(), "Add topic /tracks")

    assert any(topic.name == "/tracks" for topic in refined.topics)
    assert "/tracks topic was added by refinement." in refined.notes


def test_cli_writes_refined_spec_to_output(tmp_path: Path) -> None:
    spec_path = tmp_path / "base.yaml"
    output_path = tmp_path / "refined.yaml"
    write_spec(_base_spec(), spec_path)
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "refine",
            "--spec",
            str(spec_path),
            "--instruction",
            "Add a tracker node after the detector",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.is_file()
    refined = load_spec(output_path)
    assert any(node.name == "tracker_node" for node in refined.nodes)


def test_unsupported_instruction_adds_note_without_breaking_spec() -> None:
    refined = refine_spec(_base_spec(), "Make it more robust")

    assert refined.selected_template == OBJECT_DETECTION
    assert validate_spec(refined).is_valid
    assert any("Unsupported refinement instruction" in note for note in refined.notes)


def test_llm_refinement_returns_clear_not_implemented_message() -> None:
    try:
        refine_spec(_base_spec(), "Add a tracker node", planner="llm")
    except ValueError as exc:
        assert "not implemented yet" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
