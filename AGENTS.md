
# AGENTS.md

## Project Goal

RoboPilot is a no-ROS-required static engineering toolchain for ROS-style projects.

It helps robotics learners and developers plan, refine, validate, generate, inspect, update, roll back, document, and eventually migrate ROS/ROS2-style projects without requiring a local ROS installation.

RoboPilot should grow as a practical developer toolchain, not as a general-purpose coding agent and not as a runtime ROS automation tool.

## Product Positioning

RoboPilot is intentionally designed to work without:

- ROS installation
- ROS2 installation
- catkin workspace
- colcon workspace
- robot hardware
- simulator runtime
- launch execution
- generated node execution

The core value is static engineering support:

```txt
spec-first project planning
static project inspection
safe project updates
dependency and structure analysis
ROS1 / ROS2 migration assistance
optional LLM-assisted ProjectSpec workflows
```

RoboPilot should avoid competing directly with general coding agents. Its niche is ROS-style project structure, static analysis, safe update planning, and migration support.

## Current Architecture

RoboPilot currently follows a spec-first and safety-first workflow:

```txt
natural language task
        ↓
planner
        ↓
ProjectSpec
        ↓
refine
        ↓
diff
        ↓
validate
        ↓
apply-preview
        ↓
apply-plan
        ↓
apply
        ↓
rollback
        ↓
inspect
        ↓
repair-suggest
        ↓
report
```

The central design principle is:

```txt
LLM or rule-based planner/refiner may produce or refine ProjectSpec.
RoboPilot validates ProjectSpec.
RoboPilot deterministically renders files.
RoboPilot previews changes before writing.
RoboPilot writes only through validated plans.
RoboPilot backs up before updating.
RoboPilot supports rollback from backups.
```

Do not bypass the `ProjectSpec` workflow when adding planning, refinement, generation, apply, or migration-related features.

## Current Capabilities

RoboPilot currently supports:

1. Offline ROS-style project generation.
2. Prompt-driven template selection.
3. Structured `ProjectSpec` generation.
4. Spec validation.
5. Generation from `robopilot.yaml`.
6. Spec refinement.
7. LLM-assisted spec refinement.
8. Spec diff.
9. Apply preview.
10. Apply plan export.
11. Apply plan validation.
12. Safe apply from plan.
13. Rollback from RoboPilot backups.
14. Static project inspection.
15. Read-only repair suggestions.
16. Markdown project report export.
17. Robotics error log debugging.
18. Mermaid workflow graph generation.
19. Optional LLM planner and refiner.
20. English and Chinese documentation.
21. ROS project detection without requiring ROS.
22. ROS1 static inspection without requiring ROS.
23. Dependency analysis without requiring ROS.
24. ROS1-to-ROS2 static migration planning.
25. Pytest test coverage and GitHub Actions CI.

## Current Priority

The current priority is:

```txt
v0.20.0 ROS1 to ROS2 Migration Plan
```

The goal is to add a no-ROS-required static migration planning command for ROS1 catkin packages moving toward ROS2-style structure.

Expected commands:

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
```

Optional JSON output:

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.json --format json
```

Expected behavior:

- Reuse `detect_project`, `inspect_ros1_project`, and dependency analysis.
- Generate package.xml, build system, source code, launch, interface, dependency, suggested file change, manual review, risk, and next-step sections.
- Support deterministic YAML-like and JSON output.
- Do not require ROS or ROS2.
- Do not run `catkin_make` or colcon.
- Do not execute launch files or generated code.
- Do not import user project modules.
- Do not modify the source project or generate migrated files.

## Important Constraints

- Do NOT require a real ROS installation.
- Do NOT require a real ROS2 installation.
- Do NOT require a GPU.
- Do NOT require Docker.
- Do NOT run heavy model training.
- Do NOT execute generated ROS nodes.
- Do NOT execute launch files.
- Do NOT run `catkin_make`.
- Do NOT run `colcon build`.
- Do NOT call OpenAI API or any LLM API unless the task explicitly involves optional LLM planning or refinement.
- Do NOT add LangChain, Streamlit, Gradio, RAG, VSCode extension, or large frameworks unless explicitly requested.
- Prefer pure Python implementations.
- Keep the project lightweight and easy to clone, install, test, and understand.
- Generated code may be ROS/ROS2-style pseudocode if runtime support is not available.
- Static analysis must not execute user code.

## Development Philosophy

RoboPilot should feel like a real developer toolchain.

Prioritize:

