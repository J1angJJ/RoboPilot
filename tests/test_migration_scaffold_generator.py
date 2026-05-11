import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.api.migration import generate_migration_scaffold as api_generate_migration_scaffold
from robopilot.main import app
from robopilot.migration import scaffold_generator
from robopilot.migration.ros1_to_ros2 import write_migration_plan
from robopilot.migration.scaffold_generator import generate_migration_scaffold
from robopilot.migration.scaffold_preview import MigrationScaffoldPreviewResult, ScaffoldFile


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
    components = " ".join(
        dep for dep in ("roscpp" if cpp else "", "rospy" if python else "", "std_msgs", "message_generation") if dep
    )
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


def _files(path: Path) -> set[str]:
    return {file.relative_to(path).as_posix() for file in path.rglob("*") if file.is_file()}


def test_python_oriented_scaffold_generation_creates_expected_files(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    output = tmp_path / "ros2_scaffold"
    _ros1_package(project, python=True, cpp=False)

    result = generate_migration_scaffold(_plan(tmp_path, project), output)

    assert result.conflicts == ()
    assert result.target_style == "ament_python"
    expected = {
        "package.xml",
        "setup.py",
        "setup.cfg",
        "resource/ros1_migration_demo",
        "ros1_migration_demo/__init__.py",
        "ros1_migration_demo/talker_node.py",
        "launch/demo.launch.py",
        "config/params.yaml",
        "MIGRATION_NOTES.md",
    }
    assert expected.issubset(_files(output))


def test_cpp_oriented_scaffold_generation_creates_expected_files(tmp_path: Path) -> None:
    project = tmp_path / "ros1_cpp"
    output = tmp_path / "ros2_scaffold"
    _ros1_package(project, python=False, cpp=True)

    result = generate_migration_scaffold(_plan(tmp_path, project), output)

    assert result.conflicts == ()
    assert result.target_style == "ament_cmake"
    expected = {
        "package.xml",
        "CMakeLists.txt",
        "src/listener_node.cpp",
        "launch/demo.launch.py",
        "config/params.yaml",
        "MIGRATION_NOTES.md",
    }
    assert expected.issubset(_files(output))


def test_mixed_target_style_does_not_overclaim_automatic_migration(tmp_path: Path) -> None:
    project = tmp_path / "ros1_mixed"
    output = tmp_path / "ros2_scaffold"
    _ros1_package(project, python=True, cpp=True)

    result = generate_migration_scaffold(_plan(tmp_path, project), output)

    assert result.target_style == "mixed_review_required"
    assert result.conflicts == ()
    assert "MIGRATION_NOTES.md" in _files(output)
    assert "package.xml" in _files(output)
    assert "setup.py" not in _files(output)
    assert "CMakeLists.txt" not in _files(output)
    assert any("Build-system choice requires manual review" in risk for risk in result.risks)


def test_generation_refuses_to_overwrite_existing_files_by_default(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    output = tmp_path / "ros2_scaffold"
    _ros1_package(project, python=True, cpp=False)
    _write(output / "package.xml", "local file\n")

    result = generate_migration_scaffold(_plan(tmp_path, project), output)

    assert any("file already exists: package.xml" in item for item in result.conflicts)
    assert result.files_created == ()
    assert (output / "package.xml").read_text(encoding="utf-8") == "local file\n"
    assert not (output / "setup.py").exists()


def test_overwrite_updates_only_intended_scaffold_files(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    output = tmp_path / "ros2_scaffold"
    _ros1_package(project, python=True, cpp=False)
    _write(output / "package.xml", "local file\n")
    _write(output / "notes.txt", "unrelated\n")

    result = generate_migration_scaffold(_plan(tmp_path, project), output, overwrite=True)

    assert result.conflicts == ()
    assert "ROS2 migration scaffold generated by RoboPilot" in (output / "package.xml").read_text(encoding="utf-8")
    assert (output / "notes.txt").read_text(encoding="utf-8") == "unrelated\n"


def test_unsafe_path_traversal_is_rejected(tmp_path: Path, monkeypatch) -> None:
    preview = MigrationScaffoldPreviewResult(
        plan_path=str(tmp_path / "plan.yaml"),
        source_path=str(tmp_path / "source"),
        target="ros2",
        package_name="demo",
        target_style="ament_python",
        scaffold_files_to_create=(ScaffoldFile("../evil.txt", "unsafe", "test"),),
        placeholder_files=(),
        files_requiring_manual_migration=(),
        interface_files_to_review=(),
        dependency_items_to_review=(),
        build_system_notes=(),
        launch_notes=(),
        risks=(),
        conflicts=(),
        suggested_next_steps=(),
        safety_note="preview",
    )
    monkeypatch.setattr(scaffold_generator, "preview_migration_scaffold", lambda _plan: preview)

    result = generate_migration_scaffold(tmp_path / "plan.yaml", tmp_path / "out")

    assert any("unsafe scaffold path rejected" in item for item in result.conflicts)
    assert not (tmp_path / "evil.txt").exists()


def test_generated_files_stay_under_output_directory(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    output = tmp_path / "ros2_scaffold"
    _ros1_package(project, python=True, cpp=False)

    result = generate_migration_scaffold(_plan(tmp_path, project), output)

    root = output.resolve()
    assert result.conflicts == ()
    for file in output.rglob("*"):
        if file.is_file():
            assert file.resolve().is_relative_to(root)


def test_invalid_migration_plan_is_rejected(tmp_path: Path) -> None:
    plan = tmp_path / "bad_plan.yaml"
    plan.write_text('target: "ros2"\n', encoding="utf-8")

    try:
        generate_migration_scaffold(plan, tmp_path / "out")
    except ValueError as exc:
        assert "Invalid migration plan" in str(exc)
    else:
        raise AssertionError("invalid plan was not rejected")


def test_unsupported_target_is_rejected(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    _ros1_package(project, python=True, cpp=False)
    plan = _plan(tmp_path, project)
    plan.write_text(plan.read_text(encoding="utf-8").replace('target: "ros2"', 'target: "ros3"'), encoding="utf-8")

    try:
        generate_migration_scaffold(plan, tmp_path / "out")
    except ValueError as exc:
        assert "target must be ros2" in str(exc)
    else:
        raise AssertionError("unsupported target was not rejected")


def test_json_output_has_stable_top_level_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    output = tmp_path / "ros2_scaffold"
    _ros1_package(project, python=True, cpp=False)
    plan = _plan(tmp_path, project)

    result = CliRunner().invoke(app, ["migrate-scaffold", "--plan", str(plan), "--output", str(output), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert list(data.keys()) == [
        "plan_path",
        "output_path",
        "source_path",
        "target",
        "package_name",
        "target_style",
        "dry_run",
        "files_to_create",
        "files_created",
        "conflicts",
        "skipped_files",
        "manual_migration_required",
        "interface_files_to_review",
        "dependency_items_to_review",
        "risks",
        "suggested_next_steps",
        "safety_note",
    ]


def test_api_wrapper_returns_structured_data(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    output = tmp_path / "ros2_scaffold"
    _ros1_package(project, python=True, cpp=False)

    result = api_generate_migration_scaffold(_plan(tmp_path, project), output)

    assert result["target_style"] == "ament_python"
    assert "files_created" in result


def test_original_source_project_and_plan_are_not_modified(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    output = tmp_path / "ros2_scaffold"
    _ros1_package(project, python=True, cpp=False)
    plan = _plan(tmp_path, project)
    before_project = _files(project)
    before_plan = plan.read_text(encoding="utf-8")

    generate_migration_scaffold(plan, output)

    assert _files(project) == before_project
    assert plan.read_text(encoding="utf-8") == before_plan


def test_generated_files_contain_todo_manual_migration_warnings(tmp_path: Path) -> None:
    project = tmp_path / "ros1_py"
    output = tmp_path / "ros2_scaffold"
    _ros1_package(project, python=True, cpp=False)

    generate_migration_scaffold(_plan(tmp_path, project), output)

    node_text = (output / "ros1_migration_demo" / "talker_node.py").read_text(encoding="utf-8")
    launch_text = (output / "launch" / "demo.launch.py").read_text(encoding="utf-8")
    notes = (output / "MIGRATION_NOTES.md").read_text(encoding="utf-8")
    assert "This is not an automatic migration" in node_text
    assert "TODO: migrate node initialization" in node_text
    assert "TODO: migrate ROS1 XML launch semantics" in launch_text
    assert "No runtime validation was performed" in notes
