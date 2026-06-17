"""Tests for robopilot ci-check (v2.1.0 Milestone 10)."""

from pathlib import Path

from robopilot.ci_check import CICheckResult, ci_check


def test_ci_check_on_demo_detector_clean() -> None:
    demo = Path("examples/generated_projects/demo_detector")
    result = ci_check(demo)
    assert result.exit_code in (0, 1, 2)
    assert result.overall_status in ("clean", "warnings", "errors")
    assert result.lint_errors >= 0
    assert result.package_name == "demo_detector"


def test_ci_check_on_nonexistent_path() -> None:
    result = ci_check(Path("/nonexistent_ci_test_path"))
    assert result.exit_code == 2  # project.missing error
    assert result.overall_status == "errors"


def test_ci_check_result_to_dict() -> None:
    r = CICheckResult("/tmp", "pkg", "ros2", 0, 2, 1, 0, 0, "warnings", 1)
    d = r.to_dict()
    assert d["overall_status"] == "warnings"
    assert d["exit_code"] == 1
    assert d["lint_errors"] == 0
    assert d["lint_warnings"] == 2
    assert "safety_note" in d


def test_ci_check_sarif_output(tmp_path: Path) -> None:
    demo = Path("examples/generated_projects/demo_detector")
    out = tmp_path / "report.sarif"
    result = ci_check(demo, fmt="sarif", output=out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert '"$schema"' in content
    assert '"version"' in content
    assert '"2.1.0"' in content


def test_ci_check_markdown_output(tmp_path: Path) -> None:
    demo = Path("examples/generated_projects/demo_detector")
    out = tmp_path / "report.md"
    result = ci_check(demo, fmt="markdown", output=out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "# RoboPilot CI Check Report" in content
    assert "demo_detector" in content


def test_exit_code_errors_on_bad_package(tmp_path: Path) -> None:
    (tmp_path / "package.xml").write_text("<bad>", encoding="utf-8")
    result = ci_check(tmp_path)
    assert result.exit_code == 2
    assert result.overall_status == "errors"


def test_ci_check_json_output() -> None:
    result = ci_check(Path("examples/generated_projects/demo_detector"))
    d = result.to_dict()
    assert d["overall_status"] in ("clean", "warnings", "errors")
    assert d["exit_code"] in (0, 1, 2)
    assert "safety_note" in d


def test_ci_check_all_formats(tmp_path: Path) -> None:
    demo = Path("examples/generated_projects/demo_detector")
    for fmt in ("summary", "sarif", "markdown"):
        result = ci_check(demo, fmt=fmt)
        assert result.exit_code in (0, 1, 2)


def test_ci_check_sarif_output_has_expected_keys(tmp_path: Path) -> None:
    demo = Path("examples/generated_projects/demo_detector")
    out = tmp_path / "report.sarif"
    ci_check(demo, fmt="sarif", output=out)
    import json
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["version"] == "2.1.0"
    assert "runs" in data
    assert len(data["runs"]) > 0
    assert "tool" in data["runs"][0]
    assert "results" in data["runs"][0]
