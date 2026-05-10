"""Markdown report generation for RoboPilot project inspections."""

from __future__ import annotations

from pathlib import Path

from robopilot.inspector.project_inspector import inspect_project
from robopilot.repair.repair_suggester import RepairSuggestion, suggest_repairs


STATIC_SAFETY_NOTE = (
    "This report is generated from static inspection only. RoboPilot did not "
    "execute ROS2, launch files, colcon, or generated Python code."
)


def generate_project_report(project_path: Path) -> str:
    """Generate a deterministic Markdown report for a project directory."""
    inspection = inspect_project(project_path)
    repairs = suggest_repairs(project_path)

    lines = [
        "# RoboPilot Project Report",
        "",
        "## Project Summary",
        "",
        f"- Project path: {inspection.project_path}",
        f"- Exists: {_bool(inspection.exists)}",
        f"- Empty: {_bool(inspection.is_empty)}",
        f"- Package name: {inspection.package_name or 'unknown'}",
        f"- Spec exists: {_bool(inspection.spec.exists)}",
        f"- Spec valid: {_bool(inspection.spec.valid)}",
        f"- Selected template: {inspection.spec.selected_template or 'unknown'}",
        "",
        "## Spec Status",
        "",
        f"- robopilot.yaml exists: {_bool(inspection.spec.exists)}",
        f"- Valid spec: {_bool(inspection.spec.valid)}",
        f"- Selected template: {inspection.spec.selected_template or 'unknown'}",
        f"- Spec errors: {_join_or_none(inspection.spec.errors)}",
        "",
        "## Detected Files",
        "",
        f"- package.xml: {_bool(inspection.files.package_xml)}",
        f"- setup.py: {_bool(inspection.files.setup_py)}",
        f"- setup.cfg: {_bool(inspection.files.setup_cfg)}",
        f"- README.md: {_bool(inspection.files.readme)}",
        f"- Launch files: {_join_or_none(inspection.files.launch_files)}",
        f"- Config files: {_join_or_none(inspection.files.config_files)}",
        f"- Python node files: {_join_or_none(inspection.files.python_node_files)}",
        "",
        "## Potential Issues",
        "",
    ]
    lines.extend(_bullet_list(inspection.issues, "No obvious structural issues detected."))
    lines.extend(["", "## Repair Suggestions", ""])
    lines.extend(_repair_suggestions(repairs.repair_suggestions))
    lines.extend(["", "## Suggested Commands", ""])
    lines.extend(_bullet_list(repairs.suggested_commands, "No commands suggested."))
    lines.extend(["", "## Safety Note", "", STATIC_SAFETY_NOTE, repairs.safety_note, ""])
    return "\n".join(lines)


def write_project_report(project_path: Path, output_path: Path) -> str:
    """Generate and write a Markdown report, returning the rendered text."""
    markdown = generate_project_report(project_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    return markdown


def _repair_suggestions(suggestions: tuple[RepairSuggestion, ...]) -> list[str]:
    if not suggestions:
        return ["- No repair suggestions needed."]
    return [
        f"- [{suggestion.severity}] {suggestion.issue}: {suggestion.suggestion}"
        for suggestion in suggestions
    ]


def _bullet_list(values: tuple[str, ...], empty_message: str) -> list[str]:
    if not values:
        return [f"- {empty_message}"]
    return [f"- {value}" for value in values]


def _join_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _bool(value: bool) -> str:
    return "true" if value else "false"
