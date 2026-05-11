# Proposed v1.0.0 Scope

RoboPilot v1.0.0 should be the first stable release of the no-ROS-required static engineering toolchain.

## Proposed Scope

- Stable `ProjectSpec` planning, validation, generation, refinement, and diff workflow.
- Stable safe apply / rollback / history loop.
- Static project inspection, repair suggestions, and Markdown reports.
- Static ROS project detection.
- ROS1 catkin static inspection.
- Conservative dependency analyzer.
- ROS1-to-ROS2 migration plan, validation, diff, and preview workflow.
- Optional LLM planner and refiner constrained to validated `ProjectSpec` data.
- Clear documentation for command reference, workflows, architecture, safety model, and demos.
- CI-tested Python 3.10 and 3.11 support.
- No ROS runtime requirement.

## Experimental Features Carried Into v1.0

Some features may remain experimental in v1.0 while still being useful and documented:

- Optional LLM planner and refiner.
- ROS1-to-ROS2 migration planning.
- Migration plan diff.
- Migration preview.
- Conservative dependency inference heuristics.

Experimental features must still preserve RoboPilot's safety boundaries: no runtime ROS execution, no direct LLM file modification, and no migration apply without a future explicit design.

## Non-Goals

- Real ROS runtime execution.
- ROS2 runtime execution.
- `catkin_make` or `colcon` execution.
- Automatic migration apply.
- Real robot deployment.
- Simulator orchestration.
- Replacing general-purpose coding agents.
- Direct LLM code generation or direct LLM file modification.
- RAG, Streamlit, Gradio, or VSCode extension as part of the core v1.0.0 scope.

## v1.0.0 Readiness Checklist

- Core commands have stable help text.
- Testing, release process, compatibility, known limitations, and stability policy docs are present.
- JSON outputs used by tests and integrations have stable keys.
- File-writing flows are dry-run-first or explicit-output-only.
- Apply writes only through validated plans.
- Rollback restores only from RoboPilot backups.
- Migration workflows remain read-only until a future explicit migration apply design is reviewed.
- README is concise and links to detailed docs.
- Tests pass in CI and on Windows with the documented pytest temp workaround.

## Before v1.0.0-rc.1

- Run the full test suite locally and in GitHub Actions.
- Manually verify core CLI help pages.
- Review `docs/compatibility.md` and `docs/known_limitations.md`.
- Ensure `CHANGELOG.md` has release-candidate notes.
- Ensure `pyproject.toml` uses the valid Python package version `1.0.0rc1`.
- Confirm no API keys, local outputs, backups, or history entries are tracked.
- Decide whether any experimental JSON schema fields need final pre-v1 adjustments.
