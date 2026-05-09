"""Offline Mermaid graph generator for robotics workflow pipelines."""

from __future__ import annotations


class PipelineParseError(ValueError):
    """Raised when a pipeline description cannot be parsed."""


def generate_mermaid(pipeline: str) -> str:
    """Convert an arrow-based pipeline into a Mermaid left-to-right graph."""
    nodes = parse_pipeline(pipeline)
    lines = ["graph LR"]
    lines.extend(
        f"    {source} --> {target}"
        for source, target in zip(nodes, nodes[1:])
    )
    return "\n".join(lines)


def parse_pipeline(pipeline: str) -> list[str]:
    """Parse a pipeline such as 'camera -> detector -> tracker'."""
    if not pipeline or not pipeline.strip():
        raise PipelineParseError("Pipeline input cannot be empty.")

    nodes = [part.strip() for part in pipeline.split("->")]
    if any(not node for node in nodes):
        raise PipelineParseError("Pipeline contains an empty node around an arrow.")

    if len(nodes) < 2:
        raise PipelineParseError("Pipeline must contain at least two nodes.")

    return nodes

