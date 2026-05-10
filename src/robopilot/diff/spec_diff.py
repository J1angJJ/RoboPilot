"""Deterministic ProjectSpec diffing."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from robopilot.generator.project_spec import NodeSpec, ProjectSpec, TopicSpec
from robopilot.spec.io import load_spec
from robopilot.spec.validator import validate_spec


@dataclass(frozen=True)
class SpecDiffResult:
    """Structured difference report for two ProjectSpec files."""

    old_spec: str
    new_spec: str
    valid: bool
    changed_fields: dict[str, dict[str, str]]
    added_nodes: tuple[dict[str, str], ...]
    removed_nodes: tuple[dict[str, str], ...]
    added_topics: tuple[dict[str, str], ...]
    removed_topics: tuple[dict[str, str], ...]
    added_config_files: tuple[str, ...]
    removed_config_files: tuple[str, ...]
    added_launch_files: tuple[str, ...]
    removed_launch_files: tuple[str, ...]
    added_notes: tuple[str, ...]
    removed_notes: tuple[str, ...]
    has_changes: bool

    def to_dict(self) -> dict[str, object]:
        """Return a stable JSON-serializable representation."""
        return {
            "old_spec": self.old_spec,
            "new_spec": self.new_spec,
            "valid": self.valid,
            "changed_fields": self.changed_fields,
            "added_nodes": list(self.added_nodes),
            "removed_nodes": list(self.removed_nodes),
            "added_topics": list(self.added_topics),
            "removed_topics": list(self.removed_topics),
            "added_config_files": list(self.added_config_files),
            "removed_config_files": list(self.removed_config_files),
            "added_launch_files": list(self.added_launch_files),
            "removed_launch_files": list(self.removed_launch_files),
            "added_notes": list(self.added_notes),
            "removed_notes": list(self.removed_notes),
            "has_changes": self.has_changes,
        }


def diff_spec_files(old_path: Path, new_path: Path) -> SpecDiffResult:
    """Load, validate, and diff two ProjectSpec files."""
    old_spec = load_spec(old_path)
    new_spec = load_spec(new_path)
    return diff_specs(old_spec, new_spec, old_label=str(old_path), new_label=str(new_path))


def diff_specs(
    old_spec: ProjectSpec,
    new_spec: ProjectSpec,
    *,
    old_label: str = "old",
    new_label: str = "new",
) -> SpecDiffResult:
    """Compare two valid ProjectSpec objects without modifying either one."""
    _validate_or_raise(old_spec, "Old ProjectSpec")
    _validate_or_raise(new_spec, "New ProjectSpec")

    changed_fields = _changed_scalar_fields(old_spec, new_spec)
    added_nodes, removed_nodes = _diff_node_items(old_spec.nodes, new_spec.nodes)
    added_topics, removed_topics = _diff_topic_items(old_spec.topics, new_spec.topics)
    added_config_files, removed_config_files = _diff_scalars(
        old_spec.config_files,
        new_spec.config_files,
    )
    added_launch_files, removed_launch_files = _diff_scalars(
        old_spec.launch_files,
        new_spec.launch_files,
    )
    added_notes, removed_notes = _diff_scalars(old_spec.notes, new_spec.notes)

    has_changes = any(
        (
            changed_fields,
            added_nodes,
            removed_nodes,
            added_topics,
            removed_topics,
            added_config_files,
            removed_config_files,
            added_launch_files,
            removed_launch_files,
            added_notes,
            removed_notes,
        )
    )

    return SpecDiffResult(
        old_spec=old_label,
        new_spec=new_label,
        valid=True,
        changed_fields=changed_fields,
        added_nodes=added_nodes,
        removed_nodes=removed_nodes,
        added_topics=added_topics,
        removed_topics=removed_topics,
        added_config_files=added_config_files,
        removed_config_files=removed_config_files,
        added_launch_files=added_launch_files,
        removed_launch_files=removed_launch_files,
        added_notes=added_notes,
        removed_notes=removed_notes,
        has_changes=has_changes,
    )


def _validate_or_raise(spec: ProjectSpec, label: str) -> None:
    result = validate_spec(spec)
    if not result.is_valid:
        raise ValueError(f"{label} is invalid: " + "; ".join(result.errors))


def _changed_scalar_fields(
    old_spec: ProjectSpec,
    new_spec: ProjectSpec,
) -> dict[str, dict[str, str]]:
    changed: dict[str, dict[str, str]] = {}
    for field_name in ("package_name", "task", "selected_template", "generated_by"):
        old_value = getattr(old_spec, field_name)
        new_value = getattr(new_spec, field_name)
        if old_value != new_value:
            changed[field_name] = {"old": old_value, "new": new_value}
    return changed


def _diff_node_items(
    old_nodes: tuple[NodeSpec, ...],
    new_nodes: tuple[NodeSpec, ...],
) -> tuple[tuple[dict[str, str], ...], tuple[dict[str, str], ...]]:
    old_keys = {_node_key(node) for node in old_nodes}
    new_keys = {_node_key(node) for node in new_nodes}
    added = tuple(asdict(node) for node in new_nodes if _node_key(node) not in old_keys)
    removed = tuple(asdict(node) for node in old_nodes if _node_key(node) not in new_keys)
    return added, removed


def _diff_topic_items(
    old_topics: tuple[TopicSpec, ...],
    new_topics: tuple[TopicSpec, ...],
) -> tuple[tuple[dict[str, str], ...], tuple[dict[str, str], ...]]:
    old_keys = {_topic_key(topic) for topic in old_topics}
    new_keys = {_topic_key(topic) for topic in new_topics}
    added = tuple(asdict(topic) for topic in new_topics if _topic_key(topic) not in old_keys)
    removed = tuple(asdict(topic) for topic in old_topics if _topic_key(topic) not in new_keys)
    return added, removed


def _diff_scalars(
    old_values: tuple[str, ...],
    new_values: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    old_set = set(old_values)
    new_set = set(new_values)
    added = tuple(value for value in new_values if value not in old_set)
    removed = tuple(value for value in old_values if value not in new_set)
    return added, removed


def _node_key(node: NodeSpec) -> tuple[str, str, str, str, str, str]:
    return (
        node.name,
        node.executable,
        node.module,
        node.class_name,
        node.file_name,
        node.description,
    )


def _topic_key(topic: TopicSpec) -> tuple[str, str, str, str]:
    return (
        topic.name,
        topic.direction,
        topic.message_type,
        topic.description,
    )
