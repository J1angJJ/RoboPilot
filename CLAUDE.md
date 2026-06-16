# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RoboPilot is a **no-ROS-required static engineering toolchain** for ROS/ROS2-style projects. It helps users plan, generate, inspect, analyze, migrate, and document ROS-style project structures without installing ROS, ROS2, catkin, or colcon.

- Python package: `robopilot` (v2.1.0, Python 3.10-3.11)
- PyPI: `pip install robopilot`
- VSCode extension: `j1angjj.robopilot-vscode` (thin CLI/API wrapper, lives under `vscode-extension/`)

### 2.x Direction: Two Tracks

After v2.1.0, development follows two complementary tracks:

- **Track A — Education & Onboarding**: Expand templates (5→12), add interactive tutorial mode, error diagnosis for 30+ ROS patterns, user-configurable templates. Goal: best tool for learning ROS structure without installing ROS.
- **Track B — Static Quality Tooling**: Add `robopilot lint` (package health checks), `robopilot migrate-score` (migration readiness 0-100), launch file validation, workspace-level analysis, CI-friendly report export. Goal: linting and quality analysis for real ROS projects.

v2.1.0 is shipped (10 milestones). v2.2.0 is planned with 7 deepening milestones, tracked in `roadmap.md`.

## Git & Release Conventions

- **No AI attribution**: Never include AI-authored signatures in commits, PR descriptions, or files. No `Co-authored-by`, `Generated with Claude Code`, `AI-generated`, or similar tags. Use the user's global git settings exclusively for commit authorship.
- **Commits**: Add and commit locally as needed. Do NOT push — the user handles push (requires credentials).
- **Releases**: No PyPI or VSCode Marketplace publish permissions. When release-ready, suggest the manual steps (build, twine check, tag, publish) for the user to execute.

## Dev Environment

This project has a dedicated conda environment. **Never install packages in the base conda environment.**

```bash
# Activate the dev conda environment
conda activate robopilot     # Python 3.10, located at C:\Users\JJ406\.conda\envs\robopilot

# Reinstall in editable mode after pulling changes
pip install -e "R:/RoboPilot[dev]"

# Run Python directly (avoids conda GBK encoding issues on Windows)
C:/Users/JJ406/.conda/envs/robopilot/python.exe -m pytest R:/RoboPilot/tests --basetemp="R:/RoboPilot/.pytest_tmp" -p no:cacheprovider

# Or use conda run (may have Unicode output issues with Rich tables)
conda run -n robopilot python -m pytest R:/RoboPilot/tests --basetemp="R:/RoboPilot/.pytest_tmp" -p no:cacheprovider
```

### Other conda environments
- `robopilot-pypi-test` — for testing PyPI installs (Python 3.10)

## Commands

```bash
# Activate dev environment
conda activate robopilot

# Reinstall after pulling changes
pip install -e "R:/RoboPilot[dev]"

# Run all tests (from project root)
python -m pytest R:/RoboPilot/tests --basetemp="R:/RoboPilot/.pytest_tmp" -p no:cacheprovider

# Run a single test file
python -m pytest tests/test_project_generator.py

# Run a single test
python -m pytest tests/test_project_generator.py::test_generate_basic_project -v

# Packaging checks
python -m pip install -U build twine
python -m build
python -m twine check dist/*

# Run the CLI
python -m robopilot.main --help

# Quick smoke test a template
python -m robopilot.main plan --name test_proj --task "Create a SLAM mapping node for lidar data"
python -m robopilot.main generate --name test_proj --task "..." -o outputs/

# Verify Chinese doc encoding
python -m pytest tests/test_docs_encoding.py
```

## Architecture

