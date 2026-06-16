"""Python API wrappers for RoboPilot static analysis features."""

from __future__ import annotations

from robopilot.api.models import PathLike, StructuredResult, normalize_path, to_structured_result
from robopilot.deps.analyzer import DependencyAnalysis, analyze_dependencies
from robopilot.detector.project_detector import ProjectDetection, detect_project
from robopilot.inspector.project_inspector import ProjectInspection, inspect_project
from robopilot.lint import LintResult, lint_project
from robopilot.report.project_report import generate_project_report, write_project_report
from robopilot.ros1.inspector import ROS1Inspection, inspect_ros1_project
from robopilot.ros2.inspector import ROS2Inspection, inspect_ros2_project


def detect_project_type(
    project_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | ProjectDetection:
    """Detect a project type without printing or requiring ROS."""
    result = detect_project(normalize_path(project_path))
    return to_structured_result(result) if as_dict else result


def inspect_project_static(
    project_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | ProjectInspection:
    """Inspect a RoboPilot-generated or ROS-style project statically."""
    result = inspect_project(normalize_path(project_path))
    return to_structured_result(result) if as_dict else result


def inspect_ros1_project_static(
    project_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | ROS1Inspection:
    """Inspect a ROS1 catkin package statically without requiring ROS."""
    result = inspect_ros1_project(normalize_path(project_path))
    return to_structured_result(result) if as_dict else result


def inspect_ros2_project_static(
    project_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | ROS2Inspection:
    """Inspect a ROS2 ament package statically without requiring ROS2."""
    result = inspect_ros2_project(normalize_path(project_path))
    return to_structured_result(result) if as_dict else result


def analyze_project_dependencies(
    project_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | DependencyAnalysis:
    """Analyze dependencies from static project files."""
    result = analyze_dependencies(normalize_path(project_path))
    return to_structured_result(result) if as_dict else result


def export_project_report(project_path: PathLike, output_path: PathLike | None = None) -> str:
    """Generate a Markdown project report, writing it only when output_path is provided."""
    normalized_project_path = normalize_path(project_path)
    if output_path is None:
        return generate_project_report(normalized_project_path)
    return write_project_report(normalized_project_path, normalize_path(output_path))


def lint_project_api(
    project_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | LintResult:
    """Run static lint checks on a ROS-style project without modifying files."""
    result = lint_project(normalize_path(project_path))
    return to_structured_result(result) if as_dict else result
