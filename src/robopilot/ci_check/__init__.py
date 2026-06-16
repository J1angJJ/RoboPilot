"""CI-friendly quality check with SARIF/Markdown export (v2.1.0 M10)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from robopilot.deps.analyzer import analyze_dependencies
from robopilot.detector.project_detector import detect_project
from robopilot.launch_lint import lint_launch_files
from robopilot.lint import lint_project

SAFETY_NOTE = (
    "This CI check is static and read-only. RoboPilot did not require ROS, "
    "run catkin_make, run colcon, execute launch files, execute code, or "
    "import user project modules."
)


@dataclass(frozen=True)
class CICheckResult:
    project_path: str
    package_name: str | None
    project_type: str
    lint_errors: int
    lint_warnings: int
    lint_infos: int
    dep_warnings: int
    launch_issues: int
    overall_status: str  # "clean", "warnings", "errors"
    exit_code: int       # 0=clean, 1=warnings, 2=errors

    def to_dict(self) -> dict[str, object]:
        return {
            "project_path": self.project_path,
            "package_name": self.package_name,
            "project_type": self.project_type,
            "lint_errors": self.lint_errors,
            "lint_warnings": self.lint_warnings,
            "lint_infos": self.lint_infos,
            "dep_warnings": self.dep_warnings,
            "launch_issues": self.launch_issues,
            "overall_status": self.overall_status,
            "exit_code": self.exit_code,
            "safety_note": SAFETY_NOTE,
        }


def ci_check(
    project_path: Path,
    *,
    fmt: str = "summary",
    output: Path | None = None,
) -> CICheckResult:
    """Run aggregated quality checks and optionally export a report."""
    path = Path(project_path).resolve()
    lint_result = lint_project(path)
    deps_result = analyze_dependencies(path)
    launch_result = lint_launch_files(path)
    detection = detect_project(path)

    status = "clean"
    exit_code = 0
    if lint_result.error_count > 0 or launch_result.error_count > 0:
        status = "errors"
        exit_code = 2
    elif lint_result.warning_count > 0 or deps_result.warnings or launch_result.warning_count > 0:
        status = "warnings"
        exit_code = 1

    pkg_name = lint_result.package_name

    result = CICheckResult(
        project_path=str(path),
        package_name=pkg_name,
        project_type=detection.project_type,
        lint_errors=lint_result.error_count,
        lint_warnings=lint_result.warning_count,
        lint_infos=lint_result.info_count,
        dep_warnings=len(deps_result.warnings),
        launch_issues=launch_result.error_count + launch_result.warning_count,
        overall_status=status,
        exit_code=exit_code,
    )

    if output and fmt == "sarif":
        _write_sarif(result, lint_result, launch_result, output)
    elif output and fmt == "markdown":
        _write_markdown(result, output)

    return result


# ---------------------------------------------------------------------------
# SARIF export (GitHub Code Scanning)
# ---------------------------------------------------------------------------


def _write_sarif(
    result: CICheckResult,
    lint_result: object,
    launch_result: object,
    path: Path,
) -> None:
    rules: list[dict] = []
    results: list[dict] = []
    rule_index: dict[str, int] = {}

    for issue in getattr(lint_result, "issues", ()):
        rid = issue.rule
        if rid not in rule_index:
            rule_index[rid] = len(rules)
            rules.append({
                "id": rid,
                "shortDescription": {"text": issue.message[:100]},
                "helpUri": "https://github.com/J1angJJ/RoboPilot",
            })
        sev = {"error": "error", "warning": "warning", "info": "note"}.get(issue.severity, "warning")
        loc = {"physicalLocation": {"artifactLocation": {"uri": issue.file}}}
        if issue.line:
            loc["physicalLocation"]["region"] = {"startLine": issue.line}
        results.append({
            "ruleId": rid,
            "ruleIndex": rule_index[rid],
            "level": sev,
            "message": {"text": issue.message},
            "locations": [loc],
        })

    for issue in getattr(launch_result, "issues", ()):
        rid = issue.rule
        if rid not in rule_index:
            rule_index[rid] = len(rules)
            rules.append({
                "id": rid,
                "shortDescription": {"text": issue.message[:100]},
                "helpUri": "https://github.com/J1angJJ/RoboPilot",
            })
        sev = {"error": "error", "warning": "warning", "info": "note"}.get(issue.severity, "warning")
        results.append({
            "ruleId": rid,
            "ruleIndex": rule_index[rid],
            "level": sev,
            "message": {"text": issue.message},
            "locations": [{"physicalLocation": {"artifactLocation": {"uri": issue.file}}}],
        })

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "RoboPilot",
                    "informationUri": "https://github.com/J1angJJ/RoboPilot",
                    "rules": rules,
                }
            },
            "results": results,
        }],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sarif, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Markdown report export
# ---------------------------------------------------------------------------


def _write_markdown(result: CICheckResult, path: Path) -> None:
    lines = [
        "# RoboPilot CI Check Report",
        "",
        f"**Project:** {result.package_name or 'unknown'}",
        f"**Path:** {result.project_path}",
        f"**Type:** {result.project_type}",
        f"**Status:** {result.overall_status.upper()}",
        "",
        "## Summary",
        "",
        f"| Check | Result |",
        f"|-------|--------|",
        f"| Lint errors | {result.lint_errors} |",
        f"| Lint warnings | {result.lint_warnings} |",
        f"| Lint info | {result.lint_infos} |",
        f"| Dep warnings | {result.dep_warnings} |",
        f"| Launch issues | {result.launch_issues} |",
        f"| **Overall** | **{result.overall_status}** |",
        "",
        "## Safety Note",
        "",
        SAFETY_NOTE,
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
