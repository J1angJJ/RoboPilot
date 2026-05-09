
# AGENTS.md

## Project Goal

RoboPilot is an AI-native robotics development assistant for ROS-style workflows, debugging, and code generation.

The project explores how lightweight AI-assisted developer tools can help robotics learners and developers scaffold projects, analyze errors, generate workflow diagrams, and accelerate robotics software development without requiring a full ROS2 runtime environment.

## Current MVP Scope

The current MVP focuses on lightweight, local, and reproducible functionality.

### MVP Features

1. Generate ROS-style Python package skeletons from natural language task descriptions.
2. Generate common robotics development files:
   - `package.xml`
   - `setup.py`
   - `setup.cfg`
   - launch files
   - config files
   - Python node templates
   - README files
3. Analyze pasted robotics-related error logs and provide debugging suggestions.
4. Generate Mermaid workflow diagrams for robot software pipelines.
5. Provide a clean CLI interface for local use.

## Important Constraints

- Do NOT require a real ROS2 installation.
- Do NOT require a GPU.
- Do NOT require Docker for the MVP.
- Do NOT run heavy model training.
- Do NOT depend on large frameworks unless clearly necessary.
- Prefer pure Python implementations.
- Keep the project lightweight and easy to clone, install, and test.
- Generated code may be ROS2-style pseudocode if real ROS2 runtime support is not available.

## Development Philosophy

RoboPilot should feel like a real developer tool, not a course assignment.

Prioritize:

- Clear project structure
- Small and testable features
- Good CLI experience
- Readable generated code
- Good README examples
- Useful demo outputs
- Minimal dependencies
- Safe file operations

Avoid:

- Overengineering
- Unnecessary multi-agent architecture
- Heavy framework lock-in
- Large dependencies in the MVP
- Unclear generated files
- Features that require unavailable hardware or runtime environments

## Recommended Tech Stack

- Python 3.10+
- Typer for CLI
- Rich for terminal output
- Pytest for tests
- pathlib for file operations

Optional future dependencies:

- OpenAI SDK for LLM-powered generation
- Streamlit or Gradio for lightweight UI
- Mermaid for workflow visualization
- Ruff or Black for formatting

## Code Style

- Use type hints.
- Prefer `pathlib.Path` over `os.path`.
- Keep functions small and focused.
- Separate business logic from CLI code.
- Separate templates from file-writing logic.
- Use clear function and variable names.
- Add docstrings for public functions.
- Avoid hidden side effects.
- Avoid global mutable state.

## Expected Project Structure

Core package:

```txt
src/robopilot/
├─ __init__.py
├─ main.py
├─ generator/
│  ├─ __init__.py
│  ├─ project_generator.py
│  └─ templates.py
├─ debugger/
│  ├─ __init__.py
│  └─ log_analyzer.py
├─ prompts/
│  └─ templates.py
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
└─ generated_projects/

tests/
```

## Safety Rules

- Never delete user files automatically.
- Never overwrite existing files unless explicitly allowed.
- When overwriting is necessary, create a backup or ask for confirmation.
- Generated projects should be written to `outputs/` by default.
- Never commit API keys, tokens, private paths, or local environment files.
- Never assume the user has ROS2 installed.
- Never require external services for offline MVP features.

## Testing

Before finalizing a change, run:

```bash
pytest
```

If the CLI exists, also run:

```bash
robopilot --help
```

For generator-related changes, test:

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

## Preferred Development Workflow

1. Read `README.md`, `roadmap.md`, and this file first.
2. Implement one small feature at a time.
3. Add or update tests.
4. Run tests.
5. Update README usage examples when behavior changes.
6. Summarize changed files and design decisions.

## Current Priority

The current priority is to build a working offline MVP:

```txt
natural language task description
        ↓
ROS-style project skeleton
        ↓
generated files in outputs/
```

Do not start LLM orchestration, RAG, Streamlit UI, or complex agent planning until the offline generator is stable.

## First Implementation Target

Implement the first command:

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

The command should create:

```txt
outputs/demo_detector/
├─ package.xml
├─ setup.py
├─ setup.cfg
├─ README.md
├─ launch/
│  └─ demo_detector.launch.py
├─ config/
│  └─ params.yaml
└─ demo_detector/
   ├─ __init__.py
   └─ detector_node.py
```

This first implementation should be offline and template-based.
