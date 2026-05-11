"""Python API wrappers for RoboPilot safe apply, rollback, and history features."""

from __future__ import annotations

from robopilot.api.models import PathLike, StructuredResult, normalize_path, to_structured_result
from robopilot.apply.apply_plan import ApplySummary, apply_from_plan
from robopilot.apply_plan.plan import (
    ApplyPlanValidationResult,
    export_apply_plan as core_export_apply_plan,
    validate_apply_plan_file as core_validate_apply_plan_file,
)
from robopilot.apply_preview.preview import ApplyPreviewResult, preview_apply as core_preview_apply
from robopilot.history.journal import HistoryReport, list_history
from robopilot.rollback.rollback import RollbackSummary, rollback_project


def preview_apply(
    spec_path: PathLike,
    project_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | ApplyPreviewResult:
    """Preview ProjectSpec application without modifying the project."""
    result = core_preview_apply(normalize_path(spec_path), normalize_path(project_path))
    return to_structured_result(result) if as_dict else result


def export_apply_plan(
    spec_path: PathLike,
    project_path: PathLike,
    output_path: PathLike,
    *,
    output_format: str = "yaml",
) -> StructuredResult:
    """Export an apply plan file without modifying the target project."""
    return core_export_apply_plan(
        spec_path=normalize_path(spec_path),
        project_path=normalize_path(project_path),
        output_path=normalize_path(output_path),
        output_format=output_format,
    )


def validate_apply_plan_file(
    plan_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | ApplyPlanValidationResult:
    """Validate an apply plan file without executing it."""
    result = core_validate_apply_plan_file(normalize_path(plan_path))
    if not as_dict:
        return result
    return {
        "is_valid": result.is_valid,
        "errors": list(result.errors),
    }


def apply_exported_plan(
    plan_path: PathLike,
    *,
    confirm: bool = False,
    as_dict: bool = True,
) -> StructuredResult | ApplySummary:
    """Dry-run or apply a validated plan depending on confirm."""
    result = apply_from_plan(normalize_path(plan_path), confirm=confirm)
    return to_structured_result(result) if as_dict else result


def rollback_project_backup(
    project_path: PathLike,
    backup_path: PathLike,
    *,
    confirm: bool = False,
    as_dict: bool = True,
) -> StructuredResult | RollbackSummary:
    """Dry-run or restore files from a RoboPilot backup depending on confirm."""
    result = rollback_project(
        project_path=normalize_path(project_path),
        backup_path=normalize_path(backup_path),
        confirm=confirm,
    )
    return to_structured_result(result) if as_dict else result


def read_project_history(
    project_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | HistoryReport:
    """Read project-local RoboPilot history without printing."""
    result = list_history(normalize_path(project_path))
    return to_structured_result(result) if as_dict else result
