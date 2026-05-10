"""Offline repair suggestions based on RoboPilot project inspection reports."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from robopilot.inspector.project_inspector import ProjectInspection, inspect_project


SAFETY_NOTE = (
    "RoboPilot repair-suggest does not modify files automatically. "
    "Review suggestions before making changes."
)


@dataclass(frozen=True)
class RepairSuggestion:
    """One deterministic repair suggestion for an inspected issue."""

    issue: str
    suggestion: str
    severity: str

    def to_dict(self) -> dict[str, str]:
        """Return a deterministic JSON-ready mapping."""
        return {
            "issue": self.issue,
            "suggestion": self.suggestion,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class RepairSuggestionReport:
    """Repair suggestion report for a project directory."""

    project_path: str
    issues: tuple[str, ...]
    repair_suggestions: tuple[RepairSuggestion, ...]
    safety_note: str
    suggested_commands: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-ready mapping."""
        return {
            "project_path": self.project_path,
            "issues": list(self.issues),
            "repair_suggestions": [
                suggestion.to_dict() for suggestion in self.repair_suggestions
            ],
            "safety_note": self.safety_note,
            "suggested_commands": list(self.suggested_commands),
        }


def suggest_repairs(project_path: Path) -> RepairSuggestionReport:
    """Inspect a project directory and suggest safe offline repairs."""
    inspection = inspect_project(project_path)
    suggestions = tuple(
        _suggestion_for_issue(issue, inspection) for issue in inspection.issues
    )
    commands = _suggested_commands(inspection)
    return RepairSuggestionReport(
        project_path=inspection.project_path,
        issues=inspection.issues,
        repair_suggestions=suggestions,
        safety_note=SAFETY_NOTE,
        suggested_commands=commands,
    )


def _suggestion_for_issue(
    issue: str,
    inspection: ProjectInspection,
) -> RepairSuggestion:
    spec_path = _spec_path(inspection)
    project_name = _project_name_hint(inspection)

    if issue == "project path does not exist":
        return RepairSuggestion(
            issue=issue,
            suggestion=(
                "Check that the project path exists, then run inspect or "
                "repair-suggest again."
            ),
            severity="critical",
        )
    if issue == "project path is not a directory":
        return RepairSuggestion(
            issue=issue,
            suggestion="Provide a project directory path instead of a file path.",
            severity="critical",
        )
    if issue == "empty project directory":
        return RepairSuggestion(
            issue=issue,
            suggestion=(
                "Bootstrap the directory by generating a project from a task or from a valid "
                "robopilot.yaml spec."
            ),
            severity="critical",
        )
    if issue == "missing package.xml":
        return RepairSuggestion(
            issue=issue,
            suggestion=_regenerate_or_restore(
                "Regenerate package.xml from robopilot.yaml if the spec is valid, "
                "or restore a ROS-style package.xml manually.",
                inspection,
            ),
            severity="warning",
        )
    if issue == "missing setup.py":
        return RepairSuggestion(
            issue=issue,
            suggestion=_regenerate_or_restore(
                "Regenerate setup.py from robopilot.yaml if the spec is valid, "
                "or recreate the Python package setup file manually.",
                inspection,
            ),
            severity="warning",
        )
    if issue == "missing setup.cfg":
        return RepairSuggestion(
            issue=issue,
            suggestion=_regenerate_or_restore(
                "Regenerate setup.cfg from robopilot.yaml if the spec is valid, "
                "or restore the ROS-style install script configuration manually.",
                inspection,
            ),
            severity="warning",
        )
    if issue == "missing README.md":
        return RepairSuggestion(
            issue=issue,
            suggestion=(
                "Regenerate README.md from the project spec or add a concise "
                "project README manually."
            ),
            severity="info",
        )
    if issue == "missing launch directory":
        return RepairSuggestion(
            issue=issue,
            suggestion=(
                "Regenerate from a valid spec or create launch/ with the expected "
                "launch file manually."
            ),
            severity="warning",
        )
    if issue == "missing config directory":
        return RepairSuggestion(
            issue=issue,
            suggestion="Regenerate from a valid spec or create config/ with params.yaml manually.",
            severity="warning",
        )
    if issue == "missing Python package directory":
        return RepairSuggestion(
            issue=issue,
            suggestion=(
                f"Create the Python package directory for {project_name} with __init__.py "
                "and the expected node file, or regenerate from a valid spec."
            ),
            severity="warning",
        )
    if issue == "missing robopilot.yaml":
        return RepairSuggestion(
            issue=issue,
            suggestion=(
                "Create a ProjectSpec with robopilot plan, review it, then validate it "
                "before regenerating files."
            ),
            severity="warning",
        )
    if issue == "robopilot.yaml exists but fails validation":
        return RepairSuggestion(
            issue=issue,
            suggestion=f"Run robopilot validate --spec {spec_path} and fix the reported fields.",
            severity="critical",
        )
    if issue.startswith("spec validation: "):
        return RepairSuggestion(
            issue=issue,
            suggestion=(
                f"Fix this ProjectSpec validation error in {spec_path}: "
                f"{issue.removeprefix('spec validation: ')}"
            ),
            severity="critical",
        )

    return RepairSuggestion(
        issue=issue,
        suggestion="Review the reported issue and repair the project files manually.",
        severity="info",
    )


def _regenerate_or_restore(
    base_suggestion: str,
    inspection: ProjectInspection,
) -> str:
    if inspection.spec.exists and inspection.spec.valid:
        return base_suggestion
    return (
        base_suggestion
        + " Since robopilot.yaml is missing or invalid, create or validate the spec first."
    )


def _suggested_commands(inspection: ProjectInspection) -> tuple[str, ...]:
    path = inspection.project_path
    spec_path = _spec_path(inspection)
    project_name = _project_name_hint(inspection)
    parent = str(Path(path).parent)

    commands: list[str] = []
    if "project path does not exist" in inspection.issues:
        commands.append(f"robopilot inspect {path}")
    if "project path is not a directory" in inspection.issues:
        commands.append("robopilot inspect path/to/project_directory")
    if "empty project directory" in inspection.issues:
        commands.append(
            f'robopilot generate --name {project_name} --task "Describe your robotics task."'
        )
    if "missing robopilot.yaml" in inspection.issues:
        commands.append(
            f'robopilot plan --name {project_name} --task "Describe your robotics task." '
            f"--output {spec_path}"
        )
    if "robopilot.yaml exists but fails validation" in inspection.issues:
        commands.append(f"robopilot validate --spec {spec_path}")
    if _has_regenerable_missing_file(inspection):
        commands.append(
            f"robopilot generate --spec {spec_path} --output-root {parent} --overwrite"
        )
    if not commands:
        commands.append(f"robopilot inspect {path}")
    return tuple(dict.fromkeys(commands))


def _has_regenerable_missing_file(inspection: ProjectInspection) -> bool:
    if not (inspection.spec.exists and inspection.spec.valid):
        return False
    return any(
        issue
        in {
            "missing package.xml",
            "missing setup.py",
            "missing setup.cfg",
            "missing README.md",
            "missing launch directory",
            "missing config directory",
            "missing Python package directory",
        }
        for issue in inspection.issues
    )


def _spec_path(inspection: ProjectInspection) -> str:
    return str(Path(inspection.project_path) / "robopilot.yaml")


def _project_name_hint(inspection: ProjectInspection) -> str:
    if inspection.package_name:
        return inspection.package_name
    name = Path(inspection.project_path).name
    return name if name else "demo_project"
