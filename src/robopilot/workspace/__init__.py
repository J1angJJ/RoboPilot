"""Workspace-level static analysis for multi-package projects (v2.1.0 M7)."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path

from robopilot.detector.project_detector import detect_project


SAFETY_NOTE = (
    "This workspace analysis is static and read-only. RoboPilot did not require "
    "ROS, run catkin_make, run colcon, execute launch files, execute code, or "
    "import user project modules."
)

PACKAGE_INDICATORS = {"package.xml", "setup.py", "CMakeLists.txt"}


@dataclass(frozen=True)
class WorkspacePackage:
    name: str
    path: str
    package_type: str
    dependencies: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "path": self.path,
            "package_type": self.package_type,
            "dependencies": list(self.dependencies),
        }


@dataclass(frozen=True)
class WorkspaceResult:
    workspace_path: str
    workspace_type: str
    package_count: int
    packages: tuple[WorkspacePackage, ...]
    dependency_graph: dict[str, list[str]]
    circular_deps: tuple[tuple[str, ...], ...]
    migration_order: tuple[str, ...]
    issues: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "workspace_path": self.workspace_path,
            "workspace_type": self.workspace_type,
            "package_count": self.package_count,
            "packages": [p.to_dict() for p in self.packages],
            "dependency_graph": {
                k: list(v) for k, v in self.dependency_graph.items()
            },
            "circular_deps": [list(c) for c in self.circular_deps],
            "migration_order": list(self.migration_order),
            "issues": list(self.issues),
            "safety_note": SAFETY_NOTE,
        }


def analyze_workspace(workspace_path: Path) -> WorkspaceResult:
    """Analyze a multi-package ROS workspace without executing anything."""
    root = Path(workspace_path).resolve()
    issues: list[str] = []

    if not root.is_dir():
        return WorkspaceResult(
            str(root), "nonexistent", 0, (), {}, (), (), ("Workspace path does not exist.",),
        )

    # Discover packages
    packages = _discover_packages(root, issues)
    if not packages:
        return WorkspaceResult(
            str(root), _classify_workspace(root, []), 0, (), {}, (), (),
            tuple(issues) or ("No ROS packages found in workspace.",),
        )

    # Build dependency graph
    dep_graph = _build_dep_graph(packages, issues)

    # Detect circular dependencies
    circular = _detect_circular_deps(dep_graph)

    # Compute migration order (topological sort, leaves first)
    order = _topological_order(packages, dep_graph)

    ws_type = _classify_workspace(root, packages)

    return WorkspaceResult(
        workspace_path=str(root),
        workspace_type=ws_type,
        package_count=len(packages),
        packages=tuple(packages),
        dependency_graph={name: list(deps) for name, deps in dep_graph.items()},
        circular_deps=circular,
        migration_order=order,
        issues=tuple(issues),
    )


# ---------------------------------------------------------------------------
# Package discovery
# ---------------------------------------------------------------------------


def _discover_packages(root: Path, issues: list[str]) -> list[WorkspacePackage]:
    """Discover all ROS packages under a workspace root."""
    packages: list[WorkspacePackage] = []
    seen_names: set[str] = set()

    # Check common workspace layouts
    src_dir = root / "src"
    search_roots = [root]
    if src_dir.is_dir():
        search_roots = [src_dir]

    for search_root in search_roots:
        for item in sorted(search_root.iterdir()):
            if not item.is_dir() or item.name.startswith("."):
                continue
            pkgs = _PACKAGE_INDICATORS & {p.name for p in item.iterdir()}
            if not pkgs:
                # Check one level deeper (some workspaces have nested structure)
                for sub in sorted(item.iterdir()):
                    if sub.is_dir() and not sub.name.startswith("."):
                        sub_pkgs = _PACKAGE_INDICATORS & {p.name for p in sub.iterdir()}
                        if sub_pkgs:
                            pkg = _build_package(sub, root, issues)
                            if pkg and pkg.name not in seen_names:
                                seen_names.add(pkg.name)
                                packages.append(pkg)
                continue
            pkg = _build_package(item, root, issues)
            if pkg and pkg.name not in seen_names:
                seen_names.add(pkg.name)
                packages.append(pkg)

    return packages


def _build_package(path: Path, root: Path, issues: list[str]) -> WorkspacePackage | None:
    detection = detect_project(path)
    name = _extract_name(path)

    if detection.project_type in ("non_ros_project", "unknown") and name == "unknown":
        return None

    # Extract dependencies from package.xml
    deps = _extract_deps(path)

    try:
        rel = str(path.relative_to(root))
    except ValueError:
        rel = str(path)

    return WorkspacePackage(name, rel, detection.project_type, deps)


def _extract_name(path: Path) -> str:
    pkg_xml = path / "package.xml"
    if pkg_xml.exists():
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(str(pkg_xml))
            name_el = tree.getroot().find("name")
            if name_el is not None and name_el.text:
                return name_el.text.strip()
        except Exception:
            pass
    return path.name


def _extract_deps(path: Path) -> tuple[str, ...]:
    pkg_xml = path / "package.xml"
    if not pkg_xml.exists():
        return ()
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(str(pkg_xml))
        deps: list[str] = []
        for child in tree.getroot():
            if child.tag in ("depend", "build_depend", "exec_depend", "buildtool_depend"):
                if child.text:
                    deps.append(child.text.strip())
        return tuple(sorted(set(deps)))
    except Exception:
        return ()


_PACKAGE_INDICATORS = PACKAGE_INDICATORS


# ---------------------------------------------------------------------------
# Dependency graph
# ---------------------------------------------------------------------------


def _build_dep_graph(
    packages: list[WorkspacePackage],
    issues: list[str],
) -> dict[str, set[str]]:
    """Build adjacency list: package name → set of intra-workspace dependency names."""
    names = {p.name for p in packages}
    graph: dict[str, set[str]] = {p.name: set() for p in packages}

    for pkg in packages:
        for dep in pkg.dependencies:
            if dep in names and dep != pkg.name:
                graph[pkg.name].add(dep)

    return graph


# ---------------------------------------------------------------------------
# Circular dependency detection
# ---------------------------------------------------------------------------


def _detect_circular_deps(graph: dict[str, set[str]]) -> tuple[tuple[str, ...], ...]:
    """Find all cycles in the dependency graph using DFS."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {name: WHITE for name in graph}
    cycles: list[tuple[str, ...]] = []
    stack: list[str] = []

    def dfs(node: str) -> None:
        color[node] = GRAY
        stack.append(node)
        for neighbor in graph.get(node, set()):
            if color.get(neighbor, BLACK) == GRAY:
                # Found a cycle: extract it from the stack
                idx = stack.index(neighbor)
                cycles.append(tuple(stack[idx:]))
            elif color.get(neighbor, BLACK) == WHITE:
                dfs(neighbor)
        stack.pop()
        color[node] = BLACK

    for name in graph:
        if color.get(name, WHITE) == WHITE:
            dfs(name)

    # Deduplicate (same cycle in different rotations)
    unique: list[tuple[str, ...]] = []
    seen = set()
    for cycle in cycles:
        key = tuple(sorted(cycle))
        if key not in seen:
            seen.add(key)
            unique.append(cycle)
    return tuple(unique)


