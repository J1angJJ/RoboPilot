"""User-configurable templates without editing RoboPilot source (v2.1.0 M8).

Custom templates are YAML files stored under .robopilot/templates/<name>/template.yaml.
They can extend built-in templates via the ``extends`` field, overriding select fields
while inheriting the rest.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from robopilot.generator.project_spec import NodeSpec, ProjectSpec, TopicSpec
from robopilot.generator.template_registry import (
    TEMPLATE_REGISTRY,
    TemplateDefinition,
    build_project_spec,
)

TEMPLATES_DIR = ".robopilot/templates"
TEMPLATE_FILE = "template.yaml"

REQUIRED_FIELDS = {"template_name", "node"}
NODE_FIELDS = {"file_name", "executable_name", "node_name", "class_name"}


@dataclass(frozen=True)
class CustomTemplate:
    """A user-defined template loaded from disk."""

    name: str
    extends: str | None
    definition: TemplateDefinition

    @property
    def node_file_name(self) -> str:
        return self.definition.node_file_name

    @property
    def executable_name(self) -> str:
        return self.definition.executable_name

    @property
    def node_name(self) -> str:
        return self.definition.node_name

    @property
    def class_name(self) -> str:
        return self.definition.class_name

    @property
    def description(self) -> str:
        return self.definition.description


@dataclass(frozen=True)
class TemplateValidationResult:
    """Result of validating a custom template."""

    template_name: str
    template_path: str
    is_valid: bool
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "template_name": self.template_name,
            "template_path": self.template_path,
            "is_valid": self.is_valid,
            "errors": list(self.errors),
        }


# ---------------------------------------------------------------------------
# Template init
# ---------------------------------------------------------------------------


def init_templates_dir(root: Path | None = None) -> Path:
    """Scaffold a .robopilot/templates/ directory with a sample custom template."""
    base = Path(root or Path.cwd()).resolve()
    templates_dir = base / TEMPLATES_DIR
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Create README
    (templates_dir / "README.md").write_text(_README_CONTENT, encoding="utf-8")

    # Create example template
    example_dir = templates_dir / "my_custom_node"
    example_dir.mkdir(parents=True, exist_ok=True)
    if not (example_dir / TEMPLATE_FILE).exists():
        (example_dir / TEMPLATE_FILE).write_text(_EXAMPLE_TEMPLATE, encoding="utf-8")

    return templates_dir


_README_CONTENT = """# Custom Templates

Place your custom templates here. Each template lives in its own directory
with a `template.yaml` file.

## Directory structure

    .robopilot/templates/
    ├── README.md
    └── my_custom_node/
        └── template.yaml

## Usage

    robopilot plan --template my_custom_node --name my_project --task "..."
    robopilot template-validate --path .robopilot/templates/my_custom_node
    robopilot template-init

## Template format

See `my_custom_node/template.yaml` for a complete example.
The `extends` field is optional; when set, the template inherits from the
named built-in template (e.g., `generic_node`, `object_detection`, `slam`).
"""

_EXAMPLE_TEMPLATE = """# Custom template: my_custom_node
# This example extends the generic_node built-in template.
# Remove or change 'extends' to inherit from a different base.

template_name: my_custom_node
extends: generic_node
description: "My custom ROS-style node template."

node:
  file_name: my_node.py
  executable_name: my_node
  node_name: my_custom_node
  class_name: MyCustomNode
  description: "Custom node for my project."

topics:
  - name: /my_input
    direction: subscribe
    message_type: std_msgs/String
    description: "Custom input topic."
  - name: /my_output
    direction: publish
    message_type: std_msgs/String
    description: "Custom output topic."

config_files:
  - config/my_params.yaml

launch_files: []

notes:
  - "This is a user-defined custom template."
  - "It inherits defaults from generic_node where not overridden."
