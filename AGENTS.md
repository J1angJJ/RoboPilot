# AGENTS.md

## Project Goal

RoboPilot is a no-ROS-required static engineering toolchain for ROS-style projects.

It helps robotics learners and developers plan, refine, validate, generate, inspect, update, roll back, document, analyze, and migrate ROS/ROS2-style project structure without requiring a local ROS installation.

RoboPilot should grow as a practical developer toolchain, not as a general-purpose coding agent and not as a runtime ROS automation tool.

## Product Positioning

RoboPilot intentionally works without:

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

RoboPilot should avoid competing directly with general-purpose coding agents. Its niche is ROS-style project structure, no-ROS-required static analysis, safe update planning, dependency analysis, migration assistance, and beginner-friendly robotics engineering workflows.

## Current Stable Baseline

The current stable baseline is:

```txt
v2.0.1
```

The stable baseline includes:

- no-ROS-required default behavior
- ProjectSpec-based generation
- read-only detect / inspect / deps / report workflows
- dry-run-first apply / rollback workflows
- project-local history journal
- ROS project detection
- ROS1 static inspection
- ROS2 static inspection
- static dependency analysis
- ROS1-to-ROS2 migration planning
- migration plan validation and diff
- migration preview
- migration scaffold preview / generate / validate / report workflow
- examples, tutorials, demo pack, and migration workflow UX polish
- Chinese documentation expansion and encoding guardrails
- VSCode Marketplace availability for extension id `j1angjj.robopilot-vscode`
- optional LLM planner / refiner boundaries

Do not break the v1.0.0 command surface or documented safety model unless the task explicitly asks for a planned compatibility change.

## Current Priority

The current priority is:

```txt
v2.x Education & Static Quality Toolchain
```

v2.0.1 is the stable baseline. Future 2.x work follows two complementary tracks:

**Track A — Education & Onboarding (学用 ROS，无需安装 ROS):**
Expand RoboPilot as the best tool for learning ROS project structure without installing ROS. More templates, interactive tutorials, better error diagnosis, and beginner-friendly workflows.

**Track B — Static Quality Tooling (ROS 项目静态体检):**
Make RoboPilot a linting and quality-analysis tool for real ROS projects. Package health checks, migration readiness scoring, dependency consistency validation, and CI-friendly report exports.

These two tracks share the same no-ROS-required safety model. Track A grows the top of the funnel (new users), Track B grows the bottom (retained users with real projects).

## v2.1.0 Milestone Plan

v2.1.0 is a single release containing 10 development milestones. Each milestone
is an internal checkpoint, not a separate PyPI release. Milestones are completed
sequentially and committed to main.

```txt
Milestone 1  Template Expansion I (Track A)              [DONE]
             Expand from 5 to 12 generation templates: add slam, navigation,
             sensor_fusion, image_processing, robot_arm, rosbag_tools, and
             state_machine. Make topic names and message types configurable
             in robopilot.yaml per-node instead of fully hardcoded.

Milestone 2  ROS Package Lint (Track B)                  [DONE]
             Add robopilot lint command. Static checks for package.xml format
             version, required fields, dependency declaration consistency,
             missing buildtool_depend, common CMakeLists.txt issues (missing
             find_package, missing catkin_package/ament_package), and
             setup.py/setup.cfg ament_python convention checks.

Milestone 3  Migration Readiness Scoring (Track B)      [DONE]
             Add robopilot migrate-score command. Score a ROS1 package on
             migration readiness (0-100). Break down by: API surface patterns,
             build system complexity, dependency availability in ROS2, launch
             file conversion complexity, custom message/service/action surface.

Milestone 4  Interactive Tutorial Mode (Track A)        [DONE]
             Add robopilot tutorial command. Step-by-step guided workflow
             through plan→validate→generate→inspect→report. Target: a complete
             beginner can finish in under 15 minutes without ROS knowledge.

Milestone 5  Launch File Static Validation (Track B)     [DONE]
             Extend launch file analysis for ROS1 XML and ROS2 Python launch
             files. Detect: missing node declarations, unreferenced parameters,
             undefined arguments, deprecated ROS1-only patterns, missing remap
             targets. Integrate into lint and migrate-score.

Milestone 6  Error Diagnosis Expansion (Track A)           [DONE]
             Expand debugger from basic cv_bridge patterns to 30+ common ROS
             errors. Cover: tf/tf2, parameter server, actionlib, nodelet,
             QoS mismatches, build failures, CMake/Python import errors.

Milestone 7  Workspace-level Static Analysis (Track B)    [DONE]
             Add robopilot workspace command. Multi-package workspace detection,
             cross-package dependency graph, circular dependency detection,
             suggested migration ordering, inter-package version conflict hints.

Milestone 8  User-configurable Templates (Track A)        [DONE]
             Support user template overrides via .robopilot/templates/.
             Template inheritance. Add robopilot template-init and
             robopilot template-validate.

Milestone 9  VSCode Education & Quality Workflow (Track A+B) [DONE]
             Polish VSCode extension: template browser, lint-on-save via
             robopilot lint --json, migration score in status bar, guided
             tutorial panel, inline issue annotations.

Milestone 10 Quality Report Export & CI Integration (Track B)
             Exportable quality reports in Markdown and SARIF format.
             CI-friendly structured output. Add robopilot ci-check as
             a unified command for CI pipelines. Stable exit codes for gating.
```

