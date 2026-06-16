"""No-ROS-required static linter for ROS-style projects."""

from __future__ import annotations

import ast
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from robopilot.detector.project_detector import detect_project


SAFETY_NOTE = (
    "This lint check is static and read-only. RoboPilot did not require ROS, "
    "run catkin_make, run colcon, execute launch files, execute code, or "
    "import user project modules."
)

ROS1_PACKAGE_FORMAT = 2
ROS2_PACKAGE_FORMAT = 3

PACKAGE_XML_REQUIRED = {
    "name", "version", "description", "maintainer", "license",
}


@dataclass(frozen=True)
class LintIssue:
    """A single lint finding."""

    severity: str
    file: str
    rule: str
    message: str
    line: int | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "severity": self.severity,
            "file": self.file,
            "rule": self.rule,
            "message": self.message,
            "line": self.line,
        }


@dataclass(frozen=True)
class LintResult:
    """Aggregated lint result for one project directory."""

    project_path: str
    package_name: str | None
    project_type: str
    issues: tuple[LintIssue, ...]
    error_count: int
    warning_count: int
    info_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "project_path": self.project_path,
            "package_name": self.package_name,
            "project_type": self.project_type,
            "issues": [issue.to_dict() for issue in self.issues],
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "safety_note": SAFETY_NOTE,
        }


def lint_project(project_path: Path) -> LintResult:
    """Run all static lint checks on a project directory."""
    path = Path(project_path).resolve()
    detection = detect_project(path)
    package_name = None
    issues: list[LintIssue] = []

    if not path.exists():
        return LintResult(
            project_path=str(path),
            package_name=None,
            project_type="unknown",
            issues=(LintIssue("error", "", "project.missing", "Project path does not exist"),),
            error_count=1, warning_count=0, info_count=0,
        )
    if not path.is_dir():
        return LintResult(
            project_path=str(path),
            package_name=None,
            project_type="unknown",
            issues=(LintIssue("error", "", "project.not_directory", "Project path is not a directory"),),
            error_count=1, warning_count=0, info_count=0,
        )

    pkg_xml = path / "package.xml"
    if pkg_xml.exists():
        issues.extend(_lint_package_xml(pkg_xml, detection.project_type))
        package_name = _extract_package_name(pkg_xml)

    cmake = path / "CMakeLists.txt"
    if cmake.exists():
        issues.extend(_lint_cmake(cmake, detection.project_type))

    setup_py = path / "setup.py"
    if setup_py.exists():
        issues.extend(_lint_setup_py(setup_py))

    setup_cfg = path / "setup.cfg"
    if setup_cfg.exists():
        issues.extend(_lint_setup_cfg(setup_cfg))

    error_count = sum(1 for i in issues if i.severity == "error")
    warning_count = sum(1 for i in issues if i.severity == "warning")
    info_count = sum(1 for i in issues if i.severity == "info")

    return LintResult(
        project_path=str(path),
        package_name=package_name,
        project_type=detection.project_type,
        issues=tuple(issues),
        error_count=error_count,
        warning_count=warning_count,
        info_count=info_count,
    )


# ---------------------------------------------------------------------------
# package.xml
# ---------------------------------------------------------------------------


def _lint_package_xml(path: Path, project_type: str) -> list[LintIssue]:
    issues: list[LintIssue] = []
    try:
        tree = ET.parse(str(path))
        root = tree.getroot()
    except ET.ParseError as exc:
        issues.append(LintIssue("error", "package.xml", "package_xml.parse_error",
                                f"Cannot parse package.xml: {exc}"))
        return issues

    issues.extend(_check_package_format(root, project_type))
    issues.extend(_check_required_fields(root))
    issues.extend(_check_dependency_consistency(root))
    return issues


def _check_package_format(root: ET.Element, project_type: str) -> list[LintIssue]:
    fmt_str = root.get("format", "")
    try:
        fmt = int(fmt_str)
    except (ValueError, TypeError):
        return [LintIssue("error", "package.xml", "package_xml.missing_format",
                          "Missing or invalid package format attribute")]
    if fmt < ROS1_PACKAGE_FORMAT:
        return [LintIssue("error", "package.xml", "package_xml.bad_format",
                          f"Package format is {fmt}, expected at least {ROS1_PACKAGE_FORMAT}")]
    if "ros2" in project_type and fmt < ROS2_PACKAGE_FORMAT:
        return [LintIssue("warning", "package.xml", "package_xml.ros1_format_for_ros2",
                          f"ROS2 package uses format {fmt}; format {ROS2_PACKAGE_FORMAT} is recommended")]
    return []


def _check_required_fields(root: ET.Element) -> list[LintIssue]:
    issues: list[LintIssue] = []
    present = {child.tag for child in root}
    for field in sorted(PACKAGE_XML_REQUIRED - present):
        issues.append(LintIssue("error", "package.xml", "package_xml.missing_required",
                                f"Missing required field: <{field}>"))
    return issues


def _check_dependency_consistency(root: ET.Element) -> list[LintIssue]:
    issues: list[LintIssue] = []
    dep_tags = {
        "buildtool_depend", "build_depend", "build_export_depend",
        "exec_depend", "depend", "test_depend",
    }
    declared: dict[str, list[str]] = {tag: [] for tag in dep_tags}
    for child in root:
        if child.tag in dep_tags and child.text:
            declared[child.tag].append(child.text.strip())

    # Missing buildtool_depend
    if not declared["buildtool_depend"]:
        issues.append(LintIssue("warning", "package.xml", "package_xml.missing_buildtool",
                                "No <buildtool_depend> declared"))

    return issues


