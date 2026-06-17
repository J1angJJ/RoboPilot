"""Conservative ROS2 migration scaffold generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from robopilot.migration.scaffold_preview import (
    MigrationScaffoldPreviewResult,
    ScaffoldFile,
    preview_migration_scaffold,
)


SAFETY_NOTE = (
    "This migration scaffold was generated from a validated migration plan. "
    "RoboPilot generated scaffold placeholders only; it did not modify the "
    "original ROS1 source project, modify the migration plan, require ROS, "
    "require ROS2, run catkin_make, run colcon, execute launch files, execute "
    "code, import user project modules, or validate runtime behavior."
)


@dataclass(frozen=True)
class MigrationScaffoldGenerationResult:
    """Result for a conservative migration scaffold generation attempt."""

    plan_path: str
    output_path: str
    source_path: str
    target: str
    package_name: str
    target_style: str
    dry_run: bool
    files_to_create: tuple[str, ...]
    files_created: tuple[str, ...]
    conflicts: tuple[str, ...]
    skipped_files: tuple[str, ...]
    manual_migration_required: tuple[str, ...]
    interface_files_to_review: tuple[str, ...]
    dependency_items_to_review: tuple[str, ...]
    risks: tuple[str, ...]
    suggested_next_steps: tuple[str, ...]
    safety_note: str

    def to_dict(self) -> dict[str, object]:
        """Return stable JSON-ready generation data."""
        return {
            "plan_path": self.plan_path,
            "output_path": self.output_path,
            "source_path": self.source_path,
            "target": self.target,
            "package_name": self.package_name,
            "target_style": self.target_style,
            "dry_run": self.dry_run,
            "files_to_create": list(self.files_to_create),
            "files_created": list(self.files_created),
            "conflicts": list(self.conflicts),
            "skipped_files": list(self.skipped_files),
            "manual_migration_required": list(self.manual_migration_required),
            "interface_files_to_review": list(self.interface_files_to_review),
            "dependency_items_to_review": list(self.dependency_items_to_review),
            "risks": list(self.risks),
            "suggested_next_steps": list(self.suggested_next_steps),
            "safety_note": self.safety_note,
        }


def generate_migration_scaffold(
    plan_path: Path,
    output_path: Path,
    *,
    overwrite: bool = False,
) -> MigrationScaffoldGenerationResult:
    """Generate a conservative ROS2 scaffold from a migration plan.

    The original ROS1 project and migration plan are never modified. Existing
    scaffold files are not overwritten unless ``overwrite`` is explicitly true.
    """
    preview = preview_migration_scaffold(plan_path)
    files = render_migration_scaffold_files(preview)
    file_paths = tuple(sorted(files))
    output_root = Path(output_path)
    conflicts = list(_blocking_preview_conflicts(preview))

    resolved_targets: dict[str, Path] = {}
    try:
        output_root_resolved = output_root.resolve(strict=False)
        for relative_path in file_paths:
            resolved_targets[relative_path] = _safe_output_path(output_root_resolved, relative_path)
    except ValueError as exc:
        conflicts.append(str(exc))

    if output_root.exists() and not output_root.is_dir():
        conflicts.append(f"output path is not a directory: {output_root}")

    for relative_path, target in resolved_targets.items():
        if target.exists() and not overwrite:
            conflicts.append(f"file already exists: {relative_path}")

    normalized_conflicts = _sorted_unique(conflicts)
    if normalized_conflicts:
        return _result(
            preview=preview,
            output_path=output_root,
            files_to_create=file_paths,
            files_created=(),
            conflicts=normalized_conflicts,
            skipped_files=file_paths,
        )

    for relative_path in file_paths:
        target = resolved_targets[relative_path]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(files[relative_path], encoding="utf-8")

    return _result(
        preview=preview,
        output_path=output_root,
        files_to_create=file_paths,
        files_created=file_paths,
        conflicts=(),
        skipped_files=(),
    )


def _result(
    *,
    preview: MigrationScaffoldPreviewResult,
    output_path: Path,
    files_to_create: tuple[str, ...],
    files_created: tuple[str, ...],
    conflicts: tuple[str, ...],
    skipped_files: tuple[str, ...],
) -> MigrationScaffoldGenerationResult:
    suggested_next_steps = [
        "Review generated placeholders before manually migrating source logic.",
        "Review MIGRATION_NOTES.md before running any ROS2 build or runtime checks.",
        "Run robopilot migrate-scaffold-validate --plan <migration_plan.yaml> --scaffold <ros2_scaffold>.",
        "Run static inspection and dependency analysis on the scaffold after manual edits.",
    ]
    if conflicts:
        suggested_next_steps.insert(0, "Resolve scaffold generation conflicts before trying again. Existing files are not overwritten unless --overwrite is explicit.")
    return MigrationScaffoldGenerationResult(
        plan_path=preview.plan_path,
        output_path=str(output_path),
        source_path=preview.source_path,
        target=preview.target,
        package_name=preview.package_name,
        target_style=preview.target_style,
        dry_run=False,
        files_to_create=files_to_create,
        files_created=files_created,
        conflicts=conflicts,
        skipped_files=skipped_files,
        manual_migration_required=preview.files_requiring_manual_migration,
        interface_files_to_review=preview.interface_files_to_review,
        dependency_items_to_review=preview.dependency_items_to_review,
        risks=preview.risks,
        suggested_next_steps=tuple(suggested_next_steps),
        safety_note=SAFETY_NOTE,
    )


def render_migration_scaffold_files(preview: MigrationScaffoldPreviewResult) -> dict[str, str]:
    """Render expected scaffold files to memory without writing them."""
    files: dict[str, str] = {}
    items = _generation_items(preview)
    for item in items:
        files[item.path] = _render_item(preview, item)
    files["MIGRATION_NOTES.md"] = _render_migration_notes(preview, tuple(sorted(files)))
    return files


def _generation_items(preview: MigrationScaffoldPreviewResult) -> tuple[ScaffoldFile, ...]:
    if preview.target_style == "manual_review_required":
        return ()

    items: list[ScaffoldFile] = []
    if preview.target_style == "mixed_review_required":
        for item in preview.scaffold_files_to_create:
            if item.path == "package.xml":
                items.append(item)
        for item in preview.placeholder_files:
            if item.path.startswith("launch/") or item.path == "config/params.yaml":
                items.append(item)
        return _dedupe_items(items)

    items.extend(preview.scaffold_files_to_create)
    items.extend(preview.placeholder_files)
    return _dedupe_items(items)


def _render_item(preview: MigrationScaffoldPreviewResult, item: ScaffoldFile) -> str:
    path = item.path
    if path == "package.xml":
        return _render_package_xml(preview)
    if path == "setup.py":
        return _render_setup_py(preview.package_name)
    if path == "setup.cfg":
        return _render_setup_cfg()
    if path.startswith("resource/"):
        return ""
    if path.endswith("__init__.py"):
        return '"""ROS2 scaffold package generated by RoboPilot."""\n'
    if path == "CMakeLists.txt":
        return _render_cmakelists(preview)
    if path.endswith(".py") and path.startswith("launch/"):
        return _render_launch_placeholder(preview, item)
    if path.endswith(".py"):
        return _render_python_node_placeholder(preview, item)
    if path.endswith(".cpp"):
        return _render_cpp_node_placeholder(preview, item)
    if path == "config/params.yaml":
        return _render_params_yaml(preview)
    return _render_generic_placeholder(preview, item)


def _render_package_xml(preview: MigrationScaffoldPreviewResult) -> str:
    package_name = _safe_name(preview.package_name)
    lines = [
        '<?xml version="1.0"?>',
        '<package format="3">',
        f"  <name>{package_name}</name>",
        "  <version>0.0.0</version>",
        "  <description>ROS2 migration scaffold generated by RoboPilot.</description>",
        "  <maintainer email=\"todo@example.com\">TODO Maintainer</maintainer>",
        "  <license>TODO</license>",
        "",
        "  <!-- Generated by RoboPilot migration scaffold. -->",
        "  <!-- This is not an automatic migration. Review dependencies manually. -->",
    ]
    if preview.target_style == "ament_cmake":
        lines.append("  <buildtool_depend>ament_cmake</buildtool_depend>")
    if preview.target_style == "ament_python":
        lines.extend(["", "  <export>", "    <build_type>ament_python</build_type>", "  </export>"])
    lines.append("</package>")
    return "\n".join(lines) + "\n"


def _render_setup_py(package_name: str) -> str:
    name = _safe_name(package_name)
    return f'''"""ROS2 ament_python scaffold generated by RoboPilot."""

from setuptools import find_packages, setup

package_name = "{name}"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="TODO",
    maintainer_email="todo@example.com",
    description="ROS2 migration scaffold generated by RoboPilot.",
    license="TODO",
    tests_require=["pytest"],
    entry_points={{
        "console_scripts": [
            # TODO: add migrated node entry points after manual review.
        ],
    }},
)
'''


def _render_setup_cfg() -> str:
    return """[develop]
