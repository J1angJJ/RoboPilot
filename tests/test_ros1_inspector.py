import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.main import app
from robopilot.ros1.inspector import inspect_ros1_project


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _valid_ros1_package(path: Path) -> None:
    _write(
        path / "package.xml",
        """
<package format="2">
  <name>ros1_demo</name>
  <version>0.0.1</version>
  <buildtool_depend>catkin</buildtool_depend>
  <build_depend>roscpp</build_depend>
  <build_depend>rospy</build_depend>
  <exec_depend>std_msgs</exec_depend>
  <run_depend>sensor_msgs</run_depend>
</package>
""",
    )
    _write(
        path / "CMakeLists.txt",
        """
cmake_minimum_required(VERSION 3.0.2)
project(ros1_demo)
find_package(catkin REQUIRED COMPONENTS roscpp rospy std_msgs message_generation)
add_message_files(FILES Demo.msg)
add_service_files(FILES Demo.srv)
add_action_files(FILES Demo.action)
generate_messages(DEPENDENCIES std_msgs)
catkin_package()
""",
    )
    _write(path / "launch" / "demo.launch", "<launch></launch>\n")
    _write(path / "scripts" / "talker.py", "#!/usr/bin/env python\nimport rospy\n")
    _write(path / "src" / "listener.cpp", "#include <ros/ros.h>\nint main() { ros::init(0, nullptr, \"listener\"); }\n")
    _write(path / "msg" / "Demo.msg", "string data\n")
    _write(path / "srv" / "Demo.srv", "string input\n---\nstring output\n")
    _write(path / "action" / "Demo.action", "string goal\n---\nstring result\n---\nstring feedback\n")


def test_inspects_valid_minimal_ros1_catkin_package(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _valid_ros1_package(project)

    result = inspect_ros1_project(project)

    assert result.exists
    assert result.detected_project_type == "ros1_catkin_package"
    assert result.package_name == "ros1_demo"
    assert result.catkin.catkin_package


def test_extracts_package_name_from_package_xml(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _valid_ros1_package(project)

    assert inspect_ros1_project(project).package_name == "ros1_demo"


def test_extracts_catkin_buildtool_dependency(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _valid_ros1_package(project)

    assert inspect_ros1_project(project).dependencies.buildtool == ("catkin",)


def test_extracts_build_exec_run_dependencies(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _valid_ros1_package(project)
    deps = inspect_ros1_project(project).dependencies

    assert deps.build == ("roscpp", "rospy")
    assert deps.exec == ("std_msgs",)
    assert deps.run == ("sensor_msgs",)


def test_extracts_catkin_components_from_cmake(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _valid_ros1_package(project)

    components = inspect_ros1_project(project).catkin.catkin_components

    assert components == ("message_generation", "roscpp", "rospy", "std_msgs")


def test_detects_catkin_package(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _valid_ros1_package(project)

    assert inspect_ros1_project(project).catkin.catkin_package is True


def test_detects_launch_msg_srv_action_files(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _valid_ros1_package(project)
    files = inspect_ros1_project(project).files

    assert files.launch_files == ("launch/demo.launch",)
    assert files.msg_files == ("msg/Demo.msg",)
    assert files.srv_files == ("srv/Demo.srv",)
    assert files.action_files == ("action/Demo.action",)


def test_detects_rospy_python_node_candidates(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _valid_ros1_package(project)
    result = inspect_ros1_project(project)

    assert result.rospy_usage
    assert result.nodes.python_node_candidates == ("scripts/talker.py",)


def test_detects_roscpp_cpp_node_candidates(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _valid_ros1_package(project)
    result = inspect_ros1_project(project)

    assert result.roscpp_usage
    assert result.nodes.cpp_node_candidates == ("src/listener.cpp",)


def test_reports_missing_package_xml(tmp_path: Path) -> None:
    project = tmp_path / "broken_ros1"
    _write(project / "CMakeLists.txt", "find_package(catkin REQUIRED)\ncatkin_package()\n")

    result = inspect_ros1_project(project)

    assert "missing package.xml" in result.issues


def test_reports_missing_cmakelists(tmp_path: Path) -> None:
    project = tmp_path / "broken_ros1"
    _write(project / "package.xml", "<package format=\"2\"><name>broken</name><buildtool_depend>catkin</buildtool_depend></package>")

    result = inspect_ros1_project(project)

    assert "missing CMakeLists.txt" in result.issues


def test_warns_when_detector_says_non_ros_project(tmp_path: Path) -> None:
    project = tmp_path / "plain"
    _write(project / "README.md", "plain project\n")

    result = inspect_ros1_project(project)

    assert result.detected_project_type == "non_ros_project"
    assert "detector classified this project as non_ros_project" in result.issues


def test_json_output_has_stable_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _valid_ros1_package(project)
    runner = CliRunner()

    result = runner.invoke(app, ["inspect-ros1", str(project), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert list(data.keys()) == [
        "project_path",
        "exists",
        "package_name",
        "package_format",
        "detected_project_type",
        "dependencies",
        "catkin",
        "files",
        "nodes",
        "rospy_usage",
        "roscpp_usage",
        "issues",
        "suggested_next_steps",
        "safety_note",
    ]


def test_no_user_code_is_executed(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _valid_ros1_package(project)
    marker = tmp_path / "executed.txt"
    _write(
        project / "scripts" / "danger.py",
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\nimport rospy\n",
    )

    result = inspect_ros1_project(project)

    assert "scripts/danger.py" in result.nodes.python_node_candidates
    assert not marker.exists()


def test_cli_readable_output_works(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _valid_ros1_package(project)
    runner = CliRunner()

    result = runner.invoke(app, ["inspect-ros1", str(project)])

    assert result.exit_code == 0
    assert "ROS1 Inspection Summary" in result.output
    assert "ros1_demo" in result.output
