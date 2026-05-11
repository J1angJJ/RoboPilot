"""No-ROS-required static inspector for ROS2 ament packages."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from robopilot.detector.project_detector import detect_project


SAFETY_NOTE = (
    "This ROS2 inspection is static only. RoboPilot did not require ROS2, "
    "require ROS, run colcon, run catkin_make, execute launch files, execute "
    "generated code, or import user project modules."
)


@dataclass(frozen=True)
class ROS2Dependencies:
    """Dependencies extracted from package.xml."""

    buildtool: tuple[str, ...]
    build: tuple[str, ...]
    exec: tuple[str, ...]
    test: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "buildtool": list(self.buildtool),
            "build": list(self.build),
            "exec": list(self.exec),
            "test": list(self.test),
        }


@dataclass(frozen=True)
class ROS2BuildSystem:
    """ROS2 build system signals."""

    ament_cmake: bool
    ament_python: bool
    ament_package: bool
    setup_py: bool
    setup_cfg: bool
    resource_marker: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "ament_cmake": self.ament_cmake,
            "ament_python": self.ament_python,
            "ament_package": self.ament_package,
            "setup_py": self.setup_py,
            "setup_cfg": self.setup_cfg,
            "resource_marker": self.resource_marker,
        }


@dataclass(frozen=True)
class ROS2Files:
    """ROS2 package files detected by path."""

    launch_files: tuple[str, ...]
    config_files: tuple[str, ...]
    msg_files: tuple[str, ...]
    srv_files: tuple[str, ...]
    action_files: tuple[str, ...]
    python_files: tuple[str, ...]
    cpp_files: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "launch_files": list(self.launch_files),
            "config_files": list(self.config_files),
            "msg_files": list(self.msg_files),
            "srv_files": list(self.srv_files),
            "action_files": list(self.action_files),
            "python_files": list(self.python_files),
            "cpp_files": list(self.cpp_files),
        }


@dataclass(frozen=True)
class ROS2Nodes:
    """Likely ROS2 node candidates."""

    python_node_candidates: tuple[str, ...]
    cpp_node_candidates: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "python_node_candidates": list(self.python_node_candidates),
            "cpp_node_candidates": list(self.cpp_node_candidates),
        }


@dataclass(frozen=True)
class ROS2Inspection:
    """Static ROS2 inspection result."""

    project_path: str
    exists: bool
    package_name: str
    package_format: str
    detected_project_type: str
    dependencies: ROS2Dependencies
    build_system: ROS2BuildSystem
    files: ROS2Files
    nodes: ROS2Nodes
    rclpy_usage: bool
    rclcpp_usage: bool
    issues: tuple[str, ...]
    suggested_next_steps: tuple[str, ...]
    safety_note: str

    def to_dict(self) -> dict[str, object]:
        """Return stable JSON-ready data."""
        return {
            "project_path": self.project_path,
            "exists": self.exists,
            "package_name": self.package_name,
            "package_format": self.package_format,
            "detected_project_type": self.detected_project_type,
            "dependencies": self.dependencies.to_dict(),
            "build_system": self.build_system.to_dict(),
            "files": self.files.to_dict(),
            "nodes": self.nodes.to_dict(),
            "rclpy_usage": self.rclpy_usage,
            "rclcpp_usage": self.rclcpp_usage,
            "issues": list(self.issues),
            "suggested_next_steps": list(self.suggested_next_steps),
            "safety_note": self.safety_note,
        }


def inspect_ros2_project(project_path: Path) -> ROS2Inspection:
    """Inspect a ROS2 ament package statically."""
    path = Path(project_path)
    detection = detect_project(path)
    if not path.exists() or not path.is_dir():
        issues = ("project path does not exist",) if not path.exists() else ("project path is not a directory",)
        return ROS2Inspection(
            project_path=str(project_path),
            exists=path.exists(),
            package_name="",
            package_format="",
            detected_project_type=detection.project_type,
            dependencies=_empty_dependencies(),
            build_system=ROS2BuildSystem(False, False, False, False, False, False),
            files=_empty_files(),
            nodes=ROS2Nodes((), ()),
            rclpy_usage=False,
            rclcpp_usage=False,
            issues=issues,
            suggested_next_steps=("Provide a ROS2 ament package directory.",),
            safety_note=SAFETY_NOTE,
        )

    package = _parse_package_xml(path / "package.xml")
    cmake_text = _read_text(path / "CMakeLists.txt")
    setup_py_text = _read_text(path / "setup.py")
    setup_cfg_text = _read_text(path / "setup.cfg")
    files = _inspect_files(path)
    nodes, rclpy_usage, rclcpp_usage = _detect_nodes(path, files)
    build_system = _detect_build_system(
        path=path,
        package_name=str(package["package_name"]),
        dependencies=package["dependencies"],
        cmake_text=cmake_text,
        package_build_types=package["build_types"],
        setup_py_text=setup_py_text,
        setup_cfg_text=setup_cfg_text,
        rclpy_usage=rclpy_usage,
        rclcpp_usage=rclcpp_usage,
    )
    issues = _detect_issues(
        path=path,
        detection_type=detection.project_type,
        dependencies=package["dependencies"],
        build_types=package["build_types"],
        build_system=build_system,
        files=files,
        nodes=nodes,
        cmake_text=cmake_text,
        package_text=_read_text(path / "package.xml"),
    )
    return ROS2Inspection(
        project_path=str(project_path),
        exists=True,
        package_name=str(package["package_name"]),
        package_format=str(package["package_format"]),
        detected_project_type=detection.project_type,
        dependencies=package["dependencies"],
        build_system=build_system,
        files=files,
        nodes=nodes,
        rclpy_usage=rclpy_usage,
        rclcpp_usage=rclcpp_usage,
        issues=issues,
        suggested_next_steps=_suggest_next_steps(detection.project_type, issues),
        safety_note=SAFETY_NOTE,
    )


def _parse_package_xml(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {
            "package_name": "",
            "package_format": "",
            "dependencies": _empty_dependencies(),
            "build_types": (),
        }

    try:
        root = ET.fromstring(path.read_text(encoding="utf-8", errors="ignore"))
    except ET.ParseError:
        return {
            "package_name": "",
            "package_format": "",
            "dependencies": _empty_dependencies(),
            "build_types": (),
        }

    def values(*tags: str) -> tuple[str, ...]:
        deps: list[str] = []
        for tag in tags:
            deps.extend(
                child.text.strip()
                for child in root.findall(tag)
                if child.text and child.text.strip()
            )
        return tuple(sorted(dict.fromkeys(deps)))

    generic = values("depend")
    build_types = tuple(
        sorted(
            child.text.strip()
            for child in root.findall(".//build_type")
            if child.text and child.text.strip()
        )
    )
    return {
        "package_name": root.findtext("name", default="").strip(),
        "package_format": root.attrib.get("format", ""),
        "dependencies": ROS2Dependencies(
            buildtool=values("buildtool_depend"),
            build=tuple(sorted(dict.fromkeys(values("build_depend") + generic))),
            exec=tuple(sorted(dict.fromkeys(values("exec_depend") + generic))),
            test=values("test_depend"),
        ),
        "build_types": build_types,
    }


def _detect_build_system(
    *,
    path: Path,
    package_name: str,
    dependencies: ROS2Dependencies,
    cmake_text: str,
    package_build_types: tuple[str, ...],
    setup_py_text: str,
    setup_cfg_text: str,
    rclpy_usage: bool,
    rclcpp_usage: bool,
) -> ROS2BuildSystem:
    setup_text = f"{setup_py_text}\n{setup_cfg_text}".lower()
    package_build_type_set = set(package_build_types)
    resource_marker = _has_resource_marker(path, package_name)
    ament_package = bool(
        re.search(r"\bament_package\s*\(", _strip_cmake_comments(cmake_text), flags=re.IGNORECASE)
    )
    ament_cmake = (
        "ament_cmake" in dependencies.buildtool
        or ament_package
        or rclcpp_usage
    )
    ament_python = (
        "ament_python" in package_build_type_set
        or "ament_python" in dependencies.buildtool
        or "ament_python" in setup_text
        or resource_marker
        or rclpy_usage
    )
    return ROS2BuildSystem(
        ament_cmake=ament_cmake,
        ament_python=ament_python,
        ament_package=ament_package,
        setup_py=(path / "setup.py").is_file(),
        setup_cfg=(path / "setup.cfg").is_file(),
        resource_marker=resource_marker,
    )


def _has_resource_marker(path: Path, package_name: str) -> bool:
    resource_dir = path / "resource"
    if not resource_dir.is_dir():
        return False
    if package_name and (resource_dir / package_name).is_file():
        return True
    return any(child.is_file() for child in resource_dir.iterdir())


def _inspect_files(path: Path) -> ROS2Files:
    return ROS2Files(
        launch_files=_relative_files(path, path / "launch", ("*.launch.py", "*.py", "*.xml")),
        config_files=_relative_files(path, path / "config", ("*.yaml", "*.yml", "*.json", "*.toml")),
        msg_files=_relative_files(path, path / "msg", ("*.msg",)),
        srv_files=_relative_files(path, path / "srv", ("*.srv",)),
        action_files=_relative_files(path, path / "action", ("*.action",)),
        python_files=_relative_files(path, path, ("*.py",)),
        cpp_files=_relative_files(path, path, ("*.cpp", "*.cc", "*.cxx", "*.hpp", "*.h")),
    )


def _detect_nodes(path: Path, files: ROS2Files) -> tuple[ROS2Nodes, bool, bool]:
    python_nodes: list[str] = []
    cpp_nodes: list[str] = []
    rclpy_usage = False
    rclcpp_usage = False

    for relative in files.python_files:
        text = _read_text(path / relative)
        if "import rclpy" in text or "from rclpy" in text or "rclpy." in text:
            rclpy_usage = True
            python_nodes.append(relative)

    for relative in files.cpp_files:
        text = _read_text(path / relative)
        if "#include <rclcpp" in text or "rclcpp::" in text:
            rclcpp_usage = True
            cpp_nodes.append(relative)

    return (
        ROS2Nodes(tuple(sorted(python_nodes)), tuple(sorted(cpp_nodes))),
        rclpy_usage,
        rclcpp_usage,
    )


def _detect_issues(
    *,
    path: Path,
    detection_type: str,
    dependencies: ROS2Dependencies,
    build_types: tuple[str, ...],
    build_system: ROS2BuildSystem,
    files: ROS2Files,
    nodes: ROS2Nodes,
    cmake_text: str,
    package_text: str,
) -> tuple[str, ...]:
    issues: list[str] = []
    if detection_type == "non_ros_project":
        issues.append("detector classified this project as non_ros_project")
    if detection_type == "ros1_catkin_package":
        issues.append("detector classified this project as ros1_catkin_package; inspect-ros2 may not be appropriate")
    if detection_type in {"unknown", "mixed_ros_project"}:
        issues.append(f"detector classified this project as {detection_type}; ROS2 structure may be partial")
    if _has_ros1_signals(package_text, cmake_text, path):
        issues.append("ROS1 signals present in a ROS2 inspection")
    if not (path / "package.xml").is_file():
        issues.append("missing package.xml")
    if build_system.ament_cmake:
        if not (path / "CMakeLists.txt").is_file():
            issues.append("missing CMakeLists.txt for ament_cmake-style package")
        if "ament_cmake" not in dependencies.buildtool:
            issues.append("package.xml missing ament_cmake buildtool dependency for C++ package")
        if not build_system.ament_package:
            issues.append("missing ament_package() for ament_cmake-style package")
    if build_system.ament_python:
        if not build_system.setup_py:
            issues.append("missing setup.py for ament_python-style package")
        if not build_system.setup_cfg:
            issues.append("missing setup.cfg for ament_python-style package")
        if not build_system.resource_marker:
            issues.append("missing resource marker for ament_python-style package")
        if "ament_python" not in build_types:
            issues.append("package.xml missing ament_python build type for Python package")
    if not build_system.ament_cmake and not build_system.ament_python:
        issues.append("unknown or partial ROS2 project structure")
    if not nodes.python_node_candidates and not nodes.cpp_node_candidates:
        issues.append("no obvious ROS2 node files detected")
    if (files.msg_files or files.srv_files or files.action_files) and not _has_interface_generation_hints(package_text, cmake_text):
        issues.append("msg/srv/action files exist but interface generation hints are missing")
    if not (path / "launch").is_dir():
        issues.append("launch directory missing")
    if not (path / "config").is_dir():
        issues.append("config directory missing")
    return tuple(dict.fromkeys(issues))


def _suggest_next_steps(detection_type: str, issues: tuple[str, ...]) -> tuple[str, ...]:
    steps: list[str] = []
    if detection_type == "non_ros_project":
        steps.append("Run robopilot detect to confirm the project type before ROS2 inspection.")
    if any("ros1_catkin" in issue for issue in issues):
        steps.append("Use inspect-ros1 for ROS1 catkin packages or review migration planning first.")
    if any("missing package.xml" in issue or "missing CMakeLists.txt" in issue or "missing setup.py" in issue for issue in issues):
        steps.append("Add or restore core ROS2 ament package files.")
    if any("interface generation hints" in issue for issue in issues):
        steps.append("Review rosidl_generate_interfaces and rosidl dependency declarations.")
    if not steps:
        steps.append("Review dependencies and node candidates before running ROS2 tooling in your own environment.")
    return tuple(dict.fromkeys(steps))


def _relative_files(root: Path, directory: Path, patterns: tuple[str, ...]) -> tuple[str, ...]:
    if not directory.is_dir():
        return ()
    paths: list[str] = []
    for pattern in patterns:
        for file_path in sorted(directory.rglob(pattern)):
            if _is_ignored(file_path.relative_to(root)):
                continue
            if file_path.is_file():
                paths.append(file_path.relative_to(root).as_posix())
    return tuple(sorted(dict.fromkeys(paths)))


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _strip_cmake_comments(text: str) -> str:
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def _has_interface_generation_hints(package_text: str, cmake_text: str) -> bool:
    lowered = f"{package_text}\n{cmake_text}".lower()
    return any(
        hint in lowered
        for hint in (
            "rosidl_generate_interfaces",
            "rosidl_default_generators",
            "rosidl_default_runtime",
            "rosidl_interface_packages",
        )
    )


def _has_ros1_signals(package_text: str, cmake_text: str, path: Path) -> bool:
    lowered = f"{package_text}\n{cmake_text}".lower()
    if "catkin" in lowered or "rospy" in lowered or "roscpp" in lowered:
        return True
    source_text = "\n".join(_read_text(path / relative) for relative in _relative_files(path, path, ("*.py", "*.cpp", "*.hpp", "*.h")))
    return any(signal in source_text for signal in ("import rospy", "from rospy", "#include <ros/ros.h>", "ros::"))


def _is_ignored(path: Path) -> bool:
    ignored = {"__pycache__", ".git", ".pytest_tmp", ".robopilot_backups", ".robopilot_history"}
    return bool(set(path.parts).intersection(ignored))


def _empty_dependencies() -> ROS2Dependencies:
    return ROS2Dependencies(buildtool=(), build=(), exec=(), test=())


def _empty_files() -> ROS2Files:
    return ROS2Files(
        launch_files=(),
        config_files=(),
        msg_files=(),
        srv_files=(),
        action_files=(),
        python_files=(),
        cpp_files=(),
    )
