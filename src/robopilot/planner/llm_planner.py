"""Optional ProjectSpec-only LLM planner."""

from __future__ import annotations

import json
from typing import Any, Protocol

from robopilot.generator.project_spec import NodeSpec, ProjectSpec, TopicSpec
from robopilot.planner.base import PlannerConfigurationError, PlannerValidationError
from robopilot.planner.prompts import build_project_spec_prompt
from robopilot.spec.validator import validate_spec


class LLMClient(Protocol):
    """Minimal injectable client interface for tests or future providers."""

    def complete(self, prompt: str) -> str | dict[str, Any]:
        """Return structured ProjectSpec-like output."""


class LLMPlanner:
    """Create ProjectSpec objects through an optional structured-output client."""

    def __init__(self, client: LLMClient | None = None) -> None:
        self.client = client

    def plan(self, *, package_name: str, task: str) -> ProjectSpec:
        """Ask the configured client for ProjectSpec-compatible data."""
        if self.client is None:
            raise PlannerConfigurationError(
                "LLM planner requested, but no LLM client is configured. "
                "Use --planner rule for offline planning."
            )

        prompt = build_project_spec_prompt(package_name=package_name, task=task)
        raw_response = self.client.complete(prompt)
        spec = _parse_project_spec(raw_response)
        validation = validate_spec(spec)
        if not validation.is_valid:
            raise PlannerValidationError(
                "LLM planner returned an invalid ProjectSpec: "
                + "; ".join(validation.errors)
            )
        return spec


def _parse_project_spec(raw_response: str | dict[str, Any]) -> ProjectSpec:
    if isinstance(raw_response, str):
        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise PlannerValidationError(
                "LLM planner returned non-JSON structured output."
            ) from exc
    elif isinstance(raw_response, dict):
        data = raw_response
    else:
        raise PlannerValidationError(
            "LLM planner returned unsupported structured output."
        )

    if not isinstance(data, dict):
        raise PlannerValidationError("LLM planner output must be a mapping.")
    return _project_spec_from_mapping(data)


def _project_spec_from_mapping(data: dict[str, Any]) -> ProjectSpec:
    return ProjectSpec(
        package_name=str(data.get("package_name", "")),
        task=str(data.get("task", "")),
        selected_template=str(data.get("selected_template", "")),
        nodes=tuple(_node_from_mapping(item) for item in _list_of_mappings(data.get("nodes"))),
        topics=tuple(
            _topic_from_mapping(item) for item in _list_of_mappings(data.get("topics"))
        ),
        config_files=tuple(str(item) for item in _list_of_scalars(data.get("config_files"))),
        launch_files=tuple(str(item) for item in _list_of_scalars(data.get("launch_files"))),
        generated_by=str(data.get("generated_by", "")),
        notes=tuple(str(item) for item in _list_of_scalars(data.get("notes"))),
    )


def _node_from_mapping(item: dict[str, Any]) -> NodeSpec:
    return NodeSpec(
        name=str(item.get("name", "")),
        executable=str(item.get("executable", "")),
        module=str(item.get("module", "")),
        class_name=str(item.get("class_name", "")),
        file_name=str(item.get("file_name", "")),
        description=str(item.get("description", "")),
    )


def _topic_from_mapping(item: dict[str, Any]) -> TopicSpec:
    return TopicSpec(
        name=str(item.get("name", "")),
        direction=str(item.get("direction", "")),
        message_type=str(item.get("message_type", "")),
        description=str(item.get("description", "")),
    )


def _list_of_mappings(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _list_of_scalars(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if not isinstance(item, dict)]
