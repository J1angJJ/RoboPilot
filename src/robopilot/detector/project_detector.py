"""No-ROS-required static project detector."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PROJECT_TYPES = {
    "robopilot_project",
    "ros1_catkin_package",
    "ros2_ament_python_package",
    "ros2_ament_cmake_package",
    "mixed_ros_project",
    "non_ros_project",
    "unknown",
}


@dataclass(frozen=True)
class ProjectDetection:
    """Static project detection result."""

    project_path: str
    exists: bool
    project_type: str
    confidence: str
    detected_signals: tuple[str, ...]
    missing_common_files: tuple[str, ...]
    notes: tuple[str, ...]
    suggested_next_steps: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a stable JSON-serializable mapping."""
        return {
            "project_path": self.project_path,
            "exists": self.exists,
            "project_type": self.project_type,
            "confidence": self.confidence,
            "detected_signals": list(self.detected_signals),
            "missing_common_files": list(self.missing_common_files),
            "notes": list(self.notes),
            "suggested_next_steps": list(self.suggested_next_steps),
        }


def detect_project(project_path: Path) -> ProjectDetection:
    """Detect the static ROS-style project type without executing anything."""
    path = Path(project_path)
    if not path.exists():
        return ProjectDetection(
            project_path=str(project_path),
            exists=False,
            project_type="unknown",
            confidence="none",
            detected_signals=(),
            missing_common_files=(),
            notes=("Project path does not exist.",),
            suggested_next_steps=("Check the project path and run detect again.",),
        )
    if not path.is_dir():
        return ProjectDetection(
            project_path=str(project_path),
            exists=True,
            project_type="unknown",
            confidence="none",
            detected_signals=(),
            missing_common_files=(),
            notes=("Project path is not a directory.",),
            suggested_next_steps=("Provide a project directory path.",),
        )

    signals = _collect_signals(path)
    project_type, confidence, notes = _classify(signals)
    missing = _missing_common_files(path, project_type)
    return ProjectDetection(
        project_path=str(project_path),
        exists=True,
        project_type=project_type,
        confidence=confidence,
        detected_signals=tuple(sorted(signals)),
        missing_common_files=missing,
        notes=notes,
        suggested_next_steps=_suggest_next_steps(project_type, confidence),
    )


def _collect_signals(path: Path) -> set[str]:
    signals: set[str] = set()
    _add_file_dir_signals(path, signals)

    package_xml = _read_text(path / "package.xml")
    cmake = _read_text(path / "CMakeLists.txt")
    setup_py = _read_text(path / "setup.py")
    setup_cfg = _read_text(path / "setup.cfg")
    source_text = _read_source_sample(path)

    _add_package_xml_signals(package_xml, signals)
    _add_cmake_signals(cmake, signals)
    _add_setup_signals(setup_py, setup_cfg, signals)
    _add_source_signals(source_text, signals)
    return signals


def _add_file_dir_signals(path: Path, signals: set[str]) -> None:
    for file_name in ("robopilot.yaml", "package.xml", "CMakeLists.txt", "setup.py", "setup.cfg"):
        if (path / file_name).is_file():
            signals.add(file_name)
    for dir_name in ("launch", "scripts", "src", "msg", "srv", "action", "resource"):
        if (path / dir_name).is_dir():
            signals.add(f"{dir_name}/")


def _add_package_xml_signals(text: str, signals: set[str]) -> None:
    normalized = text.lower()
    if not normalized:
        return
    if '<package format="1"' in normalized:
        signals.add("package.xml: format 1")
    if '<package format="2"' in normalized:
        signals.add("package.xml: format 2")
    if '<package format="3"' in normalized:
        signals.add("package.xml: format 3")
    if "<buildtool_depend>catkin</buildtool_depend>" in normalized:
        signals.add("package.xml: buildtool_depend catkin")
    if "<buildtool_depend>ament_cmake</buildtool_depend>" in normalized:
        signals.add("package.xml: buildtool_depend ament_cmake")
    if "<build_type>ament_python</build_type>" in normalized:
        signals.add("package.xml: build_type ament_python")
    if "ament_python" in normalized:
        signals.add("package.xml: ament_python")


