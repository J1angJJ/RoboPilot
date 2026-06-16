"""Static ROS1-to-ROS2 migration readiness scoring (v2.1.0 M3)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from robopilot.deps.analyzer import analyze_dependencies
from robopilot.detector.project_detector import detect_project
from robopilot.ros1.inspector import ROS1Inspection, inspect_ros1_project


SAFETY_NOTE = (
    "This migration readiness score is a static estimate, not a guarantee. "
    "RoboPilot did not require ROS, require ROS2, run catkin_make, run colcon, "
    "execute launch files, execute code, or import user project modules. "
    "Manual review is always required before migration."
)

CATEGORIES = {
    "api_surface":       ("API Surface",        0.25),
    "build_system":      ("Build System",       0.20),
    "dependency_avail":  ("Dependency Avail.",  0.25),
    "launch_complexity": ("Launch Complexity",  0.15),
    "interface_surface": ("Interface Surface",  0.15),
}


@dataclass(frozen=True)
class CategoryScore:
    key: str
    label: str
    score: int
    max_score: int
    weight: float
    findings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "label": self.label,
            "score": self.score,
            "max_score": self.max_score,
            "weight": self.weight,
            "findings": list(self.findings),
        }


@dataclass(frozen=True)
class MigrationScoreResult:
    source_path: str
    package_name: str | None
    source_project_type: str
    overall_score: int
    categories: tuple[CategoryScore, ...]
    summary: str
    suggested_next_steps: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path,
            "package_name": self.package_name,
            "source_project_type": self.source_project_type,
            "overall_score": self.overall_score,
            "categories": [c.to_dict() for c in self.categories],
            "summary": self.summary,
            "suggested_next_steps": list(self.suggested_next_steps),
            "safety_note": SAFETY_NOTE,
        }


def score_migration_readiness(source_path: Path) -> MigrationScoreResult:
    """Score a ROS1 package on ROS2 migration readiness (0-100)."""
    path = Path(source_path).resolve()
    detection = detect_project(path)
    inspection = inspect_ros1_project(path)
    deps = analyze_dependencies(path)

    cats = [
        _score_api_surface(inspection),
        _score_build_system(inspection),
        _score_dependency_availability(deps),
        _score_launch_complexity(inspection),
        _score_interface_surface(inspection),
    ]
    overall = _weighted_overall(cats)
    summary = _render_summary(overall, detection.project_type)
    steps = _suggested_steps(cats, inspection)

    return MigrationScoreResult(
        source_path=str(path),
        package_name=inspection.package_name or None,
        source_project_type=detection.project_type,
        overall_score=overall,
        categories=tuple(cats),
        summary=summary,
        suggested_next_steps=steps,
    )


# ---------------------------------------------------------------------------
# Category scorers
# ---------------------------------------------------------------------------


def _score_api_surface(inspection: ROS1Inspection) -> CategoryScore:
    key = "api_surface"
    label, weight = CATEGORIES[key]
    score = 100
    findings: list[str] = []

    py_nodes = len(inspection.nodes.python_node_candidates)
    cpp_nodes = len(inspection.nodes.cpp_node_candidates)
    total_nodes = py_nodes + cpp_nodes

    if total_nodes == 0:
        return CategoryScore(key, label, 100, 100, weight, ("No ROS1 nodes detected.",))

    if inspection.rospy_usage:
        score -= 15
        findings.append(f"rospy usage detected in {py_nodes} Python node(s). API migration: rospy.init_node → rclpy.init, rospy.Publisher → create_publisher, rospy.Subscriber → create_subscription, rospy.spin → rclpy.spin.")
    elif py_nodes > 0:
        score -= 5
        findings.append(f"{py_nodes} Python node(s) without explicit rospy import. Manual API review recommended.")

    if inspection.roscpp_usage:
        score -= 15
        findings.append(f"roscpp usage detected in {cpp_nodes} C++ node(s). API migration: ros::init → rclcpp::init, ros::NodeHandle → rclcpp::Node, ros::Publisher → create_publisher, ros::spin → rclcpp::spin.")
    elif cpp_nodes > 0:
        score -= 5
        findings.append(f"{cpp_nodes} C++ node(s) without explicit roscpp include. Manual API review recommended.")

    if not findings:
        findings.append("No rospy or roscpp usage patterns detected.")

    return CategoryScore(key, label, max(0, score), 100, weight, tuple(findings))


def _score_build_system(inspection: ROS1Inspection) -> CategoryScore:
    key = "build_system"
    label, weight = CATEGORIES[key]
    score = 100
    findings: list[str] = []

    if inspection.catkin.find_package_catkin:
        score -= 10
        comps = ", ".join(inspection.catkin.catkin_components) if inspection.catkin.catkin_components else "none"
        findings.append(f"find_package(catkin REQUIRED COMPONENTS {comps}) detected. Migrate to explicit ROS2 find_package calls.")

    if inspection.catkin.catkin_package:
        score -= 10
        findings.append("catkin_package() detected. Replace with ament_package() in ROS2.")

    if len(inspection.catkin.catkin_components) > 5:
        score -= 10
        findings.append(f"{len(inspection.catkin.catkin_components)} catkin components; high build complexity. Review each for ROS2 equivalents.")

    if cpp := len(inspection.nodes.cpp_node_candidates):
        if cpp > 3:
            score -= 10
            findings.append(f"{cpp} C++ node(s). ROS2 ament_cmake migration may require significant CMake restructuring.")

    if not findings:
        findings.append("Build system appears straightforward for migration.")
        score = 95

    return CategoryScore(key, label, max(0, score), 100, weight, tuple(findings))


def _score_dependency_availability(deps) -> CategoryScore:
    from robopilot.deps.analyzer import DependencyAnalysis
    key = "dependency_avail"
    label, weight = CATEGORIES[key]
    score = 100
    findings: list[str] = []

    all_deps = set(deps.declared_dependencies.build + deps.declared_dependencies.exec + deps.declared_dependencies.run)
    known_ros2: set[str] = {
        "roscpp", "rospy", "std_msgs", "sensor_msgs", "geometry_msgs",
        "nav_msgs", "tf", "tf2", "tf2_ros", "actionlib", "actionlib_msgs",
        "diagnostic_msgs", "visualization_msgs", "shape_msgs",
        "trajectory_msgs", "moveit_core", "moveit_msgs",
    }
    unknown: list[str] = []
    for dep in sorted(all_deps):
        if dep in known_ros2:
            continue
        if dep in ("catkin", "message_generation", "message_runtime", "genmsg", "gencpp", "genpy"):
            findings.append(f"Build-only dep '{dep}' has a known ROS2 equivalent. This is low-risk.")
            score -= 2
        else:
            unknown.append(dep)

    if unknown:
        score -= min(30, len(unknown) * 5)
        findings.append(f"{len(unknown)} dependencies without known ROS2 equivalents: {', '.join(unknown[:5])}{'...' if len(unknown) > 5 else ''}. Review each manually.")

    if deps.possibly_missing:
        score -= min(10, len(deps.possibly_missing) * 3)
        findings.append(f"{len(deps.possibly_missing)} possibly missing dependencies flagged by static analysis.")

    if not findings:
        findings.append("All declared dependencies have known ROS2 equivalents.")

    return CategoryScore(key, label, max(0, score), 100, weight, tuple(findings))


def _score_launch_complexity(inspection: ROS1Inspection) -> CategoryScore:
    key = "launch_complexity"
    label, weight = CATEGORIES[key]
    score = 100
    findings: list[str] = []
    launch_files = inspection.files.launch_files

    if not launch_files:
        return CategoryScore(key, label, 100, 100, weight, ("No ROS1 launch files detected.",))

    if len(launch_files) > 3:
        score -= 15
        findings.append(f"{len(launch_files)} launch files. ROS1 XML → ROS2 Python launch migration requires manual review for each file.")
    elif len(launch_files) > 1:
        score -= 5
        findings.append(f"{len(launch_files)} launch files. Moderate launch migration effort.")
    else:
        score -= 5
        findings.append("1 launch file. Simple launch migration.")

    # Check launch file content for complexity signals
    for lf in launch_files:
        lf_path = Path(inspection.project_path) / lf
        if lf_path.exists():
            content = lf_path.read_text(encoding="utf-8", errors="ignore")
            if "<arg " in content:
                score -= 5
                findings.append(f"Launch file '{lf}' uses <arg> tags (ROS1 launch arguments). Migrate to Python LaunchConfiguration.")
                break

    for lf in launch_files:
        lf_path = Path(inspection.project_path) / lf
        if lf_path.exists():
            content = lf_path.read_text(encoding="utf-8", errors="ignore")
            if "<include " in content or "<group " in content or "<machine " in content:
                score -= 5
                findings.append(f"Launch file '{lf}' uses nested includes/groups/machines. Manual restructuring required.")
                break

    return CategoryScore(key, label, max(0, score), 100, weight, tuple(findings))


def _score_interface_surface(inspection: ROS1Inspection) -> CategoryScore:
    key = "interface_surface"
    label, weight = CATEGORIES[key]
    score = 100
    findings: list[str] = []

    msg_count = len(inspection.files.msg_files)
    srv_count = len(inspection.files.srv_files)
    action_count = len(inspection.files.action_files)
    total = msg_count + srv_count + action_count

    if total == 0:
        return CategoryScore(key, label, 100, 100, weight, ("No custom msg/srv/action files detected.",))

    if msg_count:
        score -= min(10, msg_count * 2)
        findings.append(f"{msg_count} custom message file(s). .msg files are generally reusable in ROS2; update CMake rules from add_message_files to rosidl_generate_interfaces.")
    if srv_count:
        score -= min(10, srv_count * 3)
        findings.append(f"{srv_count} custom service file(s). .srv files are reusable; review service call patterns for ROS2 API changes.")
    if action_count:
        score -= min(15, action_count * 5)
        findings.append(f"{action_count} custom action file(s). ROS1 actionlib → ROS2 action API requires significant manual migration.")

    return CategoryScore(key, label, max(0, score), 100, weight, tuple(findings))


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------


def _weighted_overall(categories: list[CategoryScore]) -> int:
    total = 0.0
    for cat in categories:
        norm = cat.score / cat.max_score if cat.max_score > 0 else 0
        total += norm * cat.weight * 100
    return max(0, min(100, round(total)))


def _render_summary(score: int, project_type: str) -> str:
    if score >= 80:
        band = "LOW difficulty"
    elif score >= 60:
        band = "MODERATE difficulty"
    elif score >= 40:
        band = "HIGH difficulty"
    else:
        band = "VERY HIGH difficulty"

    if project_type != "ros1_catkin_package":
        return (f"Overall score {score}/100 — {band}. "
                f"Source project was classified as '{project_type}', not a confirmed ROS1 catkin package. "
                "Verify the project type before relying on this score.")

    return (f"Overall score {score}/100 — {band}. "
            "This is a static estimate based on file structure, API patterns, declared dependencies, "
            "launch files, and interface files. Manual review is always required.")


def _suggested_steps(
    categories: list[CategoryScore],
    inspection: ROS1Inspection,
) -> tuple[str, ...]:
    steps = [
        "Review this score breakdown before planning migration work.",
        "Run robopilot lint on the source package to check for structural issues.",
        "Run robopilot deps to review dependency hints in detail.",
        "Run robopilot migrate-plan to generate a detailed migration plan.",
        "Create a separate branch before manually migrating any files.",
    ]
    weak = [cat for cat in categories if cat.score < 70]
    if weak:
        steps.insert(3, f"Focus attention on weakest categories: {', '.join(c.label for c in weak)}")
    return tuple(steps)