# ---------------------------------------------------------------------------
# CMakeLists.txt
# ---------------------------------------------------------------------------


def _lint_cmake(path: Path, project_type: str) -> list[LintIssue]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    issues: list[LintIssue] = []

    issues.extend(_check_cmake_minimum_version(content, lines))
    issues.extend(_check_cmake_find_package(content))
    issues.extend(_check_cmake_package_macro(content, project_type))
    return issues


def _check_cmake_minimum_version(content: str, lines: list[str]) -> list[LintIssue]:
    if "cmake_minimum_required" not in content:
        return [LintIssue("error", "CMakeLists.txt", "cmake.missing_minimum_version",
                          "Missing cmake_minimum_required")]
    pattern = re.search(r"cmake_minimum_required\s*\(\s*VERSION\s+(\d+\.\d+)", content)
    if pattern:
        version = float(pattern.group(1))
        if version < 3.0:
            return [LintIssue("warning", "CMakeLists.txt", "cmake.low_minimum_version",
                              f"cmake_minimum_required VERSION {pattern.group(1)} is below 3.0")]
    return []


def _check_cmake_find_package(content: str) -> list[LintIssue]:
    if "find_package" not in content:
        return [LintIssue("warning", "CMakeLists.txt", "cmake.no_find_package",
                          "No find_package calls found")]
    return []


def _check_cmake_package_macro(content: str, project_type: str) -> list[LintIssue]:
    issues: list[LintIssue] = []
    if "ament_package" not in content and "catkin_package" not in content:
        if "ros1" in project_type:
            issues.append(LintIssue("warning", "CMakeLists.txt", "cmake.missing_catkin_package",
                                    "No catkin_package() call found in ROS1 project"))
        elif "ros2" in project_type:
            issues.append(LintIssue("warning", "CMakeLists.txt", "cmake.missing_ament_package",
                                    "No ament_package() call found in ROS2 project"))
    return issues


# ---------------------------------------------------------------------------
# setup.py
# ---------------------------------------------------------------------------


def _lint_setup_py(path: Path) -> list[LintIssue]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    issues: list[LintIssue] = []
    try:
        tree = ast.parse(content)
    except SyntaxError:
        issues.append(LintIssue("error", "setup.py", "setup_py.syntax_error",
                                "setup.py has a syntax error and could not be parsed"))
        return issues

    issues.extend(_check_setup_py_package_name(tree, path))
    issues.extend(_check_setup_py_entry_points(tree))
    issues.extend(_check_setup_py_data_files(tree))
    return issues


def _check_setup_py_package_name(tree: ast.Module, path: Path) -> list[LintIssue]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "package_name":
                    return []
    return [LintIssue("warning", "setup.py", "setup_py.missing_package_name",
                      "No package_name variable assigned at module level")]


def _check_setup_py_entry_points(tree: ast.Module) -> list[LintIssue]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _is_setup_call(node):
            for kw in node.keywords:
                if kw.arg == "entry_points" and _is_console_scripts_present(kw.value):
                    return []
    return [LintIssue("warning", "setup.py", "setup_py.missing_entry_points",
                      "No entry_points with console_scripts found in setup() call")]


def _check_setup_py_data_files(tree: ast.Module) -> list[LintIssue]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _is_setup_call(node):
            for kw in node.keywords:
                if kw.arg == "data_files":
                    return []
    return [LintIssue("info", "setup.py", "setup_py.missing_data_files",
                      "No data_files found in setup() call")]


def _is_setup_call(node: ast.Call) -> bool:
    if isinstance(node.func, ast.Name) and node.func.id == "setup":
        return True
    return False


def _is_console_scripts_present(node: ast.expr) -> bool:
    if isinstance(node, ast.Dict):
        for key in node.keys:
            if isinstance(key, ast.Constant) and key.value == "console_scripts":
                return True
    return False


# ---------------------------------------------------------------------------
# setup.cfg
# ---------------------------------------------------------------------------


def _lint_setup_cfg(path: Path) -> list[LintIssue]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    issues: list[LintIssue] = []
    if "[develop]" not in content:
        issues.append(LintIssue("info", "setup.cfg", "setup_cfg.missing_develop",
                                "Missing [develop] section"))
    else:
        if "script_dir" not in content:
            issues.append(LintIssue("warning", "setup.cfg", "setup_cfg.missing_script_dir",
                                    "No script_dir defined in [develop] section"))
    if "[install]" not in content:
        issues.append(LintIssue("info", "setup.cfg", "setup_cfg.missing_install",
                                "Missing [install] section"))
    elif "install_scripts" not in content:
        issues.append(LintIssue("warning", "setup.cfg", "setup_cfg.missing_install_scripts",
                                "No install_scripts in [install] section"))
    return issues


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _extract_package_name(pkg_xml: Path) -> str | None:
    try:
        tree = ET.parse(str(pkg_xml))
        root = tree.getroot()
        name_el = root.find("name")
        if name_el is not None and name_el.text:
            return name_el.text.strip()
    except ET.ParseError:
        pass
    return None