def _add_cmake_signals(text: str, signals: set[str]) -> None:
    normalized = text.lower()
    if not normalized:
        return
    if "catkin_package" in normalized:
        signals.add("CMakeLists.txt: catkin_package")
    if "find_package(catkin required" in normalized.replace("\n", " "):
        signals.add("CMakeLists.txt: find_package catkin")
    if "ament_package()" in normalized or "ament_package (" in normalized:
        signals.add("CMakeLists.txt: ament_package")


def _add_setup_signals(setup_py: str, setup_cfg: str, signals: set[str]) -> None:
    text = f"{setup_py}\n{setup_cfg}".lower()
    if "ament_python" in text:
        signals.add("setup: ament_python")
    if "data_files" in text and "resource" in text:
        signals.add("setup.py: resource data_files")


def _add_source_signals(text: str, signals: set[str]) -> None:
    normalized = text.lower()
    if "import rclpy" in normalized or "from rclpy" in normalized:
        signals.add("source: rclpy")
    if "#include <rclcpp" in normalized or "rclcpp::" in normalized:
        signals.add("source: rclcpp")
    if "import rospy" in normalized or "from rospy" in normalized:
        signals.add("source: rospy")
    if "#include <ros/ros.h>" in normalized or "ros::" in normalized:
        signals.add("source: roscpp")


def _classify(signals: set[str]) -> tuple[str, str, tuple[str, ...]]:
    if "robopilot.yaml" in signals:
        return (
            "robopilot_project",
            "high",
            ("Detected robopilot.yaml, so this is treated as a RoboPilot-managed project.",),
        )

    ros1_score = _score(signals, _ROS1_SIGNALS)
    ros2_py_score = _score(signals, _ROS2_PY_SIGNALS)
    ros2_cpp_score = _score(signals, _ROS2_CPP_SIGNALS)
    ros2_score = max(ros2_py_score, ros2_cpp_score)
    ros1_strong_score = _score(signals, _ROS1_STRONG_SIGNALS)
    ros2_strong_score = _score(signals, _ROS2_PY_STRONG_SIGNALS | _ROS2_CPP_STRONG_SIGNALS)

    if ros1_strong_score >= 1 and ros2_strong_score >= 1:
        return (
            "mixed_ros_project",
            "high",
            ("Detected both ROS1/catkin and ROS2/ament signals.",),
        )
    if _is_ros1(signals):
        return (
            "ros1_catkin_package",
            "high" if ros1_score >= 3 else "medium",
            ("Detected catkin package signals without executing ROS tools.",),
        )
    if _is_ros2_python(signals):
        return (
            "ros2_ament_python_package",
            "high" if ros2_py_score >= 3 else "medium",
            ("Detected ament Python package signals without importing project modules.",),
        )
    if _is_ros2_cmake(signals):
        return (
            "ros2_ament_cmake_package",
            "high" if ros2_cpp_score >= 3 else "medium",
            ("Detected ament CMake package signals without running colcon.",),
        )
    if not signals or signals.isdisjoint(_ROS_LIKE_SIGNALS):
        return (
            "non_ros_project",
            "high",
            ("No ROS-style package metadata, directories, or code signals were detected.",),
        )
    return (
        "unknown",
        "low",
        ("Detected partial ROS-like structure, but not enough to classify confidently.",),
    )


def _missing_common_files(path: Path, project_type: str) -> tuple[str, ...]:
    expected = {
        "robopilot_project": ("robopilot.yaml", "package.xml", "setup.py", "README.md"),
        "ros1_catkin_package": ("package.xml", "CMakeLists.txt"),
        "ros2_ament_python_package": ("package.xml", "setup.py", "setup.cfg", "resource/"),
        "ros2_ament_cmake_package": ("package.xml", "CMakeLists.txt"),
    }.get(project_type, ())
    missing: list[str] = []
    for item in expected:
        item_path = path / item.rstrip("/")
        if item.endswith("/"):
            if not item_path.is_dir():
                missing.append(item)
        elif not item_path.is_file():
            missing.append(item)
    return tuple(missing)


