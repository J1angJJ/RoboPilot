"""Static launch file validation for ROS1 XML and ROS2 Python (v2.1.0 M5)."""

from __future__ import annotations

import ast
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


SAFETY_NOTE = (
    "Launch file validation is static only. RoboPilot did not require ROS, "
    "run catkin_make, run colcon, execute launch files, or execute "
    "generated code."
)

DEPRECATED_ROS1_ATTRS = {"ns", "machine", "env", "cwd"}


@dataclass(frozen=True)
class LaunchIssue:
    """A single launch file lint finding."""

    severity: str
    file: str
    rule: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "severity": self.severity,
            "file": self.file,
            "rule": self.rule,
            "message": self.message,
        }


@dataclass(frozen=True)
class LaunchLintResult:
    """Lint result for one or more launch files."""

    files_checked: tuple[str, ...]
    issues: tuple[LaunchIssue, ...]
    error_count: int
    warning_count: int
    info_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "files_checked": list(self.files_checked),
            "issues": [i.to_dict() for i in self.issues],
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "safety_note": SAFETY_NOTE,
        }


def lint_launch_files(project_path: Path) -> LaunchLintResult:
    """Find and lint all launch files in a project directory."""
    path = Path(project_path)
    if not path.is_dir():
        return LaunchLintResult((), (), 0, 0, 0)

    launch_dirs = [
        p for p in path.rglob("*")
        if p.is_dir() and p.name == "launch"
    ]
    if not launch_dirs:
        # Also check root-level .launch or .launch.py files
        root_launch = list(path.glob("*.launch")) + list(path.glob("*.launch.py"))
        if not root_launch:
            return LaunchLintResult((), (), 0, 0, 0)
        files = [str(f.relative_to(path)) for f in root_launch]
    else:
        files = []
        for ld in launch_dirs:
            for f in sorted(ld.rglob("*.launch")) + sorted(ld.rglob("*.launch.py")):
                try:
                    files.append(str(f.relative_to(path)))
                except ValueError:
                    files.append(str(f))

    all_issues: list[LaunchIssue] = []
    for fname in files:
        fpath = path / fname if (path / fname).exists() else Path(fname)
        if not fpath.exists():
            continue
        if fname.endswith(".py"):
            all_issues.extend(_lint_ros2_launch(fpath, fname))
        else:
            all_issues.extend(_lint_ros1_launch(fpath, fname))

    errors = sum(1 for i in all_issues if i.severity == "error")
    warnings = sum(1 for i in all_issues if i.severity == "warning")
    infos = sum(1 for i in all_issues if i.severity == "info")

    return LaunchLintResult(
        files_checked=tuple(files),
        issues=tuple(all_issues),
        error_count=errors,
        warning_count=warnings,
        info_count=infos,
    )


# ---------------------------------------------------------------------------
# ROS1 XML launch parser
# ---------------------------------------------------------------------------

_PATTERN_ARG = re.compile(r"\$\(arg\s+(\w+)\)")
_PATTERN_FIND = re.compile(r"\$\(find\s+(\w+)\)")


