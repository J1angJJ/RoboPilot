"""Python API wrappers for RoboPilot ProjectSpec and generation workflows."""

from __future__ import annotations

from pathlib import Path

from robopilot.api.models import PathLike, StructuredResult, normalize_path, to_structured_result
from robopilot.diff.spec_diff import SpecDiffResult, diff_spec_files
from robopilot.generator.project_generator import (
    GeneratedProject,
    generate_project as core_generate_project,
    generate_project_from_spec,
)
from robopilot.generator.project_spec import ProjectSpec
from robopilot.planner import (
    LLMProviderConfig,
    LLMPlanner,
    OpenAIPlannerClient,
    PlannerConfigurationError,
    RuleBasedPlanner,
)
from robopilot.refiner.llm_refiner import LLMRefiner
from robopilot.refiner.spec_refiner import refine_spec
from robopilot.spec.io import load_spec, write_spec
from robopilot.spec.validator import SpecValidationResult, validate_spec


def plan_project(
    name: str,
    task: str,
    *,
    planner: str = "rule",
    model: str | None = None,
    output_path: PathLike | None = None,
    as_dict: bool = True,
) -> StructuredResult | ProjectSpec:
    """Create a ProjectSpec, writing it only when output_path is provided."""
    selected_planner = _build_planner(planner, model=model)
    spec = selected_planner.plan(package_name=name, task=task)
    if output_path is not None:
        write_spec(spec, normalize_path(output_path))
    return _project_spec_to_dict(spec) if as_dict else spec


def refine_project_spec(
    spec_path: PathLike,
    instruction: str,
    *,
    output_path: PathLike | None = None,
    planner: str = "rule",
    model: str | None = None,
    as_dict: bool = True,
) -> StructuredResult | ProjectSpec:
    """Refine a ProjectSpec, writing it only when output_path is provided."""
    original_spec = load_spec(normalize_path(spec_path))
    refined_spec = _refine_with_selected_planner(
        original_spec,
        instruction,
        planner_name=planner,
        model=model,
    )
    if output_path is not None:
        write_spec(refined_spec, normalize_path(output_path))
    return _project_spec_to_dict(refined_spec) if as_dict else refined_spec


def diff_project_specs(
    old_path: PathLike,
    new_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | SpecDiffResult:
    """Compare two ProjectSpec files without modifying either file."""
    result = diff_spec_files(normalize_path(old_path), normalize_path(new_path))
    return to_structured_result(result) if as_dict else result


def validate_project_spec(
    spec_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | SpecValidationResult:
    """Validate a ProjectSpec file."""
    spec = load_spec(normalize_path(spec_path))
    result = validate_spec(spec)
    if not as_dict:
        return result
    return {
        "spec_path": str(normalize_path(spec_path)),
        "is_valid": result.is_valid,
        "errors": list(result.errors),
    }


def generate_project(
    *,
    name: str | None = None,
    task: str | None = None,
    spec_path: PathLike | None = None,
    output_root: PathLike = Path("outputs"),
    overwrite: bool = False,
    as_dict: bool = True,
) -> StructuredResult | GeneratedProject:
    """Generate a project from a task or ProjectSpec file."""
    if spec_path is not None:
        if name is not None or task is not None:
            raise ValueError("Use either spec_path or name/task, not both.")
        spec = load_spec(normalize_path(spec_path))
        result = generate_project_from_spec(
            spec=spec,
            output_root=normalize_path(output_root),
            overwrite=overwrite,
        )
    else:
        if name is None or task is None:
            raise ValueError("Provide name and task, or provide spec_path.")
        result = core_generate_project(
            name=name,
            task=task,
            output_root=normalize_path(output_root),
            overwrite=overwrite,
        )
    return to_structured_result(result) if as_dict else result


def _build_planner(
    planner_name: str,
    *,
    model: str | None = None,
) -> RuleBasedPlanner | LLMPlanner:
    normalized = planner_name.strip().lower()
    if normalized == "rule":
        return RuleBasedPlanner()
    if normalized == "llm":
        config = LLMProviderConfig.from_env(model_override=model)
        return LLMPlanner(client=OpenAIPlannerClient(config))
    raise PlannerConfigurationError(
        f"Unknown planner: {planner_name}. Use 'rule' or 'llm'."
    )


def _refine_with_selected_planner(
    project_spec: ProjectSpec,
    instruction: str,
    *,
    planner_name: str,
    model: str | None = None,
) -> ProjectSpec:
    normalized = planner_name.strip().lower()
    if normalized == "rule":
        return refine_spec(project_spec, instruction, planner="rule")
    if normalized == "llm":
        config = LLMProviderConfig.from_env(model_override=model)
        refiner = LLMRefiner(client=OpenAIPlannerClient(config))
        return refiner.refine(project_spec, instruction)
    raise PlannerConfigurationError(
        f"Unknown refinement planner: {planner_name}. Use 'rule' or 'llm'."
    )


def _project_spec_to_dict(spec: ProjectSpec) -> StructuredResult:
    return {
        "package_name": spec.package_name,
        "task": spec.task,
        "selected_template": spec.selected_template,
        "nodes": [to_structured_result(node) for node in spec.nodes],
        "topics": [to_structured_result(topic) for topic in spec.topics],
        "config_files": list(spec.config_files),
        "launch_files": list(spec.launch_files),
        "generated_by": spec.generated_by,
        "notes": list(spec.notes),
    }