```
src/robopilot/
├── main.py          # Typer CLI — presentation layer only, routes to API
├── api/             # Public Python API (no Rich, no stdout, no sys.exit)
│   ├── project.py   # plan, refine, diff, validate, generate
│   ├── static_analysis.py  # detect, inspect, deps, report
│   ├── migration.py # migrate-plan, scaffold, validate, report
│   ├── apply.py     # apply-preview, apply, rollback, history
│   └── models.py    # Shared helpers: to_structured_result, normalize_path
├── generator/       # Spec creation, template registry, project rendering
│   ├── project_spec.py    # ProjectSpec, NodeSpec, TopicSpec dataclasses
│   ├── template_registry.py  # 5 template types, build_project_spec()
│   ├── project_generator.py  # Deterministic file rendering from ProjectSpec
│   └── task_classifier.py    # Rule-based task → template mapping
├── spec/            # Hand-written YAML subset parser (no PyYAML dependency)
│   ├── io.py        # spec_to_yaml, load_spec, write_spec
│   └── validator.py # validate_spec
├── planner/         # Planner interface + two implementations
│   ├── base.py      # Planner ABC
│   ├── rule_based_planner.py  # Deterministic offline planner (default)
│   ├── llm_planner.py         # Optional OpenAI-powered planner
│   └── openai_client.py       # OpenAI SDK wrapper
├── refiner/         # Rule-based and LLM spec refinement
├── diff/            # ProjectSpec diff
├── apply_preview/   # Compare rendered spec vs existing project
├── apply_plan/      # Export/validate apply plans
├── apply/           # Execute apply plans (dry-run by default)
├── rollback/        # Restore from RoboPilot backups
├── history/         # Read .robopilot_history/ journal
├── detector/        # Classify project type (robopilot/ros1/ros2/mixed/unknown)
├── ros1/            # Static ROS1 catkin package inspection
├── ros2/            # Static ROS2 ament package inspection
├── deps/            # Dependency analysis (declared + detected)
├── inspector/       # Project structure inspection
├── repair/          # Repair suggestions from inspection issues
├── report/          # Markdown project report export
├── migration/       # ROS1→ROS2 migration planning, preview, scaffold
├── debugger/        # Robotics error log analyzer
├── graph/           # Pipeline → Mermaid graph generator
└── utils/
    └── file_ops.py  # Safe create/write with overwrite protection
```

### Data Flow

```
task text → planner → ProjectSpec → validate → generate (writes files)
                                   → refine → diff → validate
                                   → apply-preview → apply-plan → apply (--confirm)
                                   → rollback (from backup)
                                   → history (read journal)

detect → inspect-ros1 / inspect-ros2 → deps
                                      → migrate-plan → validate → diff
                                                      → migrate-preview
                                                      → migrate-scaffold-preview
                                                      → migrate-scaffold → validate → report
```

### Key Design Decisions

- **ProjectSpec** is the central intermediate representation. All generation, refinement, and apply flows go through it. It's a frozen dataclass with package_name, task, selected_template, nodes, topics, config_files, launch_files, notes.
- **No PyYAML dependency**: spec IO uses a hand-written YAML subset parser (`spec/io.py`).
- **5 offline templates**: camera_subscriber, object_detection, velocity_controller, perception_pipeline, generic_node.
- **API is a thin pass-through**: API functions validate inputs, call core modules, return structured results. CLI is the presentation layer (Typer + Rich). API never prints, renders Rich, or calls sys.exit.
- **Safety chain for writes**: preview → plan → validate-plan → dry-run → --confirm → backup → rollback. Apply re-runs preview and rejects stale plans.
- **VSCode extension wraps CLI with `--json`**: spawns `robopilot` CLI, parses JSON stdout. No RoboPilot logic duplicated in TypeScript.
- **Tests mirror source structure**: each source module has a corresponding `tests/test_*.py` file. Tests run in CI on Python 3.10 and 3.11 via GitHub Actions.

## Critical Constraints

- Never require ROS, ROS2, catkin, colcon, Docker, GPU, or robot hardware.
- Never execute generated code, launch files, `catkin_make`, or `colcon build`.
- Static analysis must not import or execute user project modules.
- LLM features are optional (`pip install robopilot[llm]`). LLMs only produce ProjectSpec data — never write files directly or bypass validation.
- Default behavior for file-writing is dry-run. Confirmed writes require `--confirm`.
- Generated projects go to `outputs/` (gitignored).
- Keep the v1.0.0 command surface and safety model intact unless explicitly planned.
- Do not add new product commands during packaging/release work.
- Prefer pure Python, pathlib, type hints. Keep functions small. Separate CLI from business logic.

### Planned Module Additions (v2.2.0 milestones)

```
src/robopilot/
├── doctor/          # M17: environment self-diagnostic
├── deps/            # M13: workspace-level dep resolution, rosdep hints
├── lint/            # M12: cross-file rules, ROS2-specific checks
├── report/          # M16: HTML/PDF export, trend history, diff mode
├── templates/       # M11: quality polish, Chinese comments
├── tutorial/        # M14: 4 new lessons, Chinese text, progress tracking
└── user_templates/  # M17: template-install, template-search, community
```

New commands must follow the existing pattern: core module → API wrapper → CLI command, with `--json` support and read-only safety.

## Key Files for Context

- `AGENTS.md` — comprehensive developer guide with full CLI command reference and rules
- `roadmap.md` — full version history and v2.1.0 milestone plan
- `docs/architecture.md` — architectural overview
- `docs/api.md` — Python API documentation
- `docs/json_contracts.md` — stable JSON output schemas
- `docs/command_reference.md` — CLI command reference
- `docs/research/README.md` — research planning process for 2.x features
