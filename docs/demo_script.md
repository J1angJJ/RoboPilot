# RoboPilot Demo Script

This script is a short walkthrough for recording a demo video, presenting the project, or manually checking the current MVP.

## 1. Introduce the Project

RoboPilot is a lightweight offline developer tool for ROS-style robotics workflows.

Key message:

- It does not require ROS2.
- It does not require a GPU.
- It does not call an external LLM API.
- It focuses on local, reproducible robotics development helpers.

Current core commands:

- `robopilot plan`
- `robopilot refine`
- `robopilot diff`
- `robopilot validate`
- `robopilot apply-preview`
- `robopilot apply-plan`
- `robopilot apply-plan-validate`
- `robopilot apply`
- `robopilot rollback`
- `robopilot history`
- `robopilot detect`
- `robopilot inspect-ros1`
- `robopilot deps`
- `robopilot migrate-plan`
- `robopilot generate`
- `robopilot inspect`
- `robopilot repair-suggest`
- `robopilot report`
- `robopilot debug`
- `robopilot graph`

## 2. Install and Check the CLI

```bash
pip install -e ".[dev]"
robopilot --help
```

Expected result:

The CLI lists the available commands, including `plan`, `refine`, `diff`, `validate`, `apply-preview`, `apply-plan`, `apply-plan-validate`, `apply`, `rollback`, `history`, `detect`, `inspect-ros1`, `deps`, `migrate-plan`, `generate`, `inspect`, `repair-suggest`, `report`, `debug`, and `graph`.

## 3. Demo: Plan a ProjectSpec

Run:

```bash
robopilot plan --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes." --output robopilot.yaml
```

Point out:

- RoboPilot first converts the task into a structured ProjectSpec.
- The spec records the package name, selected template, nodes, topics, config files, launch files, and notes.
- The spec is saved as `robopilot.yaml` and can be reviewed before generation.

Refine the spec:

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --planner rule --output refined.yaml
```

Diff the base and refined specs:

```bash
robopilot diff --old robopilot.yaml --new refined.yaml
robopilot diff --old robopilot.yaml --new refined.yaml --json
```

Validate the refined spec:

```bash
robopilot validate --spec refined.yaml
```

Preview applying the refined spec to an existing project:

```bash
robopilot apply-preview --spec refined.yaml --project examples/generated_projects/demo_detector
robopilot apply-preview --spec refined.yaml --project examples/generated_projects/demo_detector --json
```

Export and validate a read-only apply plan:

```bash
robopilot apply-plan --spec refined.yaml --project examples/generated_projects/demo_detector --output apply_plan.yaml
robopilot apply-plan-validate --plan apply_plan.yaml
robopilot apply-plan --spec refined.yaml --project examples/generated_projects/demo_detector --output apply_plan.json --format json
```

Dry-run or confirm apply from the plan:

```bash
robopilot apply --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml --confirm
```

Dry-run or confirm rollback from a RoboPilot backup:

```bash
robopilot rollback --project examples/generated_projects/demo_detector --backup examples/generated_projects/demo_detector/.robopilot_backups/<timestamp>
robopilot rollback --project examples/generated_projects/demo_detector --backup examples/generated_projects/demo_detector/.robopilot_backups/<timestamp> --confirm
```

Show project-local history:

```bash
robopilot history --project examples/generated_projects/demo_detector
robopilot history --project examples/generated_projects/demo_detector --json
```

Detect project type:

```bash
robopilot detect examples/generated_projects/demo_detector
robopilot detect examples/generated_projects/demo_detector --json
```

Inspect a ROS1 catkin package statically:

```bash
robopilot inspect-ros1 .pytest_tmp/ros1_demo
robopilot inspect-ros1 .pytest_tmp/ros1_demo --json
```

Analyze dependencies statically:

```bash
robopilot deps .pytest_tmp/ros1_dep_demo
robopilot deps .pytest_tmp/ros1_dep_demo --json
```

Create a ROS1-to-ROS2 migration plan:

```bash
robopilot migrate-plan --from .pytest_tmp/ros1_migration_demo --to ros2 --output .pytest_tmp/migration_plan.yaml
robopilot migrate-plan --from .pytest_tmp/ros1_migration_demo --to ros2 --output .pytest_tmp/migration_plan.json --format json
```

Point out:

- `refine` loads an existing ProjectSpec and writes a new refined spec.
- The original spec is not modified.
- v0.9.0 refinement is deterministic and rule-based.
- v0.10.0 diff is static, read-only, and validates both specs before comparison.
- v0.11.0 adds optional LLM-assisted refinement that still returns only ProjectSpec-compatible data.
- v0.12.0 apply-preview compares a spec to a project directory without modifying files.
- v0.13.0 apply-plan exports the preview result for review without modifying files.
- v0.14.0 apply is dry-run by default and only writes with `--confirm`.
- Existing files are backed up before update, and conflicts stop apply.
- v0.15.0 rollback is dry-run by default and only restores with `--confirm`.
- Rollback restores only files from a RoboPilot backup and does not delete newly created files.
- v0.16.0 history records confirmed apply and rollback operations under `.robopilot_history/`.
- History entries are project-local metadata and do not include file contents.
- v0.17.0 detect classifies RoboPilot, ROS1 catkin, ROS2 ament Python, ROS2 ament C++, mixed ROS-style, non-ROS, and unknown projects.
- Detection is static: it does not import user modules, execute launch files, run catkin, or run colcon.
- v0.18.0 inspect-ros1 extracts ROS1 package metadata, dependencies, catkin signals, files, node candidates, and package issues.
- ROS1 inspection is static: it does not require ROS, import user modules, execute launch files, run `catkin_make`, or run colcon.
- v0.19.0 deps reports declared dependencies, detected usage, possibly missing dependencies, possibly unused dependencies, and conservative hints.
- Dependency analysis is static: it does not require ROS, import user modules, execute launch files, run `catkin_make`, or run colcon.
- v0.20.0 migrate-plan creates a static ROS1-to-ROS2 migration plan from detect, inspect-ros1, and deps results.
- Migration planning is read-only: it does not modify source files, generate migrated files, run ROS, run `catkin_make`, or run colcon.
- Real LLM refinement requires `OPENAI_API_KEY`.
- Run `robopilot diff` before generating from an LLM-refined spec.

Optional LLM refinement:

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --planner llm --model gpt-4.1-mini --output llm_refined.yaml
robopilot diff --old robopilot.yaml --new llm_refined.yaml
```