### Design Principles

- v2.1.0 releases as a single MINOR bump when all 10 milestones are complete.
- Each milestone is self-contained: one theme, complete tests, updated docs.
- Track A and Track B alternate to keep both user groups engaged.
- No command from v1.0.0–v2.0.1 is removed or silently changed.
- The no-ROS-required safety model applies to every new feature.
- Static analysis never imports or executes user project code.
- New CLI commands use --json for integration readiness from day one.

## 2.x Planning Rules

2.x work follows the Track A (Education) / Track B (Quality) plan. Implementation is milestone-scoped and review-first:

- Each milestone implements one accepted theme. Do not mix Track A and Track B work in the same milestone.
- Capture product research under `docs/research/` before starting a milestone.
- Use accepted research briefs as the source for scoped implementation tasks.
- Do not expand beyond the planned milestone scope without explicit user approval.
- Treat `docs/research/feature_backlog_2x.md` and `docs/research/decision_log.md` as planning inputs, not product specifications, unless an item is marked accepted.
- Preserve RoboPilot's no-ROS-required safety model in every new feature.
- Avoid broad rewrites and speculative feature expansion.
- Prefer small, testable, documented improvements.
- New CLI commands should ship with --json support from the start.
- VSCode extension updates should remain thin wrappers over CLI/API.

## Important Constraints

- Do not require a real ROS installation.
- Do not require a real ROS2 installation.
- Do not require a GPU.
- Do not require Docker.
- Do not run heavy model training.
- Do not execute generated ROS nodes.
- Do not execute launch files.
- Do not run `catkin_make`.
- Do not run `colcon build`.
- Do not call OpenAI API or any LLM API unless the task explicitly involves optional LLM planning or refinement.
- Do not add LangChain, Streamlit, Gradio, RAG, VSCode extension, or large frameworks unless explicitly requested.
- Do not introduce new product commands during packaging / release-engineering work.
- Prefer pure Python implementations.
- Keep the project lightweight and easy to clone, install, test, publish, and understand.
- Static analysis must not execute user code.

## PyPI and Packaging Rules

For packaging-related work:

- Prefer PyPI Trusted Publishing over long-lived API tokens.
- Do not commit PyPI tokens.
- Do not commit TestPyPI tokens.
- Do not commit `.pypirc`.
- Do not commit build artifacts from `dist/`.
- Do not commit wheel or sdist files unless explicitly requested.
- Use standard packaging tools such as `build` and `twine` for local checks.
- Keep package metadata accurate and conservative.
- Keep `pyproject.toml` as the source of package metadata.
- Ensure the `robopilot` console script remains available.
- Ensure default installation does not require optional LLM dependencies.
- Optional LLM dependencies should remain under an extra such as `llm`.

Suggested packaging checks:

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

If GitHub Actions publishing is added, it should use a dedicated workflow such as:

```txt
.github/workflows/publish.yml
```

If Trusted Publishing is used, the PyPI pending publisher should match:

```txt
Owner: J1angJJ
Repository: RoboPilot
Workflow: publish.yml
Environment: pypi
Project name: robopilot
```

## Open-source Project Rules

For public developer experience work, prefer adding or updating:

- `CONTRIBUTING.md`
- `SECURITY.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/pull_request_template.md`
- `docs/pypi_publish.md`
- `docs/developer_setup.md`

Keep these documents concise and practical.

Do not overpromise community processes that are not actually maintained yet.

## API Layer Direction

The API layer should make RoboPilot easier to integrate with VSCode, scripts, and future UI tools.

Preferred direction:

```txt
src/robopilot/api/
├─ __init__.py
├─ project.py
├─ static_analysis.py
├─ migration.py
├─ apply.py
└─ models.py
```

The API layer should:

- avoid Rich rendering
- avoid direct stdout printing
- avoid `sys.exit`
- return dataclasses, typed results, or stable dictionaries
- expose predictable exceptions or result objects
- keep file-writing explicit
- reuse existing core modules
- allow CLI to remain a presentation layer

The CLI should eventually become:

```txt
CLI command
    ↓
API function
    ↓
core module
    ↓
result object
    ↓
CLI renderer
```

Do not perform a broad API refactor during packaging work unless explicitly requested.

## VSCode Extension Direction

A future VSCode extension should be beginner-friendly but thin.

Preferred first approach:

```txt
VSCode extension
    ↓
spawn robopilot CLI with --json
    ↓
parse JSON
    ↓
display TreeView / Webview / OutputChannel
```

The extension should not reimplement RoboPilot logic in TypeScript.

Possible VSCode MVP commands:

