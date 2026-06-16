"""Tests for robopilot launch file validation (v2.1.0 Milestone 5)."""

from pathlib import Path

from robopilot.launch_lint import (
    LaunchIssue,
    LaunchLintResult,
    _lint_ros1_launch,
    _lint_ros2_launch,
    lint_launch_files,
)


# ---------------------------------------------------------------------------
# ROS1 XML launch
# ---------------------------------------------------------------------------


def test_valid_ros1_launch(tmp_path: Path) -> None:
    lf = tmp_path / "test.launch"
    lf.write_text(
        '<?xml version="1.0"?>\n<launch>\n'
        '  <node pkg="foo" type="foo_node" name="foo_node" output="screen"/>\n'
        '  <arg name="debug" default="false"/>\n'
        '</launch>\n',
        encoding="utf-8",
    )
    issues = _lint_ros1_launch(lf, "test.launch")
    # Valid launch should have no errors
    errors = [i for i in issues if i.severity == "error"]
    assert len(errors) == 0


def test_ros1_node_missing_name(tmp_path: Path) -> None:
    lf = tmp_path / "test.launch"
    lf.write_text(
        '<?xml version="1.0"?>\n<launch>\n'
        '  <node pkg="foo" type="foo_node"/>\n'
        '</launch>\n',
        encoding="utf-8",
    )
    issues = _lint_ros1_launch(lf, "test.launch")
    assert any(i.rule == "launch.ros1.node_no_name" for i in issues)


def test_deprecated_machine_tag(tmp_path: Path) -> None:
    lf = tmp_path / "test.launch"
    lf.write_text(
        '<?xml version="1.0"?>\n<launch>\n'
        '  <machine name="robot1" address="10.0.0.1"/>\n'
        '  <node pkg="foo" type="foo_node" name="foo"/>\n'
        '</launch>\n',
        encoding="utf-8",
    )
    issues = _lint_ros1_launch(lf, "test.launch")
    assert any(i.rule == "launch.ros1.deprecated_machine" for i in issues)


def test_ros1_arg_no_default(tmp_path: Path) -> None:
    lf = tmp_path / "test.launch"
    lf.write_text(
        '<?xml version="1.0"?>\n<launch>\n'
        '  <arg name="map_file"/>\n'
        '</launch>\n',
        encoding="utf-8",
    )
    issues = _lint_ros1_launch(lf, "test.launch")
    assert any(i.rule == "launch.ros1.arg_no_default" for i in issues)


def test_ros1_parse_error(tmp_path: Path) -> None:
    lf = tmp_path / "test.launch"
    lf.write_text("not xml <<<", encoding="utf-8")
    issues = _lint_ros1_launch(lf, "test.launch")
    assert any(i.rule == "launch.parse_error" for i in issues)


# ---------------------------------------------------------------------------
# ROS2 Python launch
# ---------------------------------------------------------------------------


def test_valid_ros2_launch(tmp_path: Path) -> None:
    lf = tmp_path / "my.launch.py"
    lf.write_text(
        "from launch import LaunchDescription\n"
        "from launch_ros.actions import Node\n\n"
        "def generate_launch_description():\n"
        "    return LaunchDescription([\n"
        "        Node(package='foo', executable='bar', name='bar',\n"
        "             parameters=['config/params.yaml']),\n"
        "    ])\n",
        encoding="utf-8",
    )
    issues = _lint_ros2_launch(lf, "my.launch.py")
    errors = [i for i in issues if i.severity == "error"]
    assert len(errors) == 0


def test_ros2_no_launch_description(tmp_path: Path) -> None:
    lf = tmp_path / "bad.launch.py"
    lf.write_text("x = 1\n", encoding="utf-8")
    issues = _lint_ros2_launch(lf, "bad.launch.py")
    assert any(i.rule == "launch.ros2.no_launch_description" for i in issues)


def test_ros2_syntax_error(tmp_path: Path) -> None:
    lf = tmp_path / "broken.launch.py"
    lf.write_text("def broken(\n", encoding="utf-8")
    issues = _lint_ros2_launch(lf, "broken.launch.py")
    assert any(i.rule == "launch.python_syntax" for i in issues)


# ---------------------------------------------------------------------------
# Integration
# ---------------------------------------------------------------------------


def test_lint_launch_files_on_ros1_demo() -> None:
    """Real ROS1 demo has a launch directory."""
    result = lint_launch_files(Path("examples/ros1_migration_demo"))
    assert result.files_checked
    assert isinstance(result.error_count, int)


def test_lint_on_project_without_launch_files(tmp_path: Path) -> None:
    (tmp_path / "package.xml").write_text(
        '<?xml version="1.0"?><package format="2"><name>p</name></package>',
        encoding="utf-8",
    )
    result = lint_launch_files(tmp_path)
    assert len(result.files_checked) == 0
    assert len(result.issues) == 0


def test_result_to_dict() -> None:
    result = LaunchLintResult(
        ("f1.launch", "f2.launch.py"),
        (LaunchIssue("warning", "f1.launch", "r.id", "msg"),),
        0, 1, 0,
    )
    d = result.to_dict()
    assert "safety_note" in d
    assert d["files_checked"] == ["f1.launch", "f2.launch.py"]
    assert len(d["issues"]) == 1
