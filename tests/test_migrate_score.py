"""Tests for robopilot migrate-score (v2.1.0 Milestone 3)."""

from pathlib import Path

from robopilot.migrate_score import (
    CategoryScore,
    MigrationScoreResult,
    _score_api_surface,
    _score_build_system,
    _score_dependency_availability,
    _score_interface_surface,
    _score_launch_complexity,
    _weighted_overall,
    score_migration_readiness,
)


def test_score_on_ros1_migration_demo() -> None:
    """Real ROS1 demo package should produce a valid score 0-100."""
    demo = Path("examples/ros1_migration_demo")
    result = score_migration_readiness(demo)
    assert 0 <= result.overall_score <= 100
    assert result.package_name == "ros1_migration_demo"
    assert result.source_project_type == "ros1_catkin_package"
    assert len(result.categories) == 5
    for cat in result.categories:
        assert 0 <= cat.score <= 100
        assert cat.label
    d = result.to_dict()
    assert "safety_note" in d


def test_score_unknown_path() -> None:
    """Non-existent path should still produce data but may have issues."""
    result = score_migration_readiness(Path("/nonexistent_migrate_score_test"))
    assert 0 <= result.overall_score <= 100


def test_weighted_overall_perfect() -> None:
    cats = [
        CategoryScore("a", "A", 100, 100, 0.25, ()),
        CategoryScore("b", "B", 100, 100, 0.25, ()),
        CategoryScore("c", "C", 100, 100, 0.25, ()),
        CategoryScore("d", "D", 100, 100, 0.15, ()),
        CategoryScore("e", "E", 100, 100, 0.10, ()),
    ]
    assert _weighted_overall(cats) == 100


def test_weighted_overall_zero() -> None:
    cats = [
        CategoryScore("a", "A", 0, 100, 0.25, ()),
        CategoryScore("b", "B", 0, 100, 0.25, ()),
        CategoryScore("c", "C", 0, 100, 0.25, ()),
        CategoryScore("d", "D", 0, 100, 0.15, ()),
        CategoryScore("e", "E", 0, 100, 0.10, ()),
    ]
    assert _weighted_overall(cats) == 0


def test_score_result_roundtrip_json() -> None:
    result = score_migration_readiness(Path("examples/ros1_migration_demo"))
    d = result.to_dict()
    assert "overall_score" in d
    assert "categories" in d
    assert isinstance(d["categories"], list)
    assert len(d["categories"]) == 5
    cat0 = d["categories"][0]
    assert isinstance(cat0, dict)
    assert "key" in cat0 and "score" in cat0 and "findings" in cat0


def test_no_launch_files_gives_full_score() -> None:
    from robopilot.ros1.inspector import ROS1Files, ROS1Inspection, ROS1Nodes, ROS1Dependencies, CatkinSignals

    inspection = ROS1Inspection(
        project_path="/tmp/test",
        exists=True,
        package_name="test",
        package_format="2",
        detected_project_type="ros1_catkin_package",
        dependencies=ROS1Dependencies((), (), (), ()),
        catkin=CatkinSignals(False, (), False),
        files=ROS1Files((), (), (), (), (), ()),
        nodes=ROS1Nodes((), ()),
        rospy_usage=False,
        roscpp_usage=False,
        issues=(),
        suggested_next_steps=(),
        safety_note="",
    )
    cat = _score_launch_complexity(inspection)
    assert cat.score == 100
    assert "No ROS1 launch files" in cat.findings[0]


def test_no_interfaces_gives_full_score() -> None:
    from robopilot.ros1.inspector import ROS1Files, ROS1Inspection, ROS1Nodes, ROS1Dependencies, CatkinSignals

    inspection = ROS1Inspection(
        project_path="/tmp/test",
        exists=True,
        package_name="test",
        package_format="2",
        detected_project_type="ros1_catkin_package",
        dependencies=ROS1Dependencies((), (), (), ()),
        catkin=CatkinSignals(False, (), False),
        files=ROS1Files((), (), (), (), (), ()),
        nodes=ROS1Nodes((), ()),
        rospy_usage=False,
        roscpp_usage=False,
        issues=(),
        suggested_next_steps=(),
        safety_note="",
    )
    cat = _score_interface_surface(inspection)
    assert cat.score == 100
    assert "No custom msg/srv/action" in cat.findings[0]
