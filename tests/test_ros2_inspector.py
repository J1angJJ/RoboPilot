import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.api.static_analysis import inspect_ros2_project_static
from robopilot.main import app
from robopilot.ros2.inspector import inspect_ros2_project


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _valid_ament_python_package(path: Path) -> None:
    _write(
        path / "package.xml",
        """
<package format="3">
  <name>ros2_py_demo</name>
  <version>0.0.1</version>
  <description>Demo ROS2 Python package</description>
  <maintainer email="demo@example.com">Demo</maintainer>
  <license>MIT</license>
  <exec_depend>rclpy</exec_depend>
  <exec_depend>std_msgs</exec_depend>
  <test_depend>pytest</test_depend>
  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
""",
    )
    _write(
        path / "setup.py",
        """
from setuptools import setup

package_name = 'ros2_py_demo'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
)
""",
    )
    _write(path / "setup.cfg", "[develop]\nscript_dir=$base/lib/ros2_py_demo\n")
    _write(path / "resource" / "ros2_py_demo", "")
    _write(path / "ros2_py_demo" / "__init__.py", "")
    _write(path / "ros2_py_demo" / "talker.py", "import rclpy\nrclpy.init()\n")
    _write(path / "launch" / "demo.launch.py", "from launch import LaunchDescription\n")
    _write(path / "config" / "params.yaml", "ros__parameters: {}\n")
    _write(path / "msg" / "Demo.msg", "string data\n")
    _write(path / "srv" / "Demo.srv", "string input\n---\nstring output\n")
    _write(path / "action" / "Demo.action", "string goal\n---\nstring result\n---\nstring feedback\n")


def _valid_ament_cmake_package(path: Path) -> None:
    _write(
        path / "package.xml",
        """
<package format="3">
  <name>ros2_cpp_demo</name>
  <version>0.0.1</version>
  <description>Demo ROS2 C++ package</description>
  <maintainer email="demo@example.com">Demo</maintainer>
  <license>MIT</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <depend>rclcpp</depend>
  <depend>std_msgs</depend>
  <build_depend>rosidl_default_generators</build_depend>
  <exec_depend>rosidl_default_runtime</exec_depend>
  <test_depend>ament_lint_auto</test_depend>
  <member_of_group>rosidl_interface_packages</member_of_group>
</package>
""",
    )
    _write(
        path / "CMakeLists.txt",
        """
cmake_minimum_required(VERSION 3.8)
project(ros2_cpp_demo)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME} "msg/Demo.msg")
ament_package()
""",
    )
    _write(path / "src" / "listener.cpp", "#include <rclcpp/rclcpp.hpp>\nint main() { rclcpp::init(0, nullptr); }\n")
    _write(path / "launch" / "demo.launch.py", "from launch import LaunchDescription\n")
    _write(path / "config" / "params.yaml", "ros__parameters: {}\n")
    _write(path / "msg" / "Demo.msg", "string data\n")


def test_inspects_valid_minimal_ros2_ament_python_package(tmp_path: Path) -> None:
    project = tmp_path / "ros2_py_demo"
    _valid_ament_python_package(project)

    result = inspect_ros2_project(project)

    assert result.exists
    assert result.detected_project_type == "ros2_ament_python_package"
    assert result.package_name == "ros2_py_demo"
    assert result.build_system.ament_python is True


def test_inspects_valid_minimal_ros2_ament_cmake_package(tmp_path: Path) -> None:
    project = tmp_path / "ros2_cpp_demo"
    _valid_ament_cmake_package(project)

    result = inspect_ros2_project(project)

    assert result.exists
    assert result.detected_project_type == "ros2_ament_cmake_package"
    assert result.package_name == "ros2_cpp_demo"
    assert result.build_system.ament_cmake is True


def test_extracts_package_name_from_package_xml(tmp_path: Path) -> None:
    project = tmp_path / "ros2_py_demo"
    _valid_ament_python_package(project)

    assert inspect_ros2_project(project).package_name == "ros2_py_demo"


def test_extracts_ament_cmake_buildtool_dependency(tmp_path: Path) -> None:
    project = tmp_path / "ros2_cpp_demo"
    _valid_ament_cmake_package(project)

    assert inspect_ros2_project(project).dependencies.buildtool == ("ament_cmake",)


def test_extracts_ament_python_build_type(tmp_path: Path) -> None:
    project = tmp_path / "ros2_py_demo"
    _valid_ament_python_package(project)

    result = inspect_ros2_project(project)

    assert result.build_system.ament_python is True
    assert "package.xml missing ament_python build type for Python package" not in result.issues


def test_detects_setup_cfg_and_resource_marker(tmp_path: Path) -> None:
    project = tmp_path / "ros2_py_demo"
    _valid_ament_python_package(project)

    build = inspect_ros2_project(project).build_system

    assert build.setup_py is True
    assert build.setup_cfg is True
    assert build.resource_marker is True


