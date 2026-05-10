"""Project specification objects for generated ROS-style packages."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectSpec:
    """Resolved generation plan for one ROS-style package."""

    package_name: str
    task: str
    selected_template: str
    node_file_name: str
    executable_name: str
    node_name: str
    class_name: str
    description: str
    notes: tuple[str, ...]

    @property
    def module_name(self) -> str:
        """Return the Python module name for the selected node file."""
        return self.node_file_name.removesuffix(".py")

