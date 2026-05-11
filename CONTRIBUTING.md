# Contributing to RoboPilot

Thanks for helping improve RoboPilot.

RoboPilot is a no-ROS-required static engineering toolchain for ROS-style projects. Contributions should preserve that design: static first, safe by default, and explicit about file-writing behavior.

## Development Setup

```bash
git clone https://github.com/J1angJJ/RoboPilot.git
cd RoboPilot
python -m pip install -U pip
pip install -e ".[dev]"
```

See [docs/developer_setup.md](docs/developer_setup.md) for environment details.

## Run Tests

```bash
python -m pytest
```

Windows fallback:

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

## Coding Style

- Use type hints for new public functions.
- Prefer `pathlib.Path`.
- Keep CLI presentation separate from core logic.
- Keep behavior deterministic and testable.
- Do not execute user ROS code, launch files, catkin, or colcon.
- Keep optional LLM paths optional and constrained to validated structured data.

## Documentation

Update docs when behavior, safety notes, CLI usage, or public workflows change.

Useful docs:

- [Command Reference](docs/command_reference.md)
- [Workflows](docs/workflows.md)
- [Architecture](docs/architecture.md)
- [Testing](docs/testing.md)

## Issues and Pull Requests

Good issues and PRs include:

- clear problem statement
- reproduction steps or example command
- expected behavior
- actual behavior
- relevant OS and Python version
- tests or docs updates when appropriate

## Safety Principles

- File-writing workflows should be dry-run-first where practical.
- Confirmed writes should be explicit.
- Apply must write only through validated plans.
- Rollback must restore only from RoboPilot backups.
- Static analysis must not import or execute user project modules.
