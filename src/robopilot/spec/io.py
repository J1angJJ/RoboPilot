"""Read and write RoboPilot ProjectSpec files.

This module intentionally supports only RoboPilot's small YAML schema. It avoids
adding a YAML dependency while keeping generated spec files readable.
"""

from __future__ import annotations

from pathlib import Path

from robopilot.generator.project_spec import NodeSpec, ProjectSpec, TopicSpec


LIST_SECTIONS = {"nodes", "topics", "config_files", "launch_files", "notes"}


def spec_to_yaml(spec: ProjectSpec) -> str:
    """Serialize a ProjectSpec to RoboPilot's readable YAML subset."""
    lines = [
        f"package_name: {spec.package_name}",
        f'task: "{_quote(spec.task)}"',
        f"selected_template: {spec.selected_template}",
        f"generated_by: {spec.generated_by}",
        "nodes:",
    ]
    for node in spec.nodes:
        lines.extend(
            [
                f"  - name: {node.name}",
                f"    executable: {node.executable}",
                f"    module: {node.module}",
                f"    class_name: {node.class_name}",
                f"    file_name: {node.file_name}",
                f'    description: "{_quote(node.description)}"',
            ]
        )

    lines.append("topics:")
    for topic in spec.topics:
        lines.extend(
            [
                f"  - name: {topic.name}",
                f"    direction: {topic.direction}",
                f"    message_type: {topic.message_type}",
                f'    description: "{_quote(topic.description)}"',
            ]
        )

    lines.append("config_files:")
    lines.extend(f"  - {path}" for path in spec.config_files)
    lines.append("launch_files:")
    lines.extend(f"  - {path}" for path in spec.launch_files)
    lines.append("notes:")
    lines.extend(f'  - "{_quote(note)}"' for note in spec.notes)
    return "\n".join(lines) + "\n"


def write_spec(spec: ProjectSpec, path: Path) -> None:
    """Write a ProjectSpec to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(spec_to_yaml(spec), encoding="utf-8")


def load_spec(path: Path) -> ProjectSpec:
    """Load a ProjectSpec from a RoboPilot YAML file."""
    return spec_from_yaml(path.read_text(encoding="utf-8"))


def spec_from_yaml(content: str) -> ProjectSpec:
    """Parse RoboPilot's limited YAML subset into a ProjectSpec."""
    data: dict[str, object] = {}
    current_section: str | None = None
    current_item: dict[str, str] | None = None

    for raw_line in content.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if not raw_line.startswith(" "):
            key, value = _split_key_value(raw_line)
            if value == "" and key in LIST_SECTIONS:
                current_section = key
                data[current_section] = []
                current_item = None
            else:
                current_section = None
                current_item = None
                data[key] = _unquote(value)
            continue

        if current_section is None:
            raise ValueError(f"Unexpected indented line outside a section: {raw_line}")

        section = data[current_section]
        if not isinstance(section, list):
            raise ValueError(f"Section is not a list: {current_section}")

        stripped = raw_line.strip()
        if stripped.startswith("- "):
            item = stripped[2:]
            if ":" in item:
                key, value = _split_key_value(item)
                current_item = {key: _unquote(value)}
                section.append(current_item)
            else:
                current_item = None
                section.append(_unquote(item))
            continue

        if current_item is None:
            raise ValueError(f"Unexpected mapping line without list item: {raw_line}")
        key, value = _split_key_value(stripped)
        current_item[key] = _unquote(value)

    return _project_spec_from_data(data)


def _project_spec_from_data(data: dict[str, object]) -> ProjectSpec:
    nodes = tuple(
        NodeSpec(
            name=str(item.get("name", "")),
            executable=str(item.get("executable", "")),
            module=str(item.get("module", "")),
            class_name=str(item.get("class_name", "")),
            file_name=str(item.get("file_name", "")),
            description=str(item.get("description", "")),
        )
        for item in _list_of_dicts(data.get("nodes", []))
    )
    topics = tuple(
        TopicSpec(
            name=str(item.get("name", "")),
            direction=str(item.get("direction", "")),
            message_type=str(item.get("message_type", "")),
            description=str(item.get("description", "")),
        )
        for item in _list_of_dicts(data.get("topics", []))
    )
    return ProjectSpec(
        package_name=str(data.get("package_name", "")),
        task=str(data.get("task", "")),
        selected_template=str(data.get("selected_template", "")),
        nodes=nodes,
        topics=topics,
        config_files=tuple(str(item) for item in _list_of_scalars(data.get("config_files", []))),
        launch_files=tuple(str(item) for item in _list_of_scalars(data.get("launch_files", []))),
        generated_by=str(data.get("generated_by", "")),
        notes=tuple(str(item) for item in _list_of_scalars(data.get("notes", []))),
    )


def _split_key_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"Expected key/value line: {line}")
    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def _quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    return value.replace('\\"', '"').replace("\\\\", "\\")


def _list_of_dicts(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _list_of_scalars(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if not isinstance(item, dict)]
