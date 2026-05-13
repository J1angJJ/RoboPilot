# Tutorial: ROS1 to ROS2 Migration Scaffold Workflow

This tutorial walks through RoboPilot's static ROS1-to-ROS2 migration assistant workflow using the checked-in demo package at `examples/ros1_migration_demo/`.

No ROS installation is required. RoboPilot does not run ROS, ROS2, `catkin_make`, `colcon`, launch files, or generated nodes in this workflow.

## Prerequisites

Install RoboPilot:

```bash
pip install robopilot
```

When working from a source checkout, install it in editable mode instead:

```bash
python -m pip install -e ".[dev]"
```

On Windows with a conda environment:

```powershell
conda activate robopilot
robopilot --help
```

## Demo Package

The tutorial source package is:

```txt
examples/ros1_migration_demo/
```

It is intentionally small and illustrative. It contains ROS1-style `package.xml`, `CMakeLists.txt`, launch, Python, C++, message, service, and action files so the migration workflow has realistic structure to inspect.

## 1. Detect the Project

```bash
robopilot detect examples/ros1_migration_demo
```

Expected result: RoboPilot should classify the directory as a ROS1-style catkin package.

## 2. Inspect ROS1 Structure

```bash
robopilot inspect-ros1 examples/ros1_migration_demo
```

This reads package metadata, launch files, interface files, Python files, and C++ files statically.

## 3. Analyze Dependencies

```bash
robopilot deps examples/ros1_migration_demo
```

Review declared dependencies, detected imports/includes, and ROS1-to-ROS2 dependency hints.

## 4. Generate a Migration Plan

```bash
robopilot migrate-plan --from examples/ros1_migration_demo --to ros2 --output .pytest_tmp_v114_manual/migration_plan.yaml
```

The output plan is a review artifact. It does not edit the source project.

## 5. Validate the Plan

```bash
robopilot migrate-plan-validate --plan .pytest_tmp_v114_manual/migration_plan.yaml
```

Validation checks that the plan has the expected structure before scaffold preview or generation.

## 6. Preview the Scaffold

```bash
robopilot migrate-scaffold-preview --plan .pytest_tmp_v114_manual/migration_plan.yaml
```

This reports the target style, files RoboPilot expects to create, placeholder files, risks, conflicts, and next steps. It is read-only.

## 7. Generate the Scaffold

```bash
robopilot migrate-scaffold --plan .pytest_tmp_v114_manual/migration_plan.yaml --output .pytest_tmp_v114_manual/ros2_scaffold
```

The scaffold is conservative. It creates placeholders and notes only under the explicit output directory and refuses overwrites by default.

This is not a full automatic migration. Business logic, QoS, parameters, node lifecycle, launch behavior, interfaces, and dependencies still require manual ROS2 review.

## 8. Validate the Scaffold

```bash
robopilot migrate-scaffold-validate --plan .pytest_tmp_v114_manual/migration_plan.yaml --scaffold .pytest_tmp_v114_manual/ros2_scaffold
```

Validation checks expected scaffold files, migration notes, placeholder safety wording, static ROS2 inspection summary, issues, warnings, and suggested next steps. It does not import or execute scaffold code.

## 9. Export a Scaffold Report

```bash
robopilot migrate-scaffold-report --plan .pytest_tmp_v114_manual/migration_plan.yaml --scaffold .pytest_tmp_v114_manual/ros2_scaffold --output .pytest_tmp_v114_manual/scaffold_report.md
```

The report is a deterministic Markdown summary for review or handoff. If `--output` is omitted, RoboPilot prints the report to stdout.

## Output Files

Typical tutorial artifacts:

- `.pytest_tmp_v114_manual/migration_plan.yaml`: static migration plan
- `.pytest_tmp_v114_manual/ros2_scaffold/`: conservative ROS2 scaffold placeholders
- `.pytest_tmp_v114_manual/scaffold_report.md`: Markdown validation report

Checked-in sample artifacts live under:

- `examples/migration_outputs/`
- `examples/ros2_scaffold_demo/`

## Limitations

RoboPilot does not prove runtime correctness. Passing validation does not mean the scaffold builds, launches, or behaves correctly in ROS2.

Manual review means a developer must inspect and adapt:

- ROS2 build system selection
- dependencies and package metadata
- Python and C++ node APIs
- QoS, parameters, time, logging, and callback behavior
- launch substitutions, remaps, namespaces, and arguments
- message, service, and action interfaces

The workflow is designed to make that review visible and repeatable, not to replace it.
