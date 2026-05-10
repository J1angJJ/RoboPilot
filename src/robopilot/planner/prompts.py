"""Prompt templates for optional ProjectSpec-only LLM planning."""

from __future__ import annotations


PROJECT_SPEC_PROMPT = """\
You are helping RoboPilot plan a ROS-style Python package.

Return only structured ProjectSpec-compatible data. Do not write code. Do not
generate project files. Do not include prose outside the structured data.

Required fields:
- package_name
- task
- selected_template
- generated_by
- nodes
- topics
- config_files
- launch_files
- notes

Allowed selected_template values:
- camera_subscriber
- object_detection
- velocity_controller
- perception_pipeline
- generic_node

Package name: {package_name}
Task: {task}
"""


def build_project_spec_prompt(*, package_name: str, task: str) -> str:
    """Build the optional LLM planner prompt."""
    return PROJECT_SPEC_PROMPT.format(package_name=package_name, task=task)
