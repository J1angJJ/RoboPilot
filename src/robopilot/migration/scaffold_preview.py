"""Read-only ROS2 scaffold preview derived from a migration plan."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from robopilot.migration.ros1_to_ros2 import load_migration_plan, validate_migration_plan
from robopilot.ros1.inspector import ROS1Inspection, inspect_ros1_project


SAFETY_NOTE = (
    "This migration scaffold preview is static and read-only. RoboPilot did not "
    "generate scaffold files, modify the source project, modify the migration "
    "plan, require ROS, require ROS2, run catkin_make, run colcon, execute "
    "launch files, execute code, or import user project modules."
)


@dataclass(frozen=True)
class ScaffoldFile:
    """A planned scaffold file item."""

    path: str
    purpose: str
    source_basis: str
    status: str = "planned"

    def to_dict(self) -> dict[str, str]:
        """Return JSON-ready scaffold item data."""
        return {
            "path": self.path,
            "purpose": self.purpose,
            "source_basis": self.source_basis,
            "status": self.status,
        }


@dataclass(frozen=True)
class MigrationScaffoldPreviewResult:
    """Read-only ROS2 target scaffold preview."""

    plan_path: str
    source_path: str
    target: str
    package_name: str
    target_style: str
    scaffold_files_to_create: tuple[ScaffoldFile, ...]
    placeholder_files: tuple[ScaffoldFile, ...]
    files_requiring_manual_migration: tuple[str, ...]
    interface_files_to_review: tuple[str, ...]
    dependency_items_to_review: tuple[str, ...]
    build_system_notes: tuple[str, ...]
    launch_notes: tuple[str, ...]
    risks: tuple[str, ...]
    conflicts: tuple[str, ...]
    suggested_next_steps: tuple[str, ...]
    safety_note: str

    def to_dict(self) -> dict[str, object]:
        """Return stable JSON-ready data."""
        return {
            "plan_path": self.plan_path,
            "source_path": self.source_path,
            "target": self.target,
            "package_name": self.package_name,
            "target_style": self.target_style,
            "scaffold_files_to_create": [item.to_dict() for item in self.scaffold_files_to_create],
            "placeholder_files": [item.to_dict() for item in self.placeholder_files],
            "files_requiring_manual_migration": list(self.files_requiring_manual_migration),
            "interface_files_to_review": list(self.interface_files_to_review),
            "dependency_items_to_review": list(self.dependency_items_to_review),
            "build_system_notes": list(self.build_system_notes),
            "launch_notes": list(self.launch_notes),
            "risks": list(self.risks),
            "conflicts": list(self.conflicts),
            "suggested_next_steps": list(self.suggested_next_steps),
            "safety_note": self.safety_note,
        }


def preview_migration_scaffold(plan_path: Path) -> MigrationScaffoldPreviewResult:
    """Preview a future ROS2 scaffold from a migration plan without writing files."""
    plan = load_migration_plan(plan_path)
    validation = validate_migration_plan(plan)
    if not validation.is_valid:
        raise ValueError("Invalid migration plan: " + "; ".join(validation.errors))

    source_path = str(plan.get("source_path", ""))
    source = Path(source_path) if source_path else Path()
    inspection = inspect_ros1_project(source) if source_path and source.exists() and source.is_dir() else None
    package_name = _package_name(plan, inspection)
    target = str(plan.get("target", "")).strip().lower()
    target_style = _infer_target_style(plan, inspection)
    scaffold_files = _scaffold_files(plan, package_name, target_style)
    placeholders = _placeholder_files(plan, package_name, target_style, inspection)
    manual_files = _manual_migration_files(plan, inspection)
    interface_files = _interface_files(plan, inspection)
    dependency_items = _dependency_items_to_review(plan)
    build_notes = _build_system_notes(plan, target_style)
    launch_notes = _launch_notes(plan, inspection)
    conflicts = _conflicts(plan=plan, source_path=source_path, target_style=target_style)
    risks = _risks(plan, conflicts, target_style)

    return MigrationScaffoldPreviewResult(
        plan_path=str(plan_path),
        source_path=source_path,
        target=target,
        package_name=package_name,
        target_style=target_style,
        scaffold_files_to_create=scaffold_files,
        placeholder_files=placeholders,
        files_requiring_manual_migration=manual_files,
        interface_files_to_review=interface_files,
        dependency_items_to_review=dependency_items,
        build_system_notes=build_notes,
        launch_notes=launch_notes,
        risks=risks,
        conflicts=conflicts,
        suggested_next_steps=_suggested_next_steps(conflicts, target_style),
        safety_note=SAFETY_NOTE,
    )


def _package_name(plan: dict[str, object], inspection: ROS1Inspection | None) -> str:
    value = str(plan.get("package_name") or "").strip()
    if value:
        return value
    if inspection and inspection.package_name:
        return inspection.package_name
    return "unknown"


def _infer_target_style(plan: dict[str, object], inspection: ROS1Inspection | None) -> str:
    if inspection:
        has_python = bool(inspection.nodes.python_node_candidates or inspection.rospy_usage)
        has_cpp = bool(inspection.nodes.cpp_node_candidates or inspection.roscpp_usage)
        if has_python and has_cpp:
            return "mixed_review_required"
        if has_cpp:
            return "ament_cmake"
        if has_python:
            return "ament_python"

    text = _plan_text(plan)
    python_signals = ("rospy", "rclpy", "ament_python", "setup.py", "python")
    cpp_signals = ("roscpp", "rclcpp", "ament_cmake", "cmakelists.txt", "c++", "cpp")
    has_python = any(signal in text for signal in python_signals)
    has_cpp = any(signal in text for signal in cpp_signals)
    if has_python and has_cpp:
        return "mixed_review_required"
    if has_cpp:
        return "ament_cmake"
    if has_python:
        return "ament_python"
    return "manual_review_required"


def _scaffold_files(
    plan: dict[str, object],
    package_name: str,
    target_style: str,
) -> tuple[ScaffoldFile, ...]:
    files: list[ScaffoldFile] = [
        ScaffoldFile(
            path="package.xml",
            purpose="ROS2 package metadata",
            source_basis="package_xml_migration",
        )
    ]
    if target_style in {"ament_cmake", "mixed_review_required", "manual_review_required"}:
        files.append(
            ScaffoldFile(
                path="CMakeLists.txt",
                purpose="ROS2 ament_cmake build configuration",
                source_basis="build_system_migration",
            )
        )
    if target_style in {"ament_python", "mixed_review_required"}:
        files.extend(
            [
                ScaffoldFile("setup.py", "ROS2 ament_python package setup", "build_system_migration"),
                ScaffoldFile("setup.cfg", "ROS2 ament_python install configuration", "build_system_migration"),
                ScaffoldFile(f"resource/{package_name}", "ROS2 ament_python resource marker", "build_system_migration"),
                ScaffoldFile(f"{package_name}/__init__.py", "Python package marker", "build_system_migration"),
            ]
        )
    return _dedupe_scaffold_files(files)


def _placeholder_files(
    plan: dict[str, object],
    package_name: str,
    target_style: str,
    inspection: ROS1Inspection | None,
) -> tuple[ScaffoldFile, ...]:
    files: list[ScaffoldFile] = []
    python_nodes = inspection.nodes.python_node_candidates if inspection else ()
    cpp_nodes = inspection.nodes.cpp_node_candidates if inspection else ()
    launch_files = inspection.files.launch_files if inspection else ()

    if not python_nodes and target_style == "ament_python":
        python_nodes = ("scripts/todo_node.py",)
    if not cpp_nodes and target_style == "ament_cmake":
        cpp_nodes = ("src/todo_node.cpp",)

    if target_style in {"ament_python", "mixed_review_required"}:
        for path in python_nodes:
            stem = Path(path).stem
            files.append(
                ScaffoldFile(
                    path=f"{package_name}/{stem}_node.py",
                    purpose="TODO placeholder for migrated rclpy node",
                    source_basis=path,
                    status="placeholder",
                )
            )

    if target_style in {"ament_cmake", "mixed_review_required", "manual_review_required"}:
        for path in cpp_nodes:
            stem = Path(path).stem
            files.append(
                ScaffoldFile(
                    path=f"src/{stem}_node.cpp",
                    purpose="TODO placeholder for migrated rclcpp node",
                    source_basis=path,
                    status="placeholder",
                )
            )

    if launch_files or _list(plan.get("launch_migration")):
        for path in launch_files or ("launch/todo.launch",):
            stem = Path(path).stem
            files.append(
                ScaffoldFile(
                    path=f"launch/{stem}.launch.py",
                    purpose="TODO placeholder for ROS2 Python launch file",
                    source_basis=path,
                    status="placeholder",
                )
            )

    if python_nodes or cpp_nodes or launch_files or _list(plan.get("suggested_file_changes")):
        files.append(
            ScaffoldFile(
                path="config/params.yaml",
                purpose="TODO placeholder for ROS2 parameters",
                source_basis="source_code_migration",
                status="placeholder",
            )
        )
    return _dedupe_scaffold_files(files)


def _manual_migration_files(
    plan: dict[str, object],
    inspection: ROS1Inspection | None,
) -> tuple[str, ...]:
    files: list[str] = []
    if inspection:
        files.extend(inspection.nodes.python_node_candidates)
        files.extend(inspection.nodes.cpp_node_candidates)
        files.extend(inspection.files.launch_files)
        if inspection.catkin.find_package_catkin or inspection.catkin.catkin_package:
            files.append("CMakeLists.txt")
    if not files:
        for item in _list(plan.get("source_code_migration")):
            files.append(f"plan_note: {item}")
    return tuple(sorted(dict.fromkeys(str(item) for item in files)))


def _interface_files(
    plan: dict[str, object],
    inspection: ROS1Inspection | None,
) -> tuple[str, ...]:
    if inspection:
        return tuple(
            sorted(
                dict.fromkeys(
                    inspection.files.msg_files
                    + inspection.files.srv_files
                    + inspection.files.action_files
                )
            )
        )
    return tuple(f"plan_note: {item}" for item in _list(plan.get("interface_migration")) if "No msg" not in str(item))


def _dependency_items_to_review(plan: dict[str, object]) -> tuple[str, ...]:
    migration = plan.get("dependency_migration", {})
    if not isinstance(migration, dict):
        return ()
    items: list[str] = []
    for key in (
        "ros2_equivalent_hints",
        "dependency_analyzer_migration_hints",
        "dependency_analyzer_rosdep_hints",
        "possibly_missing",
        "possibly_unused",
        "manual_review_dependencies",
    ):
        for value in _list(migration.get(key, [])):
            items.append(f"{key}: {value}")
    return tuple(sorted(dict.fromkeys(str(item) for item in items)))


def _build_system_notes(plan: dict[str, object], target_style: str) -> tuple[str, ...]:
    notes = [str(item) for item in _list(plan.get("build_system_migration"))]
    if target_style == "mixed_review_required":
        notes.insert(0, "Mixed Python and C++ signals detected; choose the ROS2 build-system strategy manually.")
    if target_style == "manual_review_required":
        notes.insert(0, "Target build system could not be inferred confidently from the migration plan.")
    return tuple(sorted(dict.fromkeys(notes)))


def _launch_notes(plan: dict[str, object], inspection: ROS1Inspection | None) -> tuple[str, ...]:
    notes = [str(item) for item in _list(plan.get("launch_migration"))]
    if inspection and inspection.files.launch_files:
        notes.extend(f"Detected ROS1 launch file for review: {path}" for path in inspection.files.launch_files)
    return tuple(sorted(dict.fromkeys(notes)))


def _conflicts(
    *,
    plan: dict[str, object],
    source_path: str,
    target_style: str,
) -> tuple[str, ...]:
    conflicts: list[str] = []
    if str(plan.get("target", "")).strip().lower() != "ros2":
        conflicts.append("migration plan target is not ros2")
    if not source_path:
        conflicts.append("migration plan source_path is missing")
    elif not Path(source_path).exists():
        conflicts.append("migration plan source_path does not exist on this machine")
    package_name = str(plan.get("package_name") or "").strip()
    if not package_name or package_name == "unknown":
        conflicts.append("migration plan package_name is missing or unknown")
    if str(plan.get("source_project_type", "")) in {"non_ros_project", "unknown"}:
        conflicts.append(f"source project type is {plan.get('source_project_type')}")
    if target_style == "mixed_review_required":
        conflicts.append("mixed Python/C++ package requires manual target-style decision")
    if target_style == "manual_review_required":
        conflicts.append("target package style could not be inferred")
    return tuple(sorted(dict.fromkeys(conflicts)))


def _risks(
    plan: dict[str, object],
    conflicts: tuple[str, ...],
    target_style: str,
) -> tuple[str, ...]:
    risks = [str(item) for item in _list(plan.get("risks"))]
    if target_style in {"mixed_review_required", "manual_review_required"}:
        risks.append("Build-system choice requires manual review before future scaffold generation.")
    if conflicts:
        risks.append("Conflicts must be resolved before any future scaffold generation workflow.")
    if not risks:
        risks.append("Generated scaffold behavior would still require manual ROS2 build and runtime validation.")
    return tuple(sorted(dict.fromkeys(risks)))


def _suggested_next_steps(conflicts: tuple[str, ...], target_style: str) -> tuple[str, ...]:
    steps = [
        "Review this scaffold preview before requesting future scaffold generation.",
        "Review placeholder files and manual migration files before editing source code.",
        "Review dependency items and choose ROS2 equivalents explicitly.",
    ]
    if target_style == "mixed_review_required":
        steps.insert(0, "Decide whether the migrated package should use ament_cmake, ament_python, or a split package structure.")
    if conflicts:
        steps.insert(0, "Resolve scaffold preview conflicts before any future generation workflow.")
    steps.append("Use a future migration scaffold generation command only after reviewing this preview.")
    return tuple(dict.fromkeys(steps))


def _plan_text(plan: dict[str, object]) -> str:
    parts: list[str] = []
    for value in plan.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif isinstance(value, dict):
            parts.extend(_flatten_dict_text(value))
    return " ".join(parts).lower()


def _flatten_dict_text(data: dict[str, object]) -> list[str]:
    parts: list[str] = []
    for value in data.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif isinstance(value, dict):
            parts.extend(_flatten_dict_text(value))
    return parts


def _dedupe_scaffold_files(items: list[ScaffoldFile]) -> tuple[ScaffoldFile, ...]:
    by_path: dict[str, ScaffoldFile] = {}
    for item in items:
        by_path.setdefault(item.path, item)
    return tuple(by_path[path] for path in sorted(by_path))


def _list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []
