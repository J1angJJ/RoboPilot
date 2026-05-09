import pytest

from robopilot.graph.mermaid_generator import PipelineParseError, generate_mermaid


def test_generate_mermaid_for_normal_linear_pipeline() -> None:
    mermaid = generate_mermaid("camera -> detector -> tracker -> planner -> controller")

    assert mermaid == "\n".join(
        [
            "graph LR",
            "    camera --> detector",
            "    detector --> tracker",
            "    tracker --> planner",
            "    planner --> controller",
        ]
    )


def test_generate_mermaid_with_extra_spaces() -> None:
    mermaid = generate_mermaid("  camera   ->   detector  ->  tracker   ")

    assert mermaid == "\n".join(
        [
            "graph LR",
            "    camera --> detector",
            "    detector --> tracker",
        ]
    )


def test_generate_mermaid_with_underscore_node_names() -> None:
    mermaid = generate_mermaid("camera_node -> detector_node -> planner_node")

    assert "camera_node --> detector_node" in mermaid
    assert "detector_node --> planner_node" in mermaid


def test_generate_mermaid_rejects_empty_input() -> None:
    with pytest.raises(PipelineParseError, match="cannot be empty"):
        generate_mermaid("   ")


def test_generate_mermaid_rejects_single_node() -> None:
    with pytest.raises(PipelineParseError, match="at least two nodes"):
        generate_mermaid("camera")
