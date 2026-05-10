# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- v0.2.0 prompt-driven template selection for `robopilot generate`.
- Offline task classification for `camera_subscriber`, `object_detection`,
  `velocity_controller`, `perception_pipeline`, and `generic_node` templates.
- Generated `robopilot.yaml` metadata with package name, task, selected template,
  generator name, and notes.
- Template registry and project specification layer for deterministic generation.

## [0.1.0] - 2026-05-09

### Added

- Offline ROS-style package generator with safe default output behavior.
- Offline robotics error log debugger for common development errors.
- Pipeline-to-Mermaid workflow graph generator.
- English and Chinese README files.
- Demo script for project walkthroughs.
- Static generated example project for GitHub showcase demos.
- Example prompts, error logs, and Mermaid graph assets.
- Pytest coverage for generator, debugger, and graph modules.
