"""Markdown report export for RoboPilot migration scaffolds."""

from __future__ import annotations

from pathlib import Path

from robopilot.migration.scaffold_preview import preview_migration_scaffold
from robopilot.migration.scaffold_validator import (
    MigrationScaffoldValidationResult,
    validate_migration_scaffold,
)


REPORT_SAFETY_NOTE = (
    "This report is generated from static validation only. RoboPilot did not "
    "run ROS. RoboPilot did not run ROS2. RoboPilot did not run catkin_make. "
    "RoboPilot did not run colcon. RoboPilot did not execute launch files. "
    "RoboPilot did not execute generated code or import generated scaffold "
    "modules. Passing validation does not mean the scaffold builds, launches, "
    "or behaves correctly at runtime."
)


def generate_migration_scaffold_report(plan_path: Path, scaffold_path: Path) -> str:
    """Generate a deterministic Markdown report for a migration scaffold."""
    validation = validate_migration_scaffold(plan_path, scaffold_path)
    preview = preview_migration_scaffold(plan_path)
    ros2_summary = validation.ros2_inspection_summary

    lines = [
        "# RoboPilot Migration Scaffold Report",
        "",
        "## Summary",
        "",
        f"- Valid: {_bool(validation.valid)}",
        f"- Issues: {len(validation.issues)}",
        f"- Warnings: {len(validation.warnings)}",
        f"- Migration notes present: {_bool(validation.migration_notes_present)}",
        "",
        "## Source and Target",
        "",
        f"- Plan path: {validation.plan_path}",
        f"- Scaffold path: {validation.scaffold_path}",
        f"- Source path: {validation.source_path or 'unknown'}",
        f"- Target: {validation.target or 'unknown'}",
        "",
        "## Package",
        "",
        f"- Package name: {validation.package_name or 'unknown'}",
        "",
        "## Target Style",
        "",
        f"- Target style: {validation.target_style or 'unknown'}",
        "",
        "## Validation Result",
        "",
        f"- Valid: {_bool(validation.valid)}",
        f"- Migration notes present: {_bool(validation.migration_notes_present)}",
        "",
        "## Expected Files",
        "",
    ]
    lines.extend(_bullet_list(validation.expected_files, "No expected files."))
    lines.extend(["", "## Present Files", ""])
    lines.extend(_bullet_list(validation.present_files, "No present files."))
    lines.extend(["", "## Missing Files", ""])
    lines.extend(_bullet_list(validation.missing_files, "No missing files."))
    lines.extend(["", "## Unexpected Files", ""])
    lines.extend(_bullet_list(validation.unexpected_files, "No unexpected files."))
    lines.extend(["", "## Placeholder Checks", ""])
    lines.extend(_placeholder_checks(validation))
    lines.extend(["", "## ROS2 Static Inspection Summary", ""])
    lines.extend(_ros2_summary_lines(ros2_summary))
    lines.extend(["", "## Manual Migration Items", ""])
    lines.extend(_bullet_list(preview.files_requiring_manual_migration, "No manual migration items reported."))
    lines.extend(["", "## Interface Files to Review", ""])
    lines.extend(_bullet_list(preview.interface_files_to_review, "No interface files reported."))
    lines.extend(["", "## Dependency Items to Review", ""])
    lines.extend(_bullet_list(preview.dependency_items_to_review, "No dependency items reported."))
    lines.extend(["", "## Issues", ""])
    lines.extend(_bullet_list(validation.issues, "No validation issues."))
    lines.extend(["", "## Warnings", ""])
    lines.extend(_bullet_list(validation.warnings, "No validation warnings."))
    lines.extend(["", "## Suggested Next Steps", ""])
    lines.extend(_bullet_list(validation.suggested_next_steps, "No next steps suggested."))
    lines.extend(
        [
            "",
            "## Safety Note",
            "",
            REPORT_SAFETY_NOTE,
            "",
            validation.safety_note,
            "",
        ]
    )
    return "\n".join(lines)


def write_migration_scaffold_report(
    plan_path: Path,
    scaffold_path: Path,
    output_path: Path,
    *,
    overwrite: bool = False,
) -> str:
    """Generate and write a Markdown scaffold report to an explicit path."""
    output = Path(output_path)
    if output.exists() and not overwrite:
        raise FileExistsError(f"report output already exists: {output}")
    markdown = generate_migration_scaffold_report(plan_path, scaffold_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
    return markdown


def _placeholder_checks(validation: MigrationScaffoldValidationResult) -> list[str]:
    if not validation.placeholder_checks:
        return ["- No placeholder checks."]
    lines: list[str] = []
    for check in validation.placeholder_checks:
        status = "passed" if check.passed else "failed"
        missing = _join_or_none(check.missing_concepts)
        lines.append(f"- {check.path}: {status}; missing concepts: {missing}")
    return lines


def _ros2_summary_lines(summary: dict[str, object]) -> list[str]:
    build_system = _dict(summary.get("build_system"))
    files = _dict(summary.get("files"))
    nodes = _dict(summary.get("nodes"))
    lines = [
        f"- Exists: {_bool(bool(summary.get('exists')))}",
        f"- Package name: {summary.get('package_name') or 'unknown'}",
        f"- Detected project type: {summary.get('detected_project_type') or 'unknown'}",
        f"- Build system: {_format_mapping(build_system)}",
        f"- Launch files: {_join_or_none(_strings(files.get('launch_files')))}",
        f"- Config files: {_join_or_none(_strings(files.get('config_files')))}",
        f"- Python node candidates: {_join_or_none(_strings(nodes.get('python_node_candidates')))}",
        f"- C++ node candidates: {_join_or_none(_strings(nodes.get('cpp_node_candidates')))}",
        f"- ROS2 inspection issues: {_join_or_none(_strings(summary.get('issues')))}",
    ]
    return lines


def _format_mapping(values: dict[str, object]) -> str:
    if not values:
        return "none"
    parts = [f"{key}={_bool(value) if isinstance(value, bool) else value}" for key, value in sorted(values.items())]
    return ", ".join(parts)


def _bullet_list(values: tuple[str, ...], empty_message: str) -> list[str]:
    if not values:
        return [f"- {empty_message}"]
    return [f"- {value}" for value in values]


def _join_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _strings(value: object) -> tuple[str, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return ()


def _dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _bool(value: object) -> str:
    return "true" if bool(value) else "false"
