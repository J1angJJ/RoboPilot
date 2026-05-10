
# Roadmap

RoboPilot is developed as a lightweight AI-native robotics development assistant for ROS-style workflows.

The project is moving from a simple template generator toward a spec-first robotics developer toolchain.

## Design Direction

RoboPilot follows a spec-first architecture:

```txt
natural language task
        ↓
ProjectSpec
        ↓
validate spec
        ↓
generate ROS-style package
        ↓
inspect generated or existing project
        ↓
repair suggestions
        ↓
Markdown report export
```

The long-term goal is to make RoboPilot a practical robotics developer assistant that can plan, validate, generate, inspect, visualize, and debug robotics software workflows without requiring a full ROS2 runtime environment.

## Completed: v0.1.0 Basic Offline MVP

Status: Completed

Goal:

Build the first runnable offline MVP.

Completed features:

- Offline ROS-style package generator
- Robotics error log debugger
- Pipeline-to-Mermaid workflow graph generator
- English README
- Chinese README
- Demo script
- Static generated example project
- Pytest tests
- GitHub Actions CI
- GitHub Release

Core commands:

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
```

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

## Completed: v0.2.0 Prompt-driven Template Selection

Status: Completed

Goal:

Upgrade the generator from a fixed template generator to a prompt-driven template selection system.

Completed features:

- Rule-based task classifier
- Multiple ROS-style generation templates
- Template registry
- `ProjectSpec` intermediate structure
- Generated `robopilot.yaml` metadata
- Refreshed static generated demo project
- Expanded tests
- Updated documentation

Supported template types:

- `camera_subscriber`
- `object_detection`
- `velocity_controller`
- `perception_pipeline`
- `generic_node`

Example commands:

```bash
robopilot generate --name camera_reader --task "Create a camera subscriber for webcam frames."
```

```bash
robopilot generate --name base_controller --task "Create a velocity controller publishing cmd_vel motion commands."
```

```bash
robopilot generate --name perception_stack --task "Create a camera -> detector -> tracker perception workflow."
```

## Completed: v0.3.0 Spec-first Generation

Status: Completed

Goal:

Upgrade RoboPilot from prompt-driven direct generation into a spec-first generation workflow.

Completed features:

- `robopilot plan`
- `robopilot validate`
- `robopilot generate --spec`
- Spec serialization and loading
- Spec validation before generation
- Generation from `robopilot.yaml`
- Backward compatibility with `generate --name --task`
- Expanded tests
- Updated documentation

Core workflow:

```bash
robopilot plan --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes." --output robopilot.yaml
```

```bash
robopilot validate --spec robopilot.yaml
```

```bash
robopilot generate --spec robopilot.yaml
```

The existing command still works:

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

## Completed: v0.4.0 Project Inspector

Status: Completed

Goal:

Add a lightweight offline project inspector that analyzes existing RoboPilot-generated or ROS-style project directories.

The inspector should not execute generated code, ROS2, launch files, or `colcon`. It should only inspect files statically.

Implemented command:

```bash
robopilot inspect examples/generated_projects/demo_detector
```

Optional JSON output:

```bash
robopilot inspect examples/generated_projects/demo_detector --json
```

Expected report:

- Project path
- Package name if detectable
- Whether `robopilot.yaml` exists
- Selected template if `robopilot.yaml` exists
- Detected package files
- Detected launch files
- Detected config files
- Detected Python node files
- Detected README file
- Potential issues
- Suggested next steps

Common issues to detect:

- Missing `package.xml`
- Missing `setup.py`
- Missing `setup.cfg`
- Missing `README.md`
- Missing launch directory
- Missing config directory
- Missing Python package directory
- Missing `robopilot.yaml`
- Invalid `robopilot.yaml`
- Empty project directory
- Non-existent project path

Implementation files:

```txt
src/robopilot/inspector/
├─ __init__.py
└─ project_inspector.py
```

Tests:

```txt
tests/test_project_inspector.py
```

Test cases:

- Inspecting a valid generated project
- Detecting missing `package.xml`
- Detecting missing `robopilot.yaml`
- Handling non-existent project path
- JSON output structure
- Validating `robopilot.yaml` through the existing validator

## Completed: v0.5.0 Project Repair Suggestions

Status: Completed

Goal:

Use the project inspector to provide safe repair suggestions for incomplete or inconsistent ROS-style projects.

Command:

```bash
robopilot repair-suggest path/to/project
```

Optional JSON output:

```bash
robopilot repair-suggest path/to/project --json
```

Expected behavior:

- Inspect project files with the existing inspector
- Detect missing files or invalid specs
- Map issues to deterministic repair suggestions
- Print suggested commands
- Never modify user files automatically
- Do not implement `--apply` yet

This remains static and safe by default.

## Completed: v0.6.0 Project Report Export

Status: Completed

Goal:

Export a deterministic Markdown report that combines static project inspection and repair suggestions.

Command:

```bash
robopilot report path/to/project --output report.md
```

Terminal output mode:

```bash
robopilot report path/to/project
```

Expected behavior:

- Inspect project files with the existing inspector
- Generate repair suggestions with the existing repair suggester
- Render a deterministic Markdown report
- Write the report to `--output` when provided
- Never modify the inspected project
- Never execute ROS2, launch files, colcon, or generated Python code

This remains static and safe by default.

## Completed: v0.7.0 Planner Interface + Optional LLM Planner

Status: Completed

Goal:

Refactor RoboPilot planning behind a planner interface and add optional LLM-assisted planning without replacing the deterministic spec-first workflow.

The LLM should not directly generate arbitrary project files. Instead, it should generate or refine `ProjectSpec`.

Target architecture:

```txt
natural language task
        ↓
