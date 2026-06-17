"""Interactive tutorial mode for RoboPilot beginners (v2.1.0 M4).

Each lesson is a sequence of steps. Each step explains a concept, runs a
RoboPilot command, and verifies the result. No ROS installation required."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


SAFETY_NOTE = (
    "This tutorial is read-only except for explicit generate steps. "
    "RoboPilot did not require ROS, require ROS2, run catkin_make, run "
    "colcon, execute launch files, or execute generated code."
)


@dataclass(frozen=True)
class TutorialStep:
    """One step in a tutorial lesson."""

    title: str
    description: str
    action: str            # "run", "explain", "check"
    command: str | None     # CLI command for "run" / "check" actions
    verification: str | None  # What to check in output for "check" actions
    expected: str | None     # Hint about expected result


@dataclass(frozen=True)
class TutorialLesson:
    """A complete tutorial lesson."""

    id: str
    title: str
    summary: str
    estimated_minutes: int
    steps: tuple[TutorialStep, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "estimated_minutes": self.estimated_minutes,
            "step_count": len(self.steps),
        }


@dataclass(frozen=True)
class TutorialResult:
    """Result from running a tutorial lesson."""

    lesson_id: str
    lesson_title: str
    completed: bool
    steps_total: int
    steps_completed: int
    current_step_title: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "lesson_id": self.lesson_id,
            "lesson_title": self.lesson_title,
            "completed": self.completed,
            "steps_total": self.steps_total,
            "steps_completed": self.steps_completed,
            "current_step_title": self.current_step_title,
            "message": self.message,
            "safety_note": SAFETY_NOTE,
        }


# ---------------------------------------------------------------------------
# Lesson registry
# ---------------------------------------------------------------------------

_LESSONS: dict[str, TutorialLesson] = {}


def _register(lesson: TutorialLesson) -> None:
    _LESSONS[lesson.id] = lesson


def list_lessons() -> tuple[TutorialLesson, ...]:
    return tuple(_LESSONS.values())


def get_lesson(lesson_id: str) -> TutorialLesson | None:
    return _LESSONS.get(lesson_id)


# ---------------------------------------------------------------------------
# M14: Progress tracking
# ---------------------------------------------------------------------------

_STATE_FILE = ".robopilot_tutorial_state"


def load_progress(root: Path | None = None) -> dict[str, bool]:
    """Load tutorial progress: lesson_id → completed."""
    base = Path(root or Path.cwd()).resolve()
    state_path = base / _STATE_FILE
    if not state_path.exists():
        return {}
    try:
        import json as _json
        data = _json.loads(state_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {str(k): bool(v) for k, v in data.items()}
    except Exception:
        pass
    return {}


def save_progress(lesson_id: str, completed: bool = True, root: Path | None = None) -> None:
    """Mark a lesson as completed in the progress file."""
    base = Path(root or Path.cwd()).resolve()
    state_path = base / _STATE_FILE
    progress = load_progress(root)
    progress[lesson_id] = completed
    import json as _json
    state_path.write_text(_json.dumps(progress, indent=2) + "\n", encoding="utf-8")


def get_progress_summary(root: Path | None = None) -> dict[str, object]:
    """Return a progress summary: total, completed, remaining."""
    lessons = list_lessons()
    progress = load_progress(root)
    total = len(lessons)
    done = sum(1 for l in lessons if progress.get(l.id, False))
    return {
        "total_lessons": total,
        "completed": done,
        "remaining": total - done,
        "lesson_ids": [l.id for l in lessons],
        "completed_ids": [l.id for l in lessons if progress.get(l.id, False)],
    }


# ---------------------------------------------------------------------------
# Lesson 1: Demo Detector
# ---------------------------------------------------------------------------

_register(TutorialLesson(
    id="demo_detector",
    title="Your First ROS Package",
    summary=(
        "Plan, validate, and generate a complete ROS-style Python package "
        "for object detection — all without installing ROS."
    ),
    estimated_minutes=10,
    steps=(
        TutorialStep(
            title="What We're Building",
            description=(
                "RoboPilot helps you plan and generate ROS-style project structure "
                "without needing ROS, ROS2, or a robot. In this lesson, we'll create "
                "an object detection package — a Python project that mirrors how real "
                "ROS2 perception nodes are structured."
            ),
            action="explain",
            command=None, verification=None, expected=None,
        ),
        TutorialStep(
            title="Step 1: Plan Your Project",
            description=(
                "First, we create a plan. The `plan` command takes a project name and "
                "a natural-language description of your task, then produces a "
                "robopilot.yaml ProjectSpec — a blueprint for your package."
            ),
            action="run",
            command="python -m robopilot.main plan --name my_detector --task "
                    "'Create an object detection node subscribing to camera images "
                    "and publishing bounding boxes.' --output outputs/tutorial/demo_detector.yaml",
            verification="package_name: my_detector",
            expected="You should see 'package_name: my_detector' and 'selected_template: object_detection' in the output.",
        ),
        TutorialStep(
            title="Step 2: Validate the Spec",
            description=(
                "Before generating files, we validate the spec. This catches "
                "missing fields or structural problems early."
            ),
            action="run",
            command="python -m robopilot.main validate --spec outputs/tutorial/demo_detector.yaml",
            verification="Valid ProjectSpec",
            expected="You should see 'Valid ProjectSpec' in green.",
        ),
        TutorialStep(
            title="Step 3: Generate the Package",
            description=(
                "Now we generate the actual project files. This creates a complete "
                "Python package with setup.py, package.xml, launch files, config "
                "files, and a detector node skeleton."
            ),
            action="run",
            command="python -m robopilot.main generate "
                    "--spec outputs/tutorial/demo_detector.yaml "
                    "-o outputs/tutorial",
            verification="Generated my_detector",
            expected="You should see a table listing 9 created files.",
        ),
        TutorialStep(
            title="Step 4: Inspect the Package",
            description=(
                "Use `inspect` to analyze the generated package structure. "
                "This is a read-only check — it looks at files without executing "
                "any code."
            ),
            action="run",
            command="python -m robopilot.main inspect outputs/tutorial/my_detector",
            verification="package_name: my_detector",
            expected="You should see a summary showing the package name, files, and no structural issues.",
        ),
        TutorialStep(
            title="Step 5: Run Lint Checks",
            description=(
                "The `lint` command checks package quality: package.xml format, "
                "CMakeLists/setup.py conventions, required fields, and more."
            ),
            action="run",
            command="python -m robopilot.main lint outputs/tutorial/my_detector",
            verification="0 errors",
            expected="A clean package should show 'No issues found' or 0 errors.",
        ),
        TutorialStep(
            title="Step 6: Read the Generated Code",
            description=(
                "Open `outputs/tutorial/my_detector/my_detector/detector_node.py` "
                "in your editor. Notice how it has: a ROS2-style Node class with "
                "__init__, subscribers and publishers (as comments showing where they "
                "go), and a main() entry point. This is pseudocode that mirrors real "
                "ROS2 patterns — you can learn the structure without installing ROS."
            ),
            action="explain",
            command=None, verification=None, expected=None,
        ),
        TutorialStep(
            title="What's Next",
            description=(
                "You've completed the first tutorial! You can now:\n"
                "  - Edit robopilot.yaml to change topic names and regenerate\n"
                "  - Try `robopilot tutorial --lesson migration_basics` for ROS1→ROS2 skills\n"
                "  - Run `robopilot --help` to see all available commands"
            ),
            action="explain",
            command=None, verification=None, expected=None,
        ),
    ),
))


# ---------------------------------------------------------------------------
# Lesson 2: Migration Basics
# ---------------------------------------------------------------------------

_register(TutorialLesson(
    id="migration_basics",
    title="ROS1 to ROS2 Migration Basics",
    summary=(
        "Learn how to analyze a ROS1 package and plan its migration to ROS2 "
        "using RoboPilot's static analysis tools."
    ),
    estimated_minutes=12,
    steps=(
        TutorialStep(
            title="What We're Doing",
            description=(
                "RoboPilot can analyze real ROS1 packages without needing ROS "
                "installed. We'll use the example ROS1 package in "
                "`examples/ros1_migration_demo/` to learn the migration workflow."
            ),
            action="explain",
            command=None, verification=None, expected=None,
        ),
        TutorialStep(
            title="Step 1: Detect the Project Type",
            description=(
                "The `detect` command identifies what kind of project you have: "
                "ROS1 catkin, ROS2 ament, RoboPilot-generated, or something else."
            ),
            action="run",
            command="python -m robopilot.main detect examples/ros1_migration_demo",
            verification="ros1_catkin_package",
            expected="The project type should be 'ros1_catkin_package'.",
        ),
        TutorialStep(
            title="Step 2: Inspect the ROS1 Package",
            description=(
                "`inspect-ros1` performs a deep static analysis: it reads "
                "package.xml for dependencies, CMakeLists.txt for build system "
                "signals, and scans for Python/C++ node candidates — all without "
                "executing any code."
            ),
            action="run",
            command="python -m robopilot.main inspect-ros1 examples/ros1_migration_demo",
            verification="ros1_migration_demo",
            expected="You should see the package name, dependencies, catkin signals, and node candidates.",
        ),
        TutorialStep(
            title="Step 3: Score Migration Readiness",
            description=(
                "`migrate-score` gives you a 0-100 score estimating how difficult "
                "migration will be. It breaks down by API surface, build system, "
                "dependencies, launch files, and interface files."
            ),
            action="run",
            command="python -m robopilot.main migrate-score examples/ros1_migration_demo",
            verification="Overall score:",
            expected="The score (0-100) with a difficulty band: LOW, MODERATE, HIGH, or VERY HIGH.",
        ),
        TutorialStep(
            title="Step 4: Generate a Migration Plan",
            description=(
                "`migrate-plan` creates a detailed migration blueprint. It tells "
                "you what to change in package.xml, CMakeLists.txt, source code, "
                "launch files, and dependencies."
            ),
            action="run",
            command="python -m robopilot.main migrate-plan "
                    "--from examples/ros1_migration_demo "
                    "--to ros2 "
                    "--output outputs/tutorial/migration_plan.yaml",
            verification="Wrote migration plan to",
            expected="A migration plan file is written with specific guidance for each file type.",
        ),
        TutorialStep(
            title="Step 5: Analyze Dependencies",
            description=(
                "`deps` analyzes declared and detected dependencies, flags "
                "possibly missing or unused dependencies, and provides ROS1→ROS2 "
                "migration hints for common packages."
            ),
            action="run",
            command="python -m robopilot.main deps examples/ros1_migration_demo",
            verification="ros1_catkin_package",
            expected="You should see declared dependencies, detected usage, and migration hints.",
        ),
        TutorialStep(
            title="Review the Migration Plan",
            description=(
                "Open `outputs/tutorial/migration_plan.yaml` in your editor. "
                "Notice the structured guidance:\n"
                "  - package_xml_migration: specific XML changes needed\n"
                "  - build_system_migration: catkin→ament transition steps\n"
                "  - source_code_migration: rospy→rclpy API notes\n"
                "  - dependency_migration: ROS2 equivalents for each dependency\n"
                "  - risks and manual_review_items: what still needs human judgment"
            ),
            action="explain",
            command=None, verification=None, expected=None,
        ),
        TutorialStep(
            title="What's Next",
            description=(
                "You've learned the migration analysis workflow! Next steps:\n"
                "  - Run `migrate-scaffold` to generate a ROS2 scaffold\n"
                "  - Try `robopilot lint` on your own packages\n"
                "  - Read `docs/tutorial_ros1_to_ros2_migration.md` for the full guide"
            ),
            action="explain",
            command=None, verification=None, expected=None,
        ),
    ),
))

# ---------------------------------------------------------------------------
# v2.2.0 M14: 4 new lessons + progress tracking
# ---------------------------------------------------------------------------

_register(TutorialLesson(
    id="slam_basics",
    title="SLAM Mapping Walkthrough",
    summary="Plan and generate a SLAM node — understand LiDAR input, occupancy grids, and map building.",
    estimated_minutes=8,
    steps=(
        TutorialStep("SLAM Concepts",
            "SLAM (Simultaneous Localization and Mapping) lets robots build maps "
            "of unknown environments while tracking their position. Core data flow: "
            "LiDAR scans in → occupancy grid map out. "
            "中文: SLAM 让机器人同时定位和建图，数据流为激光扫描输入→占据栅格地图输出。",
            "explain", None, None, None),
        TutorialStep("Step 1: Plan a SLAM Node",
            "Use plan to create a robopilot.yaml for SLAM.",
            "run", "python -m robopilot.main plan --name slam_demo "
            "--task 'Create a SLAM mapping node for lidar data' "
            "--output outputs/tutorial/slam_demo.yaml",
            "selected_template: slam", "You should see 'selected_template: slam'."),
        TutorialStep("Step 2: Generate the Package",
            "Generate the SLAM package skeleton.",
            "run", "python -m robopilot.main generate --spec outputs/tutorial/slam_demo.yaml "
            "-o outputs/tutorial --overwrite",
            "Generated slam_demo", None),
        TutorialStep("Step 3: Inspect the Code",
            "Open slam_node.py to see /scan subscription, /map publication, "
            "occupancy grid logic, and map resolution params.",
            "explain", None, None, None),
        TutorialStep("Step 4: Run Lint",
            "Verify the generated package passes lint.",
            "run", "python -m robopilot.main lint outputs/tutorial/slam_demo",
            "0 errors", "Should show 0 errors."),
        TutorialStep("Key Takeaways",
            "SLAM: /scan → /map. Key params: resolution, max_range. "
            "Use slam_toolbox (2D) or rtabmap (3D) in real ROS2. "
            "中文: SLAM 节点订阅激光扫描，发布栅格地图，分辨率和距离是核心参数。",
            "explain", None, None, None),
    ),
))

_register(TutorialLesson(
    id="navigation_stack",
    title="Navigation Stack Explained",
    summary="Understand Nav2 architecture: planner, controller, costmaps, and behavior trees.",
    estimated_minutes=10,
    steps=(
        TutorialStep("Nav2 Concepts",
            "Nav2 controls robot motion from A to B while avoiding obstacles. "
            "Components: Global Planner (path to goal), Local Controller (follow path), "
            "Costmaps (global/local), Behavior Tree (orchestration). "
            "中文: Nav2 控制机器人运动并避开障碍物，包括规划器、控制器、代价地图和行为树。",
            "explain", None, None, None),
        TutorialStep("Step 1: Plan a Navigator",
            "Create a navigator node with odom, goal, cmd_vel, and plan topics.",
            "run", "python -m robopilot.main plan --name nav_demo "
            "--task 'Build autonomous navigation with path planning and obstacle avoidance' "
            "--output outputs/tutorial/nav_demo.yaml",
            "selected_template: navigation", None),
        TutorialStep("Step 2: Generate & Examine",
            "Generate the navigator package.",
            "run", "python -m robopilot.main generate --spec outputs/tutorial/nav_demo.yaml "
            "-o outputs/tutorial --overwrite",
            "Generated nav_demo", None),
        TutorialStep("Step 3: Data Flow",
            "/odom (sub) → where am I? /goal_pose (sub) → where to? "
            "/plan (pub) → path waypoints. /cmd_vel (pub) → velocity commands.",
            "explain", None, None, None),
        TutorialStep("Step 4: Quality Check",
            "Run lint + ci-check on the generated package.",
            "run", "python -m robopilot.main lint outputs/tutorial/nav_demo",
            "0 errors", None),
        TutorialStep("Key Takeaways",
            "Nav2 separates planning from control. Costmaps merge static + sensor data. "
            "Behavior trees replace ROS1 state machines. "
            "中文: 规划和控制分离，代价地图融合静态和传感器数据，行为树替代状态机。",
            "explain", None, None, None),
    ),
))

_register(TutorialLesson(
    id="custom_authoring",
    title="Create Your Own Templates",
    summary="Define custom generation templates in YAML — no Python required.",
    estimated_minutes=8,
    steps=(
        TutorialStep("Custom Templates",
            "Define reusable ROS package blueprints in YAML. Extend built-in templates "
            "and override topics, node names, and parameters. "
            "中文: 用 YAML 定义可复用模板，继承内置模板覆盖话题和参数。",
            "explain", None, None, None),
        TutorialStep("Step 1: Init Templates",
            "Scaffold .robopilot/templates/ with an example.",
            "run", "python -m robopilot.main template-init --root outputs/tutorial",
            "Created templates directory", None),
        TutorialStep("Step 2: Validate",
            "Verify the example template structure.",
            "run", "python -m robopilot.main template-validate "
            "--path outputs/tutorial/.robopilot/templates/my_custom_node",
            "Valid template", None),
        TutorialStep("Step 3: Use It",
            "Plan a project using the custom template.",
            "run", "python -m robopilot.main plan --template my_custom_node "
            "--name my_proj --task 'My custom node' "
            "--output outputs/tutorial/my_proj.yaml",
            "selected_template: my_custom_node", None),
        TutorialStep("Next Steps",
            "Create templates for sensor drivers, processing pipelines, "
            "and standardized configs. Share via git. "
            "中文: 为传感器驱动、处理流水线创建模板，通过 git 分享。",
            "explain", None, None, None),
    ),
))

_register(TutorialLesson(
    id="lint_workflow",
    title="Lint & CI Quality Workflow",
    summary="Use lint, ci-check, and lintrc.yaml for quality gates locally and in CI.",
    estimated_minutes=7,
    steps=(
        TutorialStep("Quality Gates",
            "RoboPilot lint and ci-check act as quality gates without running ROS. "
            "Use them locally during dev and in CI on every push. "
            "中文: lint 和 ci-check 作为质量门禁，在本地和 CI 中使用。",
            "explain", None, None, None),
        TutorialStep("Step 1: Run Lint",
            "Lint the demo detector package.",
            "run", "python -m robopilot.main lint examples/generated_projects/demo_detector",
            "0 errors", "Should show 0 errors."),
        TutorialStep("Step 2: Run CI Check",
            "Aggregated check with stable exit codes.",
            "run", "python -m robopilot.main ci-check examples/generated_projects/demo_detector --json",
            "overall_status", "JSON with overall_status and exit_code."),
        TutorialStep("Step 3: SARIF Export",
            "Generate SARIF for GitHub Code Scanning.",
            "run", "python -m robopilot.main ci-check examples/generated_projects/demo_detector "
            "--format sarif --output outputs/tutorial/check.sarif",
            "Wrote sarif report", None),
        TutorialStep("Step 4: lintrc.yaml",
            "Configure rules via .robopilot/lintrc.yaml: "
            "disable_<rule>: true, severity_<rule>: error|warning|info|off. "
            "中文: 通过 lintrc.yaml 配置规则：禁用或修改严重级别。",
            "explain", None, None, None),
        TutorialStep("CI Integration",
            "GitHub Actions: pip install robopilot → robopilot ci-check --format sarif → "
            "github/codeql-action/upload-sarif@v3. "
            "中文: CI 中运行 ci-check，生成 SARIF 上载到 GitHub。",
            "explain", None, None, None),
    ),
))