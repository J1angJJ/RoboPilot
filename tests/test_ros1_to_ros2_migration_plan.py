import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.main import app
from robopilot.migration.ros1_to_ros2 import generate_migration_plan, write_migration_plan


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _ros1_package(path: Path) -> None:
    _write(
        path / "package.xml",
        """
<package format="2">
  <name>ros1_migration_demo</name>
  <version>0.0.1</version>
  <buildtool_depend>catkin</buildtool_depend>
  <build_depend>roscpp</build_depend>
  <build_depend>rospy</build_depend>
  <build_depend>std_msgs</build_depend>
  <build_depend>message_generation</build_depend>
  <exec_depend>sensor_msgs</exec_depend>
  <exec_depend>message_runtime</exec_depend>
  <test_depend>rostest</test_depend>
</package>
""",
    )
    _write(
        path / "CMakeLists.txt",
        """
cmake_minimum_required(VERSION 3.0.2)
project(ros1_migration_demo)
find_package(catkin REQUIRED COMPONENTS roscpp rospy std_msgs message_generation)
add_message_files(FILES Demo.msg)
add_service_files(FILES Demo.srv)
add_action_files(FILES Demo.action)
generate_messages(DEPENDENCIES std_msgs)
catkin_package()
""",
    )
    _write(path / "launch" / "demo.launch", '<launch><node pkg="ros1_migration_demo" type="talker.py" /></launch>')
    _write(path / "scripts" / "talker.py", "import rospy\nrospy.init_node('talker')\n")
    _write(path / "src" / "listener.cpp", "#include <ros/ros.h>\nint main() { ros::NodeHandle nh; }\n")
    _write(path / "msg" / "Demo.msg", "string data\n")
    _write(path / "srv" / "Demo.srv", "string in\n---\nstring out\n")
    _write(path / "action" / "Demo.action", "string goal\n---\nstring result\n---\nstring feedback\n")


def test_generates_migration_plan_for_minimal_ros1_catkin_package(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    plan = generate_migration_plan(project, "ros2")

    assert plan.source_project_type == "ros1_catkin_package"
    assert plan.target == "ros2"
    assert plan.confidence == "high"


def test_migration_plan_includes_package_name(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    assert generate_migration_plan(project).package_name == "ros1_migration_demo"


def test_migration_plan_includes_package_xml_suggestions(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    suggestions = generate_migration_plan(project).package_xml_migration

    assert any("package.xml" in item for item in suggestions)
    assert any("catkin" in item and "ament" in item for item in suggestions)


def test_migration_plan_includes_catkin_to_ament_suggestions(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    suggestions = generate_migration_plan(project).build_system_migration

    assert any("catkin_package()" in item and "ament_package()" in item for item in suggestions)
    assert any("find_package(catkin" in item for item in suggestions)


def test_migration_plan_includes_rospy_to_rclpy_suggestions(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    suggestions = generate_migration_plan(project).source_code_migration

    assert any("rospy" in item and "rclpy" in item for item in suggestions)


def test_migration_plan_includes_roscpp_to_rclcpp_suggestions(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    suggestions = generate_migration_plan(project).source_code_migration

    assert any("roscpp" in item and "rclcpp" in item for item in suggestions)


def test_migration_plan_includes_launch_migration_suggestions(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    suggestions = generate_migration_plan(project).launch_migration

    assert any("ROS2 Python launch" in item for item in suggestions)


def test_migration_plan_includes_msg_srv_action_notes(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    notes = generate_migration_plan(project).interface_migration

    assert any("msg files" in item for item in notes)
    assert any("srv files" in item for item in notes)
    assert any("action files" in item for item in notes)


def test_migration_plan_includes_dependency_migration_hints(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    dependency = generate_migration_plan(project).dependency_migration

    hints = dependency["ros2_equivalent_hints"]
    assert isinstance(hints, list)
    assert any("rospy -> rclpy" in item for item in hints)
    assert any("roscpp -> rclcpp" in item for item in hints)


def test_non_ros_project_produces_warning_or_clear_risk(tmp_path: Path) -> None:
    project = tmp_path / "plain"
    _write(project / "README.md", "plain project\n")

    plan = generate_migration_plan(project)

    assert plan.source_project_type == "non_ros_project"
    assert any("non_ros_project" in item for item in plan.risks)


def test_unsupported_target_is_rejected(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    try:
        generate_migration_plan(project, "ros3")
    except ValueError as exc:
        assert "Unsupported migration target" in str(exc)
    else:
        raise AssertionError("unsupported target was not rejected")


def test_json_output_has_stable_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    runner = CliRunner()
    output = tmp_path / "migration_plan.json"

    result = runner.invoke(app, ["migrate-plan", "--from", str(project), "--to", "ros2", "--output", str(output), "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    assert list(data.keys()) == [
        "generated_by",
        "source_path",
        "target",
        "source_project_type",
        "package_name",
        "confidence",
        "summary",
        "package_xml_migration",
        "build_system_migration",
        "source_code_migration",
        "launch_migration",
        "interface_migration",
        "dependency_migration",
        "suggested_file_changes",
        "manual_review_items",
        "risks",
        "suggested_next_steps",
        "safety_note",
    ]


def test_output_file_is_written(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    output = tmp_path / "migration_plan.yaml"

    write_migration_plan(source_path=project, target="ros2", output_path=output)

    assert output.is_file()
    assert "package_xml_migration:" in output.read_text(encoding="utf-8")


def test_no_source_project_files_are_modified(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    before = {
        file_path.relative_to(project).as_posix(): file_path.read_text(encoding="utf-8")
        for file_path in sorted(project.rglob("*"))
        if file_path.is_file()
    }

    write_migration_plan(
        source_path=project,
        target="ros2",
        output_path=tmp_path / "migration_plan.yaml",
    )

    after = {
        file_path.relative_to(project).as_posix(): file_path.read_text(encoding="utf-8")
        for file_path in sorted(project.rglob("*"))
        if file_path.is_file()
    }
    assert after == before


def test_cli_rejects_unsupported_target(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    runner = CliRunner()

    result = runner.invoke(app, ["migrate-plan", "--from", str(project), "--to", "ros3", "--output", str(tmp_path / "plan.yaml")])

    assert result.exit_code == 1
    assert "Unsupported migration target" in result.output