def _suggest_next_steps(project_type: str, confidence: str) -> tuple[str, ...]:
    if project_type == "robopilot_project":
        return ("Run robopilot inspect on the project for a structural health check.",)
    if project_type in {
        "ros1_catkin_package",
        "ros2_ament_python_package",
        "ros2_ament_cmake_package",
    }:
        return ("Review detected signals before using ROS-specific tooling.",)
    if project_type == "mixed_ros_project":
        return ("Review ROS1 and ROS2 signals manually before migration or apply workflows.",)
    if project_type == "non_ros_project":
        return ("Use RoboPilot on ROS-style projects or generate a new ProjectSpec first.",)
    if confidence == "low":
        return ("Add or review package metadata such as package.xml, setup.py, or CMakeLists.txt.",)
    return ("Review the project structure manually.",)


def _is_ros1(signals: set[str]) -> bool:
    return (
        "package.xml" in signals
        and "CMakeLists.txt" in signals
        and bool(signals.intersection(_ROS1_STRONG_SIGNALS))
    )


def _is_ros2_python(signals: set[str]) -> bool:
    return (
        "package.xml" in signals
        and "setup.py" in signals
        and bool(signals.intersection(_ROS2_PY_STRONG_SIGNALS))
    )


def _is_ros2_cmake(signals: set[str]) -> bool:
    return (
        "package.xml" in signals
        and "CMakeLists.txt" in signals
        and bool(signals.intersection(_ROS2_CPP_STRONG_SIGNALS))
    )


def _score(signals: set[str], needles: Iterable[str]) -> int:
    return sum(1 for needle in needles if needle in signals)


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_source_sample(path: Path) -> str:
    chunks: list[str] = []
    for pattern in ("*.py", "*.cpp", "*.hpp", "*.h", "*.cc"):
        for file_path in sorted(path.rglob(pattern)):
            if _is_ignored_path(file_path.relative_to(path)):
                continue
            try:
                chunks.append(file_path.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
            if len(chunks) >= 50:
                return "\n".join(chunks)
    return "\n".join(chunks)


def _is_ignored_path(path: Path) -> bool:
    ignored = {"__pycache__", ".git", ".pytest_tmp", ".robopilot_backups", ".robopilot_history"}
    return bool(set(path.parts).intersection(ignored))


_ROS1_STRONG_SIGNALS = {
    "package.xml: buildtool_depend catkin",
    "CMakeLists.txt: catkin_package",
    "CMakeLists.txt: find_package catkin",
}
_ROS1_SIGNALS = _ROS1_STRONG_SIGNALS | {"source: rospy", "source: roscpp"}

_ROS2_PY_STRONG_SIGNALS = {
    "package.xml: build_type ament_python",
    "package.xml: ament_python",
    "setup: ament_python",
    "source: rclpy",
    "resource/",
    "setup.py: resource data_files",
}
_ROS2_PY_SIGNALS = _ROS2_PY_STRONG_SIGNALS | {"setup.py", "setup.cfg"}

_ROS2_CPP_STRONG_SIGNALS = {
    "package.xml: buildtool_depend ament_cmake",
    "CMakeLists.txt: ament_package",
    "source: rclcpp",
}
_ROS2_CPP_SIGNALS = _ROS2_CPP_STRONG_SIGNALS | {"CMakeLists.txt", "src/"}

_ROS_LIKE_SIGNALS = (
    _ROS1_SIGNALS
    | _ROS2_PY_SIGNALS
    | _ROS2_CPP_SIGNALS
    | {
        "robopilot.yaml",
        "package.xml",
        "CMakeLists.txt",
        "launch/",
        "scripts/",
        "src/",
        "msg/",
        "srv/",
        "action/",
        "resource/",
    }
)
