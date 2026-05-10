
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

## Current: v0.4.0 Project Inspector

Status: Current work

Goal:

Add a lightweight offline project inspector that analyzes existing RoboPilot-generated or ROS-style project directories.

The inspector should not execute generated code, ROS2, launch files, or `colcon`. It should only inspect files statically.

Planned command:

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

Suggested implementation files:

```txt
src/robopilot/inspector/
├─ __init__.py
└─ project_inspector.py
```

Suggested tests:

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

## Future: v0.5.0 Optional LLM Planner

Status: Planned

Goal:

Add optional LLM-assisted planning without replacing the deterministic spec-first workflow.

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
robopilot plan --name demo_detector --task "Create an object detection pipeline" --llm
```

Requirements:

- Offline rule-based planning must remain available.
- LLM mode must be optional.
- API keys must be loaded from environment variables.
- No secrets should be committed.
- Generated specs should be validated before generation.
- LLM output should be constrained to RoboPilot's `ProjectSpec` schema.

Possible implementation files:

```txt
src/robopilot/planner/
├─ __init__.py
├─ rule_based_planner.py
└─ llm_planner.py
```

## Future: v0.6.0 Project Repair Suggestions

Status: Planned

Goal:

Use the project inspector and debugger together to provide repair suggestions for incomplete or inconsistent ROS-style projects.

Possible command:

```bash
robopilot repair-suggest path/to/project
```

Expected behavior:

- Inspect project files
- Detect missing files or inconsistent spec fields
- Suggest safe fixes
- Optionally generate a patch plan
- Do not modify user files automatically without explicit confirmation

This should remain static and safe by default.

## Future: v0.7.0 Web Demo

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
v0.4.0 Project Inspector
        ↓
v0.5.0 Optional LLM Planner
        ↓
v0.6.0 Project Repair Suggestions
        ↓
v0.7.0 Web Demo
        ↓
VSCode Integration
```

RoboPilot should grow as a practical robotics developer toolchain, not as a one-time demo script.