def _lint_ros1_launch(path: Path, relname: str) -> list[LaunchIssue]:
    try:
        tree = ET.parse(str(path))
        root = tree.getroot()
    except ET.ParseError as exc:
        return [LaunchIssue("error", relname, "launch.parse_error",
                            f"Cannot parse launch XML: {exc}")]

    if root.tag not in ("launch", "robot"):
        return [LaunchIssue("warning", relname, "launch.unexpected_root",
                            f"Root element is <{root.tag}>, expected <launch>")]

    issues: list[LaunchIssue] = []
    nodes = root.findall(".//node")
    remaps = root.findall(".//remap")
    params = root.findall(".//param")
    includes = root.findall(".//include")
    groups = root.findall(".//group")
    machines = root.findall(".//machine")

    # Check node declarations
    for node in nodes:
        issues.extend(_check_ros1_node(node, relname))

    # Check remaps reference real nodes
    node_names = {n.get("name", "") for n in nodes}
    for remap in remaps:
        frm = remap.get("from", "")
        to = remap.get("to", "")
        if frm and not to:
            issues.append(LaunchIssue("warning", relname, "launch.ros1.remap_missing_to",
                                      f"Remap from '{frm}' has no 'to' target"))
        if to and not frm:
            issues.append(LaunchIssue("warning", relname, "launch.ros1.remap_missing_from",
                                      f"Remap to '{to}' has no 'from' source"))

    # Check params
    for param in params:
        name = param.get("name", "")
        value = param.get("value", "")
        text = (param.text or "").strip()
        if not name:
            issues.append(LaunchIssue("warning", relname, "launch.ros1.param_no_name",
                                      "A <param> tag is missing a 'name' attribute"))
        if not value and not text:
            issues.append(LaunchIssue("info", relname, "launch.ros1.param_no_value",
                                      f"Parameter '{name}' has no value or text content"))

    # Check args
    for arg in root.findall("arg"):
        arg_name = arg.get("name", "")
        default = arg.get("default", "")
        if arg_name and not default:
            issues.append(LaunchIssue("info", relname, "launch.ros1.arg_no_default",
                                      f"Argument '{arg_name}' has no default value"))

    # Check includes
    for inc in includes:
        inc_file = inc.get("file", "")
        if not inc_file:
            issues.append(LaunchIssue("warning", relname, "launch.ros1.include_no_file",
                                      "An <include> tag has no 'file' attribute"))

    # Deprecated: <machine> tag
    if machines:
        for m in machines:
            issues.append(LaunchIssue("warning", relname, "launch.ros1.deprecated_machine",
                                      f"<machine> tag '{m.get('name', '?')}' is not supported in ROS2. Replace with launch arguments or environment variables."))

    # Deprecated attributes on nodes
    for node in nodes:
        for attr in DEPRECATED_ROS1_ATTRS:
            val = node.get(attr, "")
            if val:
                issues.append(LaunchIssue("warning", relname, "launch.ros1.deprecated_attr",
                                          f"Node '{node.get('name', '?')}' uses deprecated '{attr}' attribute. Migrate to ROS2 equivalents."))

    # Check groups
    if groups:
        for g in groups:
            if g.get("ns"):
                issues.append(LaunchIssue("info", relname, "launch.ros1.group_ns",
                                          "<group ns='...'> namespace grouping: review for ROS2 PushROSNamespace equivalent"))

    return issues


def _check_ros1_node(node: ET.Element, relname: str) -> list[LaunchIssue]:
    issues: list[LaunchIssue] = []
    node_name = node.get("name", "")
    pkg = node.get("pkg", "")
    node_type = node.get("type", "")

    if not node_name:
        issues.append(LaunchIssue("error", relname, "launch.ros1.node_no_name",
                                  "A <node> tag is missing the 'name' attribute"))
    if not pkg:
        issues.append(LaunchIssue("warning", relname, "launch.ros1.node_no_pkg",
                                  f"Node '{node_name}' is missing the 'pkg' attribute"))
    if not node_type:
        issues.append(LaunchIssue("warning", relname, "launch.ros1.node_no_type",
                                  f"Node '{node_name}' is missing the 'type' attribute"))
    return issues


# ---------------------------------------------------------------------------
# ROS2 Python launch parser
# ---------------------------------------------------------------------------

REQUIRED_IMPORTS = {
    "LaunchDescription": "from launch import LaunchDescription",
    "Node": "from launch_ros.actions import Node",
    "DeclareLaunchArgument": "from launch.actions import DeclareLaunchArgument",
}


def _lint_ros2_launch(path: Path, relname: str) -> list[LaunchIssue]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    issues: list[LaunchIssue] = []

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return [LaunchIssue("error", relname, "launch.python_syntax",
                            "Python launch file has syntax errors")]

    # Check for LaunchDescription
    has_ld = any(
        isinstance(node, ast.FunctionDef) and node.name == "generate_launch_description"
        for node in ast.walk(tree)
    )
    if not has_ld:
        issues.append(LaunchIssue("error", relname, "launch.ros2.no_launch_description",
                                  "No generate_launch_description() function found"))

    # Check for Node() calls inside LaunchDescription
    has_node = any(
        isinstance(node, ast.Call)
        and (isinstance(node.func, ast.Name) and node.func.id == "Node"
             or isinstance(node.func, ast.Attribute) and node.func.attr == "Node")
        for node in ast.walk(tree)
    )

    # Check for try/except ImportError as fallback — this is fine for RoboPilot
    has_try = any(
        isinstance(node, ast.Try) for node in ast.walk(tree)
    )

    # Check for DeclareLaunchArgument
    has_arg = any(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        and node.func.id == "DeclareLaunchArgument"
        for node in ast.walk(tree)
    )

    if has_ld and not has_node and not has_try:
        issues.append(LaunchIssue("info", relname, "launch.ros2.no_nodes",
                                  "LaunchDescription has no Node() calls"))

    # Check for param references
    has_params = any(
        isinstance(node, ast.keyword) and node.arg == "parameters"
        for node in ast.walk(tree)
    )
    if has_ld and not has_params and not has_try:
        issues.append(LaunchIssue("info", relname, "launch.ros2.no_parameters",
                                  "No parameters defined in launch nodes"))

    return issues
