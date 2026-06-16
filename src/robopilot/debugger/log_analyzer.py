"""Rule-based offline analyzer for 30+ common robotics development errors."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LogAnalysis:
    """Structured diagnosis for a robotics-related error log."""

    error_type: str
    diagnosis: str
    possible_causes: tuple[str, ...]
    suggested_fixes: tuple[str, ...]
    confidence: str


def analyze_log(log_text: str) -> LogAnalysis:
    """Analyze robotics-related log text using offline rules (30+ patterns)."""
    normalized = _normalize(log_text)
    if not normalized:
        return _unknown_error()

    # Check patterns from most specific to most generic.
    for check in _PATTERNS:
        result = check(normalized, log_text)
        if result is not None:
            return result

    return _unknown_error()


# ---------------------------------------------------------------------------
# v2.0.0 existing patterns (8)
# ---------------------------------------------------------------------------

_PATTERNS: list[callable] = []


def _p0_cv_bridge(normalized: str, _raw: str) -> LogAnalysis | None:
    if "cv_bridge" in normalized and _any(normalized,
                                          "modulenotfounderror", "no module named",
                                          "importerror", "cannot import", "missing"):
        return LogAnalysis(
            error_type="cv_bridge missing",
            diagnosis="The log suggests that cv_bridge is missing or not visible from the active Python environment.",
            possible_causes=(
                "ROS environment setup has not been sourced.",
                "cv_bridge is not installed for the ROS or Python environment in use.",
                "The active Python interpreter does not match the ROS workspace.",
            ),
            suggested_fixes=(
                "Check that the intended ROS setup script or workspace setup file is sourced.",
                "Verify that cv_bridge is installed and discoverable in the active environment.",
                "Confirm that the command is using the expected Python interpreter.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p0_cv_bridge)


def _p0_cuda(normalized: str, _raw: str) -> LogAnalysis | None:
    if "cuda out of memory" in normalized or ("outofmemoryerror" in normalized and "cuda" in normalized):
        return LogAnalysis(
            error_type="CUDA out of memory",
            diagnosis="A GPU workload tried to allocate more CUDA memory than was available.",
            possible_causes=(
                "Model, image batch, or tensor size is too large for the GPU.",
                "Another process is already using GPU memory.",
                "Intermediate tensors are being retained longer than expected.",
            ),
            suggested_fixes=(
                "Reduce batch size, image resolution, or model size.",
                "Close other GPU processes or choose a less busy GPU.",
                "Clear unused tensors and avoid keeping unnecessary computation graphs.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p0_cuda)


def _p0_camera(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "camera timeout", "cannot read frame", "can't read frame") or (
        "opencv" in normalized and _any(normalized, "timeout", "read frame", "videocapture")):
        return LogAnalysis(
            error_type="OpenCV camera read failure",
            diagnosis="OpenCV could not receive frames from the camera device or stream.",
            possible_causes=(
                "The camera index, device path, or stream URL is incorrect.",
                "The camera is disconnected, busy, or blocked by permissions.",
                "Frame capture timed out because the stream is unavailable or too slow.",
            ),
            suggested_fixes=(
                "Check the camera index or stream URL and test it with a minimal OpenCV script.",
                "Close other applications that may be using the camera.",
                "Verify camera permissions and reconnect or restart the device.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p0_camera)


def _p0_colcon(normalized: str, _raw: str) -> LogAnalysis | None:
    if "colcon" in normalized and _any(normalized, "failed", "failed packages", "build failed", "exited with code"):
        return LogAnalysis(
            error_type="colcon build failed",
            diagnosis="A colcon workspace build did not complete successfully.",
            possible_causes=(
                "A package failed to compile or install.",
                "A dependency is missing from the workspace or environment.",
                "Generated build artifacts are stale or inconsistent.",
            ),
            suggested_fixes=(
                "Read the first package-specific error above the colcon summary.",
                "Install missing dependencies or source the correct workspace setup file.",
                "Clean the affected package build directory and rebuild.",
            ),
            confidence="medium",
        )
    return None

_PATTERNS.append(_p0_colcon)


def _p0_package_not_found(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "package not found", "could not find package", "unknown package") or (
        "package" in normalized and "not found" in normalized):
        return LogAnalysis(
            error_type="package not found",
            diagnosis="A required package could not be located by the current toolchain.",
            possible_causes=(
                "The package is not installed or not present in the workspace.",
                "The environment has not been sourced.",
                "The package name is misspelled or differs from the import name.",
            ),
            suggested_fixes=(
                "Check the package name and workspace layout.",
                "Install the missing package or add it to the workspace.",
                "Source the relevant setup file before running the command.",
            ),
            confidence="medium",
        )
    return None

_PATTERNS.append(_p0_package_not_found)


def _p0_permission(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "permission denied", "access is denied", "errno 13"):
        return LogAnalysis(
            error_type="permission denied",
            diagnosis="The process was blocked from reading, writing, or opening a resource.",
            possible_causes=(
                "The current user lacks file, device, or serial port permissions.",
                "Another process owns the target file or device.",
                "The command is writing to a protected system path.",
            ),
            suggested_fixes=(
                "Check file, device, or serial port permissions.",
                "Close processes that may be holding the resource.",
                "Use a writable project directory for generated files and logs.",
            ),
            confidence="medium",
        )
    return None

_PATTERNS.append(_p0_permission)


def _p0_modulenotfound(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "modulenotfounderror", "no module named"):
        return LogAnalysis(
            error_type="ModuleNotFoundError",
            diagnosis="Python could not import a required module.",
            possible_causes=(
                "The dependency is not installed in the active environment.",
                "The wrong virtual environment or Python interpreter is active.",
                "The package is local but not on PYTHONPATH or not installed in editable mode.",
            ),
            suggested_fixes=(
                "Install the missing dependency in the active environment.",
                "Verify the Python interpreter and virtual environment.",
                "For local packages, run an editable install or set PYTHONPATH.",
            ),
            confidence="medium",
        )
    return None

_PATTERNS.append(_p0_modulenotfound)


# NOTE: v2.1.0 M6 specific import patterns must run BEFORE _p0_modulenotfound.
# Insert them here by reordering the _PATTERNS list: remove _p0_modulenotfound
# from its current position, append all new patterns, then re-append it.
_PATTERNS.remove(_p0_modulenotfound)


# ---------------------------------------------------------------------------
# v2.1.0 M6 new patterns (19)
# ---------------------------------------------------------------------------


def _p_tf_lookup(normalized: str, _raw: str) -> LogAnalysis | None:
    if any(t in normalized for t in ("lookup would require extrapolation", "extrapolationexception",
                                      "tf2 lookup", "lookuptransform", "transform timeout")):
        return LogAnalysis(
            error_type="TF2 transform lookup failure",
            diagnosis="A TF2 transform lookup failed — typically a timing or frame-tree issue.",
            possible_causes=(
                "The requested transform timestamp is in the future (need to wait for data).",
                "The frame is not being published at the requested time.",
                "The TF buffer is too small or the transform chain is broken.",
                "A broadcaster or static_transform_publisher is not running.",
            ),
            suggested_fixes=(
                "Use tf2_ros.Buffer with a longer cache_time or use waitForTransform.",
                "Check that all required frames are published: 'ros2 run tf2_tools view_frames'.",
                "Add a static_transform_publisher for known fixed transforms.",
                "Verify that all TF broadcasters are launched and running.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p_tf_lookup)


def _p_frame_not_found(normalized: str, _raw: str) -> LogAnalysis | None:
    if (_any(normalized, "frame does not exist", "frame not found", "frame_id not found",
             "no frame", "available frames")
            or ("does not exist" in normalized and "frame" in normalized)):
        return LogAnalysis(
            error_type="TF frame not found",
            diagnosis="A requested coordinate frame does not exist in the TF tree.",
            possible_causes=(
                "The frame is not being published by any node.",
                "The frame name is misspelled or uses wrong naming convention.",
                "The node that publishes this frame crashed or was not launched.",
            ),
            suggested_fixes=(
                "Check published frames: 'ros2 run tf2_tools view_frames' or 'ros2 topic echo /tf'.",
                "Verify the frame name matches the broadcaster's frame_id.",
                "Ensure the node broadcasting this frame is running.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p_frame_not_found)


def _p_param_not_found(normalized: str, _raw: str) -> LogAnalysis | None:
    if ("parameter" in normalized or "param" in normalized) and _any(normalized,
            "not set", "not found", "not declared", "unknown", "undeclared", "parameternotdeclaredexception"):
        return LogAnalysis(
            error_type="ROS parameter not found",
            diagnosis="A node tried to access a parameter that was not declared or set.",
            possible_causes=(
                "The parameter was not declared with declare_parameter().",
                "The parameter YAML file is missing or has a wrong path.",
                "The parameter name differs between the node and the config file.",
            ),
            suggested_fixes=(
                "Declare all parameters with declare_parameter(name, value) in node __init__.",
                "Check the YAML config file path and namespace structure.",
                "Use 'ros2 param list' and 'ros2 param get' to inspect available parameters.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p_param_not_found)


def _p_action_server(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "action server not available", "action client",
            "actionlib", "wait for action server") and _any(normalized, "timeout", "not available",
                                                             "not found", "waiting", "failed"):
        return LogAnalysis(
            error_type="ROS action server unavailable",
            diagnosis="An action client could not connect to its action server, or the action timed out.",
            possible_causes=(
                "The action server node is not running or crashed.",
                "The action name is misspelled or uses wrong namespace.",
                "A goal was sent before the action server was ready.",
            ),
            suggested_fixes=(
                "Wait for the action server: 'client.wait_for_server(timeout_sec=5.0)'.",
                "Check the action server is launched with the correct name.",
                "Verify action server status: 'ros2 action list'.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p_action_server)


def _p_qos_mismatch(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "qos mismatch", "incompatible qos", "qos profile",
            "durability incompatible", "reliability incompatible", "offered incompatible qos"):
        return LogAnalysis(
            error_type="QoS mismatch",
            diagnosis="A publisher and subscriber have incompatible Quality of Service settings.",
            possible_causes=(
                "Publisher uses RELIABLE but subscriber expects BEST_EFFORT (or vice versa).",
                "Durability settings differ: TRANSIENT_LOCAL vs VOLATILE.",
                "The topic was created with different QoS in C++ vs Python nodes.",
            ),
            suggested_fixes=(
                "Match QoS profiles: ensure RELIABILITY, DURABILITY, and LIVELINESS match.",
                "Use 'ros2 topic info /topic --verbose' to see endpoint QoS.",
                "For ROS1→ROS2 migration: ROS1 topics had different defaults; review QoS explicitly.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p_qos_mismatch)


def _p_dds_discovery(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "dds discovery", "participant", "discovery timeout",
            "no writers", "no readers", "no publisher", "no subscriber",
            "no publishers", "no subscribers"):
        return LogAnalysis(
            error_type="DDS discovery / topic connectivity issue",
            diagnosis="A DDS participant could not discover matching publishers or subscribers.",
            possible_causes=(
                "ROS_DOMAIN_ID mismatch between nodes.",
                "ROS_LOCALHOST_ONLY is set but nodes are on different machines.",
                "DDS vendor mismatch or network firewall blocking discovery traffic.",
            ),
            suggested_fixes=(
                "Check ROS_DOMAIN_ID is consistent across all terminals (default 0).",
                "Verify network connectivity and firewall rules for DDS discovery.",
                "Try 'ros2 topic list' and 'ros2 node list' to check visibility.",
            ),
            confidence="medium",
        )
    return None

_PATTERNS.append(_p_dds_discovery)


def _p_cmake_error(normalized: str, _raw: str) -> LogAnalysis | None:
    if "cmake" in normalized and _any(normalized, "error", "cmake error", "cmake failed",
                                        "configuring incomplete", "cmakelists"):
        return LogAnalysis(
            error_type="CMake build error",
            diagnosis="A CMake configuration or build step failed.",
            possible_causes=(
                "A required dependency is not installed or find_package cannot locate it.",
                "CMakeLists.txt has a syntax error or incorrect target definition.",
                "The cmake_minimum_required version is incompatible with installed CMake.",
            ),
            suggested_fixes=(
                "Read the specific CMake error line above the summary.",
                "Install missing dev packages and ensure find_package paths are correct.",
                "Check CMake version: 'cmake --version' and update cmake_minimum_required if needed.",
            ),
            confidence="medium",
        )
    return None

_PATTERNS.append(_p_cmake_error)


def _p_linker_error(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "undefined reference", "ld returned", "linker error",
            "cannot find -l", "unresolved external symbol"):
        return LogAnalysis(
            error_type="Linker error (undefined reference)",
            diagnosis="The C++ linker could not resolve one or more symbols.",
            possible_causes=(
                "A required library is not linked in CMakeLists.txt (target_link_libraries).",
                "A function signature changed but the caller was not recompiled.",
                "A third-party library is missing or installed in a non-standard location.",
            ),
            suggested_fixes=(
                "Add the missing library to target_link_libraries in CMakeLists.txt.",
                "Run a clean rebuild: delete build/ and rebuild from scratch.",
                "Check library installation paths and set CMAKE_PREFIX_PATH if needed.",
            ),
            confidence="medium",
        )
    return None

_PATTERNS.append(_p_linker_error)


def _p_rospy_import(normalized: str, _raw: str) -> LogAnalysis | None:
    if "rospy" in normalized and _any(normalized, "modulenotfounderror", "importerror",
                                         "no module", "cannot import", "not found"):
        return LogAnalysis(
            error_type="rospy import error",
            diagnosis="rospy could not be imported — likely environment or ROS1-vs-ROS2 mix-up.",
            possible_causes=(
                "The code is being run without sourcing a ROS1 environment.",
                "ROS2 is active but the code uses rospy (ROS1-only API).",
                "The Python path does not include the ROS1 distro packages.",
            ),
            suggested_fixes=(
                "For ROS1: source /opt/ros/<distro>/setup.bash before running.",
                "For migration: replace rospy with rclpy and adapt the API.",
                "Check which ROS environment is active: 'echo $ROS_DISTRO'.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p_rospy_import)


def _p_rclpy_import(normalized: str, _raw: str) -> LogAnalysis | None:
    if "rclpy" in normalized and _any(normalized, "modulenotfounderror", "importerror",
                                         "no module", "cannot import"):
        return LogAnalysis(
            error_type="rclpy import error",
            diagnosis="rclpy could not be imported — ROS2 environment may not be set up.",
            possible_causes=(
                "ROS2 has not been sourced or installed.",
                "The Python interpreter does not have access to ROS2 packages.",
                "The code is running in a virtualenv that excludes ROS2 site-packages.",
            ),
            suggested_fixes=(
                "Source the ROS2 setup file: 'source /opt/ros/<distro>/setup.bash'.",
                "Install ROS2: follow docs.ros.org for your platform.",
                "Check Python path includes ROS2: 'python -c \"import rclpy\"'.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p_rclpy_import)


def _p_msg_generation(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "no such message", "unknown message type", "cannot load message",
            "msg module not found") or ("message" in normalized and _any(normalized,
            "not found", "cannot find", "not generated", "no module")):
        return LogAnalysis(
            error_type="ROS message/service generation not found",
            diagnosis="A custom message, service, or action definition could not be found by the runtime.",
            possible_causes=(
                "The msg/srv/action package has not been built or sourced.",
                "The message name includes the package (e.g., my_pkg/MyMsg) but the package is missing.",
                "The message generation step (rosidl_generate_interfaces) failed.",
            ),
            suggested_fixes=(
                "Build the interface package: 'colcon build --packages-select <pkg>'.",
                "Source the workspace setup file after building.",
                "Check that rosidl_generate_interfaces includes all .msg/.srv/.action files.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p_msg_generation)


def _p_node_crash(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "segmentation fault", "sigsegv", "signal 11",
            "process has died", "node died", "exited with signal"):
        return LogAnalysis(
            error_type="Node crash / segmentation fault",
            diagnosis="A ROS node process crashed, likely from a memory access error.",
            possible_causes=(
                "A null pointer dereference or buffer overflow in C++ code.",
                "A hardware driver or third-party library has a bug.",
                "A Python C extension segfaulted (e.g., OpenCV, numpy with bad image data).",
            ),
            suggested_fixes=(
                "Run the node under gdb to get a backtrace: 'gdb --args ros2 run ...'.",
                "Check for null sensor data before processing.",
                "Test the node with minimal input to isolate the crash trigger.",
            ),
            confidence="medium",
        )
    return None

_PATTERNS.append(_p_node_crash)


def _p_roscore(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "roscore", "ros master", "unable to communicate with master",
            "master is not running", "roscore not running", "could not contact master"):
        return LogAnalysis(
            error_type="ROS master / roscore not running",
            diagnosis="A ROS1 node could not connect to the ROS master (roscore).",
            possible_causes=(
                "roscore is not running in any terminal.",
                "ROS_MASTER_URI is set to the wrong host or port.",
                "The network configuration prevents reaching the master.",
            ),
            suggested_fixes=(
                "Start roscore in a dedicated terminal: 'roscore'.",
                "Check ROS_MASTER_URI: 'echo $ROS_MASTER_URI' (default http://localhost:11311).",
                "Verify network connectivity to the master host.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p_roscore)


def _p_disk_full(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "no space left", "disk full", "errno 28", "disk quota exceeded",
            "not enough space", "insufficient disk space"):
        return LogAnalysis(
            error_type="Disk full / no space left",
            diagnosis="A write operation failed because the disk is full.",
            possible_causes=(
                "ROS bag files or log files have consumed all available disk space.",
                "The build directory (build/, devel/, install/) has grown very large.",
                "A temporary directory (/tmp) is full.",
            ),
            suggested_fixes=(
                "Free disk space: delete old bag files, build artifacts, and logs.",
                "Clean build directories: 'rm -rf build/ devel/ install/'.",
                "Check disk usage: 'df -h' and find large directories with 'du -sh *'.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p_disk_full)


def _p_network(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "connection refused", "network unreachable", "cannot assign requested address",
            "connection reset", "no route to host", "errno 111", "errno 113"):
        return LogAnalysis(
            error_type="Network connection error",
            diagnosis="A network connection was refused, reset, or the target is unreachable.",
            possible_causes=(
                "The target ROS node or service is not listening on the expected port.",
                "A firewall is blocking the connection.",
                "The IP address or hostname is incorrect or unreachable.",
            ),
            suggested_fixes=(
                "Check the target is running: 'ros2 node list' or 'ros2 topic list'.",
                "Verify hostname resolution and IP configuration.",
                "Check firewall rules for DDS/ROS2 ports (default: 7400-7450 UDP).",
            ),
            confidence="medium",
        )
    return None

_PATTERNS.append(_p_network)


def _p_shared_library(normalized: str, _raw: str) -> LogAnalysis | None:
    if _any(normalized, "cannot open shared object file", "lib not found",
            ".so: cannot", "error while loading shared libraries", "dylib", "dll not found"):
        return LogAnalysis(
            error_type="Shared library not found",
            diagnosis="A compiled binary or Python extension could not load a required shared library.",
            possible_causes=(
                "The library is not installed or not on LD_LIBRARY_PATH.",
                "The library was built for a different architecture or ABI version.",
                "The ROS environment has not been sourced (which sets library paths).",
            ),
            suggested_fixes=(
                "Source the ROS setup file to set library paths.",
                "Install the missing library package.",
                "Check 'ldd <binary>' to see which libraries are missing.",
            ),
            confidence="medium",
        )
    return None

_PATTERNS.append(_p_shared_library)


def _p_catkin_make(normalized: str, _raw: str) -> LogAnalysis | None:
    if "catkin" in normalized and _any(normalized, "make", "build", "failed", "error", "catkin_make"):
        return LogAnalysis(
            error_type="catkin_make build failure",
            diagnosis="A catkin workspace build (catkin_make) did not complete.",
            possible_causes=(
                "A dependency declared in package.xml is not installed.",
                "CMakeLists.txt has incorrect catkin_package or find_package calls.",
                "The workspace has a stale devel/ or build/ directory.",
            ),
            suggested_fixes=(
                "Install missing dependencies: 'rosdep install --from-paths src --ignore-src'.",
                "Clean and rebuild: 'rm -rf build/ devel/ && catkin_make'.",
                "Check the first package-specific error in the build output.",
            ),
            confidence="medium",
        )
    return None

_PATTERNS.append(_p_catkin_make)


def _p_numpy(normalized: str, _raw: str) -> LogAnalysis | None:
    if "numpy" in normalized and _any(normalized, "modulenotfounderror", "importerror",
                                        "no module"):
        return LogAnalysis(
            error_type="NumPy import error in ROS context",
            diagnosis="NumPy could not be imported — common in vision or sensor processing nodes.",
            possible_causes=(
                "NumPy is not installed in the active Python environment.",
                "The ROS Python path conflicts with a system or virtualenv Python.",
                "A pip-installed NumPy conflicts with an apt-installed ROS Python package.",
            ),
            suggested_fixes=(
                "Install NumPy: 'pip install numpy' or 'sudo apt install python3-numpy'.",
                "Check which Python is used: 'which python' and 'python -c \"import numpy\"'.",
                "For ROS2: ensure the virtualenv inherits system site-packages.",
            ),
            confidence="high",
        )
    return None

_PATTERNS.append(_p_numpy)


def _p_yaml_config(normalized: str, _raw: str) -> LogAnalysis | None:
    if "yaml" in normalized and _any(normalized, "error", "parse", "invalid", "scannererror",
                                       "could not load", "failed to load", "syntax error"):
        return LogAnalysis(
            error_type="YAML config parse error",
            diagnosis="A YAML configuration or launch file could not be parsed.",
            possible_causes=(
                "Indentation is incorrect (tabs vs spaces).",
                "A YAML value contains unescaped special characters.",
                "The file path is wrong or the file does not exist.",
            ),
            suggested_fixes=(
                "Check YAML syntax: use a YAML validator or 'python -c \"import yaml; yaml.safe_load(open('f'))\"'.",
                "Ensure consistent indentation with spaces (no tabs).",
                "Verify the file path is correct and the file is readable.",
            ),
            confidence="medium",
        )
    return None

_PATTERNS.append(_p_yaml_config)

# Re-add generic ModuleNotFoundError AFTER specific import patterns
_PATTERNS.append(_p0_modulenotfound)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize(log_text: str) -> str:
    return " ".join(log_text.strip().lower().split())


def _any(text: str, *patterns: str) -> bool:
    return any(p in text for p in patterns)


def _unknown_error() -> LogAnalysis:
    return LogAnalysis(
        error_type="unknown",
        diagnosis="RoboPilot could not confidently match this log to a known offline rule.",
        possible_causes=(
            "The key error line may be missing from the provided log.",
            "The failure may be project-specific or outside the current rule set.",
            "The log may contain multiple overlapping errors.",
        ),
        suggested_fixes=(
            "Look for the first traceback line or the first explicit error message.",
            "Rerun the command with verbose logging if available.",
            "Check environment setup, dependency installation, and file permissions.",
        ),
        confidence="low",
    )
