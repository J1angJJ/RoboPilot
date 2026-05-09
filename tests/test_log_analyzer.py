from robopilot.debugger.log_analyzer import analyze_log


def test_analyzer_detects_cv_bridge_missing() -> None:
    analysis = analyze_log("ModuleNotFoundError: No module named 'cv_bridge'")

    assert analysis.error_type == "cv_bridge missing"
    assert analysis.confidence == "high"
    assert "cv_bridge" in analysis.diagnosis


def test_analyzer_detects_opencv_camera_timeout() -> None:
    analysis = analyze_log("OpenCV camera timeout: cannot read frame")

    assert analysis.error_type == "OpenCV camera read failure"
    assert analysis.confidence == "high"
    assert "camera" in analysis.diagnosis.lower()


def test_analyzer_detects_cuda_out_of_memory() -> None:
    analysis = analyze_log("RuntimeError: CUDA out of memory")

    assert analysis.error_type == "CUDA out of memory"
    assert analysis.confidence == "high"
    assert "GPU" in analysis.possible_causes[0]


def test_analyzer_returns_unknown_fallback() -> None:
    analysis = analyze_log("robot stopped unexpectedly with no more details")

    assert analysis.error_type == "unknown"
    assert analysis.confidence == "low"
    assert analysis.suggested_fixes
