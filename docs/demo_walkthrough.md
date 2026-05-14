# Demo Walkthrough

This is a short presentation script for showing RoboPilot's no-ROS-required migration scaffold workflow.

## 5-Minute CLI Demo

Start with the static ROS1 demo package:

```bash
robopilot detect examples/ros1_migration_demo
robopilot inspect-ros1 examples/ros1_migration_demo
robopilot deps examples/ros1_migration_demo
```

Talking points:

- RoboPilot reads ROS-style project structure without requiring ROS.
- Dependency hints are static and conservative.
- The demo package is intentionally small, not production ROS code.

Generate and review the migration workflow artifacts:

```bash
robopilot migrate-plan --from examples/ros1_migration_demo --to ros2 --output .pytest_tmp_v115_manual/migration_plan.yaml
robopilot migrate-plan-validate --plan .pytest_tmp_v115_manual/migration_plan.yaml
robopilot migrate-scaffold-preview --plan .pytest_tmp_v115_manual/migration_plan.yaml
robopilot migrate-scaffold --plan .pytest_tmp_v115_manual/migration_plan.yaml --output .pytest_tmp_v115_manual/ros2_scaffold
robopilot migrate-scaffold-validate --plan .pytest_tmp_v115_manual/migration_plan.yaml --scaffold .pytest_tmp_v115_manual/ros2_scaffold
robopilot migrate-scaffold-report --plan .pytest_tmp_v115_manual/migration_plan.yaml --scaffold .pytest_tmp_v115_manual/ros2_scaffold --output .pytest_tmp_v115_manual/scaffold_report.md
```

Expected artifacts:

- `.pytest_tmp_v115_manual/migration_plan.yaml`
- `.pytest_tmp_v115_manual/ros2_scaffold/`
- `.pytest_tmp_v115_manual/scaffold_report.md`

Safety reminders:

- The source package is not modified.
- The scaffold is written only to the explicit output directory.
- RoboPilot does not run ROS, ROS2, `catkin_make`, `colcon`, launch files, or generated code.
- Passing scaffold validation is not runtime validation.

Suggested screenshots or artifacts:

- migration plan summary
- scaffold validation summary
- `MIGRATION_NOTES.md`
- `scaffold_report.md` summary and `What To Do Next`

## 5-Minute VSCode Demo

Open the repository in VSCode and run:

```txt
RoboPilot: Detect Workspace
RoboPilot: Generate Migration Plan
RoboPilot: Preview Migration Scaffold
RoboPilot: Generate Migration Scaffold
RoboPilot: Validate Migration Scaffold
RoboPilot: Generate Scaffold Report
RoboPilot: Open Scaffold Report
```

Talking points:

- The extension is a thin wrapper over the CLI and JSON contracts.
- Outputs go under `.robopilot_vscode/` by default.
- The OutputChannel is the main review surface.
- The workflow is suitable for beginner-friendly review without hiding manual migration work.

Expected VSCode artifacts:

- `.robopilot_vscode/migration_plan.json`
- `.robopilot_vscode/ros2_scaffold/`
- `.robopilot_vscode/scaffold_report.md`

## Closing Notes

Use the checked-in examples for demonstrations:

- `examples/ros1_migration_demo/`
- `examples/ros2_scaffold_demo/`
- `examples/migration_outputs/`

Keep the message simple: RoboPilot helps plan, scaffold, validate, and report migration work, but it does not automatically port or run a ROS project.