optional LLM planner
        ↓
ProjectSpec
        ↓
validate spec
        ↓
deterministic generator
        ↓
ROS-style package
```

Possible command:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner rule
```

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner llm
```

Requirements:

- Offline rule-based planning must remain available.
- LLM mode must be optional.
- The default planner must remain `rule`.
- Tests must use fake or injected clients, not real APIs.
- No secrets should be required or committed.
- Generated specs should be validated before generation.
- LLM output should be constrained to RoboPilot's `ProjectSpec` schema.
- The LLM must not write code or project files directly.

Possible implementation files:

```txt
src/robopilot/planner/
├─ __init__.py
├─ rule_based_planner.py
└─ llm_planner.py
```

## Completed: v0.8.0 Real LLM Provider Integration

Status: Completed

Goal:

Make the optional LLM planner usable with a real OpenAI provider while preserving the spec-first architecture.

Commands:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner llm
```

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner llm --model gpt-4.1-mini
```

Requirements:

- `rule` remains the default planner.
- `OPENAI_API_KEY` is required only for real LLM planning.
- `ROBOPILOT_LLM_MODEL` or `--model` selects the model.
- LLM output must be ProjectSpec-compatible JSON or YAML.
- ProjectSpec validation must run before generation.
- The LLM must not generate project files or arbitrary code directly.
- Tests must use fake or mocked provider responses.

## Completed: v0.9.0 Spec Refinement

Status: Completed

Goal:

Refine an existing `robopilot.yaml` / ProjectSpec using deterministic offline rules.

Command:

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
```

Requirements:

- Load an existing ProjectSpec.
- Apply rule-based refinement.
- Validate the refined spec before writing.
- Write a new spec to `--output`.
- Do not modify the original spec.
- Do not implement `--in-place` yet.
- Keep `--planner rule` as the default.
- Leave LLM-assisted refinement as a future milestone.

Supported rule-based refinements:

- Add tracker node
- Add camera node
- Add controller node
- Add note for unsupported instructions
- Add explicit topic names from instructions
- Avoid duplicate nodes and topics

## Completed: v0.10.0 Spec Diff

Status: Completed

