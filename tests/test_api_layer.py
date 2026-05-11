from __future__ import annotations

from pathlib import Path

from robopilot.api.apply import preview_apply, read_project_history
from robopilot.api.migration import (
    create_ros1_to_ros2_migration_plan,
    preview_migration_plan,
    validate_migration_plan_file,
)
from robopilot.api.project import plan_project
from robopilot.api.static_analysis import (
    analyze_project_dependencies,
    detect_project_type,
    inspect_ros1_project_static,
    inspect_ros2_project_static,
)


def test_detect_project_type_returns_structured_data(tmp_path: Path) -> None:
    project = _create_ros1_package(tmp_path)

    result = detect_project_type(project)

    assert result["project_path"] == str(project)
    assert result["project_type"] == "ros1_catkin_package"
    assert isinstance(result["detected_signals"], list)


def test_inspect_ros1_project_static_returns_structured_data(tmp_path: Path) -> None:
    project = _create_ros1_package(tmp_path)

    result = inspect_ros1_project_static(project)

    assert result["package_name"] == "demo_ros1"
    assert result["detected_project_type"] == "ros1_catkin_package"
    assert "dependencies" in result


def test_inspect_ros2_project_static_returns_structured_data(tmp_path: Path) -> None:
    project = _create_ros2_python_package(tmp_path)

    result = inspect_ros2_project_static(project)

    assert result["package_name"] == "demo_ros2_py"
    assert result["detected_project_type"] == "ros2_ament_python_package"
    assert "build_system" in result


def test_analyze_project_dependencies_returns_structured_data(tmp_path: Path) -> None:
    project = _create_ros1_package(tmp_path)

    result = analyze_project_dependencies(project)

    assert result["project_type"] == "ros1_catkin_package"
    assert "declared_dependencies" in result
    assert "migration_hints" in result
    assert "rosdep_hints" in result
    assert "rospy" in result["detected_usage"]["python_imports"]


def test_create_and_validate_migration_plan_from_api(tmp_path: Path) -> None:
    project = _create_ros1_package(tmp_path)
    output = tmp_path / "migration_plan.yaml"

    plan = create_ros1_to_ros2_migration_plan(project, output_path=output)
    validation = validate_migration_plan_file(output)

    assert output.exists()
    assert plan["target"] == "ros2"
    assert validation["valid"] is True


def test_preview_migration_plan_from_api(tmp_path: Path) -> None:
    project = _create_ros1_package(tmp_path)
    output = tmp_path / "migration_plan.yaml"
    create_ros1_to_ros2_migration_plan(project, output_path=output)

    result = preview_migration_plan(output, project)

    assert result["target"] == "ros2"
    assert "package.xml" in result["files_to_create"]


def test_preview_apply_returns_structured_data(tmp_path: Path) -> None:
    spec_path = tmp_path / "robopilot.yaml"
    plan_project(
        "demo_detector",
        "Create an object detection pipeline",
        output_path=spec_path,
    )

    result = preview_apply(spec_path, tmp_path / "missing_project")

    assert result["package_name"] == "demo_detector"
    assert result["missing_project"] is True
    assert "package.xml" in result["files_to_create"]


def test_read_project_history_handles_empty_history(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    result = read_project_history(project)

    assert result["project_path"] == str(project)
    assert result["entries"] == []


def test_api_functions_do_not_print_stdout(tmp_path: Path, capsys) -> None:
    project = _create_ros1_package(tmp_path)

    detect_project_type(project)
    inspect_ros1_project_static(project)
    inspect_ros2_project_static(_create_ros2_python_package(tmp_path))
    analyze_project_dependencies(project)
    read_project_history(project)

    captured = capsys.readouterr()
    assert captured.out == ""


def _create_ros1_package(tmp_path: Path) -> Path:
    project = tmp_path / "demo_ros1"
    (project / "launch").mkdir(parents=True)
    (project / "scripts").mkdir()
    (project / "src").mkdir()
    (project / "msg").mkdir()
    (project / "srv").mkdir()
    (project / "action").mkdir()

    (project / "package.xml").write_text(
        """<?xml version="1.0"?>
<package format="2">
  <name>demo_ros1</name>
  <version>0.0.1</version>
  <description>Demo ROS1 package</description>
  <maintainer email="demo@example.com">Demo</maintainer>
  <license>MIT</license>
  <buildtool_depend>catkin</buildtool_depend>
  <build_depend>rospy</build_depend>
  <exec_depend>rospy</exec_depend>
  <exec_depend>std_msgs</exec_depend>
</package>
""",
        encoding="utf-8",
    )
    (project / "CMakeLists.txt").write_text(
        """cmake_minimum_required(VERSION 3.0.2)
project(demo_ros1)
find_package(catkin REQUIRED COMPONENTS roscpp rospy std_msgs message_generation)
catkin_package()
""",
        encoding="utf-8",
    )
    (project / "launch" / "demo.launch").write_text("<launch></launch>\n", encoding="utf-8")
    (project / "scripts" / "talker.py").write_text(
        "import rospy\nrospy.init_node('talker')\n",
        encoding="utf-8",
    )
    (project / "src" / "listener.cpp").write_text(
        "#include <ros/ros.h>\nint main(int argc, char** argv) { return 0; }\n",
        encoding="utf-8",
    )
    (project / "msg" / "Demo.msg").write_text("string data\n", encoding="utf-8")
    (project / "srv" / "Demo.srv").write_text("string input\n---\nstring output\n", encoding="utf-8")
    (project / "action" / "Demo.action").write_text("string goal\n---\nstring result\n---\nstring feedback\n", encoding="utf-8")
    return project


def _create_ros2_python_package(tmp_path: Path) -> Path:
    project = tmp_path / "demo_ros2_py"
    (project / "resource").mkdir(parents=True)
    (project / "demo_ros2_py").mkdir()
    (project / "launch").mkdir()
    (project / "config").mkdir()
    (project / "package.xml").write_text(
        """<?xml version="1.0"?>
<package format="3">
  <name>demo_ros2_py</name>
  <version>0.0.1</version>
  <description>Demo ROS2 package</description>
  <maintainer email="demo@example.com">Demo</maintainer>
  <license>MIT</license>
  <exec_depend>rclpy</exec_depend>
  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
""",
        encoding="utf-8",
    )
    (project / "setup.py").write_text("from setuptools import setup\nsetup(name='demo_ros2_py')\n", encoding="utf-8")
    (project / "setup.cfg").write_text("[develop]\nscript_dir=$base/lib/demo_ros2_py\n", encoding="utf-8")
    (project / "resource" / "demo_ros2_py").write_text("", encoding="utf-8")
    (project / "demo_ros2_py" / "node.py").write_text("import rclpy\n", encoding="utf-8")
    (project / "launch" / "demo.launch.py").write_text("from launch import LaunchDescription\n", encoding="utf-8")
    (project / "config" / "params.yaml").write_text("ros__parameters: {}\n", encoding="utf-8")
    return project
