"""Offline ROS-style package generator for RoboPilot."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from robopilot.generator import templates
from robopilot.utils.file_ops import ensure_new_directory, write_text_file


PACKAGE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True)
class GeneratedProject:
    """Summary of a generated ROS-style package."""

    package_name: str
    output_dir: Path
    files: tuple[Path, ...]


def generate_project(
    *,
    name: str,
    task: str,
    output_root: Path | str = Path("outputs"),
    overwrite: bool = False,
) -> GeneratedProject:
    """Generate an offline ROS-style Python package skeleton."""
    package_name = _validate_package_name(name)
    clean_task = task.strip()
    if not clean_task:
        raise ValueError("Task description cannot be empty.")

    root = Path(output_root)
    project_dir = root / package_name
    ensure_new_directory(project_dir, overwrite=overwrite)

    files = _render_files(package_name=package_name, task=clean_task)
    written_files: list[Path] = []
    for relative_path, content in files.items():
        target_path = project_dir / relative_path
        write_text_file(target_path, content, overwrite=overwrite)
        written_files.append(target_path)

    return GeneratedProject(
        package_name=package_name,
        output_dir=project_dir,
        files=tuple(written_files),
    )


def expected_project_files(package_name: str) -> tuple[Path, ...]:
    """Return the relative files generated for a package name."""
    return tuple(_render_files(package_name=package_name, task="placeholder").keys())


def _render_files(package_name: str, task: str) -> dict[Path, str]:
    return {
        Path("package.xml"): templates.package_xml(package_name),
        Path("setup.py"): templates.setup_py(package_name),
        Path("setup.cfg"): templates.setup_cfg(package_name),
        Path("README.md"): templates.readme(package_name, task),
        Path("launch") / f"{package_name}.launch.py": templates.launch_file(
            package_name
        ),
        Path("config") / "params.yaml": templates.params_yaml(package_name),
        Path(package_name) / "__init__.py": "",
        Path(package_name) / "detector_node.py": templates.detector_node(
            package_name, task
        ),
    }


def _validate_package_name(name: str) -> str:
    package_name = name.strip()
    if not PACKAGE_NAME_PATTERN.fullmatch(package_name):
        raise ValueError(
            "Package name must start with a lowercase letter and contain only "
            "lowercase letters, numbers, and underscores."
        )
    return package_name

