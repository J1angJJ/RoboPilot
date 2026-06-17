"""No-ROS-required static linter for ROS-style projects."""

from __future__ import annotations

import ast
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from robopilot.detector.project_detector import detect_project
from robopilot.launch_lint import lint_launch_files


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

    detection = detect_project(path)

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

    # Integrate launch file checks
    launch_result = lint_launch_files(path)
    for li in launch_result.issues:
        issues.append(LintIssue(li.severity, li.file, li.rule, li.message))

    # v2.2.0 M12: cross-file consistency checks
    issues.extend(_cross_check_cmake_vs_package_xml(path))
    issues.extend(_cross_check_setup_vs_nodes(path, package_name))
    issues.extend(_check_python_imports_vs_deps(path))

    # v2.2.0 M12: ROS2-specific checks
    issues.extend(_check_ros2_node_patterns(path, package_name))

    # v2.2.0 M12: load lintrc and filter/override
    lintrc = _load_lintrc(path)
    issues = _apply_lintrc(issues, lintrc)

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
# M12: Cross-file consistency
# ---------------------------------------------------------------------------


def _cross_check_cmake_vs_package_xml(path: Path) -> list[LintIssue]:
    """Check that CMake find_package calls match package.xml dependencies."""
    cmake = path / "CMakeLists.txt"
    pkg_xml = path / "package.xml"
    if not cmake.exists() or not pkg_xml.exists():
        return []

    cmake_text = cmake.read_text(encoding="utf-8", errors="ignore")
    xml_deps = _extract_xml_deps(pkg_xml)
    if not xml_deps:
        return []

    issues: list[LintIssue] = []
    import re
    found = set(re.findall(r"find_package\s*\(\s*(\w+)", cmake_text))

    # Check xml deps missing from cmake
    for dep in sorted(xml_deps):
        if dep in ("catkin", "ament_cmake", "ament_python", "message_generation", "message_runtime"):
            continue
        if dep not in found:
            issues.append(LintIssue(
                "warning", "package.xml", "cross.xml_dep_not_in_cmake",
                f"<depend>{dep}</depend> in package.xml has no matching find_package({dep}) in CMakeLists.txt"
            ))

    # Check cmake finds missing from xml
    for dep in sorted(found):
        if dep in ("ament_cmake", "catkin", "rosidl_default_generators", "rosidl_default_runtime"):
            continue
        if dep.lower() in ("project",):  # cmake project() call, not a package dep
            continue
        if dep not in xml_deps:
            issues.append(LintIssue(
                "info", "CMakeLists.txt", "cross.cmake_find_not_in_xml",
                f"find_package({dep}) in CMakeLists.txt has no matching <depend> in package.xml"
            ))

    return issues


def _cross_check_setup_vs_nodes(path: Path, package_name: str | None) -> list[LintIssue]:
    """Check setup.py entry_points reference real node files."""
    setup = path / "setup.py"
    if not setup.exists() or not package_name:
        return []
    try:
        content = setup.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
    except SyntaxError:
        return []

    issues: list[LintIssue] = []
    # Find console_scripts entries
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k in node.keys:
                if isinstance(k, ast.Constant) and k.value == "console_scripts":
                    if isinstance(node, ast.Dict):
                        for v in node.values:
                            if isinstance(v, ast.List):
                                for item in v.elts:
                                    if isinstance(item, ast.Constant) and isinstance(item.value, str):
                                        entry = item.value
                                        # entry format: "exec_name = pkg.module:main"
                                        parts = entry.split("=")
                                        if len(parts) == 2:
                                            mod_ref = parts[1].strip().split(":")[0].strip()
                                            mod_file = mod_ref.split(".")[-1] + ".py" if "." in mod_ref else mod_ref + ".py"
                                            node_path = path / package_name / mod_file
                                            if not node_path.exists():
                                                issues.append(LintIssue(
                                                    "error", "setup.py", "cross.entry_point_missing_node",
                                                    f"console_script '{entry}' references '{mod_file}' but file does not exist at {package_name}/{mod_file}"
                                                ))
    return issues


def _check_python_imports_vs_deps(path: Path) -> list[LintIssue]:
    """Check Python imports in node files against package.xml dependencies."""
    pkg_xml = path / "package.xml"
    if not pkg_xml.exists():
        return []

    xml_deps = _extract_xml_deps(pkg_xml)
    if not xml_deps:
        return []

    issues: list[LintIssue] = []
    known_ros_imports = {
        "rclpy", "rclcpp", "std_msgs", "sensor_msgs", "geometry_msgs",
        "nav_msgs", "trajectory_msgs", "visualization_msgs", "shape_msgs",
        "diagnostic_msgs", "actionlib_msgs", "tf2_msgs", "tf2_ros", "tf2_geometry_msgs",
        "cv_bridge", "image_geometry", "image_transport",
    }
    # Scan Python files in the package directory
    pkg_dir = None
    for child in path.iterdir():
        if child.is_dir() and (child / "__init__.py").exists():
            pkg_dir = child
            break
    if not pkg_dir:
        return issues

    for py_file in pkg_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    _check_import(alias.name, xml_deps, known_ros_imports, py_file, issues, path)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    _check_import(node.module, xml_deps, known_ros_imports, py_file, issues, path)

    return issues


