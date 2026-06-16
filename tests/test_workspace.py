"""Tests for robopilot workspace analysis (v2.1.0 Milestone 7)."""

from pathlib import Path

from robopilot.workspace import (
    WorkspacePackage,
    WorkspaceResult,
    _detect_circular_deps,
    _topological_order,
    analyze_workspace,
)


def test_empty_directory(tmp_path: Path) -> None:
    result = analyze_workspace(tmp_path)
    assert result.package_count == 0
    assert len(result.issues) >= 1


def test_single_ros2_package(tmp_path: Path) -> None:
    pkg = tmp_path / "my_pkg"
    pkg.mkdir()
    (pkg / "package.xml").write_text(
        '<?xml version="1.0"?><package format="3">'
        '<name>my_pkg</name><version>0.1.0</version>'
        '<description>Test</description><maintainer email="a@b.com">A</maintainer>'
        '<license>MIT</license></package>',
        encoding="utf-8",
    )
    (pkg / "setup.py").write_text("from setuptools import setup\nsetup()\n", encoding="utf-8")

    result = analyze_workspace(tmp_path)
    assert result.package_count == 1
    assert result.packages[0].name == "my_pkg"
    assert result.circular_deps == ()


def test_two_packages_with_dependency(tmp_path: Path) -> None:
    pkg_a = tmp_path / "pkg_a"
    pkg_a.mkdir()
    (pkg_a / "package.xml").write_text(
        '<?xml version="1.0"?><package format="3">'
        '<name>pkg_a</name><version>0.1</version>'
        '<description>A</description><maintainer email="a@b.com">A</maintainer>'
        '<license>MIT</license>'
        '<depend>pkg_b</depend></package>',
        encoding="utf-8",
    )
    (pkg_a / "setup.py").write_text("package_name='pkg_a'\n", encoding="utf-8")

    pkg_b = tmp_path / "pkg_b"
    pkg_b.mkdir()
    (pkg_b / "package.xml").write_text(
        '<?xml version="1.0"?><package format="3">'
        '<name>pkg_b</name><version>0.1</version>'
        '<description>B</description><maintainer email="a@b.com">A</maintainer>'
        '<license>MIT</license></package>',
        encoding="utf-8",
    )
    (pkg_b / "setup.py").write_text("package_name='pkg_b'\n", encoding="utf-8")

    result = analyze_workspace(tmp_path)
    assert result.package_count == 2
    assert "pkg_b" in result.dependency_graph.get("pkg_a", [])
    # Migration order: pkg_b should come before pkg_a (leaf first)
    b_idx = result.migration_order.index("pkg_b")
    a_idx = result.migration_order.index("pkg_a")
    assert b_idx < a_idx, f"Expected pkg_b before pkg_a, got {result.migration_order}"


def test_circular_dependency_detection() -> None:
    graph = {"a": {"b"}, "b": {"c"}, "c": {"a"}}
    cycles = _detect_circular_deps(graph)
    assert len(cycles) >= 1


def test_no_circular_deps() -> None:
    graph = {"a": {"b"}, "b": {"c"}, "c": set()}
    cycles = _detect_circular_deps(graph)
    assert len(cycles) == 0


def test_results_to_dict() -> None:
    pkg = WorkspacePackage("test", "src/test", "ros2_ament_python", ("rclpy", "std_msgs"))
    d = pkg.to_dict()
    assert d["name"] == "test"
    assert d["dependencies"] == ["rclpy", "std_msgs"]

    result = WorkspaceResult(
        "/ws", "colcon_workspace", 1, (pkg,),
        {"test": []}, (), ("test",), (),
    )
    rd = result.to_dict()
    assert "safety_note" in rd
    assert rd["workspace_type"] == "colcon_workspace"
    assert rd["package_count"] == 1


def test_migration_order_trivial() -> None:
    """A single independent package should appear first in order."""
    pkgs = [WorkspacePackage("a", "a", "ros2_ament_python", ())]
    graph = {"a": set()}
    order = _topological_order(pkgs, graph)
    assert order == ("a",)


def test_diamond_deps() -> None:
    """a depends on b and c; b and c depend on d. Order: d, b, c, a (or d, c, b, a)."""
    pkgs = [
        WorkspacePackage("a", "a", "ros2_ament_python", ("b", "c")),
        WorkspacePackage("b", "b", "ros2_ament_python", ("d",)),
        WorkspacePackage("c", "c", "ros2_ament_python", ("d",)),
        WorkspacePackage("d", "d", "ros2_ament_python", ()),
    ]
    graph = {"a": {"b", "c"}, "b": {"d"}, "c": {"d"}, "d": set()}
    order = _topological_order(pkgs, graph)
    assert order.index("d") == 0, f"d should be first, got {order}"
    assert order.index("a") == 3, f"a should be last, got {order}"
