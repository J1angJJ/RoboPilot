"""Export and validate read-only apply plans."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from robopilot.apply_preview.preview import ApplyPreviewResult, preview_apply


GENERATED_BY = "RoboPilot ApplyPlan"
SUPPORTED_FORMATS = {"yaml", "json"}
REQUIRED_FIELDS = (
    "generated_by",
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
)
LIST_FIELDS = {
    "files_to_create",
    "files_to_update",
    "files_to_keep",
    "conflicts",
    "suggested_next_steps",
}


@dataclass(frozen=True)
class ApplyPlanValidationResult:
    """Validation result for a serialized apply plan."""

    is_valid: bool
    errors: tuple[str, ...]


def export_apply_plan(
    *,
    spec_path: Path,
    project_path: Path,
    output_path: Path,
    output_format: str = "yaml",
) -> dict[str, object]:
    """Export a deterministic apply plan without modifying the project."""
    normalized_format = output_format.strip().lower()
    if normalized_format not in SUPPORTED_FORMATS:
        raise ValueError("Unsupported apply plan format. Use 'yaml' or 'json'.")

    preview = preview_apply(spec_path, project_path)
    plan = apply_plan_from_preview(preview)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if normalized_format == "json":
        output_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    else:
        output_path.write_text(apply_plan_to_yaml(plan), encoding="utf-8")
    return plan


def apply_plan_from_preview(preview: ApplyPreviewResult) -> dict[str, object]:
    """Convert an apply-preview result into a stable apply plan mapping."""
    data = preview.to_dict()
    return {
        "generated_by": GENERATED_BY,
        "spec_path": data["spec_path"],
        "project_path": data["project_path"],
        "package_name": data["package_name"],
        "selected_template": data["selected_template"],
        "files_to_create": data["files_to_create"],
        "files_to_update": data["files_to_update"],
        "files_to_keep": data["files_to_keep"],
        "conflicts": data["conflicts"],
        "missing_project": data["missing_project"],
        "safety_note": data["safety_note"],
        "suggested_next_steps": data["suggested_next_steps"],
    }


def apply_plan_to_yaml(plan: dict[str, object]) -> str:
    """Serialize an apply plan using RoboPilot's small YAML-like subset."""
    lines: list[str] = []
    for field in REQUIRED_FIELDS:
        value = plan.get(field)
        if field in LIST_FIELDS:
            lines.append(f"{field}:")
            for item in _list_value(value):
                lines.append(f'  - "{_quote(str(item))}"')
            continue
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        else:
            rendered = f'"{_quote(str(value or ""))}"'
        lines.append(f"{field}: {rendered}")
    return "\n".join(lines) + "\n"


def validate_apply_plan_file(plan_path: Path) -> ApplyPlanValidationResult:
    """Validate a serialized apply plan without executing it."""
    try:
        plan = load_apply_plan(plan_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return ApplyPlanValidationResult(False, (str(exc),))
    return validate_apply_plan(plan)


def validate_apply_plan(plan: dict[str, object]) -> ApplyPlanValidationResult:
    """Validate required apply plan fields and basic types."""
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in plan:
            errors.append(f"{field} is required.")

    for field in LIST_FIELDS:
        if field in plan and not isinstance(plan[field], list):
            errors.append(f"{field} must be a list.")

    if "missing_project" in plan and not isinstance(plan["missing_project"], bool):
        errors.append("missing_project must be a boolean.")

    for field in (
        "generated_by",
        "spec_path",
        "project_path",
        "package_name",
        "selected_template",
        "safety_note",
    ):
        if field in plan and not isinstance(plan[field], str):
            errors.append(f"{field} must be a string.")

    return ApplyPlanValidationResult(is_valid=not errors, errors=tuple(errors))


def load_apply_plan(plan_path: Path) -> dict[str, object]:
    """Load a JSON or RoboPilot YAML-like apply plan."""
    content = plan_path.read_text(encoding="utf-8")
    if plan_path.suffix.lower() == ".json" or content.lstrip().startswith("{"):
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("Apply plan JSON must be an object.")
        return data
    return apply_plan_from_yaml(content)


def apply_plan_from_yaml(content: str) -> dict[str, object]:
    """Parse RoboPilot's small apply-plan YAML-like subset."""
    data: dict[str, object] = {}
    current_list: str | None = None
    for raw_line in content.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if not raw_line.startswith(" "):
            key, value = _split_key_value(raw_line)
            if value == "" and key in LIST_FIELDS:
                data[key] = []
                current_list = key
                continue
            current_list = None
            if key == "missing_project":
                data[key] = _parse_bool(value)
            else:
                data[key] = _unquote(value)
            continue
        if current_list is None:
            raise ValueError(f"Unexpected indented line outside a list: {raw_line}")
        stripped = raw_line.strip()
        if not stripped.startswith("- "):
            raise ValueError(f"Expected list item: {raw_line}")
        value = _unquote(stripped[2:].strip())
        current_value = data[current_list]
        if not isinstance(current_value, list):
            raise ValueError(f"Expected list field: {current_list}")
        current_value.append(value)
    return data


def _split_key_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"Expected key/value line: {line}")
    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def _parse_bool(value: str) -> bool:
    normalized = _unquote(value).strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"Expected boolean value, got: {value}")


def _quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    return value.replace('\\"', '"').replace("\\\\", "\\")


def _list_value(value: object) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []
