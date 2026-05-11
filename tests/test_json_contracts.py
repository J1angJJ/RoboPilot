from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.generator.project_generator import generate_project_from_spec
from robopilot.main import app
from robopilot.planner.rule_based_planner import RuleBasedPlanner
from robopilot.spec.io import write_spec


def test_detect_json_has_expected_top_level_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _write_ros1_package(project)

    data = _invoke_json(["detect", str(project), "--json"])

    assert list(data.keys()) == [
        "project_path",
        "exists",
        "project_type",
        "confidence",
        "detected_signals",
        "missing_common_files",
        "notes",
        "suggested_next_steps",
    ]


def test_inspect_json_has_expected_top_level_keys(tmp_path: Path) -> None:
    project = _generate_demo_project(tmp_path)

    data = _invoke_json(["inspect", str(project), "--json"])

    assert list(data.keys()) == [
        "project_path",
        "exists",
        "is_empty",
        "package_name",
        "spec",
        "files",
        "issues",
        "suggested_next_steps",
    ]


def test_inspect_ros1_json_has_expected_top_level_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _write_ros1_package(project)

    data = _invoke_json(["inspect-ros1", str(project), "--json"])

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


def test_inspect_ros2_json_has_expected_top_level_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros2_py_demo"
    _write_ros2_python_package(project)

    data = _invoke_json(["inspect-ros2", str(project), "--json"])

    assert list(data.keys()) == [
        "project_path",
        "exists",
        "package_name",
        "package_format",
        "detected_project_type",
        "dependencies",
        "build_system",
        "files",
        "nodes",
        "rclpy_usage",
        "rclcpp_usage",
        "issues",
        "suggested_next_steps",
        "safety_note",
    ]


def test_deps_json_has_expected_top_level_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _write_ros1_package(project)

    data = _invoke_json(["deps", str(project), "--json"])

    assert list(data.keys()) == [
        "project_path",
        "exists",
        "project_type",
        "declared_dependencies",
        "detected_usage",
        "inferred_dependencies",
        "possibly_missing",
        "possibly_unused",
        "hints",
        "migration_hints",
        "rosdep_hints",
        "warnings",
        "suggested_next_steps",
        "safety_note",
    ]


def test_migrate_plan_json_file_has_expected_top_level_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _write_ros1_package(project)
    output = tmp_path / "migration_plan.json"

    result = CliRunner().invoke(
        app,
        [
            "migrate-plan",
            "--from",
            str(project),
            "--to",
            "ros2",
            "--output",
            str(output),
            "--format",
            "json",
        ],
    )

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


def test_migrate_plan_validate_json_has_expected_top_level_keys(tmp_path: Path) -> None:
    plan = _write_migration_plan(tmp_path)

    data = _invoke_json(["migrate-plan-validate", "--plan", str(plan), "--json"])

    assert list(data.keys()) == [
        "plan_path",
        "valid",
        "missing_fields",
        "invalid_fields",
        "warnings",
        "suggested_next_steps",
        "safety_note",
    ]


def test_migrate_plan_diff_json_has_expected_top_level_keys(tmp_path: Path) -> None:
    old_plan = _write_migration_plan(tmp_path)
    new_plan = tmp_path / "migration_plan_new.json"
    new_plan.write_text(old_plan.read_text(encoding="utf-8"), encoding="utf-8")

    data = _invoke_json(
        ["migrate-plan-diff", "--old", str(old_plan), "--new", str(new_plan), "--json"]
    )

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


def test_migrate_preview_json_has_expected_top_level_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _write_ros1_package(project)
    plan = _write_migration_plan(tmp_path, project=project)

    data = _invoke_json(["migrate-preview", "--plan", str(plan), "--project", str(project), "--json"])

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


def test_migrate_scaffold_preview_json_has_expected_top_level_keys(tmp_path: Path) -> None:
    project = tmp_path / "ros1_demo"
    _write_ros1_package(project)
    plan = _write_migration_plan(tmp_path, project=project)

    data = _invoke_json(["migrate-scaffold-preview", "--plan", str(plan), "--json"])

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


def test_apply_preview_json_has_expected_top_level_keys(tmp_path: Path) -> None:
    spec_path = _write_demo_spec(tmp_path)

    data = _invoke_json(
        [
            "apply-preview",
            "--spec",
            str(spec_path),
            "--project",
            str(tmp_path / "missing_project"),
            "--json",
        ]
    )

    assert list(data.keys()) == [
        "spec_path",
        "project_path",
        "package_name",
        "selected_template",
        "files_to_create",
        "files_to_update",
        "files_to_keep",
        "conflicts",
        "missing_project",
        "safety_note",
        "suggested_next_steps",
    ]


def test_apply_json_has_expected_top_level_keys(tmp_path: Path) -> None:
    spec_path = _write_demo_spec(tmp_path)
    plan_path = tmp_path / "apply_plan.json"
    result = CliRunner().invoke(
        app,
        [
            "apply-plan",
            "--spec",
            str(spec_path),
            "--project",
            str(tmp_path / "apply_target"),
            "--output",
            str(plan_path),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0

    data = _invoke_json(["apply", "--plan", str(plan_path), "--json"])

    assert list(data.keys()) == [
        "plan_path",
        "project_path",
        "dry_run",
        "files_created",
        "files_updated",
        "files_kept",
        "backups_created",
        "skipped_files",
        "conflicts",
        "safety_note",
    ]


def test_history_json_has_expected_top_level_keys_for_empty_history(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    data = _invoke_json(["history", "--project", str(project), "--json"])

    assert list(data.keys()) == [
        "project_path",
        "history_dir",
        "entries",
    ]
    assert data["entries"] == []


def test_repair_suggest_json_has_expected_top_level_keys(tmp_path: Path) -> None:
    project = _generate_demo_project(tmp_path)

    data = _invoke_json(["repair-suggest", str(project), "--json"])

    assert list(data.keys()) == [
        "project_path",
        "issues",
        "repair_suggestions",
        "safety_note",
        "suggested_commands",
    ]


def _invoke_json(args: list[str]) -> dict[str, object]:
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, dict)
    return data


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_ros1_package(project: Path) -> None:
    _write(
        project / "package.xml",
        """<?xml version="1.0"?>
<package format="2">
  <name>ros1_demo</name>
  <version>0.0.1</version>
  <description>ROS1 demo</description>
  <maintainer email="demo@example.com">Demo</maintainer>
  <license>MIT</license>
  <buildtool_depend>catkin</buildtool_depend>
  <build_depend>rospy</build_depend>
  <build_depend>roscpp</build_depend>
  <exec_depend>rospy</exec_depend>
  <exec_depend>std_msgs</exec_depend>
</package>
""",
    )
    _write(
        project / "CMakeLists.txt",
        """cmake_minimum_required(VERSION 3.0.2)
project(ros1_demo)
find_package(catkin REQUIRED COMPONENTS roscpp rospy std_msgs message_generation)
catkin_package()
""",
    )
    _write(project / "launch" / "demo.launch", '<launch><node pkg="ros1_demo" type="talker.py" /></launch>\n')
    _write(project / "scripts" / "talker.py", "import rospy\nrospy.init_node('talker')\n")
    _write(project / "src" / "listener.cpp", "#include <ros/ros.h>\n")
    _write(project / "msg" / "Demo.msg", "string data\n")
    _write(project / "srv" / "Demo.srv", "string in\n---\nstring out\n")
    _write(project / "action" / "Demo.action", "string goal\n---\nstring result\n---\nstring feedback\n")


def _write_ros2_python_package(project: Path) -> None:
    _write(
        project / "package.xml",
        """<?xml version="1.0"?>
<package format="3">
  <name>ros2_py_demo</name>
  <version>0.0.1</version>
  <description>ROS2 demo</description>
  <maintainer email="demo@example.com">Demo</maintainer>
  <license>MIT</license>
  <exec_depend>rclpy</exec_depend>
  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
""",
    )
    _write(project / "setup.py", "from setuptools import setup\nsetup(name='ros2_py_demo')\n")
    _write(project / "setup.cfg", "[develop]\nscript_dir=$base/lib/ros2_py_demo\n")
    _write(project / "resource" / "ros2_py_demo", "")
    _write(project / "ros2_py_demo" / "node.py", "import rclpy\n")
    _write(project / "launch" / "demo.launch.py", "from launch import LaunchDescription\n")
    _write(project / "config" / "params.yaml", "ros__parameters: {}\n")


def _write_demo_spec(tmp_path: Path) -> Path:
    spec = RuleBasedPlanner().plan(
        package_name="demo_detector",
        task="Create an object detection pipeline",
    )
    spec_path = tmp_path / "robopilot.yaml"
    write_spec(spec, spec_path)
    return spec_path


def _generate_demo_project(tmp_path: Path) -> Path:
    spec = RuleBasedPlanner().plan(
        package_name="demo_detector",
        task="Create an object detection pipeline",
    )
    generated = generate_project_from_spec(spec=spec, output_root=tmp_path / "generated")
    return generated.output_dir


def _write_migration_plan(tmp_path: Path, *, project: Path | None = None) -> Path:
    source_project = project or tmp_path / "ros1_demo"
    if project is None:
        _write_ros1_package(source_project)
    output = tmp_path / "migration_plan.json"
    result = CliRunner().invoke(
        app,
        [
            "migrate-plan",
            "--from",
            str(source_project),
            "--to",
            "ros2",
            "--output",
            str(output),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    return output
