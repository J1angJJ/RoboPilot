import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.generator.project_generator import generate_project, generate_project_from_spec
from robopilot.generator.task_classifier import OBJECT_DETECTION
from robopilot.main import app
from robopilot.planner import (
    DEFAULT_LLM_MODEL,
    LLMPlanner,
    LLMProviderConfig,
    OpenAIPlannerClient,
    PlannerConfigurationError,
    PlannerValidationError,
    RuleBasedPlanner,
)
from robopilot.spec.io import write_spec
from robopilot.spec.validator import validate_spec


TASK = "Create an object detection node publishing bounding boxes"


class FakeLLMClient:
    def __init__(self, response: str | dict[str, object]) -> None:
        self.response = response
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str | dict[str, object]:
        self.prompts.append(prompt)
        return self.response


class FakeOpenAIResponse:
    output_text = json.dumps(
        {
            "package_name": "demo_detector",
            "task": TASK,
            "selected_template": "object_detection",
            "generated_by": "RoboPilot OpenAIPlanner",
            "nodes": [
                {
                    "name": "detector_node",
                    "executable": "detector_node",
                    "module": "detector_node",
                    "class_name": "DetectorNode",
                    "file_name": "detector_node.py",
                    "description": "ROS-style object detection node skeleton.",
                }
            ],
            "topics": [],
            "config_files": ["config/params.yaml"],
            "launch_files": ["launch/demo_detector.launch.py"],
            "notes": ["Provider response used for tests."],
        }
    )


class FakeResponses:
    def __init__(self, response: object) -> None:
        self.response = response
        self.calls: list[dict[str, str]] = []

    def create(self, *, model: str, input: str) -> object:
        self.calls.append({"model": model, "input": input})
        return self.response


class FakeOpenAISDK:
    def __init__(self, response: object) -> None:
        self.responses = FakeResponses(response)


def _valid_llm_response() -> dict[str, object]:
    return {
        "package_name": "demo_detector",
        "task": TASK,
        "selected_template": "object_detection",
        "generated_by": "RoboPilot LLMPlanner",
        "nodes": [
            {
                "name": "detector_node",
                "executable": "detector_node",
                "module": "detector_node",
                "class_name": "DetectorNode",
                "file_name": "detector_node.py",
                "description": "ROS-style object detection node skeleton.",
            }
        ],
        "topics": [
            {
                "name": "/camera/image_raw",
                "direction": "subscribe",
                "message_type": "sensor_msgs/Image",
                "description": "Input image stream for detection.",
            }
        ],
        "config_files": ["config/params.yaml"],
        "launch_files": ["launch/demo_detector.launch.py"],
        "notes": ["Generated as structured ProjectSpec data only."],
    }


def test_rule_based_planner_returns_valid_project_spec() -> None:
    spec = RuleBasedPlanner().plan(package_name="demo_detector", task=TASK)

    assert spec.package_name == "demo_detector"
    assert spec.selected_template == OBJECT_DETECTION
    assert validate_spec(spec).is_valid


