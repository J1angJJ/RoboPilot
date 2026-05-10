from dataclasses import asdict
from pathlib import Path

from typer.testing import CliRunner

from robopilot.diff.spec_diff import diff_specs
from robopilot.generator.project_spec import ProjectSpec
from robopilot.main import app
from robopilot.planner.base import PlannerValidationError
from robopilot.planner.rule_based_planner import RuleBasedPlanner
from robopilot.refiner.llm_refiner import LLMRefiner
from robopilot.refiner.spec_refiner import TRACKER_NODE, refine_spec
from robopilot.spec.io import load_spec, write_spec
from robopilot.spec.validator import validate_spec


TASK = "Create an object detection node publishing bounding boxes"


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.prompt = ""

    def complete(self, prompt: str):
        self.prompt = prompt
        return self.response


def _base_spec() -> ProjectSpec:
    return RuleBasedPlanner().plan(package_name="demo_detector", task=TASK)


def _refined_spec() -> ProjectSpec:
    return refine_spec(_base_spec(), "Add a tracker node after the detector")


def _spec_dict(spec: ProjectSpec) -> dict[str, object]:
    return {
        "package_name": spec.package_name,
        "task": spec.task,
        "selected_template": spec.selected_template,
        "generated_by": spec.generated_by,
        "nodes": [asdict(node) for node in spec.nodes],
        "topics": [asdict(topic) for topic in spec.topics],
        "config_files": list(spec.config_files),
        "launch_files": list(spec.launch_files),
        "notes": list(spec.notes),
    }


def test_rule_based_refine_still_works() -> None:
    refined = refine_spec(_base_spec(), "Add a tracker node after the detector")

    assert any(node.name == "tracker_node" for node in refined.nodes)
    assert validate_spec(refined).is_valid


def test_llm_refiner_parses_fake_valid_refined_project_spec_response() -> None:
    client = FakeClient(_spec_dict(_refined_spec()))

    refined = LLMRefiner(client=client).refine(
        _base_spec(),
        "Add a tracker node after the detector",
    )

    assert validate_spec(refined).is_valid
    assert any(node.name == "tracker_node" for node in refined.nodes)
    assert "Current ProjectSpec:" in client.prompt
    assert "Return only a full ProjectSpec-compatible JSON or YAML document." in client.prompt


def test_llm_refiner_validates_refined_project_spec() -> None:
    refined = LLMRefiner(client=FakeClient(_spec_dict(_refined_spec()))).refine(
        _base_spec(),
        "Add a tracker node after the detector",
    )

    assert validate_spec(refined).is_valid


def test_llm_refiner_rejects_invalid_structured_output() -> None:
    invalid = _spec_dict(_refined_spec())
    invalid["package_name"] = ""

    try:
        LLMRefiner(client=FakeClient(invalid)).refine(
            _base_spec(),
            "Add a tracker node after the detector",
        )
    except PlannerValidationError as exc:
        assert "invalid ProjectSpec" in str(exc)
    else:
        raise AssertionError("Expected PlannerValidationError")


def test_llm_refiner_preserves_package_name_when_not_instructed_to_change_it() -> None:
    refined = LLMRefiner(client=FakeClient(_spec_dict(_refined_spec()))).refine(
        _base_spec(),
        "Add a tracker node after the detector",
    )

    assert refined.package_name == "demo_detector"


def test_llm_refiner_rejects_unrequested_package_name_change() -> None:
    changed = _spec_dict(_refined_spec())
    changed["package_name"] = "renamed_detector"

    try:
        LLMRefiner(client=FakeClient(changed)).refine(
            _base_spec(),
            "Add a tracker node after the detector",
        )
    except PlannerValidationError as exc:
        assert "changed package_name" in str(exc)
    else:
        raise AssertionError("Expected PlannerValidationError")


def test_llm_refiner_can_add_tracker_node_from_fake_response() -> None:
    base = _base_spec()
    fake_refined = _spec_dict(base)
    fake_refined["selected_template"] = "perception_pipeline"
    fake_refined["nodes"] = [asdict(node) for node in base.nodes] + [asdict(TRACKER_NODE)]
    fake_refined["notes"] = list(base.notes) + ["tracker_node was added by LLM refinement."]

    refined = LLMRefiner(client=FakeClient(fake_refined)).refine(
        base,
        "Add a tracker node after the detector",
    )

    assert [node.name for node in refined.nodes][-1] == "tracker_node"


def test_cli_refine_llm_handles_missing_api_key_gracefully(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    spec_path = tmp_path / "base.yaml"
    output_path = tmp_path / "llm_refined.yaml"
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
            "--planner",
            "llm",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 1
    assert "OPENAI_API_KEY is not set" in result.output
    assert not output_path.exists()


def test_cli_refine_rule_still_writes_output(tmp_path: Path) -> None:
    spec_path = tmp_path / "base.yaml"
    output_path = tmp_path / "rule_refined.yaml"
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
            "--planner",
            "rule",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert any(node.name == "tracker_node" for node in load_spec(output_path).nodes)


def test_existing_diff_workflow_works_after_llm_style_refinement() -> None:
    base = _base_spec()
    refined = LLMRefiner(client=FakeClient(_spec_dict(_refined_spec()))).refine(
        base,
        "Add a tracker node after the detector",
    )

    result = diff_specs(base, refined)

    assert result.has_changes
    assert [node["name"] for node in result.added_nodes] == ["tracker_node"]
