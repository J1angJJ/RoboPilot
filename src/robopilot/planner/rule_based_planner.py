"""Offline rule-based ProjectSpec planner."""

from __future__ import annotations

import re

from robopilot.generator.project_spec import ProjectSpec
from robopilot.generator.task_classifier import classify_task
from robopilot.generator.template_registry import build_project_spec


PACKAGE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class RuleBasedPlanner:
    """Create ProjectSpec objects with deterministic local rules."""

    def plan(self, *, package_name: str, task: str) -> ProjectSpec:
        """Create a ProjectSpec from a package name and task."""
        clean_package_name = _validate_package_name(package_name)
        clean_task = task.strip()
        if not clean_task:
            raise ValueError("Task description cannot be empty.")

        selected_template = classify_task(clean_task)
        return build_project_spec(
            package_name=clean_package_name,
            task=clean_task,
            selected_template=selected_template,
        )


def _validate_package_name(package_name: str) -> str:
    clean_package_name = package_name.strip()
    if not PACKAGE_NAME_PATTERN.fullmatch(clean_package_name):
        raise ValueError(
            "Package name must start with a lowercase letter and contain only "
            "lowercase letters, numbers, and underscores."
        )
    return clean_package_name
