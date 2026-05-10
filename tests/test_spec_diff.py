from dataclasses import replace
from pathlib import Path

from typer.testing import CliRunner

from robopilot.diff.spec_diff import diff_spec_files, diff_specs
from robopilot.generator.project_spec import TopicSpec
from robopilot.generator.task_classifier import PERCEPTION_PIPELINE
from robopilot.main import app
from robopilot.planner.rule_based_planner import RuleBasedPlanner
from robopilot.refiner.spec_refiner import refine_spec
from robopilot.spec.io import write_spec


TASK = "Create an object detection node publishing bounding boxes"


def _base_spec():
    return RuleBasedPlanner().plan(package_name="demo_detector", task=TASK)


def test_diff_detects_added_tracker_node_after_refinement() -> None:
    base = _base_spec()
    refined = refine_spec(base, "Add a tracker node after the detector")

    result = diff_specs(base, refined)

    assert result.has_changes
    assert [node["name"] for node in result.added_nodes] == ["tracker_node"]
    assert result.removed_nodes == ()


def test_diff_detects_selected_template_change() -> None:
    base = _base_spec()
    refined = refine_spec(base, "Add a tracker node after the detector")

    result = diff_specs(base, refined)

    assert result.changed_fields["selected_template"] == {
        "old": base.selected_template,
        "new": PERCEPTION_PIPELINE,
    }


def test_diff_detects_added_topic() -> None:
    base = _base_spec()
    refined = replace(
        base,
        topics=base.topics
        + (
            TopicSpec(
                name="/tracks",
                direction="publish",
                message_type="std_msgs/String",
                description="Tracking output.",
            ),
        ),
    )

    result = diff_specs(base, refined)

    assert [topic["name"] for topic in result.added_topics] == ["/tracks"]


def test_diff_detects_added_note() -> None:
    base = _base_spec()
    refined = refine_spec(base, "Add a camera node")

    result = diff_specs(base, refined)

    assert "camera_node was added by refinement." in result.added_notes


def test_diff_reports_no_changes_for_identical_specs() -> None:
    base = _base_spec()

    result = diff_specs(base, base)

    assert not result.has_changes
    assert result.changed_fields == {}
    assert result.added_nodes == ()
    assert result.added_topics == ()
    assert result.added_notes == ()


def test_diff_rejects_invalid_old_spec() -> None:
    base = _base_spec()
    invalid = replace(base, package_name="")

    try:
        diff_specs(invalid, base)
    except ValueError as exc:
        assert "Old ProjectSpec is invalid" in str(exc)
        assert "package_name is required" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_diff_rejects_invalid_new_spec() -> None:
    base = _base_spec()
    invalid = replace(base, package_name="")

    try:
        diff_specs(base, invalid)
    except ValueError as exc:
        assert "New ProjectSpec is invalid" in str(exc)
        assert "package_name is required" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_json_output_has_stable_keys(tmp_path: Path) -> None:
    base_path = tmp_path / "base.yaml"
    refined_path = tmp_path / "refined.yaml"
    base = _base_spec()
    refined = refine_spec(base, "Add a tracker node after the detector")
    write_spec(base, base_path)
    write_spec(refined, refined_path)

    result = diff_spec_files(base_path, refined_path).to_dict()

    assert list(result.keys()) == [
        "old_spec",
        "new_spec",
        "valid",
        "changed_fields",
        "added_nodes",
        "removed_nodes",
        "added_topics",
        "removed_topics",
        "added_config_files",
        "removed_config_files",
        "added_launch_files",
        "removed_launch_files",
        "added_notes",
        "removed_notes",
        "has_changes",
    ]


def test_cli_readable_output_works(tmp_path: Path) -> None:
    base_path = tmp_path / "base.yaml"
    refined_path = tmp_path / "refined.yaml"
    base = _base_spec()
    refined = refine_spec(base, "Add a tracker node after the detector")
    write_spec(base, base_path)
    write_spec(refined, refined_path)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["diff", "--old", str(base_path), "--new", str(refined_path)],
    )

    assert result.exit_code == 0
    assert "Spec Summary" in result.output
    assert "Added Nodes" in result.output
    assert "tracker_node" in result.output


def test_cli_json_output_works(tmp_path: Path) -> None:
    base_path = tmp_path / "base.yaml"
    refined_path = tmp_path / "refined.yaml"
    base = _base_spec()
    refined = refine_spec(base, "Add topic /tracks")
    write_spec(base, base_path)
    write_spec(refined, refined_path)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["diff", "--old", str(base_path), "--new", str(refined_path), "--json"],
    )

    assert result.exit_code == 0
    assert '"added_topics"' in result.output
    assert '"/tracks"' in result.output
