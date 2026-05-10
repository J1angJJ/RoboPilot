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
- `robopilot validate`
- `robopilot generate`
- `robopilot inspect`
- `robopilot debug`
- `robopilot graph`

## 2. Install and Check the CLI

```bash
pip install -e ".[dev]"
robopilot --help
```

Expected result:

The CLI lists the available commands, including `generate`, `debug`, and `graph`.

## 3. Demo: Plan a ProjectSpec

Run:

```bash
robopilot plan --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes." --output robopilot.yaml
```

Point out:

- RoboPilot first converts the task into a structured ProjectSpec.
- The spec records the package name, selected template, nodes, topics, config files, launch files, and notes.
- The spec is saved as `robopilot.yaml` and can be reviewed before generation.

Validate the spec:

```bash
robopilot validate --spec robopilot.yaml
```

## 4. Demo: Generate a ROS-style Package

Run:

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

Spec-first generation:

```bash
robopilot generate --spec robopilot.yaml
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

## 6. Demo: Analyze an Error Log

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

## 7. Demo: Generate a Workflow Graph

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

## 8. Show Example Assets

Useful files to open during a demo:

- `examples/prompts/demo_detector.txt`
- `examples/generated_projects/demo_detector/robopilot.yaml`
- `examples/generated_projects/demo_detector/demo_detector/detector_node.py`
- `examples/generated_projects/demo_detector/package.xml`
- `examples/error_logs/cv_bridge_missing.txt`
- `examples/graphs/demo_pipeline.mmd`

## 9. Run Tests

```bash
pytest
```

Windows fallback if the default temp directory is blocked:

```powershell
New-Item -ItemType Directory -Path .pytest_tmp -Force
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

## 10. Close with Roadmap

Current implemented MVPs:

- MVP 0.1: Offline ROS-style Package Generator
- MVP 0.2: Robotics Error Log Debugger
- MVP 0.3: Workflow Diagram Generator
- MVP 0.4: Prompt-driven Template Selection
- MVP 0.5: Spec-first Generation
- MVP 0.6: Project Inspector

Next planned work:

- Better rule-based template selection
- Optional LLM-assisted generation while preserving offline mode
- Lightweight demo UI