def _check_import(
    mod: str,
    xml_deps: set[str],
    known: set[str],
    py_file: Path,
    issues: list[LintIssue],
    root: Path,
) -> None:
    top = mod.split(".")[0]
    if top not in known:
        return
    if top in xml_deps or top in ("rclpy", "std_msgs"):
        return
    try:
        rel = str(py_file.relative_to(root))
    except ValueError:
        rel = py_file.name
    issues.append(LintIssue(
        "warning", rel, "cross.import_not_in_xml",
        f"Python imports '{top}' but package.xml has no <depend>{top}</depend>"
    ))


# ---------------------------------------------------------------------------
# M12: ROS2-specific checks
# ---------------------------------------------------------------------------


def _check_ros2_node_patterns(path: Path, package_name: str | None) -> list[LintIssue]:
    """Check ROS2 node conventions in Python node files."""
    issues: list[LintIssue] = []
    if not package_name:
        return issues
    pkg_dir = path / package_name
    if not pkg_dir.is_dir():
        return issues

    for py_file in pkg_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)
        except SyntaxError:
            continue

        # Check for rclpy.init() call
        has_init = any(
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == "init"
            for n in ast.walk(tree)
            if isinstance(n, ast.Call)
        )
        # Check if Node subclass is defined
        has_node_class = any(
            isinstance(n, ast.ClassDef)
            for n in ast.walk(tree)
        )
        if has_node_class and not has_init:
            # Check if it uses the offline fallback pattern (try/except ImportError)
            has_try_import = "try:" in content and "ImportError" in content
            if not has_try_import:
                try:
                    rel = str(py_file.relative_to(path))
                except ValueError:
                    rel = py_file.name
                issues.append(LintIssue(
                    "info", rel, "ros2.missing_rclpy_init",
                    "Node class defined but no rclpy.init() call found. Consider adding rclpy.init() before node construction."
                ))

        # Check QoS patterns
        if "QoS" in content or "qos" in content.lower():
            # Check for common QoS profile usage
            has_qos_profile = any(
                isinstance(n, ast.Call) and (
                    isinstance(n.func, ast.Name) and "QoS" in (n.func.id if hasattr(n.func, 'id') else "")
                )
                for n in ast.walk(tree)
            )

    return issues


# ---------------------------------------------------------------------------
# M12: lintrc configuration
# ---------------------------------------------------------------------------


def _load_lintrc(path: Path) -> dict[str, object]:
    """Load .robopilot/lintrc.yaml config if present."""
    lintrc = path / ".robopilot" / "lintrc.yaml"
    if not lintrc.exists():
        return {}
    try:
        content = lintrc.read_text(encoding="utf-8")
        return _parse_lintrc(content)
    except Exception:
        return {}


def _parse_lintrc(content: str) -> dict[str, object]:
    """Parse a simple lintrc YAML-like config."""
    result: dict[str, object] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip().strip('"').strip("'")
            result[key] = value
    return result


def _apply_lintrc(issues: list[LintIssue], lintrc: dict[str, object]) -> list[LintIssue]:
    """Filter/override issues based on lintrc config."""
    if not lintrc:
        return issues

    disabled = set()
    severity_map: dict[str, str] = {}

    for k, v in lintrc.items():
        k = str(k)
        v = str(v)
        if k.startswith("disable_") and v.lower() in ("true", "yes", "1"):
            disabled.add(k[len("disable_"):])
        elif k.startswith("severity_"):
            rule = k[len("severity_"):]
            if v in ("error", "warning", "info", "off"):
                severity_map[rule] = v

    filtered: list[LintIssue] = []
    for issue in issues:
        if issue.rule in disabled:
            continue
        if issue.rule in severity_map:
            sev = severity_map[issue.rule]
            if sev == "off":
                continue
            filtered.append(LintIssue(sev, issue.file, issue.rule, issue.message, issue.line))
        else:
            filtered.append(issue)

    return filtered


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _extract_xml_deps(pkg_xml: Path) -> set[str]:
    deps: set[str] = set()
    try:
        tree = ET.parse(str(pkg_xml))
        for child in tree.getroot():
            if child.tag in ("depend", "build_depend", "exec_depend", "buildtool_depend"):
                if child.text:
                    deps.add(child.text.strip())
    except ET.ParseError:
        pass
    return deps


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