- clear architecture
- stable `ProjectSpec` workflow
- no-ROS-required usage
- deterministic behavior
- safe file operations
- dry-run-first workflows
- backup and rollback support
- auditable project updates
- testable modules
- readable generated files
- useful CLI output
- concise documentation
- minimal dependencies
- backward compatibility with existing commands

Avoid:

- overengineering
- unnecessary multi-agent architecture
- heavy framework lock-in
- unstable LLM-only behavior
- direct LLM code generation
- direct LLM file modification
- features that require unavailable hardware or runtime environments
- changing public CLI behavior without updating tests and documentation
- duplicating validation, rendering, or preview logic instead of reusing existing modules

## Recommended Tech Stack

- Python 3.10+
- Typer for CLI
- Rich for terminal output
- Pytest for tests
- pathlib for file operations
- built-in serialization helpers for RoboPilot's limited YAML-like schemas

Optional dependencies:

- OpenAI SDK for optional LLM-powered planning/refinement

Do not add optional dependencies unless they are required for the current task.

## Code Style

- Use type hints.
- Prefer `pathlib.Path` over `os.path`.
- Keep functions small and focused.
- Separate CLI code from business logic.
- Separate templates from file-writing logic.
- Reuse existing spec loader and validator where possible.
- Reuse existing apply-preview and rendering logic where possible.
- Reuse existing apply-plan validation where possible.
- Use clear function and variable names.
- Add docstrings for public functions.
- Avoid hidden side effects.
- Avoid global mutable state.
- Keep output deterministic for tests.
- Keep JSON output keys stable once introduced.

## Expected Core Package Structure

Current and expected package structure:

```txt
src/robopilot/
├─ __init__.py
├─ main.py
├─ generator/
│  ├─ __init__.py
│  ├─ project_generator.py
│  ├─ project_spec.py
│  ├─ task_classifier.py
│  ├─ template_registry.py
│  └─ templates.py
├─ spec/
│  ├─ __init__.py
│  ├─ io.py
│  └─ validator.py
├─ planner/
│  ├─ __init__.py
│  ├─ base.py
│  ├─ rule_based_planner.py
│  ├─ llm_planner.py
│  ├─ openai_client.py
│  ├─ provider_config.py
│  └─ prompts.py
├─ refiner/
│  ├─ __init__.py
│  ├─ spec_refiner.py
│  └─ llm_refiner.py
├─ diff/
│  ├─ __init__.py
│  └─ spec_diff.py
├─ apply_preview/
│  ├─ __init__.py
│  └─ preview.py
├─ apply_plan/
│  ├─ __init__.py
│  └─ plan.py
├─ apply/
│  ├─ __init__.py
│  └─ apply_plan.py
├─ rollback/
│  ├─ __init__.py
│  └─ rollback.py
├─ history/
│  ├─ __init__.py
│  └─ journal.py
├─ detector/
│  ├─ __init__.py
│  └─ project_detector.py
├─ inspector/
│  ├─ __init__.py
│  └─ project_inspector.py
├─ repair/
│  ├─ __init__.py
│  └─ repair_suggester.py
├─ report/
│  ├─ __init__.py
│  └─ project_report.py
├─ debugger/
│  ├─ __init__.py
│  └─ log_analyzer.py
├─ graph/
│  ├─ __init__.py
│  └─ mermaid_generator.py
└─ utils/
   └─ file_ops.py
```

Documentation and examples:

```txt
docs/
├─ architecture.md
├─ demo_script.md
└─ screenshots/

examples/
├─ prompts/
├─ error_logs/
├─ pipelines/
├─ graphs/
└─ generated_projects/

tests/
```

If a directory does not exist yet, create it only when needed by the current task.

## Safety Rules

- Never delete user files automatically.
- Never overwrite existing files unless explicitly allowed.
- Default behavior for file-writing operations should be dry-run when practical.
- Confirmed file-writing operations must require explicit flags such as `--confirm`.
- Generated projects should be written to `outputs/` by default.
- Do not commit generated temporary outputs from `outputs/`.
- Never commit API keys, tokens, private paths, local environment files, logs, backups, or local history artifacts.
- Never assume the user has ROS or ROS2 installed.
- Never require external services for default offline features.
- Static inspection must not execute user code.
- Static detection must not execute user code or import user modules.
- Apply must only write files listed in a validated apply plan.
- Rollback must only restore files from a RoboPilot backup.
- History / journal writing must only write RoboPilot metadata under `.robopilot_history/`.