Planner selection:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner rule
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner llm
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner llm --model gpt-4.1-mini
```

Point out:

- `--planner rule` is the default and remains fully offline.
- `--planner llm` is optional, provider-backed, and ProjectSpec-only.
- Real LLM planning requires `OPENAI_API_KEY`.
- `ROBOPILOT_LLM_MODEL` or `--model` controls the model name.
- The provider must return structured JSON or YAML; RoboPilot validates it before generation.
- The LLM never writes project files or generated code directly.

## 4. Demo: Generate a ROS-style Package

Run:

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

Spec-first generation:

```bash
robopilot generate --spec refined.yaml
```

Point out:

- Output is written to `outputs/demo_detector/`.
- Existing output directories are protected by default.
- The generated files follow ROS-style Python package conventions without requiring ROS2.

Expected generated layout:

```txt
outputs/demo_detector/
|-- package.xml
|-- setup.py
|-- setup.cfg
|-- README.md
|-- robopilot.yaml
|-- launch/
|   `-- demo_detector.launch.py
|-- config/
|   `-- params.yaml
`-- demo_detector/
    |-- __init__.py
    `-- detector_node.py
```

Static showcase version:

```txt
examples/generated_projects/demo_detector/
```

## 5. Demo: Inspect the Generated Project

Run:

```bash
robopilot inspect examples/generated_projects/demo_detector
```

Point out:

- The inspector does not run ROS2, launch files, colcon, or generated Python code.
- It reports package files, launch files, config files, Python node files, README status, and spec status.
- It reuses the existing `robopilot.yaml` loader and validator.

JSON mode:

```bash
robopilot inspect examples/generated_projects/demo_detector --json
```

## 6. Demo: Suggest Safe Repairs

Run:

```bash
robopilot repair-suggest examples/generated_projects/demo_detector
```

Point out:

- The repair suggester reuses the Project Inspector.
- It maps detected issues to deterministic suggestions and commands.
- It does not modify files automatically and does not implement `--apply`.

JSON mode:

```bash
robopilot repair-suggest examples/generated_projects/demo_detector --json
```

## 7. Demo: Export a Project Report

Run:

```bash
robopilot report examples/generated_projects/demo_detector
```

Point out:

- The report combines static inspection and repair suggestions.
- It is deterministic Markdown for demos, reviews, or issue sharing.
- It is static and read-only; RoboPilot does not execute ROS2, launch files, colcon, or generated Python code.

Write to a file:

```bash
robopilot report examples/generated_projects/demo_detector --output .pytest_tmp/demo_report.md
```

## 8. Demo: Inspect a ROS1 Catkin Package

Use a temporary ROS1-style package for the demo, then run:

```bash
robopilot detect .pytest_tmp/ros1_demo
robopilot inspect-ros1 .pytest_tmp/ros1_demo
robopilot inspect-ros1 .pytest_tmp/ros1_demo --json
```

Point out:

- The inspector reuses static project detection as context.
- It reads `package.xml`, `CMakeLists.txt`, `launch/`, `scripts/`, `src/`, `msg/`, `srv/`, `action/`, Python files, and C++ files.
- It reports dependencies, catkin components, `catkin_package()`, ROS1 node candidates, issues, and suggested next steps.
- It never imports project modules, runs ROS, runs `catkin_make`, executes launch files, or executes user code.

## 9. Demo: Analyze Dependencies

Use a temporary ROS-style package for the demo, then run:

```bash
robopilot deps .pytest_tmp/ros1_dep_demo
robopilot deps .pytest_tmp/ros1_dep_demo --json
```

Point out:

- The analyzer reuses static project detection for project type context.
- It reads `package.xml`, `CMakeLists.txt`, setup files, Python imports, C++ includes, launch references, and msg/srv/action directories.
- It reports declared dependencies, detected usage, inferred dependencies, possibly missing dependencies, possibly unused dependencies, and hints.
- It uses conservative wording and does not claim certainty from weak static signals.
- It never imports project modules, runs ROS, runs `catkin_make`, runs colcon, executes launch files, or executes user code.

## 10. Demo: Analyze an Error Log

## 10. Demo: Plan ROS1 to ROS2 Migration

Use a temporary ROS1 catkin package for the demo, then run:

```bash
robopilot detect .pytest_tmp/ros1_migration_demo
robopilot inspect-ros1 .pytest_tmp/ros1_migration_demo
robopilot deps .pytest_tmp/ros1_migration_demo
robopilot migrate-plan --from .pytest_tmp/ros1_migration_demo --to ros2 --output .pytest_tmp/migration_plan.yaml
robopilot migrate-plan --from .pytest_tmp/ros1_migration_demo --to ros2 --output .pytest_tmp/migration_plan.json --format json
```

Point out:

- The planner reuses `detect`, `inspect-ros1`, and `deps` results.
- It produces package.xml, build system, source code, launch, interface, dependency, suggested file change, manual review, risk, and next-step sections.
- It only writes the migration plan output file.
- It does not modify the source project, generate migrated files, run ROS, run `catkin_make`, run colcon, execute launch files, or execute user code.

## 11. Demo: Analyze an Error Log

Run:

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
```

