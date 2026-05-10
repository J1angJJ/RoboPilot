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

The CLI lists the available commands, including `plan`, `refine`, `diff`, `validate`, `apply-preview`, `generate`, `inspect`, `repair-suggest`, `report`, `debug`, and `graph`.

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

Point out:

- `refine` loads an existing ProjectSpec and writes a new refined spec.
- The original spec is not modified.
- v0.9.0 refinement is deterministic and rule-based.
- v0.10.0 diff is static, read-only, and validates both specs before comparison.
- v0.11.0 adds optional LLM-assisted refinement that still returns only ProjectSpec-compatible data.
- v0.12.0 apply-preview compares a spec to a project directory without modifying files.
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

## 8. Demo: Analyze an Error Log

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

## 9. Demo: Generate a Workflow Graph

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

## 10. Show Example Assets

Useful files to open during a demo:

- `examples/prompts/demo_detector.txt`
- `examples/generated_projects/demo_detector/robopilot.yaml`
- `examples/generated_projects/demo_detector/demo_detector/detector_node.py`
- `examples/generated_projects/demo_detector/package.xml`
- `examples/error_logs/cv_bridge_missing.txt`
- `examples/graphs/demo_pipeline.mmd`

## 11. Run Tests

```bash
pytest
```

Windows fallback if the default temp directory is blocked:

```powershell
New-Item -ItemType Directory -Path .pytest_tmp -Force
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

## 12. Close with Roadmap

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

Next planned work:

- Real apply workflow with explicit safety controls
- Hardening provider-backed ProjectSpec planning and refinement
- Deeper static reports and read-only repair suggestions
- Lightweight demo UI