def test_provider_config_reads_model_defaults(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("ROBOPILOT_LLM_MODEL", raising=False)

    config = LLMProviderConfig.from_env()

    assert config.api_key == "test-key"
    assert config.model == DEFAULT_LLM_MODEL


def test_provider_config_reads_model_override(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ROBOPILOT_LLM_MODEL", "env-model")

    config = LLMProviderConfig.from_env(model_override="cli-model")

    assert config.model == "cli-model"


def test_missing_openai_api_key_produces_clear_configuration_error(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    try:
        LLMProviderConfig.from_env()
    except PlannerConfigurationError as exc:
        assert "OPENAI_API_KEY is not set" in str(exc)
    else:
        raise AssertionError("Expected PlannerConfigurationError")


def test_llm_planner_parses_fake_project_spec_response() -> None:
    client = FakeLLMClient(json.dumps(_valid_llm_response()))

    spec = LLMPlanner(client=client).plan(package_name="demo_detector", task=TASK)

    assert spec.package_name == "demo_detector"
    assert spec.selected_template == OBJECT_DETECTION
    assert spec.nodes[0].file_name == "detector_node.py"
    assert "Package name: demo_detector" in client.prompts[0]


def test_openai_client_returns_fake_provider_response() -> None:
    config = LLMProviderConfig(api_key="test-key", model="test-model")
    sdk = FakeOpenAISDK(FakeOpenAIResponse())
    client = OpenAIPlannerClient(config, sdk_client=sdk)

    response = client.complete("Return a ProjectSpec")

    assert "demo_detector" in response
    assert sdk.responses.calls[0]["model"] == "test-model"


def test_llm_planner_parses_fake_valid_provider_response() -> None:
    config = LLMProviderConfig(api_key="test-key", model="test-model")
    client = OpenAIPlannerClient(config, sdk_client=FakeOpenAISDK(FakeOpenAIResponse()))

    spec = LLMPlanner(client=client).plan(package_name="demo_detector", task=TASK)

    assert spec.package_name == "demo_detector"
    assert validate_spec(spec).is_valid


def test_llm_planner_validates_generated_spec() -> None:
    client = FakeLLMClient(_valid_llm_response())

    spec = LLMPlanner(client=client).plan(package_name="demo_detector", task=TASK)

    assert validate_spec(spec).is_valid


def test_llm_planner_parses_yaml_provider_response() -> None:
    yaml_response = """\
package_name: demo_detector
task: "Create an object detection node publishing bounding boxes"
selected_template: object_detection
generated_by: RoboPilot OpenAIPlanner
nodes:
  - name: detector_node
    executable: detector_node
    module: detector_node
    class_name: DetectorNode
    file_name: detector_node.py
    description: "ROS-style object detection node skeleton."
topics:
config_files:
  - config/params.yaml
launch_files:
  - launch/demo_detector.launch.py
notes:
  - "ProjectSpec only."
"""

    spec = LLMPlanner(client=FakeLLMClient(yaml_response)).plan(
        package_name="demo_detector",
        task=TASK,
    )

    assert spec.selected_template == OBJECT_DETECTION


def test_llm_planner_rejects_invalid_structured_output() -> None:
    invalid_response = {
        "package_name": "",
        "task": TASK,
        "selected_template": "object_detection",
        "generated_by": "RoboPilot LLMPlanner",
        "nodes": [],
        "topics": [],
        "config_files": [],
        "launch_files": [],
        "notes": [],
    }

    try:
        LLMPlanner(client=FakeLLMClient(invalid_response)).plan(
            package_name="demo_detector",
            task=TASK,
        )
    except PlannerValidationError as exc:
        assert "invalid ProjectSpec" in str(exc)
    else:
        raise AssertionError("Expected PlannerValidationError")


def test_llm_planner_rejects_invalid_provider_response() -> None:
    try:
        LLMPlanner(client=FakeLLMClient("not json or yaml")).plan(
            package_name="demo_detector",
            task=TASK,
        )
    except PlannerValidationError as exc:
        assert "not valid ProjectSpec JSON or YAML" in str(exc)
    else:
        raise AssertionError("Expected PlannerValidationError")


def test_plan_cli_defaults_to_rule_planner() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["plan", "--name", "demo_detector", "--task", TASK],
    )

    assert result.exit_code == 0
    assert "package_name: demo_detector" in result.output
    assert "selected_template: object_detection" in result.output


def test_plan_cli_llm_without_api_key_returns_clear_error(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["plan", "--name", "demo_detector", "--task", TASK, "--planner", "llm"],
    )

    assert result.exit_code == 1
    assert "OPENAI_API_KEY is not set" in result.output
    assert "rule for offline planning" in result.output


def test_existing_generate_behavior_still_works(tmp_path: Path) -> None:
    project = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    assert project.selected_template == OBJECT_DETECTION
    assert (project.output_dir / "demo_detector" / "detector_node.py").is_file()


def test_existing_generate_from_spec_still_works(tmp_path: Path) -> None:
    spec = RuleBasedPlanner().plan(package_name="demo_detector", task=TASK)
    spec_path = tmp_path / "robopilot.yaml"
    write_spec(spec, spec_path)

    project = generate_project_from_spec(
        spec=spec,
        output_root=tmp_path / "generated",
    )

    assert spec_path.is_file()
    assert project.selected_template == OBJECT_DETECTION
