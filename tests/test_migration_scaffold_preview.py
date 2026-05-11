import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.api.migration import preview_migration_scaffold as api_preview_migration_scaffold
from robopilot.main import app
from robopilot.migration.ros1_to_ros2 import write_migration_plan
from robopilot.migration.scaffold_preview import preview_migration_scaffold


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _ros1_package(path: Path, *, python: bool = True, cpp: bool = False) -> None:
    build_deps = ["std_msgs", "message_generation"]
    if python:
        build_deps.append("rospy")
    if cpp:
        build_deps.append("roscpp")
    _write(
        path / "package.xml",
        "\n".join(
            [
                '<package format="2">',
                "  <name>ros1_migration_demo</name>",
                "  <version>0.0.1</version>",
                "  <buildtool_depend>catkin</buildtool_depend>",
                *(f"  <build_depend>{dep}</build_depend>" for dep in build_deps),
                "  <exec_depend>message_runtime</exec_depend>",
                "</package>",
            ]
        ),
    )
    components = " ".join(dep for dep in ("roscpp" if cpp else "", "rospy" if python else "", "std_msgs", "message_generation") if dep)
    _write(
        path / "CMakeLists.txt",
        f"""
cmake_minimum_required(VERSION 3.0.2)
project(ros1_migration_demo)
find_package(catkin REQUIRED COMPONENTS {components})
add_message_files(FILES Demo.msg)
add_service_files(FILES Demo.srv)
add_action_files(FILES Demo.action)
generate_messages(DEPENDENCIES std_msgs)
catkin_package()
""",
    )
    _write(path / "launch" / "demo.launch", '<launch><node pkg="ros1_migration_demo" type="talker.py" /></launch>')
    if python:
        _write(path / "scripts" / "talker.py", "import rospy\nrospy.init_node('talker')\n")
    if cpp:
        _write(path / "src" / "listener.cpp", "#include <ros/ros.h>\nint main() { ros::NodeHandle nh; }\n")
    _write(path / "msg" / "Demo.msg", "string data\n")
    _write(path / "srv" / "Demo.srv", "string in\n---\nstring out\n")
    _write(path / "action" / "Demo.action", "string goal\n---\nstring result\n---\nstring feedback\n")


def _plan(tmp_path: Path, project: Path) -> Path:
    plan = tmp_path / "migration_plan.yaml"
    write_migration_plan(source_path=project, target="ros2", output_path=plan)
    return plan


def _paths(items: object) -> set[str]:
    return {item.path for item in items}


def test_preview_from_valid_python_oriented_migration_plan(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    _ros1_package(project, python=True, cpp=False)

    preview = preview_migration_scaffold(_plan(tmp_path, project))

    assert preview.target == "ros2"
    assert preview.package_name == "ros1_migration_demo"
    assert preview.target_style == "ament_python"


def test_preview_from_valid_cpp_oriented_migration_plan(tmp_path: Path) -> None:
    project = tmp_path / "ros1_cpp"
    _ros1_package(project, python=False, cpp=True)

    preview = preview_migration_scaffold(_plan(tmp_path, project))

    assert preview.target_style == "ament_cmake"


def test_preview_from_mixed_python_cpp_migration_plan(tmp_path: Path) -> None:
    project = tmp_path / "ros1_mixed"
    _ros1_package(project, python=True, cpp=True)

    preview = preview_migration_scaffold(_plan(tmp_path, project))

    assert preview.target_style == "mixed_review_required"
    assert "mixed Python/C++ package requires manual target-style decision" in preview.conflicts


def test_scaffold_includes_package_xml(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    _ros1_package(project, python=True, cpp=False)

    preview = preview_migration_scaffold(_plan(tmp_path, project))

    assert "package.xml" in _paths(preview.scaffold_files_to_create)


def test_python_scaffold_includes_ament_python_files(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    _ros1_package(project, python=True, cpp=False)

    preview = preview_migration_scaffold(_plan(tmp_path, project))
    paths = _paths(preview.scaffold_files_to_create)

    assert "setup.py" in paths
    assert "setup.cfg" in paths
    assert "resource/ros1_migration_demo" in paths
    assert "ros1_migration_demo/__init__.py" in paths


def test_cpp_scaffold_includes_cmakelists(tmp_path: Path) -> None:
    project = tmp_path / "ros1_cpp"
    _ros1_package(project, python=False, cpp=True)

    preview = preview_migration_scaffold(_plan(tmp_path, project))

    assert "CMakeLists.txt" in _paths(preview.scaffold_files_to_create)


def test_launch_placeholder_is_included_when_launch_migration_exists(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    _ros1_package(project, python=True, cpp=False)

    preview = preview_migration_scaffold(_plan(tmp_path, project))

    assert "launch/demo.launch.py" in _paths(preview.placeholder_files)


def test_interface_files_are_included_for_review(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    _ros1_package(project, python=True, cpp=False)

    preview = preview_migration_scaffold(_plan(tmp_path, project))

    assert "msg/Demo.msg" in preview.interface_files_to_review
    assert "srv/Demo.srv" in preview.interface_files_to_review
    assert "action/Demo.action" in preview.interface_files_to_review


def test_dependency_items_are_included_for_review(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    _ros1_package(project, python=True, cpp=False)

    preview = preview_migration_scaffold(_plan(tmp_path, project))

    assert any("rospy -> rclpy" in item for item in preview.dependency_items_to_review)


def test_unsupported_target_is_rejected(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    _ros1_package(project, python=True, cpp=False)
    plan = _plan(tmp_path, project)
    plan.write_text(plan.read_text(encoding="utf-8").replace('target: "ros2"', 'target: "ros3"'), encoding="utf-8")

    try:
        preview_migration_scaffold(plan)
    except ValueError as exc:
        assert "target must be ros2" in str(exc)
    else:
        raise AssertionError("unsupported target was not rejected")


def test_invalid_migration_plan_is_reported_clearly(tmp_path: Path) -> None:
    plan = tmp_path / "bad_plan.yaml"
    plan.write_text('target: "ros2"\n', encoding="utf-8")

    try:
        preview_migration_scaffold(plan)
    except ValueError as exc:
        assert "Invalid migration plan" in str(exc)
    else:
        raise AssertionError("invalid plan was not rejected")


def test_json_output_has_stable_top_level_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    _ros1_package(project, python=True, cpp=False)
    plan = _plan(tmp_path, project)

    result = CliRunner().invoke(app, ["migrate-scaffold-preview", "--plan", str(plan), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert list(data.keys()) == [
        "plan_path",
        "source_path",
        "target",
        "package_name",
        "target_style",
        "scaffold_files_to_create",
        "placeholder_files",
        "files_requiring_manual_migration",
        "interface_files_to_review",
        "dependency_items_to_review",
        "build_system_notes",
        "launch_notes",
        "risks",
        "conflicts",
        "suggested_next_steps",
        "safety_note",
    ]


def test_api_wrapper_returns_structured_data(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    _ros1_package(project, python=True, cpp=False)

    result = api_preview_migration_scaffold(_plan(tmp_path, project))

    assert result["target_style"] == "ament_python"
    assert "scaffold_files_to_create" in result


def test_preview_does_not_write_scaffold_files(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    _ros1_package(project, python=True, cpp=False)
    before = sorted(path.relative_to(project).as_posix() for path in project.rglob("*") if path.is_file())

    preview_migration_scaffold(_plan(tmp_path, project))

    after = sorted(path.relative_to(project).as_posix() for path in project.rglob("*") if path.is_file())
    assert after == before
    assert not (project / "setup.py").exists()