script_dir=$base/lib/$base
[install]
install_scripts=$base/lib/$base
"""


def _render_cmakelists(preview: MigrationScaffoldPreviewResult) -> str:
    package_name = _safe_name(preview.package_name)
    return f"""cmake_minimum_required(VERSION 3.8)
project({package_name})

# Generated by RoboPilot migration scaffold.
# This is not an automatic migration. Review original ROS1 CMake logic manually.

find_package(ament_cmake REQUIRED)

# TODO: migrate ROS1 catkin dependencies to ROS2 find_package(...) calls.
# TODO: migrate publishers/subscribers, parameters, logging, time, and spin behavior in source files.
# TODO: review QoS behavior for ROS2.
# TODO: add install rules after manual migration.

ament_package()
"""


def _render_python_node_placeholder(preview: MigrationScaffoldPreviewResult, item: ScaffoldFile) -> str:
    return f'''"""ROS2 node placeholder generated by RoboPilot migration scaffold.

This is not an automatic migration. Every file requires manual review.
Original ROS1 source: {item.source_basis}
"""

from __future__ import annotations

# ROS1 → ROS2 API migration cheat sheet:
#   rospy.init_node(name)         → rclpy.init() + Node.__init__(name)
#   rospy.Publisher(topic, Type)  → self.create_publisher(Type, topic, qos)
#   rospy.Subscriber(topic, Type) → self.create_subscription(Type, topic, cb, qos)
#   rospy.Rate(hz)                → self.create_rate(hz) or Timer
#   rospy.spin()                  → rclpy.spin(node)
#   rospy.loginfo(msg)            → self.get_logger().info(msg)
#   rospy.get_param(name)         → self.declare_parameter(name, default)
#   rospy.Time                    → self.get_clock().now()
#   tf.TransformListener          → tf2_ros.Buffer + TransformListener
#   dynamic_reconfigure           → ROS2 parameters with add_on_set_parameters_callback

try:
    import rclpy
    from rclpy.node import Node
except ImportError:
    rclpy = None
    class Node:
        def __init__(self, name: str) -> None:
            self.name = name
        def get_logger(self):
            return self
        def info(self, msg: str) -> None:
            print(msg)
        def create_publisher(self, *args, **kwargs):
            pass
        def create_subscription(self, *args, **kwargs):
            pass
        def declare_parameter(self, name: str, default=None):
            return rclpy.Parameter(name) if rclpy else type('P', (), {{'value': default}})()


class MigratedNode(Node):
    """ROS2 node migrated from ROS1 source.

    TODO: replace class name with original node class name.
    TODO: migrate the __init__ method body.
    TODO: migrate callback functions with ROS2 API equivalents.
    TODO: review QoS profiles (default is RELIABLE, may need BEST_EFFORT).
    """

    def __init__(self) -> None:
        # Replace 'migrated_node' with the original ROS1 node name
        super().__init__("migrated_node")

        # TODO: declare parameters before use
        # self.declare_parameter("param_name", default_value)

        # TODO: migrate publishers
        # ROS1: self.pub = rospy.Publisher("/topic", MsgType, queue_size=10)
        # ROS2: self.pub = self.create_publisher(MsgType, "/topic", 10)

        # TODO: migrate subscribers
        # ROS1: rospy.Subscriber("/topic", MsgType, self.callback)
        # ROS2: self.sub = self.create_subscription(MsgType, "/topic", self.callback, 10)

        # TODO: migrate timers
        # ROS1: rospy.Timer(rospy.Duration(0.1), self.timer_cb)
        # ROS2: self.timer = self.create_timer(0.1, self.timer_cb)

        self.get_logger().info("Migrated node initialized — review and complete TODOs")


def main() -> None:
    """Entry point — migrate from rospy to rclpy initialization."""
    if rclpy is None:
        node = MigratedNode()
        node.get_logger().info("rclpy not available; running in offline mode.")
        return

    rclpy.init()
    node = MigratedNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
'''


def _render_cpp_node_placeholder(preview: MigrationScaffoldPreviewResult, item: ScaffoldFile) -> str:
    return f"""// ROS2 node placeholder generated by RoboPilot migration scaffold.
// This is not an automatic migration. Every file requires manual review.
// Original ROS1 source: {item.source_basis}

// ROS1 → ROS2 API migration cheat sheet:
//   ros::init(argc, argv, name)      → rclcpp::init(argc, argv)
//   ros::NodeHandle nh               → rclcpp::Node::SharedPtr node
//   nh.advertise<Type>(topic, q)     → node->create_publisher<Type>(topic, q)
//   nh.subscribe(topic, q, cb)       → node->create_subscription<Type>(topic, q, cb)
//   ros::spin()                      → rclcpp::spin(node)
//   ros::Rate(hz)                    → rclcpp::Rate(hz) or node->create_wall_timer
//   ROS_INFO("msg")                  → RCLCPP_INFO(node->get_logger(), "msg")
//   nh.param<T>("name", default)     → node->declare_parameter<T>("name", default)
//   ros::Time::now()                 → node->get_clock()->now()
//   tf::TransformListener            → tf2_ros::Buffer + TransformListener

// TODO: review QoS behavior — ROS1 defaults differ from ROS2 (RELIABLE vs BEST_EFFORT).

#include <rclcpp/rclcpp.hpp>

class MigratedNode : public rclcpp::Node {{
public:
    MigratedNode() : Node("migrated_node") {{
        // TODO: migrate publishers
        // ROS1: pub_ = nh_.advertise<Type>("/topic", 10);
        // ROS2: pub_ = this->create_publisher<Type>("/topic", 10);

        // TODO: migrate subscribers
        // ROS1: sub_ = nh_.subscribe("/topic", 10, &MigratedNode::callback, this);
        // ROS2: sub_ = this->create_subscription<Type>(
        //     "/topic", 10, std::bind(&MigratedNode::callback, this, _1));

        RCLCPP_INFO(this->get_logger(), "Migrated node initialized — review and complete TODOs.");
    }}

private:
    // TODO: migrate member variables and callback methods
}};

