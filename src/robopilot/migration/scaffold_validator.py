"""Read-only validation for RoboPilot migration scaffolds."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from robopilot.migration.scaffold_generator import render_migration_scaffold_files
from robopilot.migration.scaffold_preview import MigrationScaffoldPreviewResult, preview_migration_scaffold
from robopilot.ros2.inspector import inspect_ros2_project


SAFETY_NOTE = (
    "This migration scaffold validation is static and read-only. RoboPilot did "
    "not modify the scaffold, modify the source project, modify the migration "
    "plan, require ROS, require ROS2, run catkin_make, run colcon, execute "
    "launch files, execute generated code, or import generated scaffold modules."
)


@dataclass(frozen=True)
class PlaceholderCheck:
    """Safety wording check for a generated placeholder file."""

    path: str
    passed: bool
    missing_concepts: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """Return stable JSON-ready placeholder check data."""
        return {
            "path": self.path,
            "passed": self.passed,
            "missing_concepts": list(self.missing_concepts),
        }


@dataclass(frozen=True)
class MigrationScaffoldValidationResult:
    """Read-only validation result for a migration scaffold."""

    plan_path: str
    scaffold_path: str
    source_path: str
    target: str
    package_name: str
    target_style: str
    valid: bool
    expected_files: tuple[str, ...]
    present_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    unexpected_files: tuple[str, ...]
    placeholder_checks: tuple[PlaceholderCheck, ...]
    migration_notes_present: bool
    ros2_inspection_summary: dict[str, object]
    issues: tuple[str, ...]
    warnings: tuple[str, ...]
    suggested_next_steps: tuple[str, ...]
    safety_note: str

    def to_dict(self) -> dict[str, object]:
        """Return stable JSON-ready validation data."""
        return {
            "plan_path": self.plan_path,
            "scaffold_path": self.scaffold_path,
            "source_path": self.source_path,
            "target": self.target,
            "package_name": self.package_name,
            "target_style": self.target_style,
            "valid": self.valid,
            "expected_files": list(self.expected_files),
            "present_files": list(self.present_files),
            "missing_files": list(self.missing_files),
            "unexpected_files": list(self.unexpected_files),
            "placeholder_checks": [check.to_dict() for check in self.placeholder_checks],
            "migration_notes_present": self.migration_notes_present,
            "ros2_inspection_summary": self.ros2_inspection_summary,
            "issues": list(self.issues),
            "warnings": list(self.warnings),
            "suggested_next_steps": list(self.suggested_next_steps),
            "safety_note": self.safety_note,
        }


def validate_migration_scaffold(
    plan_path: Path,
    scaffold_path: Path,
) -> MigrationScaffoldValidationResult:
    """Validate a generated migration scaffold without modifying files."""
    preview = preview_migration_scaffold(plan_path)
    scaffold = Path(scaffold_path)
    expected_files = tuple(sorted(render_migration_scaffold_files(preview)))
    present_files = _present_files(scaffold) if scaffold.exists() and scaffold.is_dir() else ()
    present_set = set(present_files)
    expected_set = set(expected_files)
    missing_files = tuple(path for path in expected_files if path not in present_set)
    unexpected_files = tuple(path for path in present_files if path not in expected_set)
    placeholder_checks = _placeholder_checks(scaffold, preview, expected_files, present_set)
    notes_present = "MIGRATION_NOTES.md" in present_set
    ros2_summary = _ros2_summary(scaffold)
    issues = _issues(
        scaffold=scaffold,
        preview=preview,
        expected_files=expected_files,
        missing_files=missing_files,
        placeholder_checks=placeholder_checks,
        notes_present=notes_present,
        present_files=present_files,
    )
    warnings = _warnings(unexpected_files, ros2_summary)
    valid = not issues

    return MigrationScaffoldValidationResult(
        plan_path=str(plan_path),
        scaffold_path=str(scaffold_path),
        source_path=preview.source_path,
        target=preview.target,
        package_name=preview.package_name,
        target_style=preview.target_style,
        valid=valid,
        expected_files=expected_files,
        present_files=present_files,
        missing_files=missing_files,
        unexpected_files=unexpected_files,
        placeholder_checks=placeholder_checks,
        migration_notes_present=notes_present,
        ros2_inspection_summary=ros2_summary,
        issues=issues,
        warnings=warnings,
        suggested_next_steps=_suggested_next_steps(valid, issues, warnings),
        safety_note=SAFETY_NOTE,
    )


def _present_files(scaffold: Path) -> tuple[str, ...]:
    files: list[str] = []
    for path in sorted(scaffold.rglob("*")):
        relative = path.relative_to(scaffold)
        if _is_ignored(relative):
            continue
        if path.is_file():
            files.append(relative.as_posix())
    return tuple(sorted(dict.fromkeys(files)))


def _placeholder_checks(
    scaffold: Path,
    preview: MigrationScaffoldPreviewResult,
    expected_files: tuple[str, ...],
    present_files: set[str],
) -> tuple[PlaceholderCheck, ...]:
    check_paths = [
        path
        for path in expected_files
        if path == "MIGRATION_NOTES.md"
        or path.startswith("launch/")
        or path == "config/params.yaml"
        or path.endswith("_node.py")
        or path.endswith("_node.cpp")
    ]
    checks: list[PlaceholderCheck] = []
    for relative_path in check_paths:
        if relative_path not in present_files:
            checks.append(PlaceholderCheck(relative_path, False, ("file missing",)))
            continue
        text = (scaffold / relative_path).read_text(encoding="utf-8", errors="ignore")
        missing = _missing_placeholder_concepts(relative_path, text, preview.target_style)
        checks.append(PlaceholderCheck(relative_path, not missing, missing))
    return tuple(checks)


def _missing_placeholder_concepts(
    relative_path: str,
    text: str,
    target_style: str,
) -> tuple[str, ...]:
    lowered = text.lower()
    concepts: list[tuple[str, tuple[str, ...]]] = [
        ("Generated by RoboPilot", ("generated by robopilot", "robopilot migration scaffold", "robopilot generated")),
        ("not an automatic migration", ("not an automatic migration",)),
        ("manual review", ("manual", "review")),
    ]
    if relative_path != "MIGRATION_NOTES.md":
        concepts.append(("TODO", ("todo",)))
    if relative_path.endswith("_node.py") or relative_path.endswith("_node.cpp") or relative_path == "config/params.yaml":
        concepts.append(("ROS2 QoS review", ("qos",)))
    if relative_path.startswith("launch/"):
        concepts.append(("ROS1 launch review", ("ros1 xml launch", "parameters", "remaps", "namespaces")))
    if relative_path == "MIGRATION_NOTES.md":
        concepts.append(("runtime validation warning", ("no runtime validation",)))
        if target_style in {"mixed_review_required", "manual_review_required"}:
            concepts.append(("manual build-system decision", ("manual", "build-system")))

    missing: list[str] = []
    for label, needles in concepts:
        if not any(needle in lowered for needle in needles):
            missing.append(label)
    return tuple(missing)


def _ros2_summary(scaffold: Path) -> dict[str, object]:
    inspection = inspect_ros2_project(scaffold)
    return {
        "exists": inspection.exists,
        "package_name": inspection.package_name,
        "detected_project_type": inspection.detected_project_type,
        "build_system": inspection.build_system.to_dict(),
        "files": inspection.files.to_dict(),
        "nodes": inspection.nodes.to_dict(),
        "issues": list(inspection.issues),
    }


def _issues(
    *,
    scaffold: Path,
    preview: MigrationScaffoldPreviewResult,
    expected_files: tuple[str, ...],
    missing_files: tuple[str, ...],
    placeholder_checks: tuple[PlaceholderCheck, ...],
    notes_present: bool,
    present_files: tuple[str, ...],
) -> tuple[str, ...]:
    issues: list[str] = []
    if not scaffold.exists():
        issues.append("scaffold path does not exist")
    elif not scaffold.is_dir():
        issues.append("scaffold path is not a directory")
    if preview.target != "ros2":
        issues.append("migration plan target is not ros2")
    if not preview.package_name or preview.package_name == "unknown":
        issues.append("package name is missing or unknown")
    if missing_files:
        issues.extend(f"missing expected scaffold file: {path}" for path in missing_files)
    if not notes_present:
        issues.append("missing MIGRATION_NOTES.md")
    if "package.xml" not in present_files:
        issues.append("missing package.xml")
    if preview.target_style == "ament_python":
        for path in ("setup.py", "setup.cfg", f"resource/{preview.package_name}", f"{preview.package_name}/__init__.py"):
            if path not in present_files:
                issues.append(f"missing ament_python scaffold file: {path}")
    if preview.target_style == "ament_cmake" and "CMakeLists.txt" not in present_files:
        issues.append("missing CMakeLists.txt for ament_cmake scaffold")
    if preview.target_style == "mixed_review_required":
        notes_check = next((check for check in placeholder_checks if check.path == "MIGRATION_NOTES.md"), None)
        if notes_check and "manual build-system decision" in notes_check.missing_concepts:
            issues.append("mixed scaffold is missing manual build-system decision notes")
    if any(not check.passed for check in placeholder_checks):
        for check in placeholder_checks:
            if not check.passed:
                issues.append(f"placeholder safety wording incomplete: {check.path}")
    issues.extend(_unsafe_structure_issues(scaffold))
    return tuple(sorted(dict.fromkeys(issues)))


def _warnings(
    unexpected_files: tuple[str, ...],
    ros2_summary: dict[str, object],
) -> tuple[str, ...]:
    warnings: list[str] = []
    warnings.extend(f"unexpected file present: {path}" for path in unexpected_files)
    for issue in ros2_summary.get("issues", []):
        warnings.append(f"ros2_inspection: {issue}")
    return tuple(sorted(dict.fromkeys(str(item) for item in warnings)))


def _unsafe_structure_issues(scaffold: Path) -> tuple[str, ...]:
    if not scaffold.exists() or not scaffold.is_dir():
        return ()
    root = scaffold.resolve(strict=False)
    issues: list[str] = []
    for path in scaffold.rglob("*"):
        relative = path.relative_to(scaffold)
        if ".." in relative.parts or path.is_absolute() and not path.resolve(strict=False).is_relative_to(root):
            issues.append(f"unsafe scaffold path detected: {relative.as_posix()}")
        if path.is_symlink():
            try:
                resolved = path.resolve(strict=True)
            except OSError:
                issues.append(f"unsafe or broken symlink detected: {relative.as_posix()}")
                continue
            if not resolved.is_relative_to(root):
                issues.append(f"symlink escapes scaffold directory: {relative.as_posix()}")
    return tuple(sorted(dict.fromkeys(issues)))


def _suggested_next_steps(
    valid: bool,
    issues: tuple[str, ...],
    warnings: tuple[str, ...],
) -> tuple[str, ...]:
    if valid:
        steps = [
            "Review MIGRATION_NOTES.md before manual migration work.",
            "Run robopilot inspect-ros2 on the scaffold after manual edits.",
            "Run robopilot deps on the scaffold after adding real ROS2 dependencies.",
        ]
    else:
        steps = [
            "Regenerate the scaffold from the migration plan or restore missing scaffold files.",
            "Review placeholder files and restore RoboPilot safety wording before manual migration work.",
        ]
    if warnings:
        steps.append("Review unexpected files and ROS2 inspection warnings before treating the scaffold as ready.")
    return tuple(dict.fromkeys(steps))


def _is_ignored(path: Path) -> bool:
    ignored = {"__pycache__", ".git", ".pytest_tmp", ".robopilot_backups", ".robopilot_history"}
    return bool(set(path.parts).intersection(ignored))
