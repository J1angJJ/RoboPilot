import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.api.migration import validate_migration_scaffold as api_validate_migration_scaffold
from robopilot.main import app
from robopilot.migration.ros1_to_ros2 import write_migration_plan
from robopilot.migration.scaffold_generator import generate_migration_scaffold
from robopilot.migration.scaffold_validator import validate_migration_scaffold


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


def _generated_scaffold(tmp_path: Path, *, python: bool = True, cpp: bool = False) -> tuple[Path, Path, Path]:
    project = tmp_path / "ros1_project"
    scaffold = tmp_path / "ros2_scaffold"
    _ros1_package(project, python=python, cpp=cpp)
    plan = _plan(tmp_path, project)
    result = generate_migration_scaffold(plan, scaffold)
    assert result.conflicts == ()
    return plan, scaffold, project


def _snapshot(path: Path) -> dict[str, str]:
    return {
        file.relative_to(path).as_posix(): file.read_text(encoding="utf-8", errors="ignore")
        for file in sorted(path.rglob("*"))
        if file.is_file()
    }


def test_validates_generated_ament_python_scaffold(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=True, cpp=False)

    result = validate_migration_scaffold(plan, scaffold)

    assert result.valid is True
    assert result.target_style == "ament_python"
    assert result.missing_files == ()
    assert "setup.py" in result.present_files
    assert all(check.passed for check in result.placeholder_checks)


def test_validates_generated_ament_cmake_scaffold(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=False, cpp=True)

    result = validate_migration_scaffold(plan, scaffold)

    assert result.valid is True
    assert result.target_style == "ament_cmake"
    assert "CMakeLists.txt" in result.present_files


def test_validates_conservative_mixed_scaffold(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=True, cpp=True)

    result = validate_migration_scaffold(plan, scaffold)

    assert result.valid is True
    assert result.target_style == "mixed_review_required"
    assert "MIGRATION_NOTES.md" in result.present_files
    assert "setup.py" not in result.expected_files
    assert "CMakeLists.txt" not in result.expected_files
    notes = (scaffold / "MIGRATION_NOTES.md").read_text(encoding="utf-8")
    assert "not an automatic migration" in notes
    assert "Build-system choice requires manual review" in notes


def test_detects_missing_package_xml(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=True, cpp=False)
    (scaffold / "package.xml").unlink()

    result = validate_migration_scaffold(plan, scaffold)

    assert result.valid is False
    assert "package.xml" in result.missing_files
    assert any("missing package.xml" in issue for issue in result.issues)


def test_detects_missing_setup_py_for_ament_python(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=True, cpp=False)
    (scaffold / "setup.py").unlink()

    result = validate_migration_scaffold(plan, scaffold)

    assert result.valid is False
    assert "setup.py" in result.missing_files
    assert any("missing ament_python scaffold file: setup.py" in issue for issue in result.issues)


def test_detects_missing_cmakelists_for_ament_cmake(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=False, cpp=True)
    (scaffold / "CMakeLists.txt").unlink()

    result = validate_migration_scaffold(plan, scaffold)

    assert result.valid is False
    assert "CMakeLists.txt" in result.missing_files
    assert any("missing CMakeLists.txt" in issue for issue in result.issues)


def test_detects_missing_migration_notes(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=True, cpp=False)
    (scaffold / "MIGRATION_NOTES.md").unlink()

    result = validate_migration_scaffold(plan, scaffold)

    assert result.valid is False
    assert result.migration_notes_present is False
    assert "MIGRATION_NOTES.md" in result.missing_files


def test_detects_placeholder_without_todo_or_manual_review_warning(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=True, cpp=False)
    node = scaffold / "ros1_migration_demo" / "talker_node.py"
    node.write_text("print('ordinary script')\n", encoding="utf-8")

    result = validate_migration_scaffold(plan, scaffold)

    assert result.valid is False
    failed = [check for check in result.placeholder_checks if check.path == "ros1_migration_demo/talker_node.py"]
    assert failed and "TODO" in failed[0].missing_concepts
    assert any("placeholder safety wording incomplete" in issue for issue in result.issues)


def test_reports_unexpected_files_without_over_failing(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=True, cpp=False)
    _write(scaffold / "notes.txt", "local review notes\n")

    result = validate_migration_scaffold(plan, scaffold)

    assert result.valid is True
    assert result.unexpected_files == ("notes.txt",)
    assert any("unexpected file present: notes.txt" in warning for warning in result.warnings)


def test_rejects_missing_scaffold_directory(tmp_path: Path) -> None:
    project = tmp_path / "ros1_project"
    _ros1_package(project, python=True, cpp=False)
    plan = _plan(tmp_path, project)

    result = validate_migration_scaffold(plan, tmp_path / "missing_scaffold")

    assert result.valid is False
    assert "scaffold path does not exist" in result.issues


def test_rejects_invalid_migration_plan(tmp_path: Path) -> None:
    plan = tmp_path / "bad_plan.yaml"
    plan.write_text('target: "ros2"\n', encoding="utf-8")

    try:
        validate_migration_scaffold(plan, tmp_path / "scaffold")
    except ValueError as exc:
        assert "Invalid migration plan" in str(exc)
    else:
        raise AssertionError("invalid plan was not rejected")


def test_json_output_has_stable_top_level_keys(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=True, cpp=False)

    result = CliRunner().invoke(
        app,
        ["migrate-scaffold-validate", "--plan", str(plan), "--scaffold", str(scaffold), "--json"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert list(data.keys()) == [
        "plan_path",
        "scaffold_path",
        "source_path",
        "target",
        "package_name",
        "target_style",
        "valid",
        "expected_files",
        "present_files",
        "missing_files",
        "unexpected_files",
        "placeholder_checks",
        "migration_notes_present",
        "ros2_inspection_summary",
        "issues",
        "warnings",
        "suggested_next_steps",
        "safety_note",
    ]


def test_api_wrapper_returns_structured_data(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=True, cpp=False)

    result = api_validate_migration_scaffold(plan, scaffold)

    assert result["valid"] is True
    assert result["target_style"] == "ament_python"
    assert "placeholder_checks" in result


def test_validation_is_read_only_and_does_not_modify_scaffold(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=True, cpp=False)
    before = _snapshot(scaffold)

    validate_migration_scaffold(plan, scaffold)

    assert _snapshot(scaffold) == before


def test_validation_does_not_execute_generated_code(tmp_path: Path) -> None:
    plan, scaffold, _project = _generated_scaffold(tmp_path, python=True, cpp=False)
    marker = tmp_path / "executed.txt"
    node = scaffold / "ros1_migration_demo" / "talker_node.py"
    node.write_text(
        "\n".join(
            [
                '"""ROS2 node placeholder generated by RoboPilot migration scaffold."""',
                "# Generated by RoboPilot migration scaffold.",
                "# This is not an automatic migration.",
                "# TODO: manual review before migration.",
                "# TODO: review QoS behavior for ROS2.",
                f"open({str(marker)!r}, 'w').write('executed')",
            ]
        ),
        encoding="utf-8",
    )

    result = validate_migration_scaffold(plan, scaffold)

    assert result.valid is True
    assert not marker.exists()
