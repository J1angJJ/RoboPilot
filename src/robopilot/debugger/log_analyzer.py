"""Rule-based offline analyzer for common robotics development logs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LogAnalysis:
    """Structured diagnosis for a robotics-related error log."""

    error_type: str
    diagnosis: str
    possible_causes: tuple[str, ...]
    suggested_fixes: tuple[str, ...]
    confidence: str


def analyze_log(log_text: str) -> LogAnalysis:
    """Analyze robotics-related log text using offline rules."""
    normalized = _normalize(log_text)
    if not normalized:
        return _unknown_error()

    if "cv_bridge" in normalized and _contains_any(
        normalized,
        (
            "modulenotfounderror",
            "no module named",
            "importerror",
            "cannot import",
            "missing",
        ),
    ):
        return LogAnalysis(
            error_type="cv_bridge missing",
            diagnosis=(
                "The log suggests that cv_bridge is missing or not visible from "
                "the active Python environment."
            ),
            possible_causes=(
                "ROS environment setup has not been sourced.",
                "cv_bridge is not installed for the ROS or Python environment in use.",
                "The active Python interpreter does not match the ROS workspace.",
            ),
            suggested_fixes=(
                "Check that the intended ROS setup script or workspace setup file is sourced.",
                "Verify that cv_bridge is installed and discoverable in the active environment.",
                "Confirm that the command is using the expected Python interpreter.",
            ),
            confidence="high",
        )

    if "cuda out of memory" in normalized or (
        "outofmemoryerror" in normalized and "cuda" in normalized
    ):
        return LogAnalysis(
            error_type="CUDA out of memory",
            diagnosis=(
                "A GPU workload tried to allocate more CUDA memory than was available."
            ),
            possible_causes=(
                "Model, image batch, or tensor size is too large for the GPU.",
                "Another process is already using GPU memory.",
                "Intermediate tensors are being retained longer than expected.",
            ),
            suggested_fixes=(
                "Reduce batch size, image resolution, or model size.",
                "Close other GPU processes or choose a less busy GPU.",
                "Clear unused tensors and avoid keeping unnecessary computation graphs.",
            ),
            confidence="high",
        )

    if _contains_any(normalized, ("camera timeout", "cannot read frame", "can't read frame")) or (
        "opencv" in normalized and _contains_any(normalized, ("timeout", "read frame", "videocapture"))
    ):
        return LogAnalysis(
            error_type="OpenCV camera read failure",
            diagnosis=(
                "OpenCV could not receive frames from the camera device or stream."
            ),
            possible_causes=(
                "The camera index, device path, or stream URL is incorrect.",
                "The camera is disconnected, busy, or blocked by permissions.",
                "Frame capture timed out because the stream is unavailable or too slow.",
            ),
            suggested_fixes=(
                "Check the camera index or stream URL and test it with a minimal OpenCV script.",
                "Close other applications that may be using the camera.",
                "Verify camera permissions and reconnect or restart the device.",
            ),
            confidence="high",
        )

    if "colcon" in normalized and _contains_any(
        normalized,
        ("failed", "failed packages", "build failed", "exited with code"),
    ):
        return LogAnalysis(
            error_type="colcon build failed",
            diagnosis="A colcon workspace build did not complete successfully.",
            possible_causes=(
                "A package failed to compile or install.",
                "A dependency is missing from the workspace or environment.",
                "Generated build artifacts are stale or inconsistent.",
            ),
            suggested_fixes=(
                "Read the first package-specific error above the colcon summary.",
                "Install missing dependencies or source the correct workspace setup file.",
                "Clean the affected package build directory and rebuild.",
            ),
            confidence="medium",
        )

    if _contains_any(
        normalized,
        ("package not found", "could not find package", "unknown package"),
    ) or ("package" in normalized and "not found" in normalized):
        return LogAnalysis(
            error_type="package not found",
            diagnosis="A required package could not be located by the current toolchain.",
            possible_causes=(
                "The package is not installed or not present in the workspace.",
                "The environment has not been sourced.",
                "The package name is misspelled or differs from the import name.",
            ),
            suggested_fixes=(
                "Check the package name and workspace layout.",
                "Install the missing package or add it to the workspace.",
                "Source the relevant setup file before running the command.",
            ),
            confidence="medium",
        )

    if _contains_any(normalized, ("permission denied", "access is denied", "errno 13")):
        return LogAnalysis(
            error_type="permission denied",
            diagnosis="The process was blocked from reading, writing, or opening a resource.",
            possible_causes=(
                "The current user lacks file, device, or serial port permissions.",
                "Another process owns the target file or device.",
                "The command is writing to a protected system path.",
            ),
            suggested_fixes=(
                "Check file, device, or serial port permissions.",
                "Close processes that may be holding the resource.",
                "Use a writable project directory for generated files and logs.",
            ),
            confidence="medium",
        )

    if _contains_any(normalized, ("modulenotfounderror", "no module named")):
        return LogAnalysis(
            error_type="ModuleNotFoundError",
            diagnosis="Python could not import a required module.",
            possible_causes=(
                "The dependency is not installed in the active environment.",
                "The wrong virtual environment or Python interpreter is active.",
                "The package is local but not on PYTHONPATH or not installed in editable mode.",
            ),
            suggested_fixes=(
                "Install the missing dependency in the active environment.",
                "Verify the Python interpreter and virtual environment.",
                "For local packages, run an editable install or set PYTHONPATH.",
            ),
            confidence="medium",
        )

    return _unknown_error()


def _normalize(log_text: str) -> str:
    return " ".join(log_text.strip().lower().split())


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern in text for pattern in patterns)


def _unknown_error() -> LogAnalysis:
    return LogAnalysis(
        error_type="unknown",
        diagnosis=(
            "RoboPilot could not confidently match this log to a known offline rule."
        ),
        possible_causes=(
            "The key error line may be missing from the provided log.",
            "The failure may be project-specific or outside the current MVP rule set.",
            "The log may contain multiple overlapping errors.",
        ),
        suggested_fixes=(
            "Look for the first traceback line or the first explicit error message.",
            "Rerun the command with verbose logging if available.",
            "Check environment setup, dependency installation, and file permissions.",
        ),
        confidence="low",
    )
