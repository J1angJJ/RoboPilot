import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.main import app
from robopilot.migration.preview import preview_migration
from robopilot.migration.ros1_to_ros2 import write_migration_plan


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
  <exec_depend>message_runtime</exec_depend>
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


def _plan(tmp_path: Path, project: Path) -> Path:
    plan = tmp_path / "migration_plan.yaml"
    write_migration_plan(source_path=project, target="ros2", output_path=plan)
    return plan


def test_preview_from_valid_ros1_to_ros2_migration_plan(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    preview = preview_migration(_plan(tmp_path, project), project)

    assert preview.source_project_type == "ros1_catkin_package"
    assert preview.target == "ros2"
    assert preview.package_name == "ros1_migration_demo"


def test_preview_includes_planned_ros2_package_xml(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    preview = preview_migration(_plan(tmp_path, project), project)

    assert "package.xml" in preview.files_to_create


def test_preview_includes_planned_ros2_build_file(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    preview = preview_migration(_plan(tmp_path, project), project)

    assert "CMakeLists.txt" in preview.files_to_create


def test_preview_includes_ros2_launch_file_for_ros1_launch(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    preview = preview_migration(_plan(tmp_path, project), project)

    assert "launch/demo.launch.py" in preview.files_to_create


def test_preview_marks_rospy_scripts_for_manual_migration(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    preview = preview_migration(_plan(tmp_path, project), project)

    assert "scripts/talker.py" in preview.files_requiring_manual_migration


def test_preview_marks_roscpp_sources_for_manual_migration(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    preview = preview_migration(_plan(tmp_path, project), project)

    assert "src/listener.cpp" in preview.files_requiring_manual_migration


def test_preview_includes_msg_srv_action_files_for_review(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    preview = preview_migration(_plan(tmp_path, project), project)

    assert "msg/Demo.msg" in preview.interface_files_to_review
    assert "srv/Demo.srv" in preview.interface_files_to_review
    assert "action/Demo.action" in preview.interface_files_to_review
    assert "msg/Demo.msg" in preview.files_to_keep


def test_preview_includes_dependency_items_to_review(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    preview = preview_migration(_plan(tmp_path, project), project)

    assert any("rospy -> rclpy" in item for item in preview.dependency_items_to_review)
    assert any("roscpp -> rclcpp" in item for item in preview.dependency_items_to_review)


def test_preview_detects_unsupported_target(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    plan = _plan(tmp_path, project)
    text = plan.read_text(encoding="utf-8").replace('target: "ros2"', 'target: "ros3"')
    plan.write_text(text, encoding="utf-8")

    try:
        preview_migration(plan, project)
    except ValueError as exc:
        assert "target must be ros2" in str(exc)
    else:
        raise AssertionError("unsupported migration target was not rejected")


def test_preview_detects_missing_source_project(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    plan = _plan(tmp_path, project)

    preview = preview_migration(plan, tmp_path / "missing")

    assert "source project path does not exist" in preview.conflicts


def test_preview_detects_invalid_migration_plan(tmp_path: Path) -> None:
    plan = tmp_path / "bad_plan.yaml"
    plan.write_text('target: "ros2"\n', encoding="utf-8")

    try:
        preview_migration(plan, tmp_path / "project")
    except ValueError as exc:
        assert "Invalid migration plan" in str(exc)
    else:
        raise AssertionError("invalid migration plan was not rejected")


def test_json_output_has_stable_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    plan = _plan(tmp_path, project)
    runner = CliRunner()

    result = runner.invoke(app, ["migrate-preview", "--plan", str(plan), "--project", str(project), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert list(data.keys()) == [
        "plan_path",
        "project_path",
        "source_project_type",
        "target",
        "package_name",
        "files_to_create",
        "files_to_update",
        "files_to_keep",
        "files_requiring_manual_migration",
        "interface_files_to_review",
        "dependency_items_to_review",
        "conflicts",
        "risks",
        "suggested_next_steps",
        "safety_note",
    ]


def test_preview_does_not_modify_source_project_files(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    before = {
        file_path.relative_to(project).as_posix(): file_path.read_text(encoding="utf-8")
        for file_path in sorted(project.rglob("*"))
        if file_path.is_file()
    }

    preview_migration(_plan(tmp_path, project), project)

    after = {
        file_path.relative_to(project).as_posix(): file_path.read_text(encoding="utf-8")
        for file_path in sorted(project.rglob("*"))
        if file_path.is_file()
    }
    assert after == before