Point out the structured output:

- Error type
- Diagnosis
- Possible causes
- Suggested fixes
- Confidence level

Inline mode:

```bash
robopilot debug --text "ModuleNotFoundError: No module named 'cv_bridge'"
```

## 12. Demo: Generate a Workflow Graph

Run:

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

Expected output:

```mermaid
graph LR
    camera --> detector
    detector --> tracker
    tracker --> planner
    planner --> controller
```

Write to a file:

```bash
robopilot graph --pipeline "camera -> detector -> tracker" --output examples/graphs/demo_pipeline.mmd
```

## 13. Show Example Assets

Useful files to open during a demo:

- `examples/prompts/demo_detector.txt`
- `examples/generated_projects/demo_detector/robopilot.yaml`
- `examples/generated_projects/demo_detector/demo_detector/detector_node.py`
- `examples/generated_projects/demo_detector/package.xml`
- `examples/error_logs/cv_bridge_missing.txt`
- `examples/graphs/demo_pipeline.mmd`

## 14. Run Tests

```bash
pytest
```

Windows fallback if the default temp directory is blocked:

```powershell
New-Item -ItemType Directory -Path .pytest_tmp -Force
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

## 15. Close with Roadmap

Current implemented MVPs:

- MVP 0.1: Offline ROS-style Package Generator
- MVP 0.2: Robotics Error Log Debugger
- MVP 0.3: Workflow Diagram Generator
- MVP 0.4: Prompt-driven Template Selection
- MVP 0.5: Spec-first Generation
- MVP 0.6: Project Inspector
- v0.5.0: Project Repair Suggestions
- v0.6.0: Project Report Export
- v0.7.0: Planner Interface and Optional LLM Planner
- v0.8.0: Real OpenAI Provider Integration
- v0.9.0: Rule-based ProjectSpec Refinement
- v0.10.0: Static ProjectSpec Diff
- v0.11.0: Optional LLM-assisted ProjectSpec Refinement
- v0.12.0: Read-only Apply Preview
- v0.13.0: Read-only Apply Plan Export
- v0.14.0: Safe Apply from Plan
- v0.15.0: Safe Apply Rollback
- v0.16.0: Apply History / Workspace Journal
- v0.17.0: ROS Project Detector
- v0.18.0: ROS1 Static Inspector
- v0.19.0: Dependency Analyzer
- v0.20.0: ROS1 to ROS2 Migration Plan

Next planned work:

- Migration Apply Preview
- Optional LLM Report Explanation
