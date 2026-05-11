"""Read-only ROS1-to-ROS2 migration preview."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from robopilot.deps.analyzer import analyze_dependencies
from robopilot.detector.project_detector import detect_project
from robopilot.migration.ros1_to_ros2 import (
    load_migration_plan,
    validate_migration_plan,
)
from robopilot.ros1.inspector import inspect_ros1_project


SAFETY_NOTE = (
    "This migration preview is generated from static inspection only. "
    "RoboPilot did not modify source files, generate migrated files, require "
    "ROS, require ROS2, run catkin_make, run colcon, execute launch files, "
    "execute code, or import user project modules."
)


@dataclass(frozen=True)
class MigrationPreviewResult:
    """File-level preview for a ROS1-to-ROS2 migration plan."""

    plan_path: str
    project_path: str
    source_project_type: str
    target: str
    package_name: str
    files_to_create: tuple[str, ...]
    files_to_update: tuple[str, ...]
    files_to_keep: tuple[str, ...]
    files_requiring_manual_migration: tuple[str, ...]
    interface_files_to_review: tuple[str, ...]
    dependency_items_to_review: tuple[str, ...]
    conflicts: tuple[str, ...]
    risks: tuple[str, ...]
    suggested_next_steps: tuple[str, ...]
    safety_note: str

    def to_dict(self) -> dict[str, object]:
        """Return stable JSON-ready data."""
        return {
            "plan_path": self.plan_path,
            "project_path": self.project_path,
            "source_project_type": self.source_project_type,
            "target": self.target,
            "package_name": self.package_name,
            "files_to_create": list(self.files_to_create),
            "files_to_update": list(self.files_to_update),
            "files_to_keep": list(self.files_to_keep),
            "files_requiring_manual_migration": list(self.files_requiring_manual_migration),
            "interface_files_to_review": list(self.interface_files_to_review),
            "dependency_items_to_review": list(self.dependency_items_to_review),
            "conflicts": list(self.conflicts),
            "risks": list(self.risks),
            "suggested_next_steps": list(self.suggested_next_steps),
            "safety_note": self.safety_note,
        }


def preview_migration(plan_path: Path, project_path: Path) -> MigrationPreviewResult:
    """Preview a migration plan at file level without modifying files."""
    plan = load_migration_plan(plan_path)
    validation = validate_migration_plan(plan)
    if not validation.is_valid:
        raise ValueError("Invalid migration plan: " + "; ".join(validation.errors))

    path = Path(project_path)
    detection = detect_project(path)
    inspection = inspect_ros1_project(path)
    dependencies = analyze_dependencies(path)
    package_name = str(plan.get("package_name") or inspection.package_name or path.name)
    target = str(plan.get("target", "")).strip().lower()
    source_project_type = detection.project_type

    files_to_create = _planned_files_to_create(plan, inspection, package_name)
    files_to_keep = _files_to_keep(path, inspection)
    manual_files = _manual_migration_files(inspection)
    interface_files = tuple(
        sorted(
            dict.fromkeys(
                inspection.files.msg_files
                + inspection.files.srv_files
                + inspection.files.action_files
            )
        )
    )
    dependency_items = _dependency_items_to_review(plan)
    conflicts = _conflicts(
        plan=plan,
        plan_path=plan_path,
        project_path=path,
        detection_type=detection.project_type,
        planned_files=files_to_create,
    )
    risks = _risks(plan, detection.project_type, inspection.issues, dependencies.warnings, conflicts)

    return MigrationPreviewResult(
        plan_path=str(plan_path),
        project_path=str(project_path),
        source_project_type=source_project_type,
        target=target,
        package_name=package_name,
        files_to_create=files_to_create,
        files_to_update=(),
        files_to_keep=files_to_keep,
        files_requiring_manual_migration=manual_files,
        interface_files_to_review=interface_files,
        dependency_items_to_review=dependency_items,
        conflicts=conflicts,
        risks=risks,
        suggested_next_steps=_suggested_next_steps(conflicts),
        safety_note=SAFETY_NOTE,
    )


def _planned_files_to_create(
    plan: dict[str, object],
    inspection,
    package_name: str,
) -> tuple[str, ...]:
    suggested = " ".join(str(item) for item in _list(plan.get("suggested_file_changes", []))).lower()
    files: list[str] = ["package.xml"]
    if "setup.py" in suggested or "ament_python" in suggested:
        files.extend(["setup.py", "setup.cfg", f"resource/{package_name}"])
    if "cmakelists.txt" in suggested or "ament_cmake" in suggested:
        files.append("CMakeLists.txt")
    if "cmakelists.txt" not in suggested and "setup.py" not in suggested:
        files.append("CMakeLists.txt")

    for launch_file in inspection.files.launch_files:
        launch_name = Path(launch_file).stem
        files.append(f"launch/{launch_name}.launch.py")

    for python_file in inspection.nodes.python_node_candidates:
        stem = Path(python_file).stem
        files.append(f"{package_name}/{stem}_node.py")
    for cpp_file in inspection.nodes.cpp_node_candidates:
        stem = Path(cpp_file).stem
        files.append(f"src/{stem}_ros2.cpp")

    return tuple(sorted(dict.fromkeys(files)))


def _files_to_keep(path: Path, inspection) -> tuple[str, ...]:
    files: list[str] = []
    files.extend(inspection.files.msg_files)
    files.extend(inspection.files.srv_files)
    files.extend(inspection.files.action_files)
    for name in ("README.md", "README.rst", "README.txt", "LICENSE", "LICENSE.md"):
        if (path / name).is_file():
            files.append(name)
    return tuple(sorted(dict.fromkeys(files)))


def _manual_migration_files(inspection) -> tuple[str, ...]:
    files: list[str] = []
    files.extend(inspection.nodes.python_node_candidates)
    files.extend(inspection.nodes.cpp_node_candidates)
    files.extend(inspection.files.launch_files)
    if inspection.catkin.find_package_catkin or inspection.catkin.catkin_package:
        files.append("CMakeLists.txt")
    return tuple(sorted(dict.fromkeys(files)))


def _dependency_items_to_review(plan: dict[str, object]) -> tuple[str, ...]:
    migration = plan.get("dependency_migration", {})
    if not isinstance(migration, dict):
        return ()
    items: list[str] = []
    for key in (
        "ros2_equivalent_hints",
        "possibly_missing",
        "possibly_unused",
        "manual_review_dependencies",
    ):
        for value in _list(migration.get(key, [])):
            items.append(f"{key}: {value}")
    return tuple(sorted(dict.fromkeys(items)))


def _conflicts(
    *,
    plan: dict[str, object],
    plan_path: Path,
    project_path: Path,
    detection_type: str,
    planned_files: tuple[str, ...],
) -> tuple[str, ...]:
    conflicts: list[str] = []
    if str(plan.get("target", "")).strip().lower() != "ros2":
        conflicts.append("migration plan target is not ros2")
    if not project_path.exists():
        conflicts.append("source project path does not exist")
    elif not project_path.is_dir():
        conflicts.append("source project path is not a directory")

    plan_source = str(plan.get("source_path", ""))
    if plan_source and not _same_existing_path(Path(plan_source), project_path):
        conflicts.append("source project path does not match migration plan source_path")

    if detection_type == "mixed_ros_project":
        conflicts.append("source project has mixed ROS1 and ROS2 build-system signals")

    if project_path.is_dir():
        for relative in planned_files:
            if (project_path / relative).exists():
                conflicts.append(f"target ROS2 file already exists in source tree: {relative}")

    if not plan_path.exists():
        conflicts.append("migration plan path does not exist")

    return tuple(sorted(dict.fromkeys(conflicts)))


def _risks(
    plan: dict[str, object],
    detection_type: str,
    inspection_issues: tuple[str, ...],
    dependency_warnings: tuple[str, ...],
    conflicts: tuple[str, ...],
) -> tuple[str, ...]:
    risks: list[str] = []
    risks.extend(_list(plan.get("risks", [])))
    if detection_type != "ros1_catkin_package":
        risks.append(f"source project detected as {detection_type}; migration preview may be incomplete")
    if inspection_issues:
        risks.append("ROS1 inspection reported issues that require manual review")
    if dependency_warnings:
        risks.append("dependency analyzer reported warnings that require manual review")
    if conflicts:
        risks.append("conflicts must be resolved before any future migration apply workflow")
    if not risks:
        risks.append("runtime behavior remains unvalidated and requires manual ROS2 testing")
    return tuple(sorted(dict.fromkeys(str(item) for item in risks)))


def _suggested_next_steps(conflicts: tuple[str, ...]) -> tuple[str, ...]:
    steps = [
        "Review files requiring manual migration before generating any ROS2 files.",
        "Review dependency items and choose ROS2 equivalents explicitly.",
        "Create a separate branch or copy before manual migration work.",
    ]
    if conflicts:
        steps.insert(0, "Resolve preview conflicts before attempting any future migration apply workflow.")
    steps.append("Use a future migration apply-plan workflow only after reviewing this preview.")
    return tuple(steps)


def _same_existing_path(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return str(left) == str(right)


def _list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []
