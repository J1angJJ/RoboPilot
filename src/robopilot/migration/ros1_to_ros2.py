"""Static ROS1-to-ROS2 migration planning."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from robopilot.deps.analyzer import DependencyAnalysis, analyze_dependencies
from robopilot.detector.project_detector import detect_project
from robopilot.ros1.inspector import ROS1Inspection, inspect_ros1_project


GENERATED_BY = "RoboPilot ROS1ToROS2MigrationPlan"
SUPPORTED_TARGETS = {"ros2"}
SUPPORTED_FORMATS = {"yaml", "json"}
LIST_FIELDS = {
    "package_xml_migration",
    "build_system_migration",
    "source_code_migration",
    "launch_migration",
    "interface_migration",
    "suggested_file_changes",
    "manual_review_items",
    "risks",
    "suggested_next_steps",
}
SAFETY_NOTE = (
    "This migration plan is generated from static inspection only. RoboPilot "
    "did not modify source files, generate migrated files, validate runtime "
    "behavior, require ROS, run catkin_make, run colcon, execute launch files, "
    "execute code, or import user project modules."
)

TOP_LEVEL_FIELDS = (
    "generated_by",
    "source_path",
    "target",
    "source_project_type",
    "package_name",
    "confidence",
    "summary",
    "package_xml_migration",
    "build_system_migration",
    "source_code_migration",
    "launch_migration",
    "interface_migration",
    "dependency_migration",
    "suggested_file_changes",
    "manual_review_items",
    "risks",
    "suggested_next_steps",
    "safety_note",
)


@dataclass(frozen=True)
class MigrationPlanValidationResult:
    """Validation result for a serialized migration plan."""

    is_valid: bool
    errors: tuple[str, ...]


@dataclass(frozen=True)
class ROS1ToROS2MigrationPlan:
    """Deterministic static migration plan."""

    generated_by: str
    source_path: str
    target: str
    source_project_type: str
    package_name: str
    confidence: str
    summary: str
    package_xml_migration: tuple[str, ...]
    build_system_migration: tuple[str, ...]
    source_code_migration: tuple[str, ...]
    launch_migration: tuple[str, ...]
    interface_migration: tuple[str, ...]
    dependency_migration: dict[str, object]
    suggested_file_changes: tuple[str, ...]
    manual_review_items: tuple[str, ...]
    risks: tuple[str, ...]
    suggested_next_steps: tuple[str, ...]
    safety_note: str

    def to_dict(self) -> dict[str, object]:
        """Return stable JSON-ready data."""
        return {
            "generated_by": self.generated_by,
            "source_path": self.source_path,
            "target": self.target,
            "source_project_type": self.source_project_type,
            "package_name": self.package_name,
            "confidence": self.confidence,
            "summary": self.summary,
            "package_xml_migration": list(self.package_xml_migration),
            "build_system_migration": list(self.build_system_migration),
            "source_code_migration": list(self.source_code_migration),
            "launch_migration": list(self.launch_migration),
            "interface_migration": list(self.interface_migration),
            "dependency_migration": self.dependency_migration,
            "suggested_file_changes": list(self.suggested_file_changes),
            "manual_review_items": list(self.manual_review_items),
            "risks": list(self.risks),
            "suggested_next_steps": list(self.suggested_next_steps),
            "safety_note": self.safety_note,
        }


def generate_migration_plan(source_path: Path, target: str = "ros2") -> ROS1ToROS2MigrationPlan:
    """Generate a static ROS1-to-ROS2 migration plan."""
    normalized_target = target.strip().lower()
    if normalized_target not in SUPPORTED_TARGETS:
        raise ValueError("Unsupported migration target. Use 'ros2'.")

    path = Path(source_path)
    detection = detect_project(path)
    inspection = inspect_ros1_project(path)
    dependencies = analyze_dependencies(path)
    package_name = inspection.package_name or _package_name_from_path(path)
    confidence = _confidence(detection.project_type, inspection)

    return ROS1ToROS2MigrationPlan(
        generated_by=GENERATED_BY,
        source_path=str(source_path),
        target=normalized_target,
        source_project_type=detection.project_type,
        package_name=package_name,
        confidence=confidence,
        summary=_summary(detection.project_type, package_name, confidence),
        package_xml_migration=_package_xml_migration(inspection),
        build_system_migration=_build_system_migration(inspection),
        source_code_migration=_source_code_migration(inspection),
        launch_migration=_launch_migration(inspection),
        interface_migration=_interface_migration(inspection),
        dependency_migration=_dependency_migration(dependencies),
        suggested_file_changes=_suggested_file_changes(inspection),
        manual_review_items=_manual_review_items(inspection, dependencies),
        risks=_risks(detection.project_type, inspection, dependencies),
        suggested_next_steps=_suggested_next_steps(detection.project_type),
        safety_note=SAFETY_NOTE,
    )


def write_migration_plan(
    *,
    source_path: Path,
    target: str,
    output_path: Path,
    output_format: str = "yaml",
) -> ROS1ToROS2MigrationPlan:
    """Write a static migration plan without modifying the source project."""
    normalized_format = output_format.strip().lower()
    if normalized_format not in SUPPORTED_FORMATS:
        raise ValueError("Unsupported migration plan format. Use 'yaml' or 'json'.")
    plan = generate_migration_plan(source_path, target)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if normalized_format == "json":
        output_path.write_text(json.dumps(plan.to_dict(), indent=2) + "\n", encoding="utf-8")
    else:
        output_path.write_text(migration_plan_to_yaml(plan), encoding="utf-8")
    return plan


def load_migration_plan(plan_path: Path) -> dict[str, object]:
    """Load a JSON or RoboPilot YAML-like migration plan."""
    content = plan_path.read_text(encoding="utf-8-sig")
    if plan_path.suffix.lower() == ".json" or content.lstrip().startswith("{"):
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("Migration plan JSON must be an object.")
        return data
    return migration_plan_from_yaml(content)


def validate_migration_plan(plan: dict[str, object]) -> MigrationPlanValidationResult:
    """Validate required migration plan fields and basic types."""
    errors: list[str] = []
    for field in TOP_LEVEL_FIELDS:
        if field not in plan:
            errors.append(f"{field} is required.")

    for field in LIST_FIELDS:
        if field in plan and not isinstance(plan[field], list):
            errors.append(f"{field} must be a list.")

    for field in (
        "generated_by",
        "source_path",
        "target",
        "source_project_type",
        "package_name",
        "confidence",
        "summary",
        "safety_note",
    ):
        if field in plan and not isinstance(plan[field], str):
            errors.append(f"{field} must be a string.")

    if "dependency_migration" in plan and not isinstance(plan["dependency_migration"], dict):
        errors.append("dependency_migration must be a mapping.")

    if str(plan.get("target", "")).strip().lower() not in SUPPORTED_TARGETS:
        errors.append("target must be ros2.")

    return MigrationPlanValidationResult(is_valid=not errors, errors=tuple(errors))


def migration_plan_to_yaml(plan: ROS1ToROS2MigrationPlan) -> str:
    """Serialize a migration plan using RoboPilot's small YAML-like subset."""
    return _to_yaml(plan.to_dict(), TOP_LEVEL_FIELDS)


def migration_plan_from_yaml(content: str) -> dict[str, object]:
    """Parse RoboPilot's small migration-plan YAML-like subset."""
    lines = [
        (len(raw_line) - len(raw_line.lstrip(" ")), raw_line.strip())
        for raw_line in content.splitlines()
        if raw_line.strip() and not raw_line.lstrip().startswith("#")
    ]
    data: dict[str, object] = {}
    current_top: str | None = None
    current_second: str | None = None
    current_third: str | None = None

    for index, (indent, stripped) in enumerate(lines):
        next_stripped = lines[index + 1][1] if index + 1 < len(lines) else ""

        if indent == 0:
            key, value = _split_key_value(stripped)
            current_top = key
            current_second = None
            current_third = None
            if value:
                data[key] = _unquote(value)
            elif next_stripped.startswith("- "):
                data[key] = []
            else:
                data[key] = {}
            continue

        if current_top is None:
            raise ValueError(f"Unexpected indented line outside a section: {stripped}")

        if indent == 2:
            if stripped.startswith("- "):
                target = data.setdefault(current_top, [])
                if not isinstance(target, list):
                    raise ValueError(f"Expected list field: {current_top}")
                target.append(_unquote(stripped[2:].strip()))
                continue

            key, value = _split_key_value(stripped)
            parent = data.setdefault(current_top, {})
            if not isinstance(parent, dict):
                raise ValueError(f"Expected mapping field: {current_top}")
            current_second = key
            current_third = None
            if value:
                parent[key] = _unquote(value)
            elif next_stripped.startswith("- "):
                parent[key] = []
            else:
                parent[key] = {}
            continue

        if indent == 4:
            parent = data.get(current_top)
            if not isinstance(parent, dict) or current_second is None:
                raise ValueError(f"Unexpected nested line: {stripped}")
            if stripped.startswith("- "):
                target = parent.setdefault(current_second, [])
                if not isinstance(target, list):
                    raise ValueError(f"Expected list field: {current_second}")
                target.append(_unquote(stripped[2:].strip()))
                continue

            key, value = _split_key_value(stripped)
            child = parent.setdefault(current_second, {})
            if not isinstance(child, dict):
                raise ValueError(f"Expected mapping field: {current_second}")
            current_third = key
            child[key] = _unquote(value) if value else []
            continue

        if indent == 6:
            parent = data.get(current_top)
            if not isinstance(parent, dict) or current_second is None or current_third is None:
                raise ValueError(f"Unexpected deeply nested line: {stripped}")
            child = parent.get(current_second)
            if not isinstance(child, dict):
                raise ValueError(f"Expected nested mapping field: {current_second}")
            target = child.setdefault(current_third, [])
            if not isinstance(target, list):
                raise ValueError(f"Expected list field: {current_third}")
            if not stripped.startswith("- "):
                raise ValueError(f"Expected list item: {stripped}")
            target.append(_unquote(stripped[2:].strip()))
            continue

        raise ValueError(f"Unsupported indentation in migration plan: {stripped}")

    return data


def _confidence(project_type: str, inspection: ROS1Inspection) -> str:
    if project_type == "ros1_catkin_package" and inspection.package_name:
        return "high"
    if project_type in {"mixed_ros_project", "unknown"}:
        return "medium"
    return "low"


def _summary(project_type: str, package_name: str, confidence: str) -> str:
    if project_type == "ros1_catkin_package":
        return f"Static migration plan for ROS1 catkin package '{package_name}' toward ROS2."
    return (
        f"Static migration plan generated with {confidence} confidence because "
        f"the source project was classified as {project_type}."
    )


def _package_xml_migration(inspection: ROS1Inspection) -> tuple[str, ...]:
    target_style = _target_style(inspection)
    suggestions = [
        "Migrate package.xml toward ROS2 package format 3 if the project still uses ROS1 package metadata.",
        f"Replace catkin buildtool dependency with {target_style} build metadata after choosing the final ROS2 package style.",
        "Review build, exec, run, and test dependencies and move ROS2 runtime dependencies to exec_depend where appropriate.",
        "Check ROS2 equivalents for every ROS1 dependency before editing package.xml.",
    ]
    if "catkin" in inspection.dependencies.buildtool:
        suggestions.append("Remove <buildtool_depend>catkin</buildtool_depend> during ROS2 migration.")
    return tuple(suggestions)


def _build_system_migration(inspection: ROS1Inspection) -> tuple[str, ...]:
    suggestions: list[str] = []
    if inspection.nodes.cpp_node_candidates:
        suggestions.append("Migrate catkin CMakeLists.txt to ROS2 ament_cmake for C++ nodes.")
    if inspection.nodes.python_node_candidates and not inspection.nodes.cpp_node_candidates:
        suggestions.append("Migrate Python package structure toward ament_python.")
    if inspection.nodes.python_node_candidates and inspection.nodes.cpp_node_candidates:
        suggestions.append("Use ament_cmake as the primary ROS2 build system and review Python script installation rules.")
    suggestions.extend(
        [
            "Replace catkin_package() with ament_package().",
            "Replace find_package(catkin REQUIRED COMPONENTS ...) with explicit ROS2-style find_package(...) calls.",
            "Review install rules for Python scripts, C++ executables, launch files, and interface files.",
        ]
    )
    return tuple(dict.fromkeys(suggestions))


def _source_code_migration(inspection: ROS1Inspection) -> tuple[str, ...]:
    suggestions: list[str] = []
    if inspection.nodes.python_node_candidates or inspection.rospy_usage:
        suggestions.extend(
            [
                "rospy nodes should be migrated toward rclpy.",
                "rospy.init_node, rospy.Publisher, rospy.Subscriber, rospy.Rate, and rospy.spin patterns require manual migration.",
            ]
        )
    if inspection.nodes.cpp_node_candidates or inspection.roscpp_usage:
        suggestions.extend(
            [
                "roscpp nodes should be migrated toward rclcpp.",
                "ros::init, ros::NodeHandle, ros::Publisher, ros::Subscriber, and ros::spin patterns require manual migration.",
            ]
        )
    suggestions.append("Review parameters, time APIs, logging APIs, QoS settings, callback behavior, and spin behavior.")
    return tuple(dict.fromkeys(suggestions))


def _launch_migration(inspection: ROS1Inspection) -> tuple[str, ...]:
    if not inspection.files.launch_files:
        return ("No ROS1 launch files were detected; create ROS2 launch files only if the migrated package needs them.",)
    return (
        "Migrate ROS1 XML launch files toward ROS2 Python launch files.",
        "Review node declarations, remaps, params, namespaces, arguments, and environment assumptions manually.",
        "Create launch/*.launch.py equivalents for detected ROS1 launch files.",
    )


def _interface_migration(inspection: ROS1Inspection) -> tuple[str, ...]:
    notes: list[str] = []
    if inspection.files.msg_files:
        notes.append("msg files are likely reusable with ROS2 interface review.")
    if inspection.files.srv_files:
        notes.append("srv files are likely reusable with ROS2 interface review.")
    if inspection.files.action_files:
        notes.append("action files require ROS2 action interface review.")
    if inspection.files.msg_files or inspection.files.srv_files or inspection.files.action_files:
        notes.append("Migrate message generation rules from catkin to the ROS2 build system.")
    if not notes:
        notes.append("No msg/srv/action files were detected.")
    return tuple(notes)


def _dependency_migration(dependencies: DependencyAnalysis) -> dict[str, object]:
    declared = dependencies.declared_dependencies.to_dict()
    detected = {
        "inferred_dependencies": list(dependencies.inferred_dependencies),
        "python_imports": list(dependencies.detected_usage.python_imports),
        "cpp_includes": list(dependencies.detected_usage.cpp_includes),
        "catkin_components": list(dependencies.detected_usage.catkin_components),
    }
    all_deps = sorted(
        set(dependencies.inferred_dependencies)
        | set(dependencies.declared_dependencies.build)
        | set(dependencies.declared_dependencies.exec)
        | set(dependencies.declared_dependencies.run)
    )
    return {
        "declared_ros1_dependencies": declared,
        "detected_usage_dependencies": detected,
        "possibly_missing": list(dependencies.possibly_missing),
        "possibly_unused": list(dependencies.possibly_unused),
        "ros2_equivalent_hints": [_ros2_dependency_hint(dep) for dep in all_deps],
        "dependency_analyzer_migration_hints": list(dependencies.migration_hints),
        "dependency_analyzer_rosdep_hints": list(dependencies.rosdep_hints),
        "manual_review_dependencies": _manual_review_dependencies(all_deps),
    }


def _suggested_file_changes(inspection: ROS1Inspection) -> tuple[str, ...]:
    changes = [
        "create ROS2-style package.xml",
    ]
    if inspection.nodes.cpp_node_candidates:
        changes.append("create ROS2 ament_cmake CMakeLists.txt")
    elif inspection.nodes.python_node_candidates:
        changes.append("create ROS2 ament_python setup.py, setup.cfg, and resource marker")
    else:
        changes.append("choose ROS2 ament_cmake or ament_python after reviewing source files")
    if inspection.files.launch_files:
        changes.append("create launch/*.launch.py equivalents")
    if inspection.files.python_files:
        changes.append("migrate scripts/*.py to ROS2 rclpy node structure")
    if inspection.files.cpp_files:
        changes.append("migrate src/*.cpp to rclcpp node structure")
    if inspection.files.msg_files or inspection.files.srv_files or inspection.files.action_files:
        changes.append("keep msg/srv/action files for ROS2 interface review")
    return tuple(changes)


def _manual_review_items(
    inspection: ROS1Inspection,
    dependencies: DependencyAnalysis,
) -> tuple[str, ...]:
    items = [
        "custom CMake macros or non-standard catkin logic",
        "parameters, namespace behavior, remapping behavior, timing behavior, and QoS behavior",
        "hardware drivers, serial devices, sensors, and platform-specific assumptions",
        "dependencies without obvious ROS2 equivalents",
    ]
    if inspection.files.launch_files:
        items.append("dynamic launch logic and launch-time substitutions")
    if inspection.files.msg_files or inspection.files.srv_files or inspection.files.action_files:
        items.append("custom messages, services, and actions")
    if dependencies.possibly_missing or dependencies.possibly_unused:
        items.append("possibly missing or unused dependencies from static dependency analysis")
    return tuple(dict.fromkeys(items))


def _risks(
    project_type: str,
    inspection: ROS1Inspection,
    dependencies: DependencyAnalysis,
) -> tuple[str, ...]:
    risks: list[str] = []
    if project_type != "ros1_catkin_package":
        risks.append(f"source project was classified as {project_type}; ROS1 migration confidence is limited")
    if inspection.issues:
        risks.append("ROS1 inspection reported package structure issues that may affect migration planning")
    if dependencies.warnings:
        risks.append("dependency analyzer reported warnings that should be reviewed before migration")
    if inspection.files.action_files:
        risks.append("ROS1 action migration can require manual ROS2 action API review")
    if not risks:
        risks.append("runtime behavior is unvalidated; manual ROS2 build and runtime testing will still be required")
    return tuple(risks)


def _suggested_next_steps(project_type: str) -> tuple[str, ...]:
    steps = [
        "Review this migration plan before editing files.",
        "Run robopilot migrate-plan-validate --plan <migration_plan.yaml> to check the saved plan.",
        "Run robopilot migrate-scaffold-preview --plan <migration_plan.yaml> to preview the ROS2 scaffold.",
        "Run robopilot deps on the source package and review dependency hints.",
        "Create a separate branch or copy before manually migrating files.",
    ]
    if project_type != "ros1_catkin_package":
        steps.insert(0, "Confirm the source package is really a ROS1 catkin package before migration.")
    steps.append("Use robopilot migrate-scaffold only after reviewing the plan and scaffold preview.")
    return tuple(steps)


def _target_style(inspection: ROS1Inspection) -> str:
    if inspection.nodes.cpp_node_candidates:
        return "ament_cmake"
    if inspection.nodes.python_node_candidates:
        return "ament_python"
    return "ament_cmake or ament_python"


def _ros2_dependency_hint(dep: str) -> str:
    mapping = {
        "catkin": "catkin -> replace with ament_cmake or ament_python",
        "rospy": "rospy -> rclpy",
        "roscpp": "roscpp -> rclcpp",
        "message_generation": "message_generation -> rosidl_default_generators",
        "message_runtime": "message_runtime -> rosidl_default_runtime",
        "tf": "tf -> tf2_ros / tf2",
    }
    if dep in mapping:
        return mapping[dep]
    return f"{dep} -> check ROS2 package availability and API differences"


def _manual_review_dependencies(dependencies: list[str]) -> list[str]:
    obvious = {
        "rospy",
        "roscpp",
        "rclpy",
        "rclcpp",
        "std_msgs",
        "sensor_msgs",
        "geometry_msgs",
        "message_generation",
        "message_runtime",
    }
    return [dep for dep in dependencies if dep not in obvious]


def _package_name_from_path(path: Path) -> str:
    return path.name if path.name else "unknown"


def _split_key_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"Expected key/value line: {line}")
    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def _to_yaml(data: dict[str, object], field_order: tuple[str, ...]) -> str:
    lines: list[str] = []
    for field in field_order:
        _append_yaml(lines, field, data.get(field), indent=0)
    return "\n".join(lines) + "\n"


def _append_yaml(lines: list[str], key: str, value: object, *, indent: int) -> None:
    prefix = " " * indent
    if isinstance(value, dict):
        lines.append(f"{prefix}{key}:")
        for child_key, child_value in value.items():
            _append_yaml(lines, str(child_key), child_value, indent=indent + 2)
        return
    if isinstance(value, (list, tuple)):
        lines.append(f"{prefix}{key}:")
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{prefix}  -")
                for child_key, child_value in item.items():
                    _append_yaml(lines, str(child_key), child_value, indent=indent + 4)
            else:
                lines.append(f'{prefix}  - "{_quote(str(item))}"')
        return
    lines.append(f'{prefix}{key}: "{_quote(str(value or ""))}"')


def _quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    return value.replace('\\"', '"').replace("\\\\", "\\")
