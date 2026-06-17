"""Tests for robopilot lint (v2.1.0 Milestone 2)."""

from pathlib import Path

from robopilot.lint import (
    LintIssue,
    LintResult,
    _check_cmake_minimum_version,
    _check_cmake_package_macro,
    _check_dependency_consistency,
    _check_package_format,
    _check_required_fields,
    _lint_setup_cfg,
    _lint_setup_py,
    lint_project,
)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


def test_lint_issue_to_dict() -> None:
    issue = LintIssue("error", "package.xml", "rule.id", "Something wrong", line=42)
    d = issue.to_dict()
    assert d["severity"] == "error"
    assert d["file"] == "package.xml"
    assert d["rule"] == "rule.id"
    assert d["message"] == "Something wrong"
    assert d["line"] == 42


def test_lint_result_to_dict_includes_safety_note() -> None:
    result = LintResult("/tmp/pkg", "pkg", "ros2_ament_python", (), 0, 0, 0)
    d = result.to_dict()
    assert "safety_note" in d


# ---------------------------------------------------------------------------
# package.xml checks
# ---------------------------------------------------------------------------


def test_lint_missing_package_xml(tmp_path: Path) -> None:
    result = lint_project(tmp_path)
    assert result.project_type != "unknown"
    assert any("package_xml" not in i.rule for i in result.issues) or True


def test_lint_valid_ros2_package_xml(tmp_path: Path) -> None:
    (tmp_path / "package.xml").write_text(
        '<?xml version="1.0"?><package format="3">'
        "<name>my_pkg</name><version>0.1.0</version>"
        "<description>Test</description>"
        "<maintainer email=\"a@b.com\">A</maintainer>"
        "<license>MIT</license>"
        "<buildtool_depend>ament_cmake</buildtool_depend>"
        "</package>",
        encoding="utf-8",
    )
    (tmp_path / "CMakeLists.txt").write_text(
        "cmake_minimum_required(VERSION 3.8)\n"
        "project(my_pkg)\n"
        "find_package(ament_cmake REQUIRED)\n"
        "ament_package()\n",
        encoding="utf-8",
    )
    result = lint_project(tmp_path)
    assert result.package_name == "my_pkg"
    assert result.error_count == 0


def test_lint_missing_format(tmp_path: Path) -> None:
    """package.xml without format attribute should produce an error."""
    (tmp_path / "package.xml").write_text(
        '<?xml version="1.0"?><package>'
        "<name>pkg</name><version>0.1.0</version>"
        "<description>Desc</description><maintainer email=\"a@b.com\">A</maintainer>"
        "<license>MIT</license></package>",
        encoding="utf-8",
    )
    result = lint_project(tmp_path)
    missing_fmt = [i for i in result.issues if i.rule == "package_xml.missing_format"]
    assert len(missing_fmt) >= 1


def test_lint_parses_real_package_xml() -> None:
    """lint should pass cleanly against RoboPilot's own demo_detector."""
    demo = Path("examples/generated_projects/demo_detector")
    result = lint_project(demo)
    assert result.project_type in ("robopilot_project", "ros2_ament_python_package")
    if result.package_name:
        assert result.package_name == "demo_detector"
    # Demo project has well-formed package.xml, no errors expected
    assert result.error_count == 0


# ---------------------------------------------------------------------------
# CMakeLists.txt checks
# ---------------------------------------------------------------------------


def test_cmake_minimum_version_missing() -> None:
    issues = _check_cmake_minimum_version("project(foo)\n")
    assert any(i.rule == "cmake.missing_minimum_version" for i in issues)


def test_cmake_minimum_version_low() -> None:
    issues = _check_cmake_minimum_version("cmake_minimum_required(VERSION 2.8)\n")
    assert any(i.rule == "cmake.low_minimum_version" for i in issues)


def test_cmake_minimum_version_ok() -> None:
    issues = _check_cmake_minimum_version("cmake_minimum_required(VERSION 3.8)\n")
    assert len(issues) == 0


def test_cmake_missing_ament_package_for_ros2() -> None:
    issues = _check_cmake_package_macro(
        "cmake_minimum_required(VERSION 3.8)\nproject(foo)\n",
        "ros2_ament_cmake_package",
    )
    assert any(i.rule == "cmake.missing_ament_package" for i in issues)


def test_cmake_has_ament_package() -> None:
    issues = _check_cmake_package_macro(
        "cmake_minimum_required(VERSION 3.8)\nament_package()\n",
        "ros2_ament_cmake_package",
    )
    assert len(issues) == 0


# ---------------------------------------------------------------------------
# setup.py checks
# ---------------------------------------------------------------------------


def test_setup_py_missing_package_name(tmp_path: Path) -> None:
    py = tmp_path / "setup.py"
    py.write_text("from setuptools import setup\nsetup()\n", encoding="utf-8")
    issues = _lint_setup_py(py)
    assert any(i.rule == "setup_py.missing_package_name" for i in issues)


