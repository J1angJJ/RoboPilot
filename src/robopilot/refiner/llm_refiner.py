"""Optional LLM-assisted ProjectSpec refinement."""

from __future__ import annotations

from typing import Any, Protocol

from robopilot.generator.project_spec import ProjectSpec
from robopilot.planner.base import PlannerConfigurationError, PlannerValidationError
from robopilot.planner.llm_planner import parse_project_spec_response
from robopilot.spec.io import spec_to_yaml
from robopilot.spec.validator import validate_spec


class LLMRefinerClient(Protocol):
    """Minimal injectable client interface for LLM-assisted refinement."""

    def complete(self, prompt: str) -> str | dict[str, Any]:
        """Return a full refined ProjectSpec-compatible response."""


class LLMRefiner:
    """Refine ProjectSpec objects through an optional structured-output client."""

    def __init__(self, client: LLMRefinerClient | None = None) -> None:
        self.client = client

    def refine(self, spec: ProjectSpec, instruction: str) -> ProjectSpec:
        """Ask the configured client for a validated refined ProjectSpec."""
        if self.client is None:
            raise PlannerConfigurationError(
                "LLM refinement requested, but no LLM client is configured. "
                "Use --planner rule for offline refinement."
            )

        input_validation = validate_spec(spec)
        if not input_validation.is_valid:
            raise PlannerValidationError(
                "Input ProjectSpec is invalid: " + "; ".join(input_validation.errors)
            )

        clean_instruction = instruction.strip()
        if not clean_instruction:
            raise PlannerValidationError("Refinement instruction cannot be empty.")

        raw_response = self.client.complete(
            build_refinement_prompt(spec=spec, instruction=clean_instruction)
        )
        refined_spec = parse_project_spec_response(raw_response)
        _validate_refined_spec(spec, refined_spec, clean_instruction)
        return refined_spec


def build_refinement_prompt(*, spec: ProjectSpec, instruction: str) -> str:
    """Build a constrained ProjectSpec-only refinement prompt."""
    return f"""\
You are helping RoboPilot refine an existing ProjectSpec.

Return only a full ProjectSpec-compatible JSON or YAML document.
Do not include prose outside the structured data.
Do not generate source code.
Do not generate project files.
Do not add arbitrary unsupported fields.
Preserve package_name and task unless the user explicitly asks to change them.
Preserve existing useful nodes, topics, config_files, launch_files, and notes unless the instruction clearly asks to remove them.

Allowed fields:
- package_name
- task
- selected_template
- generated_by
- nodes
- topics
- config_files
- launch_files
- notes

Allowed selected_template values:
- camera_subscriber
- object_detection
- velocity_controller
- perception_pipeline
- generic_node

Current ProjectSpec:
{spec_to_yaml(spec)}

Refinement instruction:
{instruction}
"""


def _validate_refined_spec(
    original_spec: ProjectSpec,
    refined_spec: ProjectSpec,
    instruction: str,
) -> None:
    validation = validate_spec(refined_spec)
    if not validation.is_valid:
        raise PlannerValidationError(
            "LLM refiner returned an invalid ProjectSpec: "
            + "; ".join(validation.errors)
        )

    normalized_instruction = instruction.lower()
    if (
        refined_spec.package_name != original_spec.package_name
        and not _allows_package_name_change(normalized_instruction)
    ):
        raise PlannerValidationError(
            "LLM refiner changed package_name without an explicit instruction."
        )
    if (
        refined_spec.task != original_spec.task
        and not _allows_task_change(normalized_instruction)
    ):
        raise PlannerValidationError(
            "LLM refiner changed task without an explicit instruction."
        )


def _allows_package_name_change(instruction: str) -> bool:
    return any(term in instruction for term in ("package_name", "package name", "rename package"))


def _allows_task_change(instruction: str) -> bool:
    return any(term in instruction for term in ("task", "change task", "update task"))