int main(int argc, char** argv) {{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MigratedNode>());
    rclcpp::shutdown();
    return 0;
}}
"""


def _render_launch_placeholder(preview: MigrationScaffoldPreviewResult, item: ScaffoldFile) -> str:
    return f'''"""ROS2 launch placeholder generated by RoboPilot migration scaffold.

This is not an automatic migration. Every file requires manual review.
Original ROS1 launch source: {item.source_basis}

Migration patterns:
  ROS1 XML: <node pkg="p" type="t" name="n" args="a" output="screen"/>
  ROS2: Node(package="p", executable="t", name="n", arguments=["a"], output="screen")

  ROS1 XML: <param name="n" value="v"/>
  ROS2: Node(..., parameters=[{{"n": "v"}}])

  ROS1 XML: <remap from="/old" to="/new"/>
  ROS2: Node(..., remappings=[("/old", "/new")])

  ROS1 XML: <arg name="x" default="y"/>
  ROS2: DeclareLaunchArgument("x", default_value="y")

  ROS1 XML: <include file="$(find pkg)/launch/file.launch">
  ROS2: IncludeLaunchDescription(PythonLaunchDescriptionSource(
           [FindPackageShare("pkg"), "/launch/file.launch.py"]))
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """Return a scaffolded launch description. Review and complete TODOs."""
    # TODO: declare launch arguments from original ROS1 <arg> tags
    # TODO: add Node actions for each original <node> tag
    # TODO: migrate <remap> tags to Node remappings
    # TODO: migrate <include> tags to IncludeLaunchDescription
    # TODO: review parameter files and namespace handling
    return LaunchDescription([])
