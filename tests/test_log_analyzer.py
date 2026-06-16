from robopilot.debugger.log_analyzer import analyze_log


def test_analyzer_detects_cv_bridge_missing() -> None:
    analysis = analyze_log("ModuleNotFoundError: No module named 'cv_bridge'")

    assert analysis.error_type == "cv_bridge missing"
    assert analysis.confidence == "high"
    assert "cv_bridge" in analysis.diagnosis


def test_analyzer_detects_opencv_camera_timeout() -> None:
    analysis = analyze_log("OpenCV camera timeout: cannot read frame")

    assert analysis.error_type == "OpenCV camera read failure"
    assert analysis.confidence == "high"
    assert "camera" in analysis.diagnosis.lower()


def test_analyzer_detects_cuda_out_of_memory() -> None:
    analysis = analyze_log("RuntimeError: CUDA out of memory")

    assert analysis.error_type == "CUDA out of memory"
    assert analysis.confidence == "high"
    assert "GPU" in analysis.possible_causes[0]


def test_analyzer_returns_unknown_fallback() -> None:
    analysis = analyze_log("robot stopped unexpectedly with no more details")

    assert analysis.error_type == "unknown"
    assert analysis.confidence == "low"
    assert analysis.suggested_fixes


# ---------------------------------------------------------------------------
# v2.1.0 M6 new error pattern tests
# ---------------------------------------------------------------------------


def test_tf2_lookup_timeout() -> None:
    analysis = analyze_log(
        "LookupException: Lookup would require extrapolation into the future. "
        "Requested time 1620.500 but the latest data is at 1620.200"
    )
    assert analysis.error_type == "TF2 transform lookup failure"
    assert analysis.confidence == "high"


def test_frame_not_found() -> None:
    analysis = analyze_log(
        "InvalidArgumentException: Frame 'base_laser_link' does not exist. "
        "Available frames: base_link, odom, map"
    )
    assert analysis.error_type == "TF frame not found"
    assert "frame" in analysis.diagnosis.lower()


def test_parameter_not_set() -> None:
    analysis = analyze_log(
        "rclpy.exceptions.ParameterNotDeclaredException: parameter 'max_speed' not set"
    )
    assert analysis.error_type == "ROS parameter not found"


def test_action_server_unavailable() -> None:
    analysis = analyze_log(
        "Action client timed out waiting for action server '/follow_joint_trajectory'"
    )
    assert analysis.error_type == "ROS action server unavailable"


def test_qos_mismatch() -> None:
    analysis = analyze_log(
        "WARNING: New publisher discovered on topic '/scan', offering incompatible QoS. "
        "No compatible subscription found."
    )
    assert analysis.error_type == "QoS mismatch"


def test_dds_discovery() -> None:
    analysis = analyze_log(
        "No publishers found on topic '/cmd_vel'. Check ROS_DOMAIN_ID."
    )
    assert analysis.error_type == "DDS discovery / topic connectivity issue"
    assert analysis.confidence == "medium"


def test_cmake_error() -> None:
    analysis = analyze_log(
        "CMake Error at CMakeLists.txt:15 (find_package): "
        "Could not find a package configuration file provided by \"OpenCV\""
    )
    assert analysis.error_type == "CMake build error"


def test_linker_error() -> None:
    analysis = analyze_log(
        "undefined reference to `cv::imread(std::string const&)' "
        "collect2: ld returned 1 exit status"
    )
    assert analysis.error_type == "Linker error (undefined reference)"


def test_rospy_import_error() -> None:
    analysis = analyze_log(
        "ModuleNotFoundError: No module named 'rospy'"
    )
    assert analysis.error_type == "rospy import error"


def test_rclpy_import_error() -> None:
    analysis = analyze_log(
        "ImportError: cannot import name 'rclpy'"
    )
    assert analysis.error_type == "rclpy import error"


def test_message_generation_not_found() -> None:
    analysis = analyze_log(
        "ModuleNotFoundError: No module named 'my_pkg.msg' - "
        "unknown message type: my_pkg/CustomMsg"
    )
    assert analysis.error_type == "ROS message/service generation not found"


def test_segmentation_fault() -> None:
    analysis = analyze_log(
        "Process has died [pid 12345, exit code -11, signal SIGSEGV]"
    )
    assert analysis.error_type == "Node crash / segmentation fault"


def test_roscore_not_running() -> None:
    analysis = analyze_log(
        "ROS_MASTER_URI=http://localhost:11311. Unable to communicate with master!"
    )
    assert analysis.error_type == "ROS master / roscore not running"


def test_disk_full() -> None:
    analysis = analyze_log(
        "IOError: [Errno 28] No space left on device: 'output.bag'"
    )
    assert analysis.error_type == "Disk full / no space left"


def test_network_connection_refused() -> None:
    analysis = analyze_log(
        "socket.error: [Errno 111] Connection refused"
    )
    assert analysis.error_type == "Network connection error"


def test_shared_library_not_found() -> None:
    analysis = analyze_log(
        "ImportError: libopencv_core.so.4.5: cannot open shared object file: "
        "No such file or directory"
    )
    assert analysis.error_type == "Shared library not found"


def test_catkin_make_failure() -> None:
    analysis = analyze_log(
        "catkin_make failed: package 'my_ros1_pkg' build error"
    )
    assert analysis.error_type == "catkin_make build failure"


def test_numpy_import_error() -> None:
    analysis = analyze_log(
        "ModuleNotFoundError: No module named 'numpy'"
    )
    assert analysis.error_type == "NumPy import error in ROS context"


def test_yaml_parse_error() -> None:
    analysis = analyze_log(
        "YAML error: could not load config file: ScannerError: "
        "mapping values are not allowed here"
    )
    assert analysis.error_type == "YAML config parse error"
