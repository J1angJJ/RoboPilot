from pathlib import Path

from typer.testing import CliRunner

from robopilot.api.migration import generate_migration_scaffold_report as api_generate_migration_scaffold_report
from robopilot.main import app
from robopilot.migration.ros1_to_ros2 import write_migration_plan
from robopilot.migration.scaffold_generator import generate_migration_scaffold
from robopilot.migration.scaffold_report import (
    generate_migration_scaffold_report,
    write_migration_scaffold_report,
)


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


def _generated_scaffold(tmp_path: Path, *, python: bool = True, cpp: bool = False) -> tuple[Path, Path]:
    project = tmp_path / "ros1_project"
    scaffold = tmp_path / "ros2_scaffold"
    _ros1_package(project, python=python, cpp=cpp)
    plan = _plan(tmp_path, project)
    result = generate_migration_scaffold(plan, scaffold)
    assert result.conflicts == ()
    return plan, scaffold


def _snapshot(path: Path) -> dict[str, str]:
    return {
        file.relative_to(path).as_posix(): file.read_text(encoding="utf-8", errors="ignore")
        for file in sorted(path.rglob("*"))
        if file.is_file()
    }


def test_report_generation_from_valid_scaffold(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)

    report = generate_migration_scaffold_report(plan, scaffold)

    assert report.startswith("# RoboPilot Migration Scaffold Report\n")
    assert "- Valid: true" in report
    assert "- Package name: ros1_migration_demo" in report


def test_markdown_contains_key_sections(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)

    report = generate_migration_scaffold_report(plan, scaffold)

    for section in (
        "## Summary",
        "## Source and Target",
        "## Package",
        "## Target Style",
        "## Validation Result",
        "## Expected Files",
        "## Present Files",
        "## Missing Files",
        "## Unexpected Files",
        "## Placeholder Checks",
        "## ROS2 Static Inspection Summary",
        "## Manual Migration Items",
        "## Interface Files to Review",
        "## Dependency Items to Review",
        "## Issues",
        "## Warnings",
        "## What To Do Next",
        "## Suggested Next Steps",
        "## Safety Note",
    ):
        assert section in report


def test_report_includes_invalid_status_and_missing_files(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)
    (scaffold / "package.xml").unlink()

    report = generate_migration_scaffold_report(plan, scaffold)

    assert "- Valid: false" in report
    assert "## Missing Files" in report
    assert "- package.xml" in report
    assert "missing package.xml" in report


def test_report_includes_placeholder_checks_issues_and_warnings(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)
    _write(scaffold / "local_notes.md", "extra\n")
    node = scaffold / "ros1_migration_demo" / "talker_node.py"
    node.write_text("print('ordinary script')\n", encoding="utf-8")

    report = generate_migration_scaffold_report(plan, scaffold)

    assert "## Placeholder Checks" in report
    assert "ros1_migration_demo/talker_node.py: failed" in report
    assert "placeholder safety wording incomplete" in report
    assert "unexpected file present: local_notes.md" in report


def test_report_summary_includes_recommended_next_action(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)

    report = generate_migration_scaffold_report(plan, scaffold)

    assert "- Recommended next action:" in report
    assert "review MIGRATION_NOTES.md" in report
    assert "## What To Do Next" in report


def test_report_includes_safety_note(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)

    report = generate_migration_scaffold_report(plan, scaffold)

    assert "RoboPilot did not run ROS" in report
    assert "RoboPilot did not run ROS2" in report
    assert "run colcon" in report
    assert "execute launch files" in report
    assert "execute generated code" in report
    assert "Passing validation does not mean" in report


def test_output_file_is_written_when_requested(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)
    output = tmp_path / "reports" / "scaffold_report.md"

    report = write_migration_scaffold_report(plan, scaffold, output)

    assert output.read_text(encoding="utf-8") == report
    assert "# RoboPilot Migration Scaffold Report" in report


def test_existing_output_file_is_not_overwritten_by_default(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)
    output = tmp_path / "scaffold_report.md"
    output.write_text("local report\n", encoding="utf-8")

    try:
        write_migration_scaffold_report(plan, scaffold, output)
    except FileExistsError as exc:
        assert "report output already exists" in str(exc)
    else:
        raise AssertionError("existing report was overwritten")
    assert output.read_text(encoding="utf-8") == "local report\n"


def test_api_wrapper_returns_markdown(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)

    report = api_generate_migration_scaffold_report(plan, scaffold)

    assert isinstance(report, str)
    assert "# RoboPilot Migration Scaffold Report" in report


def test_cli_prints_markdown_when_output_is_omitted(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)

    result = CliRunner().invoke(
        app,
        ["migrate-scaffold-report", "--plan", str(plan), "--scaffold", str(scaffold)],
    )

    assert result.exit_code == 0, result.output
    assert result.output.startswith("# RoboPilot Migration Scaffold Report")


def test_cli_writes_report_to_file(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)
    output = tmp_path / "scaffold_report.md"

    result = CliRunner().invoke(
        app,
        ["migrate-scaffold-report", "--plan", str(plan), "--scaffold", str(scaffold), "--output", str(output)],
    )

    assert result.exit_code == 0, result.output
    assert output.is_file()
    assert "Validation status" in result.output
    assert "# RoboPilot Migration Scaffold Report" in output.read_text(encoding="utf-8")


def test_cli_refuses_to_overwrite_existing_report_by_default(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)
    output = tmp_path / "scaffold_report.md"
    output.write_text("local report\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        ["migrate-scaffold-report", "--plan", str(plan), "--scaffold", str(scaffold), "--output", str(output)],
    )

    assert result.exit_code == 1
    assert output.read_text(encoding="utf-8") == "local report\n"


def test_command_does_not_modify_scaffold_files(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)
    before = _snapshot(scaffold)

    generate_migration_scaffold_report(plan, scaffold)

    assert _snapshot(scaffold) == before


def test_command_does_not_execute_generated_code(tmp_path: Path) -> None:
    plan, scaffold = _generated_scaffold(tmp_path, python=True, cpp=False)
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

    report = generate_migration_scaffold_report(plan, scaffold)

    assert "- Valid: true" in report
    assert not marker.exists()