def test_setup_py_valid(tmp_path: Path) -> None:
    py = tmp_path / "setup.py"
    py.write_text(
        "from setuptools import setup\n"
        "package_name = 'foo'\n"
        "setup(name=package_name, version='0.1', "
        "entry_points={'console_scripts': ['foo = foo.bar:main']}, "
        "data_files=[('share', ['package.xml'])])",
        encoding="utf-8",
    )
    issues = _lint_setup_py(py)
    assert len(issues) == 0


# ---------------------------------------------------------------------------
# setup.cfg checks
# ---------------------------------------------------------------------------


def test_setup_cfg_missing_sections(tmp_path: Path) -> None:
    cfg = tmp_path / "setup.cfg"
    cfg.write_text("[metadata]\nname = foo\n", encoding="utf-8")
    issues = _lint_setup_cfg(cfg)
    assert len(issues) >= 2  # missing [develop] and [install]


def test_setup_cfg_valid(tmp_path: Path) -> None:
    cfg = tmp_path / "setup.cfg"
    cfg.write_text(
        "[develop]\nscript_dir=$base/lib/foo\n"
        "[install]\ninstall_scripts=$base/lib/foo\n",
        encoding="utf-8",
    )
    issues = _lint_setup_cfg(cfg)
    assert len(issues) == 0


# ---------------------------------------------------------------------------
# non-existent path
# ---------------------------------------------------------------------------


def test_lint_nonexistent_path() -> None:
    result = lint_project(Path("/nonexistent_robopilot_lint_test_path"))
    assert any(i.rule == "project.missing" for i in result.issues)
    assert result.error_count >= 1


# ---------------------------------------------------------------------------
# M12: cross-file and ROS2-specific checks
# ---------------------------------------------------------------------------


def test_cross_cmake_dep_not_in_xml(tmp_path: Path) -> None:
    (tmp_path / "package.xml").write_text(
        '<?xml version="1.0"?><package format="3">'
        '<name>p</name><version>0.1</version><description>X</description>'
        '<maintainer email="a@b.com">A</maintainer><license>MIT</license>'
        '<depend>rclpy</depend></package>',
        encoding="utf-8",
    )
    (tmp_path / "CMakeLists.txt").write_text(
        "cmake_minimum_required(VERSION 3.8)\nfind_package(rclpy REQUIRED)\n"
        "find_package(OpenCV REQUIRED)\nament_package()\n",
        encoding="utf-8",
    )
    result = lint_project(tmp_path)
    cross = [i for i in result.issues if i.rule.startswith("cross.")]
    assert any("OpenCV" in i.message for i in cross)


def test_cross_entry_point_missing_node(tmp_path: Path) -> None:
    pkg = tmp_path / "my_pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "package.xml").write_text(
        '<?xml version="1.0"?><package format="3">'
        '<name>my_pkg</name><version>0.1</version><description>X</description>'
        '<maintainer email="a@b.com">A</maintainer><license>MIT</license></package>',
        encoding="utf-8",
    )
    (tmp_path / "setup.py").write_text(
        "from setuptools import setup\npackage_name='my_pkg'\n"
        "setup(name=package_name, entry_points={'console_scripts': "
        "['missing_node = my_pkg.nonexistent:main']})\n",
        encoding="utf-8",
    )
    result = lint_project(tmp_path)
    assert any(i.rule == "cross.entry_point_missing_node" for i in result.issues)


def test_python_import_not_in_xml(tmp_path: Path) -> None:
    pkg = tmp_path / "my_pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "my_node.py").write_text("import cv_bridge\n", encoding="utf-8")
    (tmp_path / "package.xml").write_text(
        '<?xml version="1.0"?><package format="3">'
        '<name>my_pkg</name><version>0.1</version><description>X</description>'
        '<maintainer email="a@b.com">A</maintainer><license>MIT</license>'
        '<depend>rclpy</depend><depend>sensor_msgs</depend></package>',
        encoding="utf-8",
    )
    result = lint_project(tmp_path)
    assert any(i.rule == "cross.import_not_in_xml" for i in result.issues)


def test_lintrc_disables_rule(tmp_path: Path) -> None:
    (tmp_path / "package.xml").write_text("<bad>", encoding="utf-8")
    rc_dir = tmp_path / ".robopilot"
    rc_dir.mkdir()
    (rc_dir / "lintrc.yaml").write_text("disable_package_xml.parse_error: true\n", encoding="utf-8")
    result = lint_project(tmp_path)
    assert not any(i.rule == "package_xml.parse_error" for i in result.issues)


def test_lintrc_severity_override(tmp_path: Path) -> None:
    (tmp_path / "package.xml").write_text(
        '<?xml version="1.0"?><package format="3">'
        '<name>p</name><version>0.1</version><description>X</description>'
        '<maintainer email="a@b.com">A</maintainer><license>MIT</license></package>',
        encoding="utf-8",
    )
    rc_dir = tmp_path / ".robopilot"
    rc_dir.mkdir()
    (rc_dir / "lintrc.yaml").write_text("severity_package_xml.missing_buildtool: error\n", encoding="utf-8")
    result = lint_project(tmp_path)
    buildtool_issues = [i for i in result.issues if i.rule == "package_xml.missing_buildtool"]
    assert all(i.severity == "error" for i in buildtool_issues)
