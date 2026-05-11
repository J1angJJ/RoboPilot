import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.main import app
from robopilot.migration.plan_validator import validate_migration_plan_file
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
find_package(catkin REQUIRED COMPONENTS roscpp rospy message_generation)
catkin_package()
""",
    )
    _write(path / "scripts" / "talker.py", "import rospy\n")
    _write(path / "src" / "listener.cpp", "#include <ros/ros.h>\n")


def _plan(tmp_path: Path, project: Path) -> Path:
    plan = tmp_path / "migration_plan.yaml"
    write_migration_plan(source_path=project, target="ros2", output_path=plan)
    return plan


def test_valid_migration_plan_passes(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)

    report = validate_migration_plan_file(_plan(tmp_path, project))

    assert report.valid
    assert report.missing_fields == ()
    assert report.invalid_fields == ()


def test_missing_required_field_is_reported(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    plan = _plan(tmp_path, project)
    text = "\n".join(
        line for line in plan.read_text(encoding="utf-8").splitlines() if not line.startswith("summary:")
    )
    plan.write_text(text + "\n", encoding="utf-8")

    report = validate_migration_plan_file(plan)

    assert not report.valid
    assert "summary" in report.missing_fields


def test_unsupported_target_is_rejected(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    plan = _plan(tmp_path, project)
    plan.write_text(plan.read_text(encoding="utf-8").replace('target: "ros2"', 'target: "ros3"'), encoding="utf-8")

    report = validate_migration_plan_file(plan)

    assert not report.valid
    assert "target must be ros2" in report.invalid_fields


def test_missing_source_path_does_not_fail_validation(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    plan = _plan(tmp_path, project)
    text = plan.read_text(encoding="utf-8").replace(str(project).replace("\\", "\\\\"), str(tmp_path / "missing"))
    plan.write_text(text, encoding="utf-8")

    report = validate_migration_plan_file(plan)

    assert report.valid


def test_invalid_or_malformed_plan_is_reported_clearly(tmp_path: Path) -> None:
    plan = tmp_path / "bad.yaml"
    plan.write_text("not a valid plan line\n", encoding="utf-8")

    report = validate_migration_plan_file(plan)

    assert not report.valid
    assert any("could not be loaded" in item for item in report.invalid_fields)


def test_json_output_has_stable_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    plan = _plan(tmp_path, project)
    runner = CliRunner()

    result = runner.invoke(app, ["migrate-plan-validate", "--plan", str(plan), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert list(data.keys()) == [
        "plan_path",
        "valid",
        "missing_fields",
        "invalid_fields",
        "warnings",
        "suggested_next_steps",
        "safety_note",
    ]
    assert data["valid"] is True
