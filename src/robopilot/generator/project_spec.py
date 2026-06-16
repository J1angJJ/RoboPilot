"""Project specification objects for generated ROS-style packages."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NodeSpec:
    """A ROS-style node planned for a generated package."""

    name: str
    executable: str
    module: str
    class_name: str
    file_name: str
    description: str


@dataclass(frozen=True)
class TopicSpec:
    """A ROS-style topic used by a generated package."""

    name: str
    direction: str
    message_type: str
    description: str


@dataclass(frozen=True)
class ProjectSpec:
    """Resolved generation plan for one ROS-style package."""

    package_name: str
    task: str
    selected_template: str
    nodes: tuple[NodeSpec, ...]
    topics: tuple[TopicSpec, ...]
    config_files: tuple[str, ...]
    launch_files: tuple[str, ...]
    generated_by: str
    notes: tuple[str, ...]
    lang: str = "en"

    @property
    def primary_node(self) -> NodeSpec:
        """Return the primary node for templates that generate one node."""
        return self.nodes[0]

    @property
    def node_file_name(self) -> str:
        """Return the primary node file name."""
        return self.primary_node.file_name

    @property
    def executable_name(self) -> str:
        """Return the primary executable name."""
        return self.primary_node.executable

    @property
    def node_name(self) -> str:
        """Return the primary node name."""
        return self.primary_node.name

    @property
    def class_name(self) -> str:
        """Return the primary node class name."""
        return self.primary_node.class_name

    @property
    def description(self) -> str:
        """Return the primary node description."""
        return self.primary_node.description

    @property
    def module_name(self) -> str:
        """Return the Python module name for the selected node file."""
        return self.primary_node.module

