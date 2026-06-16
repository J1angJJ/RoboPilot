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