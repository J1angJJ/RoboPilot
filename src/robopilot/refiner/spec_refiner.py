"""Deterministic rule-based ProjectSpec refinement."""

from __future__ import annotations

import re
from dataclasses import replace

from robopilot.generator.project_spec import NodeSpec, ProjectSpec, TopicSpec
from robopilot.generator.task_classifier import PERCEPTION_PIPELINE
from robopilot.spec.validator import validate_spec


TRACKER_NODE = NodeSpec(
    name="tracker_node",
    executable="tracker_node",
    module="tracker_node",
    class_name="TrackerNode",
    file_name="tracker_node.py",
    description="ROS-style tracker node added by refinement.",
)
CAMERA_NODE = NodeSpec(
    name="camera_node",
    executable="camera_node",
    module="camera_node",
    class_name="CameraNode",
    file_name="camera_node.py",
    description="ROS-style camera node added by refinement.",
)
CONTROLLER_NODE = NodeSpec(
    name="controller_node",
    executable="controller_node",
    module="controller_node",
    class_name="ControllerNode",
    file_name="controller_node.py",
    description="ROS-style controller node added by refinement.",
)


def refine_spec(spec: ProjectSpec, instruction: str, *, planner: str = "rule") -> ProjectSpec:
    """Refine a ProjectSpec using deterministic local rules."""
    if planner.strip().lower() != "rule":
        raise ValueError(
            "LLM-assisted refinement is not implemented yet. Use --planner rule."
        )

    validation = validate_spec(spec)
    if not validation.is_valid:
        raise ValueError("Input ProjectSpec is invalid: " + "; ".join(validation.errors))

    clean_instruction = instruction.strip()
    if not clean_instruction:
        raise ValueError("Refinement instruction cannot be empty.")

    refined = _apply_rule_based_refinement(spec, clean_instruction)
    refined_validation = validate_spec(refined)
    if not refined_validation.is_valid:
        raise ValueError(
            "Refined ProjectSpec is invalid: " + "; ".join(refined_validation.errors)
        )
    return refined


def _apply_rule_based_refinement(spec: ProjectSpec, instruction: str) -> ProjectSpec:
    normalized = " ".join(instruction.lower().split())
    nodes = spec.nodes
    notes = spec.notes
    topics = spec.topics
    selected_template = spec.selected_template
    changed = False

    if "tracker" in normalized:
        nodes, note, added = _add_node_after(
            nodes,
            TRACKER_NODE,
            after_node_name="detector_node",
        )
        notes = _append_unique(notes, note)
        selected_template = PERCEPTION_PIPELINE
        changed = changed or added

    if "camera" in normalized:
        nodes, note, added = _add_node(nodes, CAMERA_NODE)
        notes = _append_unique(notes, note)
        changed = changed or added

    if "controller" in normalized or "control" in normalized:
        nodes, note, added = _add_node(nodes, CONTROLLER_NODE)
        notes = _append_unique(notes, note)
        changed = changed or added

    extracted_topic = _extract_topic(instruction)
    if extracted_topic is not None:
        topics, note, added = _add_topic(topics, extracted_topic)
        notes = _append_unique(notes, note)
        changed = changed or added

    if not changed and not any(term in normalized for term in ("tracker", "camera", "controller", "control", "topic")):
        notes = _append_unique(
            notes,
            f"Unsupported refinement instruction recorded without structural changes: {instruction}",
        )

    return replace(
        spec,
        selected_template=selected_template,
        nodes=nodes,
        topics=topics,
        notes=notes,
    )


def _add_node(nodes: tuple[NodeSpec, ...], node: NodeSpec) -> tuple[tuple[NodeSpec, ...], str, bool]:
    if any(existing.name == node.name for existing in nodes):
        return nodes, f"{node.name} already exists; refinement did not add a duplicate.", False
    return (
        nodes + (node,),
        f"{node.name} was added by refinement.",
        True,
    )


def _add_node_after(
    nodes: tuple[NodeSpec, ...],
    node: NodeSpec,
    *,
    after_node_name: str,
) -> tuple[tuple[NodeSpec, ...], str, bool]:
    if any(existing.name == node.name for existing in nodes):
        return nodes, f"{node.name} already exists; refinement did not add a duplicate.", False

    refined_nodes: list[NodeSpec] = []
    inserted = False
    for existing in nodes:
        refined_nodes.append(existing)
        if existing.name == after_node_name:
            refined_nodes.append(node)
            inserted = True
    if not inserted:
        refined_nodes.append(node)
    return (
        tuple(refined_nodes),
        f"{node.name} was added by refinement.",
        True,
    )


def _add_topic(
    topics: tuple[TopicSpec, ...],
    topic_name: str,
) -> tuple[tuple[TopicSpec, ...], str, bool]:
    if any(topic.name == topic_name for topic in topics):
        return topics, f"{topic_name} already exists; refinement did not add a duplicate topic.", False
    topic = TopicSpec(
        name=topic_name,
        direction="unspecified",
        message_type="std_msgs/String",
        description="Topic added by refinement instruction.",
    )
    return topics + (topic,), f"{topic_name} topic was added by refinement.", True


def _extract_topic(instruction: str) -> str | None:
    match = re.search(r"(?:topic|publish(?:ing)? to|subscribe(?:ing)? to)\s+([/][A-Za-z0-9_/-]+)", instruction, re.IGNORECASE)
    if match:
        return match.group(1).rstrip(".,;:")
    return None


def _append_unique(values: tuple[str, ...], value: str) -> tuple[str, ...]:
    if value in values:
        return values
    return values + (value,)
