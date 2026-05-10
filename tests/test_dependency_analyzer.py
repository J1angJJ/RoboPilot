import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.deps.analyzer import analyze_dependencies
from robopilot.main import app


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _ros1_package(path: Path, *, declare_rospy: bool = True, declare_roscpp: bool = True) -> None:
    build_deps = ["std_msgs", "unused_dep"]
    exec_deps = ["sensor_msgs"]
    if declare_rospy:
        build_deps.append("rospy")
    if declare_roscpp:
        build_deps.append("roscpp")
    _write(
        path / "package.xml",
        "\n".join(
            [
                '<package format="2">',
                "  <name>ros1_dep_demo</name>",
                "  <version>0.0.1</version>",
                "  <buildtool_depend>catkin</buildtool_depend>",
                *(f"  <build_depend>{dep}</build_depend>" for dep in build_deps),
                *(f"  <exec_depend>{dep}</exec_depend>" for dep in exec_deps),
                "  <run_depend>geometry_msgs</run_depend>",
                "  <test_depend>rostest</test_depend>",
                "</package>",
            ]
        ),
    )
    _write(
        path / "CMakeLists.txt",
        """
cmake_minimum_required(VERSION 3.0.2)
project(ros1_dep_demo)
find_package(catkin REQUIRED COMPONENTS roscpp rospy std_msgs)
catkin_package()
""",
    )
    _write(
        path / "scripts" / "talker.py",
        """
from pathlib import Path
import rospy
import numpy as np
from sensor_msgs.msg import Image
""",
    )
    _write(
        path / "src" / "listener.cpp",
        """
#include <ros/ros.h>
#include <std_msgs/String.h>
int main(int argc, char **argv) { ros::init(argc, argv, "listener"); }
""",
    )
    _write(path / "launch" / "demo.launch", '<launch><node pkg="ros1_dep_demo" type="talker.py" /></launch>')


def _ros2_py_package(path: Path) -> None:
    _write(
        path / "package.xml",
        """
<package format="3">
  <name>ros2_py_dep_demo</name>
  <version>0.0.1</version>
  <buildtool_depend>ament_python</buildtool_depend>
  <exec_depend>rclpy</exec_depend>
  <exec_depend>std_msgs</exec_depend>
  <export><build_type>ament_python</build_type></export>
</package>
""",
    )
    _write(path / "setup.py", "from setuptools import setup\nsetup(name='ros2_py_dep_demo')\n")
    _write(path / "setup.cfg", "[develop]\nscript_dir=$base/lib/ros2_py_dep_demo\n")
    _write(path / "resource" / "ros2_py_dep_demo", "")
    _write(path / "ros2_py_dep_demo" / "node.py", "import rclpy\nfrom std_msgs.msg import String\n")


def _ros2_cpp_package(path: Path) -> None:
    _write(
        path / "package.xml",
        """
<package format="3">
  <name>ros2_cpp_dep_demo</name>
  <version>0.0.1</version>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <depend>rclcpp</depend>
  <depend>geometry_msgs</depend>
</package>
""",
    )
    _write(
        path / "CMakeLists.txt",
        """
cmake_minimum_required(VERSION 3.8)
project(ros2_cpp_dep_demo)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
ament_package()
""",
    )
    _write(path / "src" / "node.cpp", "#include <rclcpp/rclcpp.hpp>\n#include <geometry_msgs/msg/twist.hpp>\n")


def test_extracts_package_xml_dependencies_from_ros1_package(tmp_path: Path) -> None:
    project = tmp_path / "ros1_dep_demo"
    _ros1_package(project)

    deps = analyze_dependencies(project).declared_dependencies

    assert deps.buildtool == ("catkin",)
    assert deps.build == ("roscpp", "rospy", "std_msgs", "unused_dep")
    assert deps.exec == ("sensor_msgs",)
    assert deps.run == ("geometry_msgs",)
    assert deps.test == ("rostest",)


def test_extracts_catkin_components_from_cmakelists(tmp_path: Path) -> None:
    project = tmp_path / "ros1_dep_demo"
    _ros1_package(project)

    usage = analyze_dependencies(project).detected_usage

    assert usage.catkin_components == ("roscpp", "rospy", "std_msgs")