def test_detects_ament_package(tmp_path: Path) -> None:
    project = tmp_path / "ros2_cpp_demo"
    _valid_ament_cmake_package(project)

    assert inspect_ros2_project(project).build_system.ament_package is True


def test_detects_launch_config_msg_srv_action_files(tmp_path: Path) -> None:
    project = tmp_path / "ros2_py_demo"
    _valid_ament_python_package(project)
    files = inspect_ros2_project(project).files

    assert files.launch_files == ("launch/demo.launch.py",)
    assert files.config_files == ("config/params.yaml",)
    assert files.msg_files == ("msg/Demo.msg",)
    assert files.srv_files == ("srv/Demo.srv",)
    assert files.action_files == ("action/Demo.action",)


def test_detects_rclpy_python_node_candidates(tmp_path: Path) -> None:
    project = tmp_path / "ros2_py_demo"
    _valid_ament_python_package(project)
    result = inspect_ros2_project(project)

    assert result.rclpy_usage
    assert result.nodes.python_node_candidates == ("ros2_py_demo/talker.py",)


def test_detects_rclcpp_cpp_node_candidates(tmp_path: Path) -> None:
    project = tmp_path / "ros2_cpp_demo"
    _valid_ament_cmake_package(project)
    result = inspect_ros2_project(project)

    assert result.rclcpp_usage
    assert result.nodes.cpp_node_candidates == ("src/listener.cpp",)


def test_reports_missing_package_xml(tmp_path: Path) -> None:
    project = tmp_path / "broken_ros2"
    _write(project / "setup.py", "from setuptools import setup\n")

    result = inspect_ros2_project(project)

    assert "missing package.xml" in result.issues


def test_reports_missing_build_system_files(tmp_path: Path) -> None:
    project = tmp_path / "broken_ros2_py"
    _write(
        project / "package.xml",
        "<package format=\"3\"><name>broken</name><export><build_type>ament_python</build_type></export></package>",
    )
    _write(project / "broken" / "node.py", "import rclpy\n")

    result = inspect_ros2_project(project)

    assert "missing setup.py for ament_python-style package" in result.issues
    assert "missing setup.cfg for ament_python-style package" in result.issues
    assert "missing resource marker for ament_python-style package" in result.issues


def test_warns_when_detector_says_ros1_catkin_package(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _write(
        project / "package.xml",
        "<package format=\"2\"><name>ros1_demo</name><buildtool_depend>catkin</buildtool_depend></package>",
    )
    _write(project / "CMakeLists.txt", "find_package(catkin REQUIRED)\ncatkin_package()\n")

    result = inspect_ros2_project(project)

    assert result.detected_project_type == "ros1_catkin_package"
    assert "detector classified this project as ros1_catkin_package; inspect-ros2 may not be appropriate" in result.issues


def test_warns_when_detector_says_non_ros_project(tmp_path: Path) -> None:
    project = tmp_path / "plain"
    _write(project / "README.md", "plain project\n")

    result = inspect_ros2_project(project)

    assert result.detected_project_type == "non_ros_project"
    assert "detector classified this project as non_ros_project" in result.issues


def test_json_output_has_stable_top_level_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros2_py_demo"
    _valid_ament_python_package(project)

    result = CliRunner().invoke(app, ["inspect-ros2", str(project), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert list(data.keys()) == [
        "project_path",
        "exists",
        "package_name",
        "package_format",
        "detected_project_type",
        "dependencies",
        "build_system",
        "files",
        "nodes",
        "rclpy_usage",
        "rclcpp_usage",
        "issues",
        "suggested_next_steps",
        "safety_note",
    ]


def test_api_wrapper_returns_structured_data(tmp_path: Path) -> None:
    project = tmp_path / "ros2_py_demo"
    _valid_ament_python_package(project)

    result = inspect_ros2_project_static(project)

    assert result["package_name"] == "ros2_py_demo"
    assert result["detected_project_type"] == "ros2_ament_python_package"
    assert "build_system" in result


def test_no_user_code_is_executed(tmp_path: Path) -> None:
    project = tmp_path / "ros2_py_demo"
    _valid_ament_python_package(project)
    marker = tmp_path / "executed.txt"
    _write(
        project / "ros2_py_demo" / "danger.py",
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\nimport rclpy\n",
    )

    result = inspect_ros2_project(project)

    assert "ros2_py_demo/danger.py" in result.nodes.python_node_candidates
    assert not marker.exists()


def test_cli_readable_output_works(tmp_path: Path) -> None:
    project = tmp_path / "ros2_py_demo"
    _valid_ament_python_package(project)

    result = CliRunner().invoke(app, ["inspect-ros2", str(project)])

    assert result.exit_code == 0
    assert "ROS2 Inspection Summary" in result.output
    assert "ros2_py_demo" in result.output
