"""No-ROS-required static dependency analyzer for ROS-style projects."""

from __future__ import annotations

import ast
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from robopilot.detector.project_detector import detect_project


SAFETY_NOTE = (
    "This dependency analysis is static only. RoboPilot did not require ROS, "
    "run catkin_make, run colcon, execute launch files, execute generated code, "
    "or import user project modules."
)


@dataclass(frozen=True)
class DeclaredDependencies:
    """Dependencies declared in package.xml."""

    buildtool: tuple[str, ...]
    build: tuple[str, ...]
    exec: tuple[str, ...]
    run: tuple[str, ...]
    test: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "buildtool": list(self.buildtool),
            "build": list(self.build),
            "exec": list(self.exec),
            "run": list(self.run),
            "test": list(self.test),
        }


@dataclass(frozen=True)
class DetectedUsage:
    """Dependency usage signals detected from static project files."""

    python_imports: tuple[str, ...]
    cpp_includes: tuple[str, ...]
    cmake_find_package: tuple[str, ...]
    catkin_components: tuple[str, ...]
    launch_references: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "python_imports": list(self.python_imports),
            "cpp_includes": list(self.cpp_includes),
            "cmake_find_package": list(self.cmake_find_package),
            "catkin_components": list(self.catkin_components),
            "launch_references": list(self.launch_references),
        }


@dataclass(frozen=True)
class DependencyAnalysis:
    """Static dependency analysis result."""

    project_path: str
    exists: bool
    project_type: str
    declared_dependencies: DeclaredDependencies
    detected_usage: DetectedUsage
    inferred_dependencies: tuple[str, ...]
    possibly_missing: tuple[str, ...]
    possibly_unused: tuple[str, ...]
    hints: tuple[str, ...]
    migration_hints: tuple[str, ...]
    rosdep_hints: tuple[str, ...]
    warnings: tuple[str, ...]
    suggested_next_steps: tuple[str, ...]
    safety_note: str

    def to_dict(self) -> dict[str, object]:
        """Return stable JSON-ready data."""
        return {
            "project_path": self.project_path,
            "exists": self.exists,
            "project_type": self.project_type,
            "declared_dependencies": self.declared_dependencies.to_dict(),
            "detected_usage": self.detected_usage.to_dict(),
            "inferred_dependencies": list(self.inferred_dependencies),
            "possibly_missing": list(self.possibly_missing),
            "possibly_unused": list(self.possibly_unused),
            "hints": list(self.hints),
            "migration_hints": list(self.migration_hints),
            "rosdep_hints": list(self.rosdep_hints),
            "warnings": list(self.warnings),
            "suggested_next_steps": list(self.suggested_next_steps),
            "safety_note": self.safety_note,
        }