Goal:

Compare two `robopilot.yaml` / ProjectSpec files using deterministic offline rules.

Command:

```bash
robopilot diff --old base.yaml --new refined.yaml
```

Optional JSON output:

```bash
robopilot diff --old base.yaml --new refined.yaml --json
```

Requirements:

- Load both ProjectSpec files.
- Validate both specs before comparison.
- Compare package name, task, selected template, nodes, topics, config files, launch files, and notes.
- Report added, removed, and changed items.
- Never modify either spec file.
- Keep output deterministic and testable.

## Completed: v0.11.0 LLM-assisted Spec Refinement

Status: Completed

Goal:

Allow optional provider-backed refinement while preserving ProjectSpec validation and preventing direct file or code generation.

Commands:

```bash
robopilot refine --spec base.yaml --instruction "Add a tracker node after the detector" --planner rule --output rule_refined.yaml
```

```bash
robopilot refine --spec base.yaml --instruction "Add a tracker node after the detector" --planner llm --output llm_refined.yaml
```

Requirements:

- `rule` remains the default refiner.
- `OPENAI_API_KEY` is required only for real LLM refinement.
- LLM output must be a full ProjectSpec-compatible JSON or YAML document.
- ProjectSpec validation must run before writing the refined spec.
- The original spec must not be modified.
- The LLM must not generate project files or arbitrary code directly.
- Users should run `robopilot diff` before generating from an LLM-refined spec.

## Current: v0.12.0 Apply Preview

Status: Current work

Goal:

Preview applying a ProjectSpec to an existing project directory without modifying files.

Command:

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
```

Optional JSON output:

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector --json
```

Requirements:

- Load and validate the ProjectSpec.
- Render expected project files in memory.
- Compare expected files with the target project directory.
- Report files to create, update, keep, and review as conflicts.
- Never modify project files.
- Do not implement real apply or `--apply` yet.

## Future: v0.13.0 Real Apply Workflow

Status: Planned

Goal:

Apply generated changes only with explicit safety controls, backups, conflict handling, and user confirmation.

## Future: v0.14.0 Web Demo

Status: Planned

Goal:

Create a lightweight web demo for showcasing RoboPilot workflows.

Possible features:

- Task input box
- ProjectSpec preview
- Spec validation panel
- Project generation preview
- Error log analysis panel
- Mermaid workflow preview
- Project inspection report viewer

Possible frameworks:

- Streamlit
- Gradio

This should be optional and should not become a required dependency for CLI usage.

## Future: VSCode Integration

Status: Long-term idea

Goal:

Explore a VSCode extension or VSCode-friendly workflow.

Possible features:

- Generate RoboPilot spec from selected text
- Validate `robopilot.yaml`
- Generate project from spec
- Inspect current workspace
- Show Mermaid workflow preview
- Provide repair suggestions

This should only be considered after the CLI workflow becomes stable.

## Non-goals for Early Versions

RoboPilot will not focus on the following in early versions:

- Real robot deployment
- Heavy model training
- Full ROS2 runtime execution
- Automatic `colcon build`
- SLAM implementation
- Reinforcement learning training
- Large-scale VLA model inference
- Embedded low-level driver development
- Complex multi-agent orchestration
- RAG system before the core workflow is stable

## Development Priorities

Priority order:

1. Keep the CLI runnable.
2. Keep the spec-first workflow stable.
3. Keep behavior deterministic and testable.
4. Avoid unnecessary dependencies.
5. Reuse existing validation and spec logic.
6. Make generated and inspected outputs easy to understand.
7. Keep documentation concise and current.
8. Add optional AI features only after deterministic workflows are reliable.

## Current Recommended Development Path

```txt
v0.12.0 Apply Preview
        ↓
v0.13.0 Real Apply Workflow
        ↓
v0.14.0 Web Demo
        ↓
VSCode Integration
```

RoboPilot should grow as a practical robotics developer toolchain, not as a one-time demo script.