"""


# ---------------------------------------------------------------------------
# Template loading
# ---------------------------------------------------------------------------


def list_custom_templates(root: Path | None = None) -> dict[str, CustomTemplate]:
    """Discover and load all custom templates from the templates directory."""
    base = Path(root or Path.cwd()).resolve()
    templates_dir = base / TEMPLATES_DIR
    if not templates_dir.is_dir():
        return {}

    result: dict[str, CustomTemplate] = {}
    for item in sorted(templates_dir.iterdir()):
        if not item.is_dir() or item.name.startswith("."):
            continue
        tpl_file = item / TEMPLATE_FILE
        if not tpl_file.is_file():
            continue
        try:
            ct = _load_template(tpl_file)
            result[ct.name] = ct
        except Exception:
            continue
    return result


def load_custom_template(name: str, root: Path | None = None) -> CustomTemplate | None:
    """Load a single custom template by name."""
    base = Path(root or Path.cwd()).resolve()
    tpl_file = base / TEMPLATES_DIR / name / TEMPLATE_FILE
    if not tpl_file.is_file():
        return None
    try:
        return _load_template(tpl_file)
    except Exception:
        return None


def _load_template(path: Path) -> CustomTemplate:
    content = path.read_text(encoding="utf-8")
    data = _parse_template_yaml(content)

    topics = _parse_topics(data.get("topics", ()))
    notes = tuple(str(n) for n in _list_of(data.get("notes", ())))

    node_data = _dict_of(data.get("node", {}))
    template_name = str(data.get("template_name", path.parent.name))
    extends = str(data["extends"]) if data.get("extends") else None

    defn = TemplateDefinition(
        template_type=template_name,
        node_file_name=str(node_data.get("file_name", f"{template_name}_node.py")),
        executable_name=str(node_data.get("executable_name", f"{template_name}_node")),
        node_name=str(node_data.get("node_name", f"{template_name}_node")),
        class_name=str(node_data.get("class_name", f"{template_name.capitalize()}Node")),
        description=str(data.get("description", str(node_data.get("description", f"Custom {template_name} node.")))),
        topics=topics,
        notes=notes,
    )

    return CustomTemplate(template_name, extends, defn)


# ---------------------------------------------------------------------------
# Simple YAML parser for templates (handles nested dicts unlike spec_from_yaml)
# ---------------------------------------------------------------------------


def _parse_template_yaml(content: str) -> dict[str, object]:
    """Parse a template YAML file supporting nested dicts and lists."""
    lines = [(len(line) - len(line.lstrip(" ")), line.strip())
             for line in content.splitlines()
             if line.strip() and not line.strip().startswith("#")]

    result: dict[str, object] = {}
    i = 0
    while i < len(lines):
        indent, stripped = lines[i]
        if indent > 0:
            i += 1
            continue
        if ":" not in stripped:
            i += 1
            continue
        key, value = _split_yaml(stripped)
        if value:
            result[key] = _unquote_yaml(value)
            i += 1
        else:
            # Look ahead: is the next line indented?
            i += 1
            if i < len(lines) and lines[i][0] > 0:
                sub_indent = lines[i][0]
                if i < len(lines) and lines[i][1].startswith("- "):
                    # List section — items may be scalars or dicts spanning multiple lines
                    items: list[object] = []
                    current_dict: dict[str, str] | None = None
                    while i < len(lines) and lines[i][0] >= sub_indent:
                        item_indent, item_stripped = lines[i]
                        if item_stripped.startswith("- "):
                            current_dict = None
                            item_val = item_stripped[2:]
                            if ":" in item_val:
                                # Start of a dict item
                                dk, dv = _split_yaml(item_val)
                                current_dict = {dk: _unquote_yaml(dv)} if dv else {dk: ""}
                                items.append(current_dict)
                            else:
                                items.append(_unquote_yaml(item_val))
                        elif item_indent > sub_indent and current_dict is not None:
                            # Continuation of the current dict item
                            dk, dv = _split_yaml(item_stripped)
                            current_dict[dk] = _unquote_yaml(dv)
                        i += 1
                    result[key] = items
                else:
                    # Mapping section
                    mapping: dict[str, object] = {}
                    while i < len(lines) and lines[i][0] >= sub_indent:
                        mi, ms = lines[i]
                        mk, mv = _split_yaml(ms)
                        if mv:
                            mapping[mk] = _unquote_yaml(mv)
                        else:
                            # Nested list under mapping
                            type_list: list[str] = []
                            i += 1
                            while i < len(lines) and lines[i][0] > mi:
                                _, ls = lines[i]
                                if ls.startswith("- "):
                                    type_list.append(_unquote_yaml(ls[2:]))
                                i += 1
                            mapping[mk] = type_list
                            continue
                        i += 1
                    result[key] = mapping
    return result


# ---------------------------------------------------------------------------
# Template validation
# ---------------------------------------------------------------------------


def validate_custom_template(path: Path) -> TemplateValidationResult:
    """Validate a custom template directory."""
    tpl_path = Path(path)
    name = tpl_path.name

    if not tpl_path.is_dir():
        return TemplateValidationResult(name, str(tpl_path), False, ("Template path is not a directory.",))

    tpl_file = tpl_path / TEMPLATE_FILE
    if not tpl_file.is_file():
        return TemplateValidationResult(name, str(tpl_path), False, (f"Missing {TEMPLATE_FILE} in template directory.",))

    errors: list[str] = []
    try:
        content = tpl_file.read_text(encoding="utf-8")
        data = _parse_template_yaml(content)
    except Exception as exc:
        return TemplateValidationResult(name, str(tpl_path), False, (f"Cannot parse template: {exc}",))

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")

    node_data = _dict_of(data.get("node", {}))
    for field in NODE_FIELDS:
        if field not in node_data:
            errors.append(f"Missing node field: '{field}'")

    if data.get("extends"):
        extends_name = str(data["extends"])
        if extends_name not in TEMPLATE_REGISTRY:
            # Check if it's a custom template name
            tpls = list_custom_templates(tpl_path.parent.parent.parent)
            if extends_name not in tpls:
                errors.append(f"Unknown base template: '{extends_name}'")

    topics = data.get("topics", [])
    if isinstance(topics, list):
        for i, t in enumerate(topics):
            if isinstance(t, dict):
                for tf in ("name", "direction", "message_type"):
                    if tf not in t:
                        errors.append(f"Topic {i} missing field: '{tf}'")

    return TemplateValidationResult(
        name, str(tpl_path),
        is_valid=not errors,
        errors=tuple(errors),
    )


# ---------------------------------------------------------------------------
# Template → ProjectSpec integration
# ---------------------------------------------------------------------------


def build_project_spec_from_custom(
    template_name: str,
    task: str,
    root: Path | None = None,
    *,
    package_name: str | None = None,
) -> ProjectSpec | None:
    """Build a ProjectSpec from a custom template, falling back to built-in."""
    ct = load_custom_template(template_name, root)
    if ct is None:
        return None

    pkg_name = package_name or template_name

    defn = ct.definition
    # Start from the base template if extending
    if ct.extends and ct.extends in TEMPLATE_REGISTRY:
        base = build_project_spec(
            package_name=pkg_name,
            task=task,
            selected_template=ct.extends,
        )
        return ProjectSpec(
            package_name=pkg_name,
            task=task,
            selected_template=ct.name,
            nodes=(
                NodeSpec(
                    name=ct.node_name,
                    executable=ct.executable_name,
                    module=ct.node_file_name.removesuffix(".py"),
                    class_name=ct.class_name,
                    file_name=ct.node_file_name,
                    description=ct.description,
                ),
            ),
            topics=defn.topics if defn.topics else base.topics,
            config_files=base.config_files,
            launch_files=base.launch_files,
            generated_by=f"RoboPilot (custom template: {ct.name})",
            notes=defn.notes if defn.notes else base.notes,
        )

    # No base: build standalone from custom definition
    return ProjectSpec(
        package_name=pkg_name,
        task=task,
        selected_template=ct.name,
        nodes=(
            NodeSpec(
                name=defn.node_name,
                executable=defn.executable_name,
                module=defn.node_file_name.removesuffix(".py"),
                class_name=defn.class_name,
                file_name=defn.node_file_name,
                description=defn.description,
            ),
        ),
        topics=defn.topics,
        config_files=("config/params.yaml",),
        launch_files=(f"launch/{pkg_name}.launch.py",),
        generated_by=f"RoboPilot (custom template: {ct.name})",
        notes=defn.notes,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_topics(data: object) -> tuple[TopicSpec, ...]:
    if not isinstance(data, (list, tuple)):
        return ()
    items: list[TopicSpec] = []
    for item in data:
        if isinstance(item, dict):
            items.append(TopicSpec(
                name=str(item.get("name", "")),
                direction=str(item.get("direction", "subscribe")),
                message_type=str(item.get("message_type", "std_msgs/String")),
                description=str(item.get("description", "")),
            ))
    return tuple(items)


def _list_of(data: object) -> tuple[str, ...]:
    if isinstance(data, (list, tuple)):
        return tuple(str(v) for v in data)
    if isinstance(data, str):
        return (data,)
    return ()


def _dict_of(data: object) -> dict[str, object]:
    if isinstance(data, dict):
        return data
    return {}


def _split_yaml(line: str) -> tuple[str, str]:
    if ":" not in line:
        return line, ""
    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def _unquote_yaml(value: str) -> str:
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
        value = value[1:-1]
    return value