- RoboPilot: Detect Workspace
- RoboPilot: Inspect ROS1 Package
- RoboPilot: Analyze Dependencies
- RoboPilot: Generate Migration Plan
- RoboPilot: Preview Migration
- RoboPilot: Preview Migration Scaffold
- RoboPilot: Generate Migration Scaffold
- RoboPilot: Validate Migration Scaffold
- RoboPilot: Generate Scaffold Report
- RoboPilot: Open Scaffold Report
- RoboPilot: Validate ProjectSpec
- RoboPilot: Open Report

VSCode work should continue to wrap the RoboPilot CLI/API instead of reimplementing core logic in TypeScript.

## Development Philosophy

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
- backward compatibility with v1.0.0 commands
- public package quality
- beginner-friendly installation and usage

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
- putting core logic inside VSCode or UI code

## Recommended Tech Stack

- Python 3.10+
- Typer for CLI
- Rich for terminal output
- Pytest for tests
- pathlib for file operations
- standard Python packaging via `pyproject.toml`
- GitHub Actions for CI / publishing
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

## Markdown Style

Markdown files should be readable in raw form and render cleanly on GitHub.

Use:

- normal line breaks
- fenced code blocks
- clear headings
- short paragraphs
- relative links to docs
- concise examples

Avoid:

- extremely long single-line Markdown sections
- dense README content that should live in `docs/`
- duplicated command documentation across many files
- outdated roadmap promises

Chinese documentation rules:

- Chinese Markdown must be UTF-8 without BOM.
- Do not use GBK, ANSI, or UTF-8 with BOM.
- Avoid wholesale rewrites for encoding-only changes.
- Prefer minimal patches.
- Use `python -m pytest tests/test_docs_encoding.py` to verify Chinese documentation encoding.

## Safety Rules

- Never delete user files automatically.
- Never overwrite existing files unless explicitly allowed.
- Default behavior for file-writing operations should be dry-run when practical.
- Confirmed file-writing operations must require explicit flags such as `--confirm`.
- Generated projects should be written to `outputs/` by default.
- Do not commit generated temporary outputs from `outputs/`.
- Never commit API keys, tokens, private paths, local environment files, logs, backups, local history artifacts, or package build artifacts.
- Never assume the user has ROS or ROS2 installed.
- Never require external services for default offline features.
- Apply must only write files listed in a validated apply plan.
- Rollback must only restore files from a RoboPilot backup.
- History writing must only write RoboPilot metadata under `.robopilot_history/`.

## Existing CLI Commands

The following commands should remain supported:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output robopilot.yaml
```

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
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
robopilot history --project outputs/demo_detector
```

```bash
robopilot detect outputs/demo_detector
```

```bash
robopilot inspect-ros1 path/to/ros1_package
```

```bash
robopilot deps path/to/project
```

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
```

```bash
robopilot migrate-plan-validate --plan migration_plan.yaml
```

```bash
robopilot migrate-plan-diff --old migration_plan_v1.yaml --new migration_plan_v2.yaml
```

```bash
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package
```

```bash
robopilot migrate-scaffold-preview --plan migration_plan.yaml
```

```bash
robopilot migrate-scaffold --plan migration_plan.yaml --output path/to/ros2_scaffold
```

```bash
robopilot migrate-scaffold-validate --plan migration_plan.yaml --scaffold path/to/ros2_scaffold
```

```bash
robopilot migrate-scaffold-report --plan migration_plan.yaml --scaffold path/to/ros2_scaffold --output scaffold_report.md
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

## ProjectSpec Rules

`ProjectSpec` is the central intermediate representation.

Generation, refinement, and apply-related features should flow through `ProjectSpec` or through validated plans derived from `ProjectSpec`.

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

For packaging-related work, also run:

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

For CLI polish, manually verify:

```bash
robopilot --help
robopilot plan --help
robopilot migrate-plan --help
robopilot apply --help
robopilot detect --help
robopilot deps --help
```

## Preferred Development Workflow

1. Read `README.md`, `README.zh-CN.md`, `roadmap.md`, `CHANGELOG.md`, `pyproject.toml`, and this file first.
2. Understand the existing architecture before editing.
3. Implement one small change at a time.
4. Reuse existing modules instead of duplicating logic.
5. Add or update tests.
6. Run tests.
7. Run relevant CLI commands manually.
8. Update README and docs when behavior changes.
9. Update `CHANGELOG.md` under `Unreleased`.
10. Summarize changed files, design decisions, and test results.

## Current Implementation Target

Implement:

```txt
v2.0.1 Post-2.0 Public Polish
```

RoboPilot has reached the stable v2.0.0 stage-completion release. This patch polishes public-facing presentation while preserving the existing no-ROS-required safety model and avoiding product feature work.

Suggested implementation items:

```txt
README.md
README.zh-CN.md
CHANGELOG.md
pyproject.toml
roadmap.md
AGENTS.md
small public documentation metadata fixes
targeted source/docs/tests for accepted scoped work
```

Do not add ROS runtime behavior, ROS2 runtime behavior, catkin/colcon execution, migration apply, automatic source conversion, real tokens, new Python CLI commands, broad VSCode product features, or new LLM behavior unless explicitly accepted through a scoped task. Do not publish PyPI or VSCode Marketplace releases unless explicitly asked.
