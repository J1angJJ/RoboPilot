import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.detector.project_detector import detect_project
from robopilot.main import app


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _ros1_package(path: Path) -> None:
    _write(
        path / "package.xml",
        """
<package format="2">
  <name>ros1_demo</name>
  <version>0.0.1</version>
  <buildtool_depend>catkin</buildtool_depend>
</package>
""",
    )
    _write(
        path / "CMakeLists.txt",
        """
cmake_minimum_required(VERSION 3.0.2)
project(ros1_demo)
find_package(catkin REQUIRED COMPONENTS rospy roscpp)
catkin_package()
""",
    )
    _write(path / "scripts" / "talker.py", "import rospy\n")


def _ros2_python_package(path: Path) -> None:
    _write(
        path / "package.xml",
        """
<package format="3">
  <name>ros2_py_demo</name>
  <version>0.0.1</version>
  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
""",
    )
    _write(path / "setup.py", "from setuptools import setup\nsetup(data_files=[('share/ament_index/resource_index/packages', ['resource/ros2_py_demo'])])\n")
    _write(path / "setup.cfg", "[develop]\nscript_dir=$base/lib/ros2_py_demo\n")
    _write(path / "resource" / "ros2_py_demo", "")
    _write(path / "ros2_py_demo" / "node.py", "import rclpy\n")


def _ros2_cmake_package(path: Path) -> None:
    _write(
        path / "package.xml",
        """
<package format="3">
  <name>ros2_cpp_demo</name>
  <version>0.0.1</version>
  <buildtool_depend>ament_cmake</buildtool_depend>
</package>
""",
    )
    _write(
        path / "CMakeLists.txt",
        """
cmake_minimum_required(VERSION 3.8)
project(ros2_cpp_demo)
find_package(ament_cmake REQUIRED)
ament_package()
""",
    )
    _write(path / "src" / "node.cpp", "#include <rclcpp/rclcpp.hpp>\n")


def test_detects_robopilot_generated_project() -> None:
    result = detect_project(Path("examples/generated_projects/demo_detector"))

    assert result.exists
    assert result.project_type == "robopilot_project"
    assert result.confidence == "high"
    assert "robopilot.yaml" in result.detected_signals


def test_detects_minimal_ros1_catkin_package(tmp_path: Path) -> None:
    project = tmp_path / "ros1_catkin_demo"
    _ros1_package(project)

    result = detect_project(project)

    assert result.project_type == "ros1_catkin_package"
    assert result.confidence == "high"
    assert "CMakeLists.txt: catkin_package" in result.detected_signals


def test_detects_ros2_ament_python_package(tmp_path: Path) -> None:
    project = tmp_path / "ros2_ament_python_demo"
    _ros2_python_package(project)

    result = detect_project(project)

    assert result.project_type == "ros2_ament_python_package"
    assert result.confidence == "high"
    assert "package.xml: build_type ament_python" in result.detected_signals


def test_detects_ros2_ament_cmake_package(tmp_path: Path) -> None:
    project = tmp_path / "ros2_ament_cmake_demo"
    _ros2_cmake_package(project)

    result = detect_project(project)

    assert result.project_type == "ros2_ament_cmake_package"
    assert result.confidence == "high"
    assert "CMakeLists.txt: ament_package" in result.detected_signals


def test_detects_mixed_ros_signals(tmp_path: Path) -> None:
    project = tmp_path / "mixed_demo"
    _ros1_package(project)
    _write(
        project / "package.xml",
        """
<package format="3">
  <name>mixed_demo</name>
  <version>0.0.1</version>
  <buildtool_depend>catkin</buildtool_depend>
  <buildtool_depend>ament_cmake</buildtool_depend>
</package>
""",
    )
    _write(project / "src" / "node.cpp", "#include <rclcpp/rclcpp.hpp>\n")

    result = detect_project(project)

    assert result.project_type == "mixed_ros_project"
    assert result.confidence == "high"


def test_detects_non_ros_project(tmp_path: Path) -> None:
    project = tmp_path / "non_ros_demo"
    _write(project / "README.md", "just a plain project\n")

    result = detect_project(project)

    assert result.project_type == "non_ros_project"
    assert result.confidence == "high"


def test_detects_missing_path(tmp_path: Path) -> None:
    result = detect_project(tmp_path / "missing")

    assert not result.exists
    assert result.project_type == "unknown"
    assert result.confidence == "none"


def test_json_output_has_stable_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_catkin_demo"
    _ros1_package(project)
    runner = CliRunner()

    result = runner.invoke(app, ["detect", str(project), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert list(data.keys()) == [
        "project_path",
        "exists",
        "project_type",
        "confidence",
        "detected_signals",
        "missing_common_files",
        "notes",
        "suggested_next_steps",
    ]
    assert data["project_type"] == "ros1_catkin_package"


def test_confidence_is_deterministic(tmp_path: Path) -> None:
    project = tmp_path / "ros2_ament_python_demo"
    _ros2_python_package(project)

    first = detect_project(project)
    second = detect_project(project)

    assert first.confidence == second.confidence
    assert first.detected_signals == second.detected_signals


def test_no_user_code_is_executed(tmp_path: Path) -> None:
    project = tmp_path / "ros2_ament_python_demo"
    _ros2_python_package(project)
    marker = tmp_path / "executed.txt"
    _write(
        project / "ros2_py_demo" / "danger.py",
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\nimport rclpy\n",
    )

    result = detect_project(project)

    assert result.project_type == "ros2_ament_python_package"
    assert not marker.exists()


def test_cli_readable_output_works(tmp_path: Path) -> None:
    project = tmp_path / "ros2_ament_cmake_demo"
    _ros2_cmake_package(project)
    runner = CliRunner()

    result = runner.invoke(app, ["detect", str(project)])

    assert result.exit_code == 0
    assert "Detection Summary" in result.output
    assert "ros2_ament_cmake_package" in result.output
