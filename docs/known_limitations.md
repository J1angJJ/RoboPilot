# Known Limitations

RoboPilot is a static engineering toolchain. It intentionally does not replace a real ROS or ROS2 runtime environment.

Current limitations:

- No runtime ROS validation.
- No runtime ROS2 validation.
- No `catkin_make` build validation.
- No `colcon` build validation.
- No launch file execution.
- No generated node execution.
- Static dependency inference may be incomplete.
- CMake parsing is conservative and string/regex based.
- Launch parsing is limited to simple static references.
- Project detection is heuristic.
- ROS1-to-ROS2 migration planning is advisory.
- Migration preview does not generate migrated files.
- Migration apply is not implemented.
- Apply only writes through validated apply plans.
- Rollback restores backed-up files but does not delete newly created files in current behavior.
- LLM output must be validated and may still be wrong or incomplete.
- Default tests do not call real LLM providers.
- VSCode extension is not implemented yet.

These limitations are part of RoboPilot's safety model. The tool should help users review structure and plans before they use real ROS tooling.