def analyze_dependencies(project_path: Path) -> DependencyAnalysis:
    """Analyze declared and used dependencies without running ROS tooling."""
    path = Path(project_path)
    detection = detect_project(path)
    if not path.exists() or not path.is_dir():
        warning = "project path does not exist" if not path.exists() else "project path is not a directory"
        return DependencyAnalysis(
            project_path=str(project_path),
            exists=path.exists(),
            project_type=detection.project_type,
            declared_dependencies=_empty_declared_dependencies(),
            detected_usage=_empty_detected_usage(),
            inferred_dependencies=(),
            possibly_missing=(),
            possibly_unused=(),
            hints=(),
            migration_hints=(),
            rosdep_hints=(),
            warnings=(warning,),
            suggested_next_steps=("Check the project path and run robopilot deps again.",),
            safety_note=SAFETY_NOTE,
        )

    package_xml = path / "package.xml"
    declared = _parse_package_xml(package_xml)
    package_name = _parse_package_name(package_xml)
    usage = DetectedUsage(
        python_imports=_detect_python_imports(path),
        cpp_includes=_detect_cpp_includes(path),
        cmake_find_package=_detect_cmake_find_packages(path / "CMakeLists.txt"),
        catkin_components=_detect_catkin_components(path / "CMakeLists.txt"),
        launch_references=_detect_launch_references(path / "launch"),
    )
    interface_files = _detect_interface_files(path)
    inferred = _infer_dependencies(usage, package_name=package_name)
    declared_all = _declared_dependency_set(declared)
    possibly_missing = tuple(dep for dep in inferred if dep not in declared_all)
    possibly_unused = _detect_possibly_unused(declared, inferred, usage, interface_files)
    warnings = _warnings_for_project(detection.project_type, path)
    migration_hints = _build_migration_hints(
        declared,
        usage,
        inferred,
        interface_files,
        detection.project_type,
    )
    rosdep_hints = _build_rosdep_hints(usage, inferred, possibly_missing, interface_files, detection.project_type)
    hints = _build_hints(
        usage,
        inferred,
        possibly_missing,
        possibly_unused,
        detection.project_type,
        interface_files,
    )
    return DependencyAnalysis(
        project_path=str(project_path),
        exists=True,
        project_type=detection.project_type,
        declared_dependencies=declared,
        detected_usage=usage,
        inferred_dependencies=inferred,
        possibly_missing=possibly_missing,
        possibly_unused=possibly_unused,
        hints=hints,
        migration_hints=migration_hints,
        rosdep_hints=rosdep_hints,
        warnings=warnings,
        suggested_next_steps=_suggest_next_steps(possibly_missing, possibly_unused, warnings),
        safety_note=SAFETY_NOTE,
    )


def _parse_package_xml(path: Path) -> DeclaredDependencies:
    if not path.is_file():
        return _empty_declared_dependencies()
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8", errors="ignore"))
    except ET.ParseError:
        return _empty_declared_dependencies()

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
    return DeclaredDependencies(
        buildtool=values("buildtool_depend"),
        build=tuple(sorted(dict.fromkeys(values("build_depend") + generic))),
        exec=tuple(sorted(dict.fromkeys(values("exec_depend") + generic))),
        run=values("run_depend"),
        test=values("test_depend"),
    )


def _detect_python_imports(path: Path) -> tuple[str, ...]:
    imports: set[str] = set()
    for file_path in _relative_files(path, ("*.py",)):
        text = _read_text(path / file_path)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            imports.update(_fallback_python_imports(text))
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".", 1)[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])
    return tuple(sorted(imports))


def _fallback_python_imports(text: str) -> set[str]:
    imports: set[str] = set()
    for match in re.finditer(r"^\s*(?:import|from)\s+([A-Za-z_][\w]*)", text, flags=re.MULTILINE):
        imports.add(match.group(1))
    return imports


def _detect_cpp_includes(path: Path) -> tuple[str, ...]:
    includes: set[str] = set()
    for file_path in _relative_files(path, ("*.cpp", "*.cc", "*.cxx", "*.hpp", "*.h")):
        text = _read_text(path / file_path)
        includes.update(
            match.group(1).strip()
            for match in re.finditer(r"^\s*#\s*include\s*[<\"]([^>\"]+)[>\"]", text, flags=re.MULTILINE)
        )
    return tuple(sorted(includes))


def _detect_cmake_find_packages(path: Path) -> tuple[str, ...]:
    text = _strip_cmake_comments(_read_text(path))
    packages = [
        match.group(1)
        for match in re.finditer(r"\bfind_package\s*\(\s*([A-Za-z_][\w]*)", text, flags=re.IGNORECASE)
    ]
    return tuple(sorted(dict.fromkeys(packages)))


