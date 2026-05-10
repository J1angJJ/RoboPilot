"""Validation helpers for RoboPilot ProjectSpec files."""

from __future__ import annotations

import re
from dataclasses import dataclass

from robopilot.generator.project_spec import ProjectSpec
from robopilot.generator.template_registry import TEMPLATE_REGISTRY


PACKAGE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True)
class SpecValidationResult:
    """Result of validating a ProjectSpec."""

    is_valid: bool
    errors: tuple[str, ...]


def validate_spec(spec: ProjectSpec) -> SpecValidationResult:
    """Validate the minimum required schema for generation."""
    errors: list[str] = []

    if not spec.package_name:
        errors.append("package_name is required.")
    elif not PACKAGE_NAME_PATTERN.fullmatch(spec.package_name):
        errors.append(
            "package_name must start with a lowercase letter and contain only lowercase letters, numbers, and underscores."
        )

    if not spec.task:
        errors.append("task is required.")

    if not spec.selected_template:
        errors.append("selected_template is required.")
    elif spec.selected_template not in TEMPLATE_REGISTRY:
        errors.append(f"selected_template is unknown: {spec.selected_template}.")

    if not spec.nodes:
        errors.append("at least one node is required.")
    else:
        for index, node in enumerate(spec.nodes):
            prefix = f"nodes[{index}]"
            if not node.name:
                errors.append(f"{prefix}.name is required.")
            if not node.executable:
                errors.append(f"{prefix}.executable is required.")
            if not node.module:
                errors.append(f"{prefix}.module is required.")
            if not node.class_name:
                errors.append(f"{prefix}.class_name is required.")
            if not node.file_name:
                errors.append(f"{prefix}.file_name is required.")

    if not spec.config_files:
        errors.append("at least one config file is required.")
    if not spec.launch_files:
        errors.append("at least one launch file is required.")
    if not spec.generated_by:
        errors.append("generated_by is required.")

    return SpecValidationResult(is_valid=not errors, errors=tuple(errors))

