"""Tests for robopilot tutorial (v2.1.0 Milestone 4)."""

from pathlib import Path

from robopilot.tutorial import (
    TutorialLesson,
    TutorialResult,
    TutorialStep,
    get_lesson,
    list_lessons,
)


def test_list_lessons_returns_all_six_lessons() -> None:
    lessons = list_lessons()
    ids = {l.id for l in lessons}
    assert "demo_detector" in ids
    assert "migration_basics" in ids
    assert "slam_basics" in ids
    assert "navigation_stack" in ids
    assert "custom_authoring" in ids
    assert "lint_workflow" in ids
    assert len(lessons) >= 6


def test_get_existing_lesson() -> None:
    lesson = get_lesson("demo_detector")
    assert lesson is not None
    assert lesson.title == "Your First ROS Package"
    assert lesson.estimated_minutes > 0
    assert len(lesson.steps) > 0


def test_get_unknown_lesson() -> None:
    assert get_lesson("nonexistent_lesson") is None


def test_lesson_to_dict() -> None:
    lesson = get_lesson("demo_detector")
    d = lesson.to_dict()
    assert d["id"] == "demo_detector"
    assert "title" in d
    assert "step_count" in d
    assert d["step_count"] == len(lesson.steps)


def test_tutorial_result_completed() -> None:
    result = TutorialResult(
        lesson_id="demo_detector",
        lesson_title="Test",
        completed=True,
        steps_total=5,
        steps_completed=5,
        current_step_title="Done",
        message="All done.",
    )
    d = result.to_dict()
    assert d["completed"] is True
    assert d["steps_total"] == 5
    assert d["steps_completed"] == 5
    assert "safety_note" in d


def test_demo_detector_lesson_structure() -> None:
    lesson = get_lesson("demo_detector")
    assert lesson is not None
    step_titles = [s.title for s in lesson.steps]
    assert "Step 1: Plan Your Project" in step_titles
    assert "Step 3: Generate the Package" in step_titles
    assert "What's Next" in step_titles
    # Verify step types
    run_steps = [s for s in lesson.steps if s.action == "run"]
    explain_steps = [s for s in lesson.steps if s.action == "explain"]
    assert len(run_steps) >= 4
    assert len(explain_steps) >= 2


def test_migration_basics_lesson_structure() -> None:
    lesson = get_lesson("migration_basics")
    assert lesson is not None
    assert lesson.estimated_minutes > 0
    step_titles = [s.title for s in lesson.steps]
    assert "Step 2: Inspect the ROS1 Package" in step_titles
    assert "Step 3: Score Migration Readiness" in step_titles


def test_progress_tracking(tmp_path: Path) -> None:
    from robopilot.tutorial import save_progress, load_progress, get_progress_summary
    # Initially empty
    assert load_progress(tmp_path) == {}
    # Mark one done
    save_progress("demo_detector", True, tmp_path)
    p = load_progress(tmp_path)
    assert p["demo_detector"] is True
    # Summary
    s = get_progress_summary(tmp_path)
    assert s["completed"] >= 1
    assert s["total_lessons"] >= 6