def _detect_catkin_components(path: Path) -> tuple[str, ...]:
    text = _strip_cmake_comments(_read_text(path))
    match = re.search(
        r"find_package\s*\(\s*catkin\s+REQUIRED(?:\s+COMPONENTS\s+(?P<components>[^)]+))?",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match or not match.group("components"):
        return ()
    return tuple(
        sorted(
            part.strip()
            for part in re.split(r"\s+", match.group("components"))
            if part.strip()
        )
    )


def _detect_launch_references(directory: Path) -> tuple[str, ...]:
    if not directory.is_dir():
        return ()
    refs: set[str] = set()
    for file_path in sorted(directory.rglob("*")):
        if not file_path.is_file():
            continue
        text = _read_text(file_path)
        refs.update(re.findall(r"\bpkg\s*=\s*[\"']([^\"']+)[\"']", text))
        refs.update(re.findall(r"\bpackage\s*=\s*[\"']([^\"']+)[\"']", text))
        refs.update(re.findall(r"\$\(find\s+([^)]+)\)", text))
    return tuple(sorted(refs))


def _detect_interface_files(path: Path) -> tuple[str, ...]:
    files: list[str] = []
    for directory, pattern in (("msg", "*.msg"), ("srv", "*.srv"), ("action", "*.action")):
        files.extend(_relative_files(path / directory, (pattern,)))
    return tuple(sorted(dict.fromkeys(files)))


def _parse_package_name(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8", errors="ignore"))
    except ET.ParseError:
        return ""
    return root.findtext("name", default="").strip()


def _infer_dependencies(usage: DetectedUsage, *, package_name: str = "") -> tuple[str, ...]:
    inferred: set[str] = set()
    for import_name in usage.python_imports:
        inferred.update(_PYTHON_IMPORT_MAP.get(import_name, ()))
    for include in usage.cpp_includes:
        for prefix, deps in _CPP_INCLUDE_MAP.items():
            if include == prefix or include.startswith(f"{prefix}/"):
                inferred.update(deps)
    inferred.update(usage.catkin_components)
    inferred.update(dep for dep in usage.cmake_find_package if dep not in {"catkin", "ament_cmake"})
    inferred.update(dep for dep in usage.launch_references if dep != package_name)
    return tuple(sorted(inferred))


def _detect_possibly_unused(
    declared: DeclaredDependencies,
    inferred: tuple[str, ...],
    usage: DetectedUsage,
    interface_files: tuple[str, ...],
) -> tuple[str, ...]:
    inferred_set = set(inferred)
    declared_runtime = set(declared.build) | set(declared.exec) | set(declared.run)
    ignored = {
        "catkin",
        "ament_cmake",
        "ament_python",
        "message_generation",
        "message_runtime",
        "rosidl_default_generators",
        "rosidl_default_runtime",
    }
    if interface_files:
        ignored.update(_INTERFACE_RUNTIME_DEPENDENCIES)
    ignored.update(_COMMON_RUNTIME_DEPENDENCIES)
    possibly_unused = [
        dep
        for dep in declared_runtime
        if dep not in ignored
        and dep not in inferred_set
        and dep not in usage.python_imports
        and dep not in usage.cmake_find_package
        and dep not in usage.catkin_components
        and dep not in usage.launch_references
    ]
    return tuple(sorted(possibly_unused))


def _warnings_for_project(project_type: str, path: Path) -> tuple[str, ...]:
    warnings: list[str] = []
    if project_type == "non_ros_project":
        warnings.append("detector classified this project as non_ros_project; dependency analysis may be limited")
    if project_type == "unknown":
        warnings.append("detector classified this project as unknown; dependency analysis may be incomplete")
    if not (path / "package.xml").is_file():
        warnings.append("package.xml not found; declared dependency extraction is limited")
    return tuple(warnings)


def _build_hints(
    usage: DetectedUsage,
    inferred: tuple[str, ...],
    possibly_missing: tuple[str, ...],
    possibly_unused: tuple[str, ...],
    project_type: str,
    interface_files: tuple[str, ...],
) -> tuple[str, ...]:
    hints: list[str] = []
    for import_name in usage.python_imports:
        deps = _PYTHON_IMPORT_MAP.get(import_name)
        if deps:
            hints.append(f"detected_usage: Python import '{import_name}' suggests dependency {', '.join(deps)}")
    for include in usage.cpp_includes:
        for prefix, deps in _CPP_INCLUDE_MAP.items():
            if include == prefix or include.startswith(f"{prefix}/"):
                hints.append(f"detected_usage: C++ include '{include}' suggests dependency {', '.join(deps)}")
                break
    if "cv2" in usage.python_imports:
        hints.append("hint: cv2 may map to opencv-python for pure Python or vision_opencv in ROS contexts")
    if "serial" in usage.python_imports:
        hints.append("hint: serial may map to python3-serial or pyserial depending on packaging context")
    if "yaml" in usage.python_imports:
        hints.append("hint: yaml may map to python3-yaml or PyYAML depending on packaging context")
    if project_type.startswith("ros1") and ("rospy" in inferred or "roscpp" in inferred):
        hints.append("hint: ROS1 usage detected from rospy or roscpp signals")
    if project_type.startswith("ros2") and ("rclpy" in inferred or "rclcpp" in inferred):
        hints.append("hint: ROS2 usage detected from rclpy or rclcpp signals")
    if interface_files and project_type.startswith("ros1"):
        hints.append("hint: interface files detected; review message_generation and message_runtime in catkin metadata")
    if interface_files and project_type.startswith("ros2"):
        hints.append(
            "hint: interface files detected; review rosidl_default_generators and rosidl_default_runtime in ROS2 metadata"
        )
    for dep in possibly_missing:
        hints.append(f"possibly_missing: detected usage suggests declaring '{dep}'")
    for dep in possibly_unused:
        hints.append(f"possibly_unused: declared dependency '{dep}' was not matched to simple static usage")
    if not hints:
        hints.append("hint: no obvious dependency mismatch detected by conservative static rules")
    return tuple(dict.fromkeys(hints))


def _build_migration_hints(
    declared: DeclaredDependencies,
    usage: DetectedUsage,
    inferred: tuple[str, ...],
    interface_files: tuple[str, ...],
    project_type: str,
) -> tuple[str, ...]:
    deps = set(_declared_dependency_set(declared)) | set(inferred)
    hints: list[str] = []
    dependency_label = "ROS1 dependency" if project_type.startswith("ros1") else "dependency"
    for dep in sorted(deps):
        target = _ROS1_TO_ROS2_DEPENDENCY_HINTS.get(dep)
        if target:
            hints.append(f"migration_hint: {dependency_label} '{dep}' should be reviewed for ROS2 direction: {target}")
    if "dynamic_reconfigure" in deps:
        hints.append("migration_hint: dynamic_reconfigure usually needs manual review toward ROS2 parameters or lifecycle nodes")
    if "actionlib" in deps or "actionlib" in usage.python_imports:
        hints.append("migration_hint: actionlib usage should be reviewed for ROS2 actions, rclcpp_action, or rclpy.action")
    if "nodelet" in deps:
        hints.append("migration_hint: nodelet usage should be reviewed for ROS2 components or composable nodes")
    if usage.launch_references and project_type.startswith("ros1"):
        hints.append("migration_hint: ROS1 launch references should be reviewed for the ROS2 Python launch system")
    if interface_files and project_type.startswith("ros1"):
        hints.append(
            "migration_hint: ROS1 interface dependencies message_generation/message_runtime usually migrate toward rosidl_default_generators/rosidl_default_runtime"
        )
    elif interface_files and project_type.startswith("ros2"):
        hints.append(
            "migration_hint: ROS2 interface files should be reviewed for rosidl_default_generators/rosidl_default_runtime metadata"
        )
    if not hints and project_type.startswith("ros2"):
        hints.append("migration_hint: project already looks ROS2-like; review dependencies for package-style consistency")
    return tuple(dict.fromkeys(hints))


def _build_rosdep_hints(
    usage: DetectedUsage,
    inferred: tuple[str, ...],
    possibly_missing: tuple[str, ...],
    interface_files: tuple[str, ...],
    project_type: str,
) -> tuple[str, ...]:
    hints: list[str] = []
    for import_name in usage.python_imports:
        hint = _PYTHON_ROSDEP_HINTS.get(import_name)
        if hint:
            hints.append(f"rosdep_hint: Python import '{import_name}' may require {hint}")
    for include in usage.cpp_includes:
        for prefix, hint in _CPP_ROSDEP_HINTS.items():
            if include == prefix or include.startswith(f"{prefix}/"):
                hints.append(f"rosdep_hint: C++ include '{include}' may require {hint}")
                break
    for dep in possibly_missing:
        hints.append(f"rosdep_hint: possibly_missing dependency '{dep}' should be checked against rosdep or package metadata")
    if interface_files and project_type.startswith("ros1"):
        hints.append("rosdep_hint: ROS1 interface files usually need message_generation and message_runtime review")
    if interface_files and project_type.startswith("ros2"):
        hints.append("rosdep_hint: ROS2 interface files usually need rosidl_default_generators and rosidl_default_runtime review")
    return tuple(dict.fromkeys(hints))


def _suggest_next_steps(
    possibly_missing: tuple[str, ...],
    possibly_unused: tuple[str, ...],
    warnings: tuple[str, ...],
) -> tuple[str, ...]:
    steps: list[str] = []
    if possibly_missing:
        steps.append("Review possibly_missing dependencies and update package metadata if the usage is intentional.")
    if possibly_unused:
        steps.append("Review possibly_unused dependencies manually before removing anything.")
    if warnings:
        steps.append("Review project type warnings before acting on dependency hints.")
    if not steps:
        steps.append("Review declared dependencies and detected usage before running ROS tooling in your own environment.")
    return tuple(steps)


# ---------------------------------------------------------------------------
# M13: Enhanced rosdep hints with install commands
# ---------------------------------------------------------------------------

_ROSDEP_APT: dict[str, str] = {
    "rclpy": "ros-<distro>-rclpy",
    "rclcpp": "ros-<distro>-rclcpp",
    "std_msgs": "ros-<distro>-std-msgs",
    "sensor_msgs": "ros-<distro>-sensor-msgs",
    "geometry_msgs": "ros-<distro>-geometry-msgs",
    "nav_msgs": "ros-<distro>-nav-msgs",
    "trajectory_msgs": "ros-<distro>-trajectory-msgs",
    "visualization_msgs": "ros-<distro>-visualization-msgs",
    "shape_msgs": "ros-<distro>-shape-msgs",
    "diagnostic_msgs": "ros-<distro>-diagnostic-msgs",
    "actionlib_msgs": "ros-<distro>-actionlib-msgs",
    "tf2": "ros-<distro>-tf2",
    "tf2_ros": "ros-<distro>-tf2-ros",
    "tf2_msgs": "ros-<distro>-tf2-msgs",
    "tf2_geometry_msgs": "ros-<distro>-tf2-geometry-msgs",
    "cv_bridge": "ros-<distro>-cv-bridge",
    "image_transport": "ros-<distro>-image-transport",
    "image_geometry": "ros-<distro>-image-geometry",
    "pcl_conversions": "ros-<distro>-pcl-conversions",
    "pcl_ros": "ros-<distro>-pcl-ros",
    "robot_state_publisher": "ros-<distro>-robot-state-publisher",
    "joint_state_publisher": "ros-<distro>-joint-state-publisher",
    "rosbag2": "ros-<distro>-rosbag2",
    "ros2bag": "ros-<distro>-ros2bag",
    "slam_toolbox": "ros-<distro>-slam-toolbox",
    "nav2": "ros-<distro>-navigation2",
    "robot_localization": "ros-<distro>-robot-localization",
    "ros2_control": "ros-<distro>-ros2-control",
    "ros2_controllers": "ros-<distro>-ros2-controllers",
    "moveit": "ros-<distro>-moveit",
    "gazebo_ros": "ros-<distro>-gazebo-ros",
    "rviz2": "ros-<distro>-rviz2",
    "teleop_twist_keyboard": "ros-<distro>-teleop-twist-keyboard",
    "teleop_twist_joy": "ros-<distro>-teleop-twist-joy",
    "xacro": "ros-<distro>-xacro",
    "urdf": "ros-<distro>-urdf",
    "rosidl_default_generators": "ros-<distro>-rosidl-default-generators",
    "rosidl_default_runtime": "ros-<distro>-rosidl-default-runtime",
}

_ROSDEP_PIP: dict[str, str] = {
    "numpy": "pip install numpy",
    "opencv": "pip install opencv-python",
    "cv2": "pip install opencv-python",
    "matplotlib": "pip install matplotlib",
    "scipy": "pip install scipy",
    "pyyaml": "pip install pyyaml",
    "yaml": "pip install pyyaml",
    "pytest": "pip install pytest",
    "torch": "pip install torch",
    "tensorflow": "pip install tensorflow",
    "transformers": "pip install transformers",
    "flask": "pip install flask",
    "requests": "pip install requests",
}

_DISTRO_PACKAGES: dict[str, set[str]] = {
    "humble": {
        "rclpy", "rclcpp", "std_msgs", "sensor_msgs", "geometry_msgs",
        "nav_msgs", "tf2", "tf2_ros", "cv_bridge", "image_transport",
        "rosbag2", "slam_toolbox", "nav2", "robot_localization",
        "ros2_control", "ros2_controllers", "rviz2",
    },
    "jazzy": {
        "rclpy", "rclcpp", "std_msgs", "sensor_msgs", "geometry_msgs",
        "nav_msgs", "tf2", "tf2_ros", "cv_bridge", "image_transport",
        "rosbag2", "slam_toolbox", "nav2", "robot_localization",
        "ros2_control", "ros2_controllers", "rviz2", "moveit",
    },
    "noetic": {
        "rospy", "roscpp", "std_msgs", "sensor_msgs", "geometry_msgs",
        "nav_msgs", "tf", "tf2", "cv_bridge", "image_transport",
        "rosbag", "slam_gmapping", "moveit",
    },
}


def get_rosdep_install_hints(deps: list[str], distro: str = "humble") -> list[str]:
    """Generate rosdep install commands for a list of package names."""
    hints: list[str] = []
    for dep in deps:
        if dep in _ROSDEP_APT:
            pkg = _ROSDEP_APT[dep].replace("<distro>", distro)
            hints.append(f"sudo apt install {pkg}")
        elif dep in _ROSDEP_PIP:
            hints.append(_ROSDEP_PIP[dep])
    return sorted(set(hints))


def check_distro_compatibility(deps: list[str], distro: str = "humble") -> dict[str, object]:
    """Check which deps are known to be available in a ROS distro."""
    known = _DISTRO_PACKAGES.get(distro.lower(), set())
    available = sorted(set(deps) & known)
    unknown = sorted(set(deps) - known)
    return {
        "distro": distro,
        "available": available,
        "unknown": unknown,
        "compat_ratio": round(len(available) / max(1, len(deps)), 2),
    }


# ---------------------------------------------------------------------------
# M13: Workspace-level dependency analysis
# ---------------------------------------------------------------------------


def analyze_workspace_deps(workspace_path: Path, distro: str = "humble") -> dict[str, object]:
    """Run dependency analysis across all packages in a workspace."""
    from robopilot.workspace import analyze_workspace as ws_analyze
    ws = ws_analyze(workspace_path)
    results: dict[str, dict] = {}
    all_deps: set[str] = set()

    for pkg in ws.packages:
        pkg_path = (Path(workspace_path) / pkg.path).resolve()
        if not pkg_path.exists():
            continue
        try:
            analysis = analyze_dependencies(pkg_path)
            results[pkg.name] = {
                "declared": sorted(set(
                    list(analysis.declared_dependencies.buildtool)
                    + list(analysis.declared_dependencies.build)
                    + list(analysis.declared_dependencies.exec)
                    + list(analysis.declared_dependencies.run)
                )),
                "possibly_missing": list(analysis.possibly_missing),
                "rosdep_hints": list(analysis.rosdep_hints),
            }
            for d in results[pkg.name]["declared"]:
                if isinstance(d, str):
                    all_deps.add(d)
        except Exception:
            results[pkg.name] = {"error": "Could not analyze dependencies"}

    install_hints = get_rosdep_install_hints(sorted(all_deps), distro)
    compat = check_distro_compatibility(sorted(all_deps), distro)

    return {
        "workspace_path": str(workspace_path),
        "distro": distro,
        "package_count": len(results),
        "packages": results,
        "all_dependencies": sorted(all_deps),
        "rosdep_install_hints": install_hints,
        "distro_compatibility": compat,
        "safety_note": SAFETY_NOTE,
    }


def _declared_dependency_set(declared: DeclaredDependencies) -> set[str]:
    return (
        set(declared.buildtool)
        | set(declared.build)
        | set(declared.exec)
        | set(declared.run)
        | set(declared.test)
    )


def _relative_files(root: Path, patterns: tuple[str, ...]) -> tuple[str, ...]:
    if not root.is_dir():
        return ()
    paths: list[str] = []
    for pattern in patterns:
        for file_path in sorted(root.rglob(pattern)):
            try:
                relative = file_path.relative_to(root)
            except ValueError:
                continue
            if file_path.is_file() and not _is_ignored(relative):
                paths.append(relative.as_posix())
    return tuple(sorted(dict.fromkeys(paths)))


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _strip_cmake_comments(text: str) -> str:
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def _is_ignored(path: Path) -> bool:
    ignored = {"__pycache__", ".git", ".pytest_tmp", ".robopilot_backups", ".robopilot_history"}
    return bool(set(path.parts).intersection(ignored))


def _empty_declared_dependencies() -> DeclaredDependencies:
    return DeclaredDependencies(buildtool=(), build=(), exec=(), run=(), test=())


def _empty_detected_usage() -> DetectedUsage:
    return DetectedUsage(
        python_imports=(),
        cpp_includes=(),
        cmake_find_package=(),
        catkin_components=(),
        launch_references=(),
    )


_PYTHON_IMPORT_MAP = {
    "cv2": ("opencv-python",),
    "numpy": ("python3-numpy",),
    "rclpy": ("rclpy",),
    "rospy": ("rospy",),
    "yaml": ("python3-yaml",),
    "serial": ("python3-serial",),
    "tf": ("tf",),
    "tf2_ros": ("tf2_ros",),
    "actionlib": ("actionlib",),
    "sensor_msgs": ("sensor_msgs",),
    "geometry_msgs": ("geometry_msgs",),
    "nav_msgs": ("nav_msgs",),
    "visualization_msgs": ("visualization_msgs",),
    "std_msgs": ("std_msgs",),
    "cv_bridge": ("cv_bridge",),
}

_CPP_INCLUDE_MAP = {
    "ros/ros.h": ("roscpp",),
    "rclcpp": ("rclcpp",),
    "rclcpp_action": ("rclcpp_action",),
    "sensor_msgs": ("sensor_msgs",),
    "geometry_msgs": ("geometry_msgs",),
    "nav_msgs": ("nav_msgs",),
    "visualization_msgs": ("visualization_msgs",),
    "std_msgs": ("std_msgs",),
    "cv_bridge": ("cv_bridge",),
    "image_transport": ("image_transport",),
    "tf": ("tf",),
    "tf2_ros": ("tf2_ros",),
    "actionlib": ("actionlib",),
}

_ROS1_TO_ROS2_DEPENDENCY_HINTS = {
    "rospy": "rclpy, with manual review of node lifecycle, parameters, logging, and spin behavior",
    "roscpp": "rclcpp, with manual review of NodeHandle, publishers, subscribers, parameters, and executors",
    "catkin": "ament_cmake or ament_python after choosing the target ROS2 package style",
    "tf": "tf2_ros, with transform listener/broadcaster API review",
    "tf2_ros": "tf2_ros, while reviewing API and QoS behavior",
    "std_msgs": "std_msgs, usually with message import/build metadata review",
    "sensor_msgs": "sensor_msgs, usually with message import/build metadata review",
    "geometry_msgs": "geometry_msgs, usually with message import/build metadata review",
    "nav_msgs": "nav_msgs, usually with message import/build metadata review",
    "visualization_msgs": "visualization_msgs, usually with message import/build metadata review",
    "cv_bridge": "cv_bridge, with OpenCV/image encoding behavior review",
    "image_transport": "image_transport, with transport plugin behavior review",
    "message_generation": "rosidl_default_generators for ROS2 interface generation",
    "message_runtime": "rosidl_default_runtime for ROS2 interface runtime dependencies",
    "dynamic_reconfigure": "ROS2 parameters or lifecycle-node review; no automatic one-to-one migration",
    "actionlib": "ROS2 actions using rclcpp_action or rclpy.action, with manual API review",
    "nodelet": "ROS2 components or composable nodes, with manual architecture review",
    "roslaunch": "ROS2 launch system, usually Python launch files",
}

_PYTHON_ROSDEP_HINTS = {
    "cv2": "opencv-python outside ROS or vision_opencv in ROS contexts",
    "numpy": "python3-numpy",
    "yaml": "python3-yaml or PyYAML depending on packaging context",
    "serial": "python3-serial or pyserial depending on packaging context",
    "rospy": "rospy",
    "rclpy": "rclpy",
    "tf": "tf",
    "tf2_ros": "tf2_ros",
    "actionlib": "actionlib",
    "std_msgs": "std_msgs",
    "sensor_msgs": "sensor_msgs",
    "geometry_msgs": "geometry_msgs",
    "nav_msgs": "nav_msgs",
    "visualization_msgs": "visualization_msgs",
    "cv_bridge": "cv_bridge",
}

_CPP_ROSDEP_HINTS = {
    "ros/ros.h": "roscpp",
    "rclcpp": "rclcpp",
    "rclcpp_action": "rclcpp_action",
    "std_msgs": "std_msgs",
    "sensor_msgs": "sensor_msgs",
    "geometry_msgs": "geometry_msgs",
    "nav_msgs": "nav_msgs",
    "visualization_msgs": "visualization_msgs",
    "cv_bridge": "cv_bridge",
    "image_transport": "image_transport",
    "tf": "tf",
    "tf2_ros": "tf2_ros",
    "actionlib": "actionlib",
}

_INTERFACE_RUNTIME_DEPENDENCIES = {
    "message_generation",
    "message_runtime",
    "rosidl_default_generators",
    "rosidl_default_runtime",
    "std_msgs",
    "sensor_msgs",
    "geometry_msgs",
    "nav_msgs",
    "visualization_msgs",
}

_COMMON_RUNTIME_DEPENDENCIES = {
    "rospy",
    "roscpp",
    "rclpy",
    "rclcpp",
    "rclcpp_action",
    "std_msgs",
    "sensor_msgs",
    "geometry_msgs",
    "nav_msgs",
    "visualization_msgs",
    "tf",
    "tf2_ros",
    "cv_bridge",
    "image_transport",
}
