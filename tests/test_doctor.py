"""Tests for robopilot doctor (v2.2.0 M22)."""

from pathlib import Path

from robopilot.doctor import (
    DoctorCheck,
    DoctorResult,
    _check_config_integrity,
    _check_disk_space,
    _check_key_deps,
    _check_python_version,
    _check_robopilot_import,
    _check_ros_detection,
    _check_workspace_structure,
    run_doctor,
)


def test_doctor_runs_all_checks() -> None:
    result = run_doctor()
    assert len(result.checks) >= 5
    assert isinstance(result.all_passed, bool)
    assert isinstance(result.error_count, int)
    assert isinstance(result.warn_count, int)


def test_doctor_result_to_dict() -> None:
    result = run_doctor()
    d = result.to_dict()
    assert "checks" in d
    assert "all_passed" in d
    assert "error_count" in d
    assert "warn_count" in d
    for check in d["checks"]:
        assert isinstance(check, dict)
        assert "name" in check and "passed" in check and "status" in check and "message" in check


def test_check_python_version() -> None:
    c = _check_python_version()
    assert c.name == "Python version"
    assert c.status in ("ok", "warn", "error")


def test_check_robopilot_import() -> None:
    c = _check_robopilot_import()
    assert c.passed is True
    assert c.status == "ok"


def test_check_key_deps() -> None:
    c = _check_key_deps()
    assert c.passed is True


def test_check_disk_space() -> None:
    c = _check_disk_space(Path.cwd())
    assert c.name == "Disk space"
    assert c.status in ("ok", "warn")


def test_check_workspace_structure() -> None:
    c = _check_workspace_structure(Path("examples/generated_projects/demo_detector"))
    assert c.passed is True
    assert "ROS package" in c.message or "robopilot.yaml" in c.message


def test_check_ros_detection() -> None:
    c = _check_ros_detection(Path.cwd())
    assert c.name == "ROS detection"
    assert c.passed is True


def test_check_config_integrity(tmp_path: Path) -> None:
    c = _check_config_integrity(tmp_path)
    assert c.passed is True
    assert "No project config" in c.message


def test_check_config_integrity_with_broken_lintrc(tmp_path: Path) -> None:
    rc_dir = tmp_path / ".robopilot"
    rc_dir.mkdir()
    (rc_dir / "lintrc.yaml").write_text("broken line without colon\n", encoding="utf-8")
    c = _check_config_integrity(tmp_path)
    assert not c.passed
    assert c.status == "warn"


def test_check_config_integrity_with_valid_lintrc(tmp_path: Path) -> None:
    rc_dir = tmp_path / ".robopilot"
    rc_dir.mkdir()
    (rc_dir / "lintrc.yaml").write_text("disable_rule: true\nseverity_rule: error\n", encoding="utf-8")
    c = _check_config_integrity(tmp_path)
    assert c.passed is True


def test_doctor_check_dataclass() -> None:
    c = DoctorCheck("test", True, "ok", "everything works")
    d = c.to_dict()
    assert d["name"] == "test"
    assert d["passed"] is True
    assert d["status"] == "ok"
    assert d["message"] == "everything works"


def test_doctor_with_root(tmp_path: Path) -> None:
    result = run_doctor(tmp_path)
    assert len(result.checks) >= 5
    assert all(isinstance(c, DoctorCheck) for c in result.checks)
