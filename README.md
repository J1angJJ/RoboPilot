# RoboPilot

AI-native robotics development assistant for ROS-style workflows, debugging, and code generation.

RoboPilot is a lightweight developer tool that helps robotics learners and developers generate ROS-style project skeletons, inspect robotics software workflows, and debug common development errors with AI-assisted workflows.

The first version focuses on local, low-cost, and hardware-friendly usage. It does not require a real ROS2 installation, GPU, Docker, or robot hardware.

## Why RoboPilot?

Robotics development often involves repetitive project setup, launch file writing, dependency configuration, and error debugging.

RoboPilot aims to make this workflow easier by acting as a robotics development copilot:

- Generate ROS-style project templates
- Explain robotics-related error logs
- Scaffold launch and config files
- Produce readable node templates
- Visualize robotics software pipelines
- Support AI-native development workflows

## Current Status

Early MVP under active development.

The current goal is to build a useful offline generator before adding LLM-powered features.

## Planned Features

- Natural language to ROS-style package generation
- Robotics error log analysis
- Launch and config scaffolding
- Mermaid workflow graph generation
- AI-assisted debugging suggestions
- Lightweight CLI interface
- Optional web demo in the future

## Example Use Case

Input:

```txt
Create an object detection node subscribing to camera images and publishing bounding boxes.
```

Expected output:

```txt
outputs/demo_detector/
|-- package.xml
|-- setup.py
|-- setup.cfg
|-- README.md
|-- launch/
|   `-- demo_detector.launch.py
|-- config/
|   `-- params.yaml
`-- demo_detector/
    |-- __init__.py
    `-- detector_node.py
```

The generated files are ROS2-style templates designed for learning, prototyping, and workflow demonstration. A real ROS2 runtime is not required for the MVP.

A static generated example is included at `examples/generated_projects/demo_detector/`, with the source prompt saved in `examples/prompts/demo_detector.txt`.

## Installation

Clone the repository:

```bash
git clone https://github.com/J1angJJ/RoboPilot.git
cd robopilot
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install the project in editable mode:

```bash
pip install -e ".[dev]"
```

## Basic Usage

Generate a ROS-style package skeleton:

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

By default, RoboPilot writes generated projects to `outputs/` and refuses to overwrite an existing project directory.

The command above creates:

```txt
outputs/demo_detector/
|-- package.xml
|-- setup.py
|-- setup.cfg
|-- README.md
|-- launch/
|   `-- demo_detector.launch.py
|-- config/
|   `-- params.yaml
`-- demo_detector/
    |-- __init__.py
    `-- detector_node.py
```

Show help:

```bash
robopilot --help
```

Analyze a robotics error log file:

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
```

Analyze inline log text:

```bash
robopilot debug --text "ModuleNotFoundError: No module named 'cv_bridge'"
```

Generate a Mermaid workflow graph:

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

Write a Mermaid workflow graph to a file:

```bash
robopilot graph --pipeline "camera -> detector -> tracker" --output examples/graphs/demo_pipeline.mmd
```

Run tests:

```bash
pytest
```

## Windows Test Notes

On some Windows setups, pytest may not be able to access the default user temp directory. In that case, run tests with a project-local temp directory:

```powershell
New-Item -ItemType Directory -Path .pytest_tmp -Force
$env:TMP='R:\RoboPilot\.pytest_tmp'
$env:TEMP='R:\RoboPilot\.pytest_tmp'
python -m pytest -p no:cacheprovider --basetemp .pytest_tmp\basetemp
```

## Project Structure

```txt
robopilot/
|-- AGENTS.md
|-- README.md
|-- roadmap.md
|-- pyproject.toml
|-- src/
|   `-- robopilot/
|       |-- main.py
|       |-- generator/
|       |-- debugger/
|       |-- prompts/
|       `-- utils/
|-- examples/
|-- tests/
`-- docs/
```

## Design Principles

- Lightweight first
- No ROS2 dependency for MVP
- No GPU requirement
- No heavy model training
- Clear generated code
- Safe file operations
- Testable small modules
- AI-native workflow design

## Roadmap

See [`roadmap.md`](roadmap.md).

## License

MIT License.
