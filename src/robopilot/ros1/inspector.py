"""No-ROS-required static inspector for ROS1 catkin packages."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from robopilot.detector.project_detector import detect_project


SAFETY_NOTE = (
    "This ROS1 inspection is static only. RoboPilot did not require ROS, run "
    "catkin_make, run colcon, execute launch files, execute generated code, or "
    "import user project modules."
)


@dataclass(frozen=True)
class ROS1Dependencies:
    """Dependencies extracted from package.xml."""

    buildtool: tuple[str, ...]
    build: tuple[str, ...]
    exec: tuple[str, ...]
    run: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "buildtool": list(self.buildtool),
            "build": list(self.build),
            "exec": list(self.exec),
            "run": list(self.run),
        }


@dataclass(frozen=True)
class CatkinSignals:
    """Catkin-related CMake signals."""

    find_package_catkin: bool
    catkin_components: tuple[str, ...]
    catkin_package: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "find_package_catkin": self.find_package_catkin,
            "catkin_components": list(self.catkin_components),
            "catkin_package": self.catkin_package,
        }


@dataclass(frozen=True)
class ROS1Files:
    """ROS1 package files detected by path."""

    launch_files: tuple[str, ...]
    msg_files: tuple[str, ...]
    srv_files: tuple[str, ...]
    action_files: tuple[str, ...]
    python_files: tuple[str, ...]
    cpp_files: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "launch_files": list(self.launch_files),
            "msg_files": list(self.msg_files),
            "srv_files": list(self.srv_files),
            "action_files": list(self.action_files),
            "python_files": list(self.python_files),
            "cpp_files": list(self.cpp_files),
        }


@dataclass(frozen=True)
class ROS1Nodes:
    """Likely ROS1 node candidates."""

    python_node_candidates: tuple[str, ...]
    cpp_node_candidates: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "python_node_candidates": list(self.python_node_candidates),
            "cpp_node_candidates": list(self.cpp_node_candidates),
        }


@dataclass(frozen=True)
class ROS1Inspection:
    """Static ROS1 inspection result."""

    project_path: str
    exists: bool
    package_name: str
    package_format: str
    detected_project_type: str
    dependencies: ROS1Dependencies
    catkin: CatkinSignals
    files: ROS1Files
    nodes: ROS1Nodes
    rospy_usage: bool
    roscpp_usage: bool
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
            "catkin": self.catkin.to_dict(),
            "files": self.files.to_dict(),
            "nodes": self.nodes.to_dict(),
            "rospy_usage": self.rospy_usage,
            "roscpp_usage": self.roscpp_usage,
            "issues": list(self.issues),
            "suggested_next_steps": list(self.suggested_next_steps),
            "safety_note": self.safety_note,
        }


def inspect_ros1_project(project_path: Path) -> ROS1Inspection:
    """Inspect a ROS1 catkin package statically."""
    path = Path(project_path)
    detection = detect_project(path)
    if not path.exists() or not path.is_dir():
        issues = ("project path does not exist",) if not path.exists() else ("project path is not a directory",)
        return ROS1Inspection(
            project_path=str(project_path),
            exists=path.exists(),
            package_name="",
            package_format="",
            detected_project_type=detection.project_type,
            dependencies=_empty_dependencies(),
            catkin=CatkinSignals(False, (), False),
            files=_empty_files(),
            nodes=ROS1Nodes((), ()),
            rospy_usage=False,
            roscpp_usage=False,
            issues=issues,
            suggested_next_steps=("Provide a ROS1 catkin package directory.",),
            safety_note=SAFETY_NOTE,
        )

    package = _parse_package_xml(path / "package.xml")
    cmake_text = _read_text(path / "CMakeLists.txt")
    catkin = _parse_catkin_signals(cmake_text)
    files = _inspect_files(path)
    nodes, rospy_usage, roscpp_usage = _detect_nodes(path, files)
    issues = _detect_issues(
        path=path,
        detection_type=detection.project_type,
        dependencies=package["dependencies"],
        catkin=catkin,
        files=files,
        nodes=nodes,
        cmake_text=cmake_text,
    )
    return ROS1Inspection(
        project_path=str(project_path),
        exists=True,
        package_name=str(package["package_name"]),
        package_format=str(package["package_format"]),
        detected_project_type=detection.project_type,
        dependencies=package["dependencies"],
        catkin=catkin,
        files=files,
        nodes=nodes,
        rospy_usage=rospy_usage,
        roscpp_usage=roscpp_usage,
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
        }

    try:
        root = ET.fromstring(path.read_text(encoding="utf-8", errors="ignore"))
    except ET.ParseError:
        return {
            "package_name": "",
            "package_format": "",
            "dependencies": _empty_dependencies(),
        }

    def values(tag: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                child.text.strip()
                for child in root.findall(tag)
                if child.text and child.text.strip()
            )
        )

    name = root.findtext("name", default="").strip()
    return {
        "package_name": name,
        "package_format": root.attrib.get("format", ""),
        "dependencies": ROS1Dependencies(
            buildtool=values("buildtool_depend"),
            build=values("build_depend"),
            exec=values("exec_depend"),
            run=values("run_depend"),
        ),
    }


def _parse_catkin_signals(cmake_text: str) -> CatkinSignals:
    normalized = _strip_cmake_comments(cmake_text)
    find_match = re.search(
        r"find_package\s*\(\s*catkin\s+REQUIRED(?:\s+COMPONENTS\s+(?P<components>[^)]+))?",
        normalized,
        flags=re.IGNORECASE | re.DOTALL,
    )
    components: tuple[str, ...] = ()
    if find_match and find_match.group("components"):
        components = tuple(
            sorted(
                part.strip()
                for part in re.split(r"\s+", find_match.group("components"))
                if part.strip()
            )
        )
    return CatkinSignals(
        find_package_catkin=find_match is not None,
        catkin_components=components,
        catkin_package=bool(
            re.search(r"\bcatkin_package\s*\(", normalized, flags=re.IGNORECASE)
        ),
    )


def _inspect_files(path: Path) -> ROS1Files:
    return ROS1Files(
        launch_files=_relative_files(path, path / "launch", ("*.launch", "*.xml", "*.py")),
        msg_files=_relative_files(path, path / "msg", ("*.msg",)),
        srv_files=_relative_files(path, path / "srv", ("*.srv",)),
        action_files=_relative_files(path, path / "action", ("*.action",)),
        python_files=_relative_files(path, path, ("*.py",)),
        cpp_files=_relative_files(path, path, ("*.cpp", "*.cc", "*.cxx", "*.hpp", "*.h")),
    )


def _detect_nodes(path: Path, files: ROS1Files) -> tuple[ROS1Nodes, bool, bool]:
    python_nodes: list[str] = []
    cpp_nodes: list[str] = []
    rospy_usage = False
    roscpp_usage = False

    for relative in files.python_files:
        text = _read_text(path / relative)
        if "import rospy" in text or "from rospy" in text or "rospy." in text:
            rospy_usage = True
            python_nodes.append(relative)

    for relative in files.cpp_files:
        text = _read_text(path / relative)
        if "#include <ros/ros.h>" in text or "ros::" in text:
            roscpp_usage = True
            cpp_nodes.append(relative)

    return (
        ROS1Nodes(tuple(sorted(python_nodes)), tuple(sorted(cpp_nodes))),
        rospy_usage,
        roscpp_usage,
    )


def _detect_issues(
    *,
    path: Path,
    detection_type: str,
    dependencies: ROS1Dependencies,
    catkin: CatkinSignals,
    files: ROS1Files,
    nodes: ROS1Nodes,
    cmake_text: str,
) -> tuple[str, ...]:
    issues: list[str] = []
    if detection_type == "non_ros_project":
        issues.append("detector classified this project as non_ros_project")
    if detection_type in {"ros2_ament_python_package", "ros2_ament_cmake_package"}:
        issues.append(f"detector classified this project as {detection_type}; inspect-ros1 may not be appropriate")
    if detection_type in {"unknown", "mixed_ros_project"}:
        issues.append(f"detector classified this project as {detection_type}; ROS1 structure may be partial")
    if not (path / "package.xml").is_file():
        issues.append("missing package.xml")
    if not (path / "CMakeLists.txt").is_file():
        issues.append("missing CMakeLists.txt")
    if "catkin" not in dependencies.buildtool:
        issues.append("package.xml missing catkin buildtool dependency")
    if not catkin.find_package_catkin:
        issues.append("CMakeLists.txt missing find_package(catkin REQUIRED ...)")
    if not catkin.catkin_package:
        issues.append("missing catkin_package()")
    if not (path / "launch").is_dir():
        issues.append("launch directory missing")
    if not (path / "scripts").is_dir():
        issues.append("scripts directory missing")
    if not nodes.python_node_candidates and not nodes.cpp_node_candidates:
        issues.append("no obvious ROS1 node files detected")
    if (files.msg_files or files.srv_files or files.action_files) and not _has_message_generation_hints(cmake_text):
        issues.append("msg/srv/action files exist but message generation hints are missing")
    for relative in nodes.python_node_candidates:
        candidate = path / relative
        if _is_probably_not_executable(candidate):
            issues.append(f"Python script may not be executable: {relative}")
    return tuple(dict.fromkeys(issues))


def _suggest_next_steps(detection_type: str, issues: tuple[str, ...]) -> tuple[str, ...]:
    steps: list[str] = []
    if detection_type == "non_ros_project":
        steps.append("Run robopilot detect to confirm the project type before ROS1 inspection.")
    if any("ros2_ament" in issue for issue in issues):
        steps.append("Use ROS2-oriented inspection in a future RoboPilot version.")
    if "missing package.xml" in issues or "missing CMakeLists.txt" in issues:
        steps.append("Add or restore core ROS1 catkin package files.")
    if any("message generation hints" in issue for issue in issues):
        steps.append("Review add_message_files, add_service_files, add_action_files, and generate_messages in CMakeLists.txt.")
    if not steps:
        steps.append("Review dependencies and node candidates before running ROS tooling in your own environment.")
    return tuple(dict.fromkeys(steps))


def _relative_files(root: Path, directory: Path, patterns: tuple[str, ...]) -> tuple[str, ...]:
    if not directory.is_dir():
        return ()
    paths: list[str] = []
    for pattern in patterns:
        for file_path in sorted(directory.rglob(pattern)):
            if _is_ignored(file_path.relative_to(root)):
                continue
            paths.append(file_path.relative_to(root).as_posix())
    return tuple(sorted(dict.fromkeys(paths)))


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _strip_cmake_comments(text: str) -> str:
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def _has_message_generation_hints(cmake_text: str) -> bool:
    lowered = cmake_text.lower()
    return any(
        hint in lowered
        for hint in (
            "add_message_files",
            "add_service_files",
            "add_action_files",
            "generate_messages",
            "message_generation",
        )
    )


def _is_probably_not_executable(path: Path) -> bool:
    try:
        mode = path.stat().st_mode
    except OSError:
        return False
    return path.suffix == ".py" and not bool(mode & 0o111)


def _is_ignored(path: Path) -> bool:
    ignored = {"__pycache__", ".git", ".robopilot_backups", ".robopilot_history"}
    return bool(set(path.parts).intersection(ignored))


def _empty_dependencies() -> ROS1Dependencies:
    return ROS1Dependencies(buildtool=(), build=(), exec=(), run=())


def _empty_files() -> ROS1Files:
    return ROS1Files(
        launch_files=(),
        msg_files=(),
        srv_files=(),
        action_files=(),
        python_files=(),
        cpp_files=(),
    )