## Existing CLI Commands

The following commands should remain supported:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output robopilot.yaml
```

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner llm --output robopilot.yaml
```

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
```

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --planner llm --output refined.yaml
```

```bash
robopilot diff --old robopilot.yaml --new refined.yaml
```

```bash
robopilot validate --spec refined.yaml
```

```bash
robopilot generate --spec refined.yaml
```

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
```

```bash
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
```

```bash
robopilot apply-plan-validate --plan apply_plan.yaml
```

```bash
robopilot apply --plan apply_plan.yaml
```

```bash
robopilot apply --plan apply_plan.yaml --confirm
```

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp>
```

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --confirm
```

```bash
robopilot history --project outputs/demo_detector
```

```bash
robopilot detect outputs/demo_detector
```

```bash
robopilot inspect-ros1 path/to/ros1_package
```

```bash
robopilot deps path/to/project
```

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
```

```bash
robopilot inspect outputs/demo_detector
```

```bash
robopilot repair-suggest outputs/demo_detector
```

```bash
robopilot report outputs/demo_detector --output report.md
```

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
```

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

The next planned command is:

```bash
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package
```

## ProjectSpec Rules

`ProjectSpec` is the central intermediate representation.

Generation, refinement, migration, and apply-related features should flow through `ProjectSpec` or through validated plans derived from `ProjectSpec`.

A valid spec should include at least:

- package name
- original task
- selected template
- nodes
- topics or topic-like fields when applicable
- config files
- launch files
- generator name
- notes

Generated projects should include a `robopilot.yaml` file.

`robopilot.yaml` should be usable as input for:

```bash
robopilot generate --spec robopilot.yaml
```

Validation logic should live in the spec validation module and should be reused by generator, inspector, refiner, diff, apply-preview, apply-plan, apply, and future migration modules.

## LLM Rules

LLM features are optional.

The default workflow must remain offline.

LLM components may:

- generate ProjectSpec
- refine ProjectSpec
- explain reports in future versions

LLM components must not:

- directly write project files
- directly generate arbitrary source files
- execute commands
- bypass validation
- bypass diff review
- bypass apply-preview or apply-plan
- modify files without explicit apply workflow

Expected safe LLM path:

```txt
LLM output
        ↓
ProjectSpec
        ↓
validate
        ↓
diff / preview
        ↓
deterministic generation or apply
```

## Testing

Before finalizing a change, run:

```bash
python -m pytest
```

On Windows, if pytest cannot access the default temporary directory, run:

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

For CLI-related changes, also run relevant commands manually.

For the current migration planning work, manually verify commands similar to:

```bash
robopilot detect .pytest_tmp/ros1_migration_demo
```

```bash
robopilot inspect-ros1 .pytest_tmp/ros1_migration_demo
```

```bash
robopilot deps .pytest_tmp/ros1_migration_demo
```

```bash
robopilot migrate-plan --from .pytest_tmp/ros1_migration_demo --to ros2 --output .pytest_tmp/migration_plan.yaml
```

```bash
robopilot migrate-plan --from .pytest_tmp/ros1_migration_demo --to ros2 --output .pytest_tmp/migration_plan.json --format json
```

## Preferred Development Workflow

1. Read `README.md`, `README.zh-CN.md`, `roadmap.md`, `CHANGELOG.md`, `pyproject.toml`, and this file first.
2. Understand the existing architecture before editing.
3. Implement one small feature at a time.
4. Reuse existing modules instead of duplicating logic.
5. Add or update tests.
6. Run tests.
7. Run relevant CLI commands manually.
8. Update README and demo docs when behavior changes.
9. Update `CHANGELOG.md` under `Unreleased`.
10. Summarize changed files, design decisions, and test results.

## Current Implementation Target

Implement:

```txt
v0.20.0 ROS1 to ROS2 Migration Plan
```

The migration planner should support:

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
```

Optional JSON output:

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.json --format json
```

Suggested implementation files:

```txt
src/robopilot/migration/
├─ __init__.py
└─ ros1_to_ros2.py
```

Suggested tests:

```txt
tests/test_ros1_to_ros2_migration_plan.py
```

The migration planner should be static, deterministic, conservative, and testable. It must not require ROS, ROS2, catkin, colcon, launch execution, generated code execution, source project modification, or user module imports.

Do not start migration apply preview, migration apply, VSCode integration, RAG, Streamlit UI, or broad multi-agent orchestration until migration planning is stable.
