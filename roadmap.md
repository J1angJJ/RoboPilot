# Roadmap

RoboPilot is a no-ROS-required static engineering toolchain for ROS-style projects.

It helps users plan, inspect, update, analyze, and migrate ROS/ROS2-style project structure without requiring ROS, ROS2, catkin, colcon, simulator runtimes, robot hardware, launch execution, or generated node execution.

## Design Direction

RoboPilot follows a spec-first and safety-first workflow:

```txt
task text
  -> planner
  -> ProjectSpec
  -> refine
  -> diff
  -> validate
  -> generate / apply-preview
  -> apply-plan
  -> apply
  -> rollback
  -> history
  -> inspect / repair-suggest / report
```

For existing ROS-style projects, RoboPilot adds static detection, inspection, dependency analysis, and migration planning.

## Completed Milestones

- v0.1.0 Basic offline MVP: generator, debugger, graph utility, docs, examples, tests, CI.
- v0.2.0 Prompt-driven template selection.
- v0.3.0 Spec-first generation.
- v0.4.0 Project inspector.
- v0.5.0 Project repair suggestions.
- v0.6.0 Project report export.
- v0.7.0 Planner interface and optional LLM planner.
- v0.8.0 Real LLM provider integration for ProjectSpec planning.
- v0.9.0 Rule-based spec refinement.
- v0.10.0 Spec diff.
- v0.11.0 LLM-assisted spec refinement.
- v0.12.0 Apply preview.
- v0.13.0 Apply plan export and validation.
- v0.14.0 Safe apply from plan.
- v0.15.0 Apply rollback.
- v0.16.0 Apply history / workspace journal.
- v0.17.0 ROS project detector.
- v0.18.0 ROS1 static inspector.
- v0.19.0 Dependency analyzer.
- v0.20.0 ROS1-to-ROS2 migration plan.
- v0.21.0 Migration apply preview.
- v0.22.0 Migration plan validation and diff.
- v0.23.0 Stability / CLI polish.

## Current: v0.24.0 v1.0 Release Candidate Preparation

Status: Current work

Goal:

Prepare RoboPilot for a future v1.0.0 release candidate by documenting testing, release process, compatibility, limitations, and stability policy.

Scope:

- Testing documentation.
- Release process documentation.
- Compatibility documentation.
- Known limitations documentation.
- Stability policy documentation.
- v1.0.0 scope updates.
- README, changelog, and roadmap link updates.

Non-goals for this milestone:

- Migration file generation.
- Migration apply.
- ROS or ROS2 runtime execution.
- `catkin_make` or `colcon` execution.
- New LLM behavior.
- Streamlit, Gradio, RAG, VSCode extension, or robot integration.

## Next Direction: v1.0.0-rc.1

The next planned milestone is `v1.0.0-rc.1`, a release candidate for the existing static toolchain.

Proposed v1.0.0 scope:

- Stable ProjectSpec workflow.
- Stable safe apply / rollback / history loop.
- Static project inspection and reporting.
- Static ROS project detection.
- ROS1 static inspection.
- Dependency analyzer.
- ROS1-to-ROS2 migration plan / validate / diff / preview.
- Optional LLM planner and refiner constrained to ProjectSpec data.
- Clear documentation and CI coverage.
- No ROS runtime requirement.

See [docs/v1_scope.md](docs/v1_scope.md) for the detailed proposed scope.

## Next: v1.0.0-rc.1

Status: Planned

Goal:

Cut a release candidate that freezes the documented command surface, safety model, compatibility notes, known limitations, and release process for broader review.

## Later Ideas

- Optional LLM report explanation.
- Migration apply-plan design.
- Migrated file generation preview.
- Lightweight VSCode wrapper around the CLI.
- Richer ROS2 static inspection.

These should stay behind the safety model: static first, preview before write, validated plans before apply, and no runtime ROS execution by default.

## Non-Goals for Early Versions

- Real robot deployment.
- Heavy model training.
- Full ROS runtime execution.
- Automatic `catkin_make`.
- Automatic `colcon build`.
- SLAM implementation.
- Reinforcement learning training.
- RAG before the core static workflow is stable.
- Replacing general-purpose coding agents.

## Development Priorities

1. Keep the CLI runnable.
2. Keep no-ROS-required usage as a core principle.
3. Keep the spec-first workflow stable.
4. Keep behavior deterministic and testable.
5. Avoid unnecessary dependencies.
6. Reuse existing validation, rendering, preview, and apply logic.
7. Make generated, inspected, and migrated outputs easy to understand.
8. Keep file-writing workflows dry-run-first and recoverable.
9. Keep documentation concise and current.
10. Add optional AI features only when they preserve deterministic safety boundaries.
