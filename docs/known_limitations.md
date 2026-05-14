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
- Migration scaffold generation creates conservative placeholders, not a complete migrated ROS2 package.
- Generated migration scaffolds are not runtime validated.
- Migration apply is not implemented.
- Automatic ROS1-to-ROS2 business logic conversion is not implemented.
- Apply only writes through validated apply plans.
- Rollback restores backed-up files but does not delete newly created files in current behavior.
- LLM output must be validated and may still be wrong or incomplete.
- Default tests do not call real LLM providers.
- Python support is limited to Python 3.10 and 3.11 for this release line; Python 3.12 is not claimed yet and Python 3.13 is not supported yet.
- Some Windows terminals may show Rich table borders or Chinese text incorrectly unless UTF-8 output is configured.
- VSCode extension is available from Visual Studio Marketplace as `j1angjj.robopilot-vscode`, and it still requires the RoboPilot CLI to be installed separately.

These limitations are part of RoboPilot's safety model. The tool should help users review structure and plans before they use real ROS tooling.
