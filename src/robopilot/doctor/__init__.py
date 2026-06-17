"""Environment self-diagnostic for RoboPilot (v2.2.0 M17)."""

from __future__ import annotations

import platform
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    passed: bool
    status: str   # "ok", "warn", "error"
    message: str

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "passed": self.passed, "status": self.status, "message": self.message}


@dataclass(frozen=True)
class DoctorResult:
    checks: tuple[DoctorCheck, ...]
    all_passed: bool
    error_count: int
    warn_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "checks": [c.to_dict() for c in self.checks],
            "all_passed": self.all_passed,
            "error_count": self.error_count,
            "warn_count": self.warn_count,
        }


def run_doctor(root: Path | None = None) -> DoctorResult:
    """Run all self-diagnostic checks."""
    base = Path(root or Path.cwd()).resolve()
    checks: list[DoctorCheck] = []

    checks.append(_check_python_version())
    checks.append(_check_robopilot_import())
    checks.append(_check_key_deps())
    checks.append(_check_disk_space(base))
    checks.append(_check_workspace_structure(base))
    checks.append(_check_ros_detection(base))
    checks.append(_check_config_integrity(base))

    errors = sum(1 for c in checks if c.status == "error")
    warns = sum(1 for c in checks if c.status == "warn")

    return DoctorResult(
        checks=tuple(checks),
        all_passed=not any(c.status == "error" for c in checks),
        error_count=errors,
        warn_count=warns,
    )


def _check_python_version() -> DoctorCheck:
    v = sys.version_info
    if v >= (3, 12):
        return DoctorCheck("Python version", True, "warn",
                           f"Python {v.major}.{v.minor}.{v.micro} — v3.12+ may have untested compatibility. v3.10–3.11 are fully tested.")
    if v >= (3, 10):
        return DoctorCheck("Python version", True, "ok",
                           f"Python {v.major}.{v.minor}.{v.micro} — supported.")
    return DoctorCheck("Python version", False, "error",
                       f"Python {v.major}.{v.minor}.{v.micro} — requires Python 3.10+.")


def _check_robopilot_import() -> DoctorCheck:
    try:
        import robopilot
        v = getattr(robopilot, "__version__", "unknown")
        return DoctorCheck("RoboPilot installed", True, "ok", f"RoboPilot v{v} importable.")
    except ImportError:
        return DoctorCheck("RoboPilot installed", False, "error", "RoboPilot is not importable. Run: pip install robopilot")


def _check_key_deps() -> DoctorCheck:
    missing: list[str] = []
    for mod, pkg in [("typer", "typer"), ("rich", "rich"), ("xml.etree.ElementTree", "stdlib")]:
        try:
            __import__(mod)
        except ImportError:
            if pkg != "stdlib":
                missing.append(pkg)
    if missing:
        return DoctorCheck("Key dependencies", False, "error", f"Missing: {', '.join(missing)}. Run: pip install {' '.join(missing)}")
    return DoctorCheck("Key dependencies", True, "ok", "typer, rich, xml.etree — all present.")


def _check_disk_space(base: Path) -> DoctorCheck:
    try:
        usage = shutil.disk_usage(base)
        gb_free = usage.free / (1024 ** 3)
        if gb_free < 1:
            return DoctorCheck("Disk space", False, "warn", f"{gb_free:.1f} GB free — low disk space may affect builds and bag files.")
        return DoctorCheck("Disk space", True, "ok", f"{gb_free:.1f} GB free.")
    except Exception:
        return DoctorCheck("Disk space", True, "ok", "Could not determine disk usage.")


def _check_workspace_structure(base: Path) -> DoctorCheck:
    ros_files = list(base.rglob("package.xml"))
    robopilot_yaml = (base / "robopilot.yaml").exists()
    custom_tpl = (base / ".robopilot" / "templates").is_dir()

    details: list[str] = []
    if ros_files:
        details.append(f"{len(ros_files)} ROS package(s) found")
    if robopilot_yaml:
        details.append("robopilot.yaml present")
    if custom_tpl:
        details.append("custom templates directory present")

    if details:
        return DoctorCheck("Workspace structure", True, "ok", "; ".join(details))
    return DoctorCheck("Workspace structure", True, "ok", "No ROS packages or RoboPilot config detected — normal for new projects.")


def _check_ros_detection(base: Path) -> DoctorCheck:
    ros_distro = _detect_ros_env()
    if ros_distro:
        return DoctorCheck("ROS detection", True, "ok", f"ROS distro detected: {ros_distro}")
    has_ros_pkgs = list(base.rglob("package.xml"))
    if has_ros_pkgs:
        return DoctorCheck("ROS detection", True, "ok",
                           f"No ROS sourced, but {len(has_ros_pkgs)} ROS package(s) found. RoboPilot works without ROS.")
    return DoctorCheck("ROS detection", True, "ok", "No ROS distro sourced — RoboPilot works offline.")


def _check_config_integrity(base: Path) -> DoctorCheck:
    lintrc = base / ".robopilot" / "lintrc.yaml"
    issues: list[str] = []
    if lintrc.exists():
        try:
            content = lintrc.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and ":" not in line:
                    issues.append(f"Malformed line in lintrc.yaml: '{line[:50]}'")
        except Exception as exc:
            issues.append(f"Cannot read lintrc.yaml: {exc}")
    if issues:
        return DoctorCheck("Config integrity", False, "warn", "; ".join(issues))
    if lintrc.exists():
        return DoctorCheck("Config integrity", True, "ok", "lintrc.yaml present and valid.")
    return DoctorCheck("Config integrity", True, "ok", "No project config files found.")


def _detect_ros_env() -> str | None:
    import os
    distro = os.environ.get("ROS_DISTRO", "")
    if distro:
        return distro
    # Check common ROS paths
    for p in ("/opt/ros", "C:\\opt\\ros"):
        if Path(p).is_dir():
            return "detected (not sourced)"
    return None
