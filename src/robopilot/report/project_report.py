"""Markdown & HTML report generation for RoboPilot project inspections."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from robopilot.ci_check import ci_check
from robopilot.inspector.project_inspector import inspect_project
from robopilot.repair.repair_suggester import RepairSuggestion, suggest_repairs


STATIC_SAFETY_NOTE = (
    "This report is generated from static inspection only. RoboPilot did not "
    "execute ROS2, launch files, colcon, or generated Python code."
)


def generate_project_report(project_path: Path) -> str:
    """Generate a deterministic Markdown report for a project directory."""
    inspection = inspect_project(project_path)
    repairs = suggest_repairs(project_path)

    lines = [
        "# RoboPilot Project Report",
        "",
        "## Project Summary",
        "",
        f"- Project path: {inspection.project_path}",
        f"- Exists: {_bool(inspection.exists)}",
        f"- Empty: {_bool(inspection.is_empty)}",
        f"- Package name: {inspection.package_name or 'unknown'}",
        f"- Spec exists: {_bool(inspection.spec.exists)}",
        f"- Spec valid: {_bool(inspection.spec.valid)}",
        f"- Selected template: {inspection.spec.selected_template or 'unknown'}",
        "",
        "## Spec Status",
        "",
        f"- robopilot.yaml exists: {_bool(inspection.spec.exists)}",
        f"- Valid spec: {_bool(inspection.spec.valid)}",
        f"- Selected template: {inspection.spec.selected_template or 'unknown'}",
        f"- Spec errors: {_join_or_none(inspection.spec.errors)}",
        "",
        "## Detected Files",
        "",
        f"- package.xml: {_bool(inspection.files.package_xml)}",
        f"- setup.py: {_bool(inspection.files.setup_py)}",
        f"- setup.cfg: {_bool(inspection.files.setup_cfg)}",
        f"- README.md: {_bool(inspection.files.readme)}",
        f"- Launch files: {_join_or_none(inspection.files.launch_files)}",
        f"- Config files: {_join_or_none(inspection.files.config_files)}",
        f"- Python node files: {_join_or_none(inspection.files.python_node_files)}",
        "",
        "## Potential Issues",
        "",
    ]
    lines.extend(_bullet_list(inspection.issues, "No obvious structural issues detected."))
    lines.extend(["", "## Repair Suggestions", ""])
    lines.extend(_repair_suggestions(repairs.repair_suggestions))
    lines.extend(["", "## Suggested Commands", ""])
    lines.extend(_bullet_list(repairs.suggested_commands, "No commands suggested."))
    lines.extend(["", "## Safety Note", "", STATIC_SAFETY_NOTE, repairs.safety_note, ""])
    return "\n".join(lines)


def write_project_report(project_path: Path, output_path: Path) -> str:
    """Generate and write a Markdown report, returning the rendered text."""
    markdown = generate_project_report(project_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    return markdown


def _repair_suggestions(suggestions: tuple[RepairSuggestion, ...]) -> list[str]:
    if not suggestions:
        return ["- No repair suggestions needed."]
    return [
        f"- [{suggestion.severity}] {suggestion.issue}: {suggestion.suggestion}"
        for suggestion in suggestions
    ]


def _bullet_list(values: tuple[str, ...], empty_message: str) -> list[str]:
    if not values:
        return [f"- {empty_message}"]
    return [f"- {value}" for value in values]


def _join_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _bool(value: bool) -> str:
    return "true" if value else "false"


# ---------------------------------------------------------------------------
# M16: HTML report
# ---------------------------------------------------------------------------

_HTML_CSS = """<style>
body { font-family: -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 2em; color: #24292e; }
h1 { border-bottom: 2px solid #0366d6; padding-bottom: .3em; }
h2 { border-bottom: 1px solid #eaecef; padding-bottom: .3em; margin-top: 1.5em; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #dfe2e5; padding: 6px 13px; text-align: left; }
th { background: #f6f8fa; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 12px; font-weight: 600; color: #fff; }
.badge-error { background: #d73a49; }
.badge-warning { background: #f9c513; color: #333; }
.badge-info { background: #0366d6; }
.badge-clean { background: #28a745; }
.severity-error { color: #d73a49; font-weight: bold; }
.severity-warning { color: #b08800; font-weight: bold; }
.severity-info { color: #0366d6; }
.timestamp { color: #586069; font-size: 90%; }
.score-bar { background: #eaecef; height: 20px; border-radius: 10px; overflow: hidden; margin: 4px 0; }
.score-fill { height: 100%; border-radius: 10px; transition: width .3s; }
</style>"""


def generate_html_report(project_path: Path, history_data: dict | None = None) -> str:
    """Generate an HTML quality report with severity badges and styling."""
    ci = ci_check(project_path)
    inspection = inspect_project(project_path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'>",
        "<title>RoboPilot Quality Report</title>",
        _HTML_CSS,
        "</head><body>",
        f"<h1>RoboPilot Quality Report</h1>",
        f"<p class='timestamp'>Generated: {now}</p>",
        "",
        "<h2>Summary</h2>",
        "<table>",
        f"<tr><td><b>Project</b></td><td>{ci.package_name or 'unknown'}</td></tr>",
        f"<tr><td><b>Type</b></td><td>{ci.project_type}</td></tr>",
        f"<tr><td><b>Status</b></td><td>{_html_badge(ci.overall_status)}</td></tr>",
        f"<tr><td><b>Path</b></td><td><code>{ci.project_path}</code></td></tr>",
        "</table>",
        "",
        "<h2>Quality Metrics</h2>",
        "<table>",
        f"<tr><td>Lint Errors</td><td class='severity-error'>{ci.lint_errors}</td></tr>",
        f"<tr><td>Lint Warnings</td><td class='severity-warning'>{ci.lint_warnings}</td></tr>",
        f"<tr><td>Lint Info</td><td class='severity-info'>{ci.lint_infos}</td></tr>",
        f"<tr><td>Dependency Warnings</td><td>{ci.dep_warnings}</td></tr>",
        f"<tr><td>Launch Issues</td><td>{ci.launch_issues}</td></tr>",
        "</table>",
    ]

    if history_data:
        prev = history_data.get("previous", {})
        lines.append("<h2>Trend Comparison</h2>")
        lines.append("<table>")
        for metric, key in [("Lint Errors", "lint_errors"), ("Lint Warnings", "lint_warnings"),
                            ("Dep Warnings", "dep_warnings"), ("Launch Issues", "launch_issues")]:
            prev_val = prev.get(key, "—")
            cur_val = getattr(ci, key, "—")
            diff_str = ""
            if isinstance(prev_val, int) and isinstance(cur_val, int):
                delta = cur_val - prev_val
                if delta > 0:
                    diff_str = f" <span class='severity-error'>(+{delta})</span>"
                elif delta < 0:
                    diff_str = f" <span style='color:#28a745'>({delta})</span>"
            lines.append(f"<tr><td>{metric}</td><td>{prev_val}</td><td>{cur_val}{diff_str}</td></tr>")
        lines.append("</table>")

    from robopilot import __version__ as _ver
    lines.append(f"<p class='timestamp'>RoboPilot v{_ver} — static analysis only, no ROS runtime.</p>")
    lines.append("</body></html>")
    return "\n".join(lines)


def _html_badge(status: str) -> str:
    cls = {"clean": "badge-clean", "warnings": "badge-warning", "errors": "badge-error"}.get(status, "badge-info")
    return f"<span class='badge {cls}'>{status.upper()}</span>"


# ---------------------------------------------------------------------------
# M16: History comparison
# ---------------------------------------------------------------------------

_HISTORY_DIR = ".robopilot_history"


def save_report_snapshot(project_path: Path) -> Path:
    """Save current quality metrics as a JSON snapshot for trend tracking."""
    history_dir = Path(project_path).resolve() / _HISTORY_DIR
    history_dir.mkdir(parents=True, exist_ok=True)
    ci = ci_check(project_path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    snap = history_dir / f"quality_{ts}.json"
    import json
    snap.write_text(json.dumps({
        "timestamp": ts,
        "lint_errors": ci.lint_errors,
        "lint_warnings": ci.lint_warnings,
        "lint_infos": ci.lint_infos,
        "dep_warnings": ci.dep_warnings,
        "launch_issues": ci.launch_issues,
        "overall_status": ci.overall_status,
    }, indent=2) + "\n", encoding="utf-8")
    return snap


def load_report_history(project_path: Path) -> list[dict]:
    """Load all quality snapshots for trend analysis."""
    history_dir = Path(project_path).resolve() / _HISTORY_DIR
    if not history_dir.is_dir():
        return []
    import json
    snapshots = sorted(history_dir.glob("quality_*.json"))
    results: list[dict] = []
    for snap in snapshots:
        try:
            data = json.loads(snap.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                results.append(data)
        except Exception:
            pass
    return results


def generate_history_report(project_path: Path) -> str:
    """Generate a Markdown report comparing current quality against historical snapshots."""
    history = load_report_history(project_path)
    ci = ci_check(project_path)

    lines = [
        "# RoboPilot Quality History",
        "",
        f"**Project:** {ci.package_name or 'unknown'}  ",
        f"**Current status:** {ci.overall_status.upper()}  ",
        "",
    ]

    if not history:
        lines.append("No historical snapshots found. Run `robopilot report --snapshot` to save one.")
        return "\n".join(lines) + "\n"

    lines.extend([
        "## Trend",
        "",
        "| Date | Errors | Warnings | Info | Dep Warnings | Launch | Status |",
        "|------|--------|----------|------|-------------|--------|--------|",
    ])

    for snap in history[-10:]:
        ts = snap.get("timestamp", "?")
        lines.append(
            f"| {ts} | {snap.get('lint_errors', '?')} | {snap.get('lint_warnings', '?')} | "
            f"{snap.get('lint_infos', '?')} | {snap.get('dep_warnings', '?')} | "
            f"{snap.get('launch_issues', '?')} | {snap.get('overall_status', '?')} |"
        )

    # Current row
    lines.append(
        f"| **current** | **{ci.lint_errors}** | **{ci.lint_warnings}** | "
        f"**{ci.lint_infos}** | **{ci.dep_warnings}** | **{ci.launch_issues}** | "
        f"**{ci.overall_status}** |"
    )

    lines.extend([
        "",
        "## Summary",
        "",
        f"- Snapshots: {len(history)}",
        f"- Current: {ci.overall_status.upper()} ({ci.lint_errors} errors, {ci.lint_warnings} warnings)",
    ])

    if len(history) >= 2:
        prev = history[-1]
        err_delta = ci.lint_errors - prev.get("lint_errors", 0)
        warn_delta = ci.lint_warnings - prev.get("lint_warnings", 0)
        if err_delta != 0 or warn_delta != 0:
            lines.append(f"- Delta from previous: {err_delta:+d} errors, {warn_delta:+d} warnings")

    return "\n".join(lines) + "\n"


def generate_diff_report(before: Path, after: Path) -> str:
    """Generate a before/after quality comparison for migration progress."""
    ci_before = ci_check(before)
    ci_after = ci_check(after)

    def delta(a: int, b: int) -> str:
        d = a - b
        if d > 0:
            return f"{a} → {b} (+{d} worse)"
        if d < 0:
            return f"{a} → {b} ({d} better)"
        return f"{a} → {b} (no change)"

    lines = [
        "# RoboPilot Migration Quality Diff",
        "",
        f"**Before:** {ci_before.package_name or before.name}  ",
        f"**After:** {ci_after.package_name or after.name}  ",
        "",
        "| Metric | Before | After | Change |",
        "|--------|--------|-------|--------|",
        f"| Lint Errors | {ci_before.lint_errors} | {ci_after.lint_errors} | {delta(ci_before.lint_errors, ci_after.lint_errors)} |",
        f"| Lint Warnings | {ci_before.lint_warnings} | {ci_after.lint_warnings} | {delta(ci_before.lint_warnings, ci_after.lint_warnings)} |",
        f"| Dep Warnings | {ci_before.dep_warnings} | {ci_after.dep_warnings} | {delta(ci_before.dep_warnings, ci_after.dep_warnings)} |",
        f"| Launch Issues | {ci_before.launch_issues} | {ci_after.launch_issues} | {delta(ci_before.launch_issues, ci_after.launch_issues)} |",
        "",
    ]
    return "\n".join(lines) + "\n"
