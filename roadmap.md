# Roadmap

RoboPilot is developed as a lightweight AI-native robotics development assistant for ROS-style workflows.

The project is moving from a simple template generator toward a spec-first robotics developer toolchain:

```txt
natural language task
        -> ProjectSpec
        -> validate spec
        -> generate ROS-style package
        -> inspect generated or existing project
        -> repair suggestions
        -> Markdown report export
        -> apply preview / apply plan / apply / rollback
```

The long-term goal is to make RoboPilot a practical robotics developer assistant that can plan, validate, generate, inspect, visualize, debug, preview, apply, and roll back robotics software workflow changes without requiring a full ROS2 runtime environment.

## Completed: v0.1.0 Basic Offline MVP

Status: Completed

Completed features:

- Offline ROS-style package generator
- Robotics error log debugger
- Pipeline-to-Mermaid workflow graph generator
- English README
- Chinese README
- Demo script
- Static generated example project
- Pytest tests
- GitHub Actions CI

Core commands:

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

## Completed Milestones

- v0.2.0 Prompt-driven Template Selection
- v0.3.0 Spec-first Generation
- v0.4.0 Project Inspector
- v0.5.0 Project Repair Suggestions
- v0.6.0 Project Report Export
- v0.7.0 Planner Interface + Optional LLM Planner
- v0.8.0 Real LLM Provider Integration
- v0.9.0 Spec Refinement
- v0.10.0 Spec Diff
- v0.11.0 LLM-assisted Spec Refinement
- v0.12.0 Apply Preview
- v0.13.0 Apply Plan Export
- v0.14.0 Apply from Plan

## Current: v0.15.0 Apply Rollback

Status: Current work

Goal:

Restore files from a RoboPilot backup directory created during `robopilot apply --confirm`.

Commands:

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp>
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --confirm
```

Requirements:

- Dry-run by default.
- Require `--confirm` before restoring files.
- Require the project path to exist.
- Require the backup path to exist and be a directory.
- Require backups to live under the project's `.robopilot_backups/` directory.
- Refuse unsafe relative paths and path traversal.
- Restore only files contained in the backup directory.
- Preserve relative paths and create parent directories as needed.
- Do not delete newly created files in this version.
- Never execute ROS2, launch files, colcon, or generated Python code.

## Future: v0.16.0 Apply Hardening

Status: Planned

Goal:

Improve conflict explanations, rollback guidance, stale-plan messaging, and human review ergonomics for apply workflows.

## Future: v0.17.0 Web Demo

Status: Planned

Goal:

Create a lightweight optional web demo for showcasing RoboPilot workflows. This should not become a required dependency for CLI usage.

## Future: VSCode Integration

Status: Long-term idea

Explore a VSCode extension or VSCode-friendly workflow after the CLI workflow becomes stable.

## Non-goals for Early Versions

- Real robot deployment
- Heavy model training
- Full ROS2 runtime execution
- Automatic `colcon build`
- SLAM implementation
- Reinforcement learning training
- Large-scale VLA model inference
- Embedded low-level driver development
- Complex multi-agent orchestration
- RAG system before the core workflow is stable

## Development Priorities

1. Keep the CLI runnable.
2. Keep the spec-first workflow stable.
3. Keep behavior deterministic and testable.
4. Avoid unnecessary dependencies.
5. Reuse existing validation and spec logic.
6. Make generated and inspected outputs easy to understand.
7. Keep documentation concise and current.
8. Add optional AI features only after deterministic workflows are reliable.

## Current Recommended Development Path

```txt
v0.15.0 Apply Rollback
        -> v0.16.0 Apply Hardening
        -> v0.17.0 Web Demo
        -> VSCode Integration
```

RoboPilot should grow as a practical robotics developer toolchain, not as a one-time demo script.