'''


def _render_params_yaml(preview: MigrationScaffoldPreviewResult) -> str:
    package_name = _safe_name(preview.package_name)
    return f"""# Generated by RoboPilot migration scaffold.
# This is not an automatic migration.
# TODO: migrate ROS1 parameters manually.
# TODO: review parameter names, namespaces, and ROS2 QoS-related behavior.
{package_name}:
  ros__parameters: {{}}
"""


def _render_generic_placeholder(preview: MigrationScaffoldPreviewResult, item: ScaffoldFile) -> str:
    return f"""# Generated by RoboPilot migration scaffold.
# This is not an automatic migration.
# Source basis: {item.source_basis}
# TODO: review and complete this file manually.
"""


def _render_migration_notes(
    preview: MigrationScaffoldPreviewResult,
    generated_files: tuple[str, ...],
) -> str:
    sections = [
        "# RoboPilot Migration Scaffold Notes",
        "",
        f"- Source path: {preview.source_path or 'unknown'}",
        f"- Package name: {preview.package_name or 'unknown'}",
        f"- Target: {preview.target}",
        f"- Target style: {preview.target_style}",
        "",
        "## Files Generated",
        _bullet_list(generated_files),
        "",
        "## Files Requiring Manual Migration",
        _bullet_list(preview.files_requiring_manual_migration),
        "",
        "## Interface Files to Review",
        _bullet_list(preview.interface_files_to_review),
        "",
        "## Dependency Items to Review",
        _bullet_list(preview.dependency_items_to_review),
        "",
        "## Risks",
        _bullet_list(preview.risks),
        "",
        "## Conflicts",
        _bullet_list(_blocking_preview_conflicts(preview)),
        "",
        "## Safety Note",
        "This is not an automatic migration. Every generated file requires manual review before ROS2 build or runtime use.",
        "",
        SAFETY_NOTE,
        "",
        "No runtime validation was performed. RoboPilot did not run ROS, ROS2, catkin_make, colcon, launch files, or generated code.",
        "",
        "## Suggested Next Steps",
        "- Run robopilot migrate-scaffold-validate --plan <migration_plan.yaml> --scaffold <ros2_scaffold>.",
        "- Export a report with robopilot migrate-scaffold-report --plan <migration_plan.yaml> --scaffold <ros2_scaffold> --output scaffold_report.md.",
        "- Manually review this file and every TODO before using ROS2 build or runtime tools.",
        "",
    ]
    return "\n".join(sections)


def _blocking_preview_conflicts(preview: MigrationScaffoldPreviewResult) -> tuple[str, ...]:
    non_blocking = {
        "mixed Python/C++ package requires manual target-style decision",
        "target package style could not be inferred",
    }
    return tuple(item for item in preview.conflicts if item not in non_blocking)


def _safe_output_path(output_root: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"unsafe scaffold path rejected: {relative_path}")
    target = (output_root / relative).resolve(strict=False)
    if not target.is_relative_to(output_root):
        raise ValueError(f"scaffold path escapes output directory: {relative_path}")
    return target


def _safe_name(package_name: str) -> str:
    value = package_name.strip()
    return value if value and value != "unknown" else "migration_scaffold"


def _bullet_list(items: tuple[str, ...] | list[str]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _dedupe_items(items: list[ScaffoldFile]) -> tuple[ScaffoldFile, ...]:
    by_path: dict[str, ScaffoldFile] = {}
    for item in items:
        by_path.setdefault(item.path, item)
    return tuple(by_path[path] for path in sorted(by_path))


def _sorted_unique(items: list[str]) -> tuple[str, ...]:
    return tuple(sorted(dict.fromkeys(items)))
