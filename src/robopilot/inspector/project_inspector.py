"""Static inspector for RoboPilot-generated or ROS-style project directories."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from robopilot.spec.io import load_spec
from robopilot.spec.validator import validate_spec


@dataclass(frozen=True)
class SpecInspection:
    """Inspection status for robopilot.yaml."""

    exists: bool
    valid: bool
    selected_template: str | None
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-ready mapping."""
        return {
            "exists": self.exists,
            "valid": self.valid,
            "selected_template": self.selected_template,
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class FileInspection:
    """Detected project files."""

    package_xml: bool
    setup_py: bool
    setup_cfg: bool
    readme: bool
    launch_files: tuple[str, ...]
    config_files: tuple[str, ...]
    python_node_files: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-ready mapping."""
        return {
            "package_xml": self.package_xml,
            "setup_py": self.setup_py,
            "setup_cfg": self.setup_cfg,
            "readme": self.readme,
            "launch_files": list(self.launch_files),
            "config_files": list(self.config_files),
            "python_node_files": list(self.python_node_files),
        }


@dataclass(frozen=True)
class ProjectInspection:
    """Static inspection report for one project directory."""

    project_path: str
    exists: bool
    is_empty: bool
    package_name: str | None
    spec: SpecInspection
    files: FileInspection
    issues: tuple[str, ...]
    suggested_next_steps: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-ready mapping."""
        return {
            "project_path": self.project_path,
            "exists": self.exists,
            "is_empty": self.is_empty,
            "package_name": self.package_name,
            "spec": self.spec.to_dict(),
            "files": self.files.to_dict(),
            "issues": list(self.issues),
            "suggested_next_steps": list(self.suggested_next_steps),
        }


def inspect_project(project_path: Path) -> ProjectInspection:
    """Inspect a project directory without executing project code."""
    path = Path(project_path)
    normalized_path = str(path)

    if not path.exists():
        return ProjectInspection(
            project_path=normalized_path,
            exists=False,
            is_empty=False,
            package_name=None,
            spec=SpecInspection(False, False, None, ()),
            files=_empty_files(),
            issues=("project path does not exist",),
            suggested_next_steps=("Check the path and run inspect again.",),
        )

    if not path.is_dir():
        return ProjectInspection(
            project_path=normalized_path,
            exists=True,
            is_empty=False,
            package_name=None,
            spec=SpecInspection(False, False, None, ()),
            files=_empty_files(),
            issues=("project path is not a directory",),
            suggested_next_steps=("Provide a project directory path.",),
        )

    is_empty = not any(path.iterdir())
    files = _inspect_files(path)
    spec = _inspect_spec(path / "robopilot.yaml")
    package_name = _detect_package_name(path, spec)
    issues = _detect_issues(
        path=path,
        is_empty=is_empty,
        package_name=package_name,
        spec=spec,
        files=files,
    )
    return ProjectInspection(
        project_path=normalized_path,
        exists=True,
        is_empty=is_empty,
        package_name=package_name,
        spec=spec,
        files=files,
        issues=issues,
        suggested_next_steps=_suggest_next_steps(issues),
    )


def _inspect_spec(spec_path: Path) -> SpecInspection:
    if not spec_path.is_file():
        return SpecInspection(False, False, None, ())

    try:
        spec = load_spec(spec_path)
    except (OSError, ValueError) as exc:
        return SpecInspection(True, False, None, (str(exc),))

    validation = validate_spec(spec)
    return SpecInspection(
        exists=True,
        valid=validation.is_valid,
        selected_template=spec.selected_template or None,
        errors=validation.errors,
    )


def _inspect_files(path: Path) -> FileInspection:
    launch_dir = path / "launch"
    config_dir = path / "config"
    package_dirs = [
        child
        for child in sorted(path.iterdir(), key=lambda item: item.name)
        if child.is_dir() and (child / "__init__.py").is_file()
    ]
    python_node_files: list[str] = []
    for package_dir in package_dirs:
        python_node_files.extend(
            _relative_file_paths(path, package_dir, pattern="*.py", exclude_init=True)
        )

    return FileInspection(
        package_xml=(path / "package.xml").is_file(),
        setup_py=(path / "setup.py").is_file(),
        setup_cfg=(path / "setup.cfg").is_file(),
        readme=(path / "README.md").is_file(),
        launch_files=tuple(_relative_file_paths(path, launch_dir, pattern="*.py")),
        config_files=tuple(_relative_file_paths(path, config_dir, pattern="*.yaml")),
        python_node_files=tuple(sorted(python_node_files)),
    )


def _relative_file_paths(
    root: Path,
    directory: Path,
    *,
    pattern: str,
    exclude_init: bool = False,
) -> list[str]:
    if not directory.is_dir():
        return []
    paths = []
    for file_path in sorted(directory.rglob(pattern)):
        if exclude_init and file_path.name == "__init__.py":
            continue
        paths.append(file_path.relative_to(root).as_posix())
    return paths


def _detect_package_name(path: Path, spec: SpecInspection) -> str | None:
    if spec.exists and spec.valid:
        try:
            loaded_spec = load_spec(path / "robopilot.yaml")
        except (OSError, ValueError):
            loaded_spec = None
        if loaded_spec is not None and loaded_spec.package_name:
            return loaded_spec.package_name

    package_xml = path / "package.xml"
    if package_xml.is_file():
        match = re.search(
            r"<name>\s*([^<\s]+)\s*</name>",
            package_xml.read_text(encoding="utf-8", errors="ignore"),
        )
        if match:
            return match.group(1)

    package_dirs = [
        child.name
        for child in sorted(path.iterdir(), key=lambda item: item.name)
        if child.is_dir() and (child / "__init__.py").is_file()
    ]
    return package_dirs[0] if package_dirs else None


def _detect_issues(
    *,
    path: Path,
    is_empty: bool,
    package_name: str | None,
    spec: SpecInspection,
    files: FileInspection,
) -> tuple[str, ...]:
    issues: list[str] = []
    if is_empty:
        issues.append("empty project directory")
    if not files.package_xml:
        issues.append("missing package.xml")
    if not files.setup_py:
        issues.append("missing setup.py")
    if not files.setup_cfg:
        issues.append("missing setup.cfg")
    if not files.readme:
        issues.append("missing README.md")
    if not (path / "launch").is_dir():
        issues.append("missing launch directory")
    if not (path / "config").is_dir():
        issues.append("missing config directory")
    if package_name is None or not (path / package_name / "__init__.py").is_file():
        issues.append("missing Python package directory")
    if not spec.exists:
        issues.append("missing robopilot.yaml")
    elif not spec.valid:
        issues.append("robopilot.yaml exists but fails validation")
        issues.extend(f"spec validation: {error}" for error in spec.errors)
    return tuple(issues)


def _suggest_next_steps(issues: tuple[str, ...]) -> tuple[str, ...]:
    if not issues:
        return (
            "Review robopilot.yaml before making manual changes.",
            "Run tests or project-specific checks in your own ROS environment if needed.",
        )

    steps: list[str] = []
    if "project path does not exist" in issues:
        steps.append("Check the path and run inspect again.")
    if "empty project directory" in issues:
        steps.append("Generate a project with robopilot generate or inspect another directory.")
    if any(issue.startswith("missing ") for issue in issues):
        steps.append("Regenerate the project from a valid robopilot.yaml or restore missing files.")
    if "robopilot.yaml exists but fails validation" in issues:
        steps.append("Run robopilot validate --spec robopilot.yaml and fix the reported fields.")
    if not steps:
        steps.append("Review the reported issues and update the project files manually.")
    return tuple(dict.fromkeys(steps))


def _empty_files() -> FileInspection:
    return FileInspection(
        package_xml=False,
        setup_py=False,
        setup_cfg=False,
        readme=False,
        launch_files=(),
        config_files=(),
        python_node_files=(),
    )

