# Stability Policy

This policy describes what is considered stable, experimental, or internal as of RoboPilot v1.0.0.

## Stable

Stable areas are expected to remain backward-compatible unless a major release notes otherwise.

- Existing CLI command names for core workflows.
- Documented top-level JSON keys in `docs/json_contracts.md`.
- No-ROS-required default behavior.
- Rule-based `ProjectSpec` planning and generation.
- `robopilot.yaml` as the generated ProjectSpec metadata file.
- Read-only behavior for `inspect`, `report`, `repair-suggest`, `detect`, `inspect-ros1`, `inspect-ros2`, `deps`, migration validation, migration diff, migration preview, migration scaffold preview, migration scaffold validation, and migration scaffold report generation without `--output`.
- Conservative behavior for `migrate-scaffold`: writes only to an explicit output directory, refuses overwrites by default, and does not modify the source project or migration plan.
- Dry-run-first behavior for `apply` and `rollback`.
- Confirmed apply writing only through validated apply plans.
- Rollback restoring only from RoboPilot backup directories.
- Project-local history under `.robopilot_history/`.

## Experimental

Experimental areas may change before v1.0 final as safety and usability improve.

- LLM planner.
- LLM refiner.
- ROS1-to-ROS2 migration planning.
- Migration preview.
- Migration scaffold preview.
- Migration scaffold generation.
- Migration scaffold validation.
- Migration scaffold report generation.
- Migration plan diff.
- Python API layer before a documented stable API contract.
- Nested heuristic JSON fields not documented as stable in `docs/json_contracts.md`.
- Heuristic dependency inference wording.

Experimental does not mean unsafe by default. These features should still remain static, deterministic where possible, and bounded by validation.

## Internal

Internal areas are implementation details and may change without compatibility guarantees.

- Internal module layout.
- Template rendering implementation details.
- Heuristic scoring details.
- Exact wording of non-contract CLI prose output.
- Rich human-readable CLI output.
- Private helper functions and dataclass internals not documented as public schemas.

## Compatibility Notes

After v1.0.0, documented command names, safety behavior, and stable JSON keys should change only with strong justification and changelog notes. Experimental areas may still evolve, but they must preserve RoboPilot's no-ROS-required and safety-first boundaries.

Machine consumers should use documented `--json` outputs or the Python API. They should not parse Rich human-readable output.

Post-v1.10 work should move toward v2.0 as a stage-completion release for the mature static toolchain. v2.0.0 is not necessarily a breaking rewrite; if no breaking changes are intended, release notes should say so clearly. Before v2.0, RoboPilot should avoid migration apply, automatic source conversion, ROS/ROS2 runtime execution, `colcon` execution, and launch execution.
