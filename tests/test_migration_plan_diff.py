import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.main import app
from robopilot.migration.plan_diff import diff_migration_plans
from robopilot.migration.ros1_to_ros2 import write_migration_plan


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _ros1_package(path: Path, *, package_name: str = "ros1_migration_demo") -> None:
    _write(
        path / "package.xml",
        f"""
<package format="2">
  <name>{package_name}</name>
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
        f"""
cmake_minimum_required(VERSION 3.0.2)
project({package_name})
find_package(catkin REQUIRED COMPONENTS roscpp rospy message_generation)
catkin_package()
""",
    )
    _write(path / "scripts" / "talker.py", "import rospy\n")
    _write(path / "src" / "listener.cpp", "#include <ros/ros.h>\n")
    _write(path / "action" / "Demo.action", "string goal\n---\nstring result\n---\nstring feedback\n")


def _plan(tmp_path: Path, project: Path, name: str = "plan.yaml") -> Path:
    plan = tmp_path / name
    write_migration_plan(source_path=project, target="ros2", output_path=plan)
    return plan


def test_identical_plans_report_no_changes(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    old = _plan(tmp_path, project, "old.yaml")
    new = tmp_path / "new.yaml"
    new.write_text(old.read_text(encoding="utf-8"), encoding="utf-8")

    result = diff_migration_plans(old, new)

    assert not result.has_changes
    assert result.changed_fields == {}


def test_scalar_field_change_is_detected(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    old = _plan(tmp_path, project, "old.yaml")
    new = tmp_path / "new.yaml"
    new.write_text(old.read_text(encoding="utf-8").replace('confidence: "high"', 'confidence: "medium"'), encoding="utf-8")

    result = diff_migration_plans(old, new)

    assert result.changed_fields["confidence"] == {"old": "high", "new": "medium"}


def test_added_manual_review_item_is_detected(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    old = _plan(tmp_path, project, "old.yaml")
    new = tmp_path / "new.yaml"
    new.write_text(
        old.read_text(encoding="utf-8").replace(
            "manual_review_items:\n",
            'manual_review_items:\n  - "review custom lifecycle behavior"\n',
        ),
        encoding="utf-8",
    )

    result = diff_migration_plans(old, new)

    assert "review custom lifecycle behavior" in result.added_items["manual_review_items"]


def test_removed_risk_item_is_detected(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    old = _plan(tmp_path, project, "old.yaml")
    old_text = old.read_text(encoding="utf-8")
    risk_line = next(line for line in old_text.splitlines() if "ROS1 inspection reported" in line)
    new = tmp_path / "new.yaml"
    new.write_text(old_text.replace(risk_line + "\n", ""), encoding="utf-8")

    result = diff_migration_plans(old, new)

    assert any("ROS1 inspection reported" in item for item in result.removed_items["risks"])


def test_changed_dependency_migration_section_is_detected(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    old = _plan(tmp_path, project, "old.yaml")
    new = tmp_path / "new.yaml"
    new.write_text(
        old.read_text(encoding="utf-8").replace(
            '  possibly_missing:\n',
            '  possibly_missing:\n    - "cv_bridge"\n',
        ),
        encoding="utf-8",
    )

    result = diff_migration_plans(old, new)

    assert any("possibly_missing: cv_bridge" in item for item in result.added_items["dependency_migration"])


def test_invalid_old_plan_is_rejected(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    old = tmp_path / "old.yaml"
    old.write_text('target: "ros2"\n', encoding="utf-8")
    new = _plan(tmp_path, project, "new.yaml")

    try:
        diff_migration_plans(old, new)
    except ValueError as exc:
        assert "old migration plan is invalid" in str(exc)
    else:
        raise AssertionError("invalid old migration plan was not rejected")


def test_invalid_new_plan_is_rejected(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    old = _plan(tmp_path, project, "old.yaml")
    new = tmp_path / "new.yaml"
    new.write_text('target: "ros2"\n', encoding="utf-8")

    try:
        diff_migration_plans(old, new)
    except ValueError as exc:
        assert "new migration plan is invalid" in str(exc)
    else:
        raise AssertionError("invalid new migration plan was not rejected")


def test_json_output_has_stable_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    old = _plan(tmp_path, project, "old.yaml")
    new = tmp_path / "new.yaml"
    new.write_text(old.read_text(encoding="utf-8"), encoding="utf-8")
    runner = CliRunner()

    result = runner.invoke(app, ["migrate-plan-diff", "--old", str(old), "--new", str(new), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert list(data.keys()) == [
        "old_plan",
        "new_plan",
        "valid",
        "has_changes",
        "changed_fields",
        "added_items",
        "removed_items",
        "unchanged_fields",
        "warnings",
        "safety_note",
    ]


def test_diff_does_not_modify_either_plan_file(tmp_path: Path) -> None:
    project = tmp_path / "ros1_migration_demo"
    _ros1_package(project)
    old = _plan(tmp_path, project, "old.yaml")
    new = tmp_path / "new.yaml"
    new.write_text(old.read_text(encoding="utf-8"), encoding="utf-8")
    before_old = old.read_text(encoding="utf-8")
    before_new = new.read_text(encoding="utf-8")

    diff_migration_plans(old, new)

    assert old.read_text(encoding="utf-8") == before_old
    assert new.read_text(encoding="utf-8") == before_new