# ---------------------------------------------------------------------------
# Topological sort (leaves first = good for migration)
# ---------------------------------------------------------------------------


def _topological_order(
    packages: list[WorkspacePackage],
    graph: dict[str, set[str]],
) -> tuple[str, ...]:
    """Topological sort: packages with no dependencies come first (leaf-first for migration)."""
    all_names = {p.name for p in packages}

    # Kahn's algorithm on the dependency graph: start with nodes that have no dependencies
    in_degree: dict[str, int] = {}
    for name in all_names:
        in_degree[name] = len(graph.get(name, set()))

    queue = deque([name for name in all_names if in_degree[name] == 0])
    order: list[str] = []

    while queue:
        name = queue.popleft()
        order.append(name)
        # name has been "built" — now packages that depend on name have one fewer dep
        for other in all_names:
            if name in graph.get(other, set()):
                in_degree[other] -= 1
                if in_degree[other] == 0:
                    queue.append(other)

    # Append any remaining (in cycles)
    for name in in_degree:
        if in_degree[name] > 0 and name not in order:
            order.append(name)

    return tuple(order)


# ---------------------------------------------------------------------------
# Workspace classification
# ---------------------------------------------------------------------------


def _classify_workspace(root: Path, packages: list[WorkspacePackage]) -> str:
    types = {p.package_type for p in packages}
    ros1 = {"ros1_catkin_package"}
    ros2 = {"ros2_ament_python_package", "ros2_ament_cmake_package", "robopilot_project"}

    has_ros1 = bool(types & ros1)
    has_ros2 = bool(types & ros2)

    if has_ros1 and has_ros2:
        return "mixed_ros_workspace"
    if has_ros1:
        return "catkin_workspace"
    if has_ros2:
        return "colcon_workspace"
    if root.name == "src" and (root.parent / "src").is_dir():
        return "catkin_or_colcon_workspace"
    # Heuristic: check for common workspace structure
    for indicator in ("src", "build", "install", "devel", "log"):
        if (root / indicator).is_dir():
            return "catkin_or_colcon_workspace"
    return "unknown_workspace"