def test_detects_python_imports(tmp_path: Path) -> None:
    project = tmp_path / "ros1_dep_demo"
    _ros1_package(project)

    imports = analyze_dependencies(project).detected_usage.python_imports

    assert "rospy" in imports
    assert "numpy" in imports
    assert "sensor_msgs" in imports


def test_detects_cpp_includes(tmp_path: Path) -> None:
    project = tmp_path / "ros1_dep_demo"
    _ros1_package(project)

    includes = analyze_dependencies(project).detected_usage.cpp_includes

    assert "ros/ros.h" in includes
    assert "std_msgs/String.h" in includes


def test_infers_missing_rospy_dependency(tmp_path: Path) -> None:
    project = tmp_path / "ros1_dep_demo"
    _ros1_package(project, declare_rospy=False)

    result = analyze_dependencies(project)

    assert "rospy" in result.possibly_missing


def test_infers_missing_roscpp_dependency(tmp_path: Path) -> None:
    project = tmp_path / "ros1_dep_demo"
    _ros1_package(project, declare_roscpp=False)

    result = analyze_dependencies(project)

    assert "roscpp" in result.possibly_missing


def test_detects_possibly_unused_declared_dependency(tmp_path: Path) -> None:
    project = tmp_path / "ros1_dep_demo"
    _ros1_package(project)

    result = analyze_dependencies(project)

    assert "unused_dep" in result.possibly_unused


def test_handles_ros2_ament_python_style_package(tmp_path: Path) -> None:
    project = tmp_path / "ros2_py_dep_demo"
    _ros2_py_package(project)

    result = analyze_dependencies(project)

    assert result.project_type == "ros2_ament_python_package"
    assert "rclpy" in result.detected_usage.python_imports
    assert "rclpy" in result.inferred_dependencies


def test_handles_ros2_ament_cpp_style_package(tmp_path: Path) -> None:
    project = tmp_path / "ros2_cpp_dep_demo"
    _ros2_cpp_package(project)

    result = analyze_dependencies(project)

    assert result.project_type == "ros2_ament_cmake_package"
    assert "rclcpp/rclcpp.hpp" in result.detected_usage.cpp_includes
    assert "rclcpp" in result.inferred_dependencies


def test_handles_non_ros_project_with_warning(tmp_path: Path) -> None:
    project = tmp_path / "plain"
    _write(project / "README.md", "plain project\n")

    result = analyze_dependencies(project)

    assert result.project_type == "non_ros_project"
    assert "detector classified this project as non_ros_project; dependency analysis may be limited" in result.warnings


def test_handles_missing_project_path(tmp_path: Path) -> None:
    result = analyze_dependencies(tmp_path / "missing")

    assert result.exists is False
    assert "project path does not exist" in result.warnings


def test_json_output_has_stable_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_dep_demo"
    _ros1_package(project)
    runner = CliRunner()

    result = runner.invoke(app, ["deps", str(project), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert list(data.keys()) == [
        "project_path",
        "exists",
        "project_type",
        "declared_dependencies",
        "detected_usage",
        "inferred_dependencies",
        "possibly_missing",
        "possibly_unused",
        "hints",
        "warnings",
        "suggested_next_steps",
        "safety_note",
    ]


def test_no_user_code_is_executed(tmp_path: Path) -> None:
    project = tmp_path / "ros1_dep_demo"
    _ros1_package(project)
    marker = tmp_path / "executed.txt"
    _write(
        project / "scripts" / "danger.py",
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\nimport rospy\n",
    )

    result = analyze_dependencies(project)

    assert "rospy" in result.detected_usage.python_imports
    assert not marker.exists()


def test_cli_readable_output_works(tmp_path: Path) -> None:
    project = tmp_path / "ros1_dep_demo"
    _ros1_package(project)
    runner = CliRunner()

    result = runner.invoke(app, ["deps", str(project)])

    assert result.exit_code == 0
    assert "Dependency Analysis Summary" in result.output
    assert "Possibly Missing Dependencies" in result.output
