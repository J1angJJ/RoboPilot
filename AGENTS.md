
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
21. Pytest test coverage and GitHub Actions CI.

## Current Priority

The current priority is:

```txt
v0.16.0 Apply History / Workspace Journal
```

The goal is to add a lightweight workspace history system that records apply and rollback operations.

Expected commands:

```bash
robopilot history --project outputs/demo_detector
```

Optional JSON output:

```bash
robopilot history --project outputs/demo_detector --json
```

Expected behavior:

- Record confirmed apply operations.
- Record confirmed rollback operations.
- Store journal entries under a project-local RoboPilot directory.
- List project history in readable terminal output.
- Support deterministic JSON output.
- Do not execute ROS2, launch files, colcon, or generated code.
- Do not modify project files except for writing RoboPilot history metadata.

Suggested history directory:

```txt
.robopilot_history/
```

Suggested history entry fields:

- operation type
- timestamp
- project path
- plan path if applicable
- backup path if applicable
- files created
- files updated
- files restored
- files kept
- conflicts
- dry-run status
- success status
- summary message

This feature should make apply and rollback workflows easier to audit.

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
robopilot history --project outputs/demo_detector
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

For the current history-related work, manually verify a workflow similar to:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output .pytest_tmp/base_spec.yaml
```

```bash
robopilot refine --spec .pytest_tmp/base_spec.yaml --instruction "Add a tracker node after the detector" --output .pytest_tmp/refined_spec.yaml
```

```bash
robopilot apply-plan --spec .pytest_tmp/refined_spec.yaml --project .pytest_tmp/history_target --output .pytest_tmp/apply_plan.yaml
```

```bash
robopilot apply --plan .pytest_tmp/apply_plan.yaml --confirm
```

```bash
robopilot history --project .pytest_tmp/history_target
```

If rollback history is implemented, also verify:

```bash
robopilot rollback --project .pytest_tmp/history_target --backup <backup_dir> --confirm
```

```bash
robopilot history --project .pytest_tmp/history_target --json
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
v0.16.0 Apply History / Workspace Journal
```

The history system should support:

```bash
robopilot history --project outputs/demo_detector
```

Optional JSON output:

```bash
robopilot history --project outputs/demo_detector --json
```

The history system should record confirmed apply operations and confirmed rollback operations.

It should not record dry-runs as successful modifications. If dry-run entries are recorded in the future, they must be clearly marked as dry-run and must not be confused with confirmed project changes.

Suggested implementation files:

```txt
src/robopilot/history/
├─ __init__.py
└─ journal.py
```

Suggested tests:

```txt
tests/test_history.py
```

The journal should be deterministic and testable.

Do not start ROS1/ROS2 project detection, ROS1 static inspection, dependency analysis, ROS1-to-ROS2 migration, VSCode integration, RAG, Streamlit UI, or broad multi-agent orchestration until the current apply/history safety loop is stable.
