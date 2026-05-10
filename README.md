# RoboPilot

[English](README.md) | [Chinese](README.zh-CN.md)

[![Tests](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml/badge.svg)](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml)

Lightweight offline developer tooling for ROS-style robotics workflows.

RoboPilot helps robotics learners and developers scaffold ROS-style Python packages, analyze common robotics error logs, and turn simple software pipelines into Mermaid workflow diagrams. The current MVP is intentionally local, reproducible, and hardware-friendly: no ROS2 installation, GPU, Docker, OpenAI API, or heavy framework is required.

## Core Capabilities

- `plan`: convert a robotics task into a readable `robopilot.yaml` ProjectSpec.
- `validate`: check a saved ProjectSpec before generation.
- `generate`: create a ROS-style Python package from a task or a saved ProjectSpec.
- `inspect`: statically inspect a generated or ROS-style project directory.
- `repair-suggest`: suggest safe repairs from inspection issues without modifying files.
- `debug`: analyze robotics-related error logs with offline rule-based diagnostics.
- `graph`: convert arrow-based robotics pipelines into Mermaid diagrams.

## Quick Start

Clone and install:

```bash
git clone https://github.com/J1angJJ/RoboPilot.git
cd RoboPilot
python -m venv .venv
```

Activate the environment.

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install in editable mode:

```bash
pip install -e ".[dev]"
```

Check the CLI:

```bash
robopilot --help
```

## Demo

Generate a ROS-style package:

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

Spec-first workflow:

```bash
robopilot plan --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes." --output robopilot.yaml
robopilot validate --spec robopilot.yaml
robopilot generate --spec robopilot.yaml
```

Inspect a generated project:

```bash
robopilot inspect examples/generated_projects/demo_detector
robopilot inspect examples/generated_projects/demo_detector --json
```

Suggest safe repairs without modifying files:

```bash
robopilot repair-suggest examples/generated_projects/demo_detector
robopilot repair-suggest examples/generated_projects/demo_detector --json
```

Generate other template types:

```bash
robopilot generate --name camera_reader --task "Create a camera subscriber for webcam frames."
robopilot generate --name base_controller --task "Create a velocity controller publishing cmd_vel motion commands."
robopilot generate --name perception_stack --task "Create a camera -> detector -> tracker perception workflow."
robopilot generate --name helper_node --task "Create a simple heartbeat node."
```

Analyze a robotics error log:

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
```

Generate a Mermaid workflow graph:

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

Write a Mermaid graph to a file:

```bash
robopilot graph --pipeline "camera -> detector -> tracker" --output examples/graphs/demo_pipeline.mmd
```

A longer walkthrough is available in [`docs/demo_script.md`](docs/demo_script.md).

## Example Outputs

Static examples are included for GitHub preview and demos:

- Generated package: [`examples/generated_projects/demo_detector/`](examples/generated_projects/demo_detector/)
- Generator prompt: [`examples/prompts/demo_detector.txt`](examples/prompts/demo_detector.txt)
- Error logs: [`examples/error_logs/`](examples/error_logs/)
- Pipeline input: [`examples/pipelines/demo_pipeline.txt`](examples/pipelines/demo_pipeline.txt)
- Mermaid graph: [`examples/graphs/demo_pipeline.mmd`](examples/graphs/demo_pipeline.mmd)

Generated package layout:

```txt
examples/generated_projects/demo_detector/
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

Mermaid graph output:

```mermaid
graph LR
    camera --> detector
    detector --> tracker
```

## Project Status

RoboPilot is an early v0.5.0 MVP focused on offline, lightweight robotics developer workflows. See [`CHANGELOG.md`](CHANGELOG.md) for release notes.

Implemented:

- MVP 0.1: Offline ROS-style Package Generator
- MVP 0.2: Robotics Error Log Debugger
- MVP 0.3: Workflow Diagram Generator
- MVP 0.4: Prompt-driven Template Selection
- MVP 0.5: Spec-first Generation
- MVP 0.6: Project Inspector
- v0.5.0: Project Repair Suggestions

Not included yet:

- Real ROS2 runtime execution
- LLM-powered generation
- RAG
- Streamlit or Gradio UI
- VSCode extension
- Robot deployment tooling

## Roadmap Summary

Near-term roadmap:

1. Deeper repair suggestions while keeping `repair-suggest` read-only by default
2. Optional LLM-assisted planning while keeping offline mode
3. Lightweight demo UI

Longer-term direction:

- Better debugging suggestions for robotics learners
- AI-assisted patch generation
- Workflow visualization and explanation

See [`roadmap.md`](roadmap.md) for the full roadmap.

## Development Notes

Run tests:

```bash
pytest
```

On some Windows setups, pytest may not be able to access the default user temp directory. In that case, run tests with a project-local temp directory:

```powershell
New-Item -ItemType Directory -Path .pytest_tmp -Force
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

Generated projects are written to `outputs/` by default. That directory is ignored by Git. Static showcase examples live under `examples/`.

## Project Structure

```txt
robopilot/
|-- README.md
|-- README.zh-CN.md
|-- roadmap.md
|-- pyproject.toml
|-- src/
|   `-- robopilot/
|       |-- main.py
|       |-- generator/
|       |-- debugger/
|       |-- graph/
|       |-- inspector/
|       |-- repair/
|       `-- utils/
|-- examples/
|-- tests/
`-- docs/
```

## License

MIT License.
