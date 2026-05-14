
# Roadmap

RoboPilot is a no-ROS-required static engineering toolchain for ROS-style projects.

The project started as a lightweight ROS-style project generator and has now reached its first stable baseline:

```txt
v1.0.0
```

After v1.0.0, RoboPilot's development should shift from rapid feature expansion to stable public distribution, API layering, beginner-friendly tooling, and carefully scoped ROS/ROS2 static engineering features.

## Product Direction

RoboPilot helps users plan, inspect, update, analyze, and migrate ROS/ROS2-style projects without requiring a local ROS installation.

RoboPilot is not intended to compete directly with general-purpose coding agents or runtime ROS automation tools.

Its niche is:

- no-ROS-required project analysis
- ROS-style project structure understanding
- ProjectSpec-based planning
- safe apply / rollback workflows
- static dependency analysis
- ROS1 / ROS2 migration assistance
- beginner-friendly robotics engineering workflows
- optional LLM-assisted spec workflows

## Core Design Principles

RoboPilot should remain:

- no-ROS-required by default
- static and deterministic where possible
- safe for beginners
- explicit about file-writing operations
- dry-run-first for risky operations
- conservative in dependency and migration inference
- friendly to CLI usage, API integration, and future VSCode UI

RoboPilot should avoid:

- requiring ROS or ROS2
- running `catkin_make`
- running `colcon`
- executing launch files
- executing generated nodes
- replacing runtime validation
- becoming a general-purpose coding agent
- hiding risky file changes behind automatic behavior

## Stable v1.0.0 Baseline

Status: Stable baseline released

v1.0.0 stabilizes RoboPilot as a no-ROS-required static engineering toolchain.

Stable areas include:

- existing core CLI command names
- no-ROS-required default behavior
- ProjectSpec-based generation
- read-only detect / inspect / deps / report workflows
- dry-run-first apply and rollback workflows
- project-local history journal
- static ROS project detection
- ROS1 static inspection
- static dependency analysis
- ROS1-to-ROS2 migration planning workflow

Experimental or advisory areas include:

- LLM planner / refiner
- ROS1-to-ROS2 migration planning
- migration preview
- migration plan diff
- JSON schemas where explicitly marked experimental

Internal areas include:

- internal module layout
- template rendering internals
- heuristic scoring details

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
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output robopilot.yaml
```

```bash
robopilot validate --spec robopilot.yaml
```

```bash
robopilot generate --spec robopilot.yaml
```

## Completed: v0.4.0 Project Inspector

Status: Completed

Goal:

Add a lightweight offline project inspector that analyzes existing RoboPilot-generated or ROS-style project directories.

Completed features:

- `robopilot inspect`
- Static project directory inspection
- Optional JSON output
- Detection of missing project files
- Detection of missing or invalid `robopilot.yaml`
- Reuse of existing spec loader and validator
- Expanded tests
- Updated documentation

Core commands:

```bash
robopilot inspect examples/generated_projects/demo_detector
```

```bash
robopilot inspect examples/generated_projects/demo_detector --json
```

## Completed: v0.5.0 Project Repair Suggestions

Status: Completed

Goal:

Use project inspection results to generate read-only repair suggestions.

Completed features:

- `robopilot repair-suggest`
- Optional JSON output
- Read-only repair suggestion layer
- Deterministic mapping from inspection issues to repair suggestions
- Suggested follow-up commands
- Expanded tests
- Updated documentation

## Completed: v0.6.0 Project Report Export

Status: Completed

Goal:

Combine project inspection and repair suggestions into a Markdown report.

Completed features:

- `robopilot report`
- Terminal Markdown report output
- Markdown report file export
- Reuse of inspector and repair suggester
- Deterministic report sections
- Expanded tests
- Updated documentation

Core commands:

```bash
robopilot report examples/generated_projects/demo_detector
```

```bash
robopilot report examples/generated_projects/demo_detector --output report.md
```

## Completed: v0.7.0 Planner Interface and Optional LLM Planner

Status: Completed

Goal:

Add a planner abstraction and prepare RoboPilot for optional LLM-assisted planning.

Completed features:

- `Planner` interface
- `RuleBasedPlanner`
- `LLMPlanner` with injectable client support
- Planner selection for `robopilot plan`
- Offline rule-based planner as default
- LLM planner path constrained to `ProjectSpec`
- Expanded tests
- Updated documentation

## Completed: v0.8.0 Real LLM Provider Integration

Status: Completed

Goal:

Make the optional LLM planner usable with a real provider while preserving the spec-first architecture.

Completed features:

- Optional OpenAI-compatible planner client
- Environment-based provider configuration
- `OPENAI_API_KEY`
- `ROBOPILOT_LLM_MODEL`
- Optional `llm` dependency extra
- Model selection for LLM planning
- Structured ProjectSpec-compatible LLM output
- Spec validation before returning LLM-generated specs
- Expanded tests
- Updated documentation

## Completed: v0.9.0 Spec Refinement

Status: Completed

Goal:

Allow users to refine existing `robopilot.yaml` / `ProjectSpec` files with deterministic rule-based instructions.

Completed features:

- `robopilot refine`
- Rule-based spec refinement
- Add tracker node
- Add camera node
- Add controller node
- Add explicit topics
- Avoid duplicate nodes and topics
- Preserve original spec by writing to a new output file
- Validate refined specs before saving
- Expanded tests
- Updated documentation

## Completed: v0.10.0 Spec Diff

Status: Completed

Goal:

Compare two ProjectSpec files and report deterministic differences.

Completed features:

- `robopilot diff`
- Optional JSON output
- Comparison of scalar fields
- Comparison of nodes
- Comparison of topics
- Comparison of config files
- Comparison of launch files
- Comparison of notes
- Validation of both specs before diffing
- Expanded tests
- Updated documentation

## Completed: v0.11.0 LLM-assisted Spec Refinement

Status: Completed

Goal:

Enable the existing refine workflow to use the optional LLM provider path safely.

Completed features:

- `LLMRefiner`
- `robopilot refine --planner llm`
- Model selection for LLM-assisted refinement
- Reuse of existing provider config and OpenAI client
- Reuse of ProjectSpec parsing and validation
- Guardrails against unrequested package name and task changes
- Original spec remains unchanged
- Expanded tests
- Updated documentation

## Completed: v0.12.0 Apply Preview

Status: Completed

Goal:

Add a safe, read-only preview workflow that compares a validated spec against an existing project directory.

Completed features:

- `robopilot apply-preview`
- Optional JSON output
- In-memory expected project rendering
- Classification of files to create, update, keep, or flag
- Refactored generator rendering into reusable deterministic rendering
- Multi-node expected Python file rendering
- Expanded tests
- Updated documentation

## Completed: v0.13.0 Apply Plan Export

Status: Completed

Goal:

Export apply-preview results into a reviewable and validatable apply plan file.

Completed features:

- `robopilot apply-plan`
- `robopilot apply-plan-validate`
- YAML-like apply plan export
- JSON apply plan export
- Stable apply plan fields
- Apply plan validation
- Reuse of apply-preview logic
- Expanded tests
- Updated documentation

## Completed: v0.14.0 Apply from Plan

Status: Completed

Goal:

Add the first safe file-writing workflow based on a validated apply plan.

Completed features:

- `robopilot apply`
- Dry-run apply by default
- Confirmed apply with `--confirm`
- JSON summary output
- Apply plan validation before applying
- Re-run apply-preview before applying
- Stale plan rejection
- Conflict rejection
- Restricted writes based on plan contents
- Backup creation before updates
- Unsafe relative path rejection
- Expanded tests
- Updated documentation

## Completed: v0.15.0 Apply Rollback

Status: Completed

Goal:

Add a safe rollback workflow for files backed up during `robopilot apply --confirm`.

Completed features:

- `robopilot rollback`
- Dry-run rollback by default
- Confirmed rollback with `--confirm`
- JSON summary output
- Restore files from RoboPilot backup directories
- Project path validation
- Backup path validation
- Path traversal protection
- Symlink protection
- No deletion of newly created files in this version
- Expanded tests
- Updated documentation

## Completed: v0.16.0 Apply History / Workspace Journal

Status: Completed

Goal:

Add a project-local history system that records confirmed apply and rollback operations.

Completed features:

- `robopilot history`
- Optional JSON output
- Project-local journal entries under `.robopilot_history/`
- Confirmed apply history entries
- Confirmed rollback history entries
- No successful modification history for dry-runs
- Apply-preview ignores RoboPilot metadata directories
- Expanded tests
- Updated documentation

## Completed: v0.17.0 ROS Project Detector

Status: Completed

Goal:

Introduce static project type detection for existing ROS-style projects.

Completed features:

- `robopilot detect`
- Optional JSON output
- Static signal collection
- Conservative project classification
- RoboPilot project detection
- ROS1 catkin package detection
- ROS2 ament Python package detection
- ROS2 ament C++ package detection
- Mixed ROS-style project detection
- Non-ROS / unknown project detection
- Expanded tests
- Updated documentation

Supported categories:

- `robopilot_project`
- `ros1_catkin_package`
- `ros2_ament_python_package`
- `ros2_ament_cmake_package`
- `mixed_ros_project`
- `non_ros_project`
- `unknown`

## Completed: v0.18.0 ROS1 Static Inspector

Status: Completed

Goal:

Extend RoboPilot's inspection capability to ROS1 catkin packages.

Completed features:

- `robopilot inspect-ros1`
- Optional JSON output
- Static parsing of `package.xml`
- Conservative parsing of `CMakeLists.txt`
- Catkin dependency and component detection
- Launch/msg/srv/action file discovery
- Python and C++ ROS1 node candidate detection
- ROS1 structure issue reporting
- Expanded tests
- Updated documentation

## Completed: v0.19.0 Dependency Analyzer

Status: Completed

Goal:

Analyze declared and detected dependencies in ROS-style projects.

Completed features:

- `robopilot deps`
- Optional JSON output
- `package.xml` dependency extraction
- CMake `find_package(...)` and catkin component extraction
- Python import detection without executing code
- C++ include detection
- Launch file package reference detection
- Conservative missing / unused dependency hints
- Expanded tests
- Updated documentation

## Completed: v0.20.0 ROS1 to ROS2 Migration Plan

Status: Completed

Goal:

Generate a static ROS1-to-ROS2 migration plan for ROS1 catkin packages.

Completed features:

- `robopilot migrate-plan`
- YAML-like output
- JSON output
- Reuse of detection, ROS1 inspection, and dependency analysis
- Package metadata migration guidance
- Catkin-to-ament build system guidance
- `rospy` to `rclpy` migration notes
- `roscpp` to `rclcpp` migration notes
- Launch migration guidance
- msg/srv/action migration notes
- Dependency migration hints
- Manual review items and risks
- Expanded tests
- Updated documentation

## Completed: v0.21.0 Migration Apply Preview

Status: Completed

Goal:

Transform a migration plan into a read-only file-level migration preview.

Completed features:

- `robopilot migrate-preview`
- Optional JSON output
- Migration plan loading and validation
- File-level migration preview
- Files to create / update / keep
- Files requiring manual migration
- Interface files to review
- Dependency items to review
- Conflicts, risks, and suggested next steps
- Expanded tests
- Updated documentation

## Completed: v0.22.0 Migration Plan Validate / Diff

Status: Completed

Goal:

Make migration plans easier to validate and compare before future migration generation or apply workflows.

Completed features:

- `robopilot migrate-plan-validate`
- `robopilot migrate-plan-diff`
- JSON output for both commands
- Required-field validation
- Unsupported target validation
- Scalar field diff
- List-like section diff
- Nested dependency migration diff
- UTF-8 BOM migration plan loading support
- Expanded tests
- Updated documentation

## Completed: v0.23.0 Stability / CLI Polish

Status: Completed

Goal:

Improve CLI clarity, documentation structure, and v1.0 readiness without adding new product capabilities.

Completed work:

- CLI help text polish
- Simplified README files
- Command reference documentation
- Workflow documentation
- Architecture documentation
- v1 scope documentation
- Updated `.gitignore`
- Updated roadmap and agent guidance
- Expanded documentation entry points
- No product command changes

## Completed: v0.24.0 v1.0 Release Candidate Preparation

Status: Completed

Goal:

Prepare RoboPilot for a future v1.0.0 release candidate.

Completed work:

- Testing documentation
- Release process documentation
- Compatibility documentation
- Known limitations documentation
- Stability policy documentation
- v1.0 scope updates
- RC versioning policy
- Documentation audit
- No new product capabilities

## Completed: v1.0.0-rc.1 Release Candidate

Status: Completed

Goal:

Perform a release candidate checklist pass for RoboPilot 1.0.

Completed work:

- Version update to `1.0.0rc1`
- GitHub tag form documented as `v1.0.0-rc.1`
- CLI help audit
- Documentation link audit
- Stability scope audit
- Known limitations audit
- Release process audit
- Testing documentation audit
- Manual help command verification
- Full test pass

## Completed: v1.0.0 First Stable Release

Status: Completed

Goal:

Release RoboPilot's first stable version as a no-ROS-required static engineering toolchain for ROS-style projects.

Stable release scope:

- ProjectSpec workflow
- safe apply / rollback / history loop
- static project detection
- ROS1 static inspection
- dependency analyzer
- ROS1-to-ROS2 migration plan / validate / diff / preview
- optional LLM planner / refiner boundaries
- no ROS runtime requirement
- stable CLI baseline
- release and stability documentation

## Completed: v1.1.0 Packaging & Public Developer Experience

Status: Completed

Goal:

Prepare RoboPilot for PyPI distribution and broader open-source use.

This milestone should not add robotics product features. It should make RoboPilot easier to install, publish, verify, and contribute to.

Expected work:

- audit `pyproject.toml` metadata
- confirm package name and console script
- add local build verification docs
- add package build checks
- add TestPyPI / PyPI publishing workflow
- prefer PyPI Trusted Publishing over long-lived API tokens
- document PyPI publishing process
- add `CONTRIBUTING.md`
- add `SECURITY.md`
- add issue templates
- add pull request template
- add developer setup docs
- update README installation instructions
- keep optional LLM dependencies optional

Possible new files:

```txt
CONTRIBUTING.md
SECURITY.md
docs/pypi_publish.md
docs/developer_setup.md
.github/ISSUE_TEMPLATE/bug_report.yml
.github/ISSUE_TEMPLATE/feature_request.yml
.github/pull_request_template.md
.github/workflows/publish.yml
.github/workflows/test-publish.yml
```

Recommended checks:

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

Manual PyPI setup should use:

```txt
Project name: robopilot
Owner: J1angJJ
Repository: RoboPilot
Workflow: publish.yml
Environment: pypi
```

The exact PyPI availability of the `robopilot` package name is determined by PyPI at publish time.

## Completed: v1.2.0 API Layer Refactor

Status: Completed

Goal:

Introduce a stable Python API layer so CLI, future VSCode extension, scripts, and possible UI tools can reuse the same core logic.

The API layer should not replace the CLI. It should make the CLI cleaner and make future integration easier.

Proposed structure:

```txt
src/robopilot/api/
├─ __init__.py
├─ project.py
├─ static_analysis.py
├─ migration.py
├─ apply.py
└─ models.py
```

Expected principles:

- no Rich rendering
- no direct stdout printing
- no `sys.exit`
- stable result objects or dictionaries
- explicit file-writing behavior
- reuse existing core modules
- clear exceptions or result types
- CLI remains a presentation layer

Possible API groups:

```txt
project.py
- plan_project
- refine_project_spec
- diff_project_specs
- validate_project_spec
- generate_project

static_analysis.py
- detect_project_type
- inspect_project_static
- inspect_ros1_project_static
- analyze_project_dependencies
- export_project_report

migration.py
- create_ros1_to_ros2_migration_plan
- validate_migration_plan_file
- diff_migration_plan_files
- preview_migration_plan

apply.py
- preview_apply
- export_apply_plan
- validate_apply_plan_file
- apply_exported_plan
- rollback_project_backup
- read_project_history
```

## Completed: v1.3.0 Stable JSON Contracts / Schema Docs

Status: Completed

Goal:

Document and stabilize JSON outputs for CLI and future VSCode integration.

Expected work:

- document JSON output for major commands
- define which JSON fields are stable
- define experimental JSON fields
- add schema-like docs for key outputs
- align CLI `--json` outputs for VSCode consumption
- add compatibility notes for JSON consumers

Important commands for JSON contract docs:

- detect
- inspect
- inspect-ros1
- deps
- migrate-plan
- migrate-plan-validate
- migrate-plan-diff
- migrate-preview
- apply-preview
- apply-plan
- apply
- rollback
- history
- report

## Completed: v1.4.0 VSCode Extension MVP

Status: Completed

Goal:

Create a beginner-friendly VSCode extension that wraps RoboPilot CLI/API functionality.

The extension should be thin. It should not duplicate RoboPilot's core logic.

Preferred initial approach:

```txt
VSCode extension
    ↓
spawn robopilot CLI with --json
    ↓
parse JSON
    ↓
display TreeView / Webview / OutputChannel
```

Possible MVP commands:

- RoboPilot: Detect Workspace
- RoboPilot: Inspect ROS1 Package
- RoboPilot: Analyze Dependencies
- RoboPilot: Generate Migration Plan
- RoboPilot: Preview Migration
- RoboPilot: Validate ProjectSpec
- RoboPilot: Open Report

Future plugin direction:

- show project type summary
- show dependency warnings
- open generated reports
- display migration plan tree
- display migration preview tree
- validate `robopilot.yaml`
- run commands from command palette

The VSCode extension should remain optional and should not be required for CLI usage.

## Completed: v1.5.0 ROS2 Static Inspector

Status: Completed

Goal:

Add a no-ROS-required static inspector for ROS2 ament packages.

Possible command:

```bash
robopilot inspect-ros2 path/to/ros2_package
```

Expected support:

- ROS2 ament Python package inspection
- ROS2 ament C++ package inspection
- `package.xml`
- `setup.py`
- `setup.cfg`
- `CMakeLists.txt`
- `resource/`
- `launch/`
- `config/`
- `msg/`
- `srv/`
- `action/`
- `rclpy` node candidates
- `rclcpp` node candidates
- `ament_package()`
- `ament_python` build type
- dependency hints
- potential structure issues

This feature should remain static and should not require ROS2 or colcon.

Expected command:

```bash
robopilot inspect-ros2 path/to/ros2_package
```

JSON output:

```bash
robopilot inspect-ros2 path/to/ros2_package --json
```

## Completed: v1.6.0 Dependency Analyzer Enhancement

Status: Completed

Goal:

Improve dependency analysis with richer ROS1 / ROS2 dependency hints and migration-oriented mappings.

Possible improvements:

- ROS1 dependency to ROS2 dependency hints
- `rosdep` package hints
- Python import to `package.xml` dependency hints
- C++ include to `package.xml` dependency hints
- clearer missing / unused dependency explanations
- richer migration dependency warnings

Possible mappings:

```txt
rospy      → rclpy
roscpp     → rclcpp
catkin     → ament_cmake / ament_python
tf         → tf2_ros
dynamic_reconfigure → ROS2 parameters / lifecycle review
```

## Completed: v1.7.0 Migration Scaffold Preview

Status: Completed

Goal:

Preview a ROS2 package scaffold derived from a ROS1-to-ROS2 migration plan.

Possible command:

```bash
robopilot migrate-scaffold-preview --plan migration_plan.yaml
```

Expected preview:

- ROS2-style `package.xml`
- ROS2-style `CMakeLists.txt` or `setup.py`
- ROS2 launch file placeholders
- config file placeholders
- node migration TODO placeholders
- files requiring manual migration
- risks and review notes

This should remain read-only.

## Completed: v1.8.0 Migration Scaffold Generate

Status: Completed

Goal:

Generate a conservative ROS2 scaffold from a migration plan.

Possible command:

```bash
robopilot migrate-scaffold --plan migration_plan.yaml --output ros2_package/
```

Expected behavior:

- generate scaffold files only
- include TODO comments for manual migration
- avoid pretending to fully migrate business logic
- remain explicit about limitations
- support dry-run / preview where practical
- avoid executing ROS2 or colcon

## Completed: v1.9.0 Migration Scaffold Validate

Status: Completed

Goal:

Validate generated ROS2 migration scaffolds against migration plans and RoboPilot scaffold expectations.

Expected command:

```bash
robopilot migrate-scaffold-validate --plan migration_plan.yaml --scaffold ros2_package/
```

Expected behavior:

- read-only validation
- deterministic `--json` output
- reuse migration plan validation, scaffold preview/generation expectations, and ROS2 static inspection
- report missing files, unexpected files, placeholder safety wording gaps, and `MIGRATION_NOTES.md` status
- do not modify the source project, migration plan, or scaffold
- do not run ROS, ROS2, catkin, colcon, launch files, or generated code
- do not import generated scaffold modules

## Completed: v1.10.0 Migration Scaffold Report

Status: Completed

Goal:

Turn scaffold validation results into a deterministic human-readable Markdown report.

Expected command:

```bash
robopilot migrate-scaffold-report --plan migration_plan.yaml --scaffold ros2_package/ --output scaffold_report.md
```

Expected behavior:

- print Markdown to stdout when `--output` is omitted
- write only the explicit report output file when `--output` is provided
- refuse to overwrite existing report files by default
- reuse migration scaffold validation
- include validation status, files, placeholder checks, ROS2 static inspection summary, manual migration items, issues, warnings, next steps, and safety notes
- do not modify the source project, migration plan, or scaffold
- do not run ROS, ROS2, catkin, colcon, launch files, or generated code
- do not import generated scaffold modules

This milestone completes the first migration scaffold review loop:

```txt
migrate-plan
  -> migrate-scaffold-preview
  -> migrate-scaffold
  -> migrate-scaffold-validate
  -> migrate-scaffold-report
```

## Completed: v1.11.0 VSCode Extension Migration Workflow Polish

Status: Completed

Goal:

Make the completed migration scaffold review loop easier to use from VSCode while keeping the CLI/API/JSON contracts as the source of truth.

Expected behavior:

- expose the existing migration planning, scaffold preview, scaffold generation, scaffold validation, and scaffold report commands clearly
- support `RoboPilot: Preview Migration Scaffold`, `RoboPilot: Generate Migration Scaffold`, `RoboPilot: Validate Migration Scaffold`, `RoboPilot: Generate Scaffold Report`, and `RoboPilot: Open Scaffold Report`
- improve command palette labels, user-facing error messages, output display, and documentation links
- keep the VSCode extension as a thin CLI/API wrapper
- preserve no-ROS-required static behavior
- do not duplicate RoboPilot migration logic in TypeScript
- do not add migration apply, automatic source conversion, ROS execution, ROS2 execution, colcon execution, or launch execution

## Completed: v1.12.0 VSCode Extension VSIX Packaging

Status: Completed

Goal:

Prepare a local VSIX packaging flow for the existing VSCode extension without changing RoboPilot core behavior.

Expected behavior:

- document repeatable VSIX build steps
- keep packaging metadata accurate and conservative
- keep the extension optional
- run extension compile/test checks when extension files change
- do not publish to the VSCode Marketplace

## Completed: v1.13.0 VSCode Marketplace Publish Preparation

Status: Completed

Goal:

Prepare Marketplace publishing materials and checks without compromising stability.

Expected behavior:

- audit extension README, icon, categories, and package metadata
- add extension changelog and Marketplace publishing checklist
- document publisher id confirmation and `VSCE_PAT` token handling
- document publishing steps and required accounts or tokens
- optionally prepare a manually triggered GitHub Actions publish workflow
- avoid committing secrets or generated marketplace artifacts
- do not actually publish to the Marketplace in this milestone
- keep Marketplace publishing separate from RoboPilot core releases

## Completed: v1.14.0 Examples / Tutorials / Demo Pack

Status: Completed

Goal:

Make the existing workflows easier to learn with concise examples and tutorials.

Expected behavior:

- add or refresh demo projects and walkthroughs
- show the complete migration scaffold review loop
- keep examples small, static, and no-ROS-required
- avoid promising automatic migration correctness

## Completed: v1.15.0 Migration Workflow UX Polish

Status: Completed

Goal:

Improve the usability of the existing migration assistant workflow without expanding into risky automation.

Expected behavior:

- improve wording, next steps, and report readability
- tighten documentation around manual review responsibilities
- preserve deterministic static behavior
- do not add migration apply or automatic source conversion

## Current: v1.16.0 Chinese Documentation Expansion + Encoding Guardrails

Status: Current priority

Goal:

Expand Chinese documentation so Chinese users can learn and use RoboPilot without relying only on English docs, and add guardrails to avoid Chinese Markdown encoding regressions.

Expected behavior:

- add `docs/zh-CN/README.md` as a Chinese documentation index
- add or expand Chinese versions of key beginner-facing docs:
  - `docs/zh-CN/tutorial_ros1_to_ros2_migration.md`
  - `docs/zh-CN/tutorial_vscode_migration_workflow.md`
  - `docs/zh-CN/troubleshooting.md`
  - `docs/zh-CN/vscode_extension.md`
  - `docs/zh-CN/vscode_packaging.md`
  - `docs/zh-CN/vscode_marketplace.md`
  - `docs/zh-CN/workflows.md`
  - `docs/zh-CN/known_limitations.md`
  - `docs/zh-CN/demo_walkthrough.md`
- keep `README.zh-CN.md` concise and link to the Chinese documentation index
- prioritize beginner-facing docs over internal developer docs
- keep command names in English
- keep technical terms clear and natural in Chinese
- keep Chinese Markdown UTF-8 without BOM
- add encoding checks for Chinese Markdown
- do not change product behavior

## Future: v1.17.0 VSCode Marketplace Publish

Status: Planned

Goal:

Publish the RoboPilot VSCode extension to Visual Studio Marketplace, or complete a publish-ready release if manual account or token setup blocks actual publishing.

Expected behavior:

- confirm VSCode extension package metadata
- confirm the Marketplace publisher id matches `vscode-extension/package.json`
- confirm extension README and CHANGELOG are Marketplace-ready
- confirm VSIX packaging still works
- use the existing `vscode-publish` workflow or a manual `vsce publish` flow
- document required manual steps for publisher setup, Azure DevOps PAT creation, `VSCE_PAT`, workflow trigger, and listing verification
- update README files only after actual Marketplace publishing succeeds
- if publishing is not performed, keep docs clear that this is Marketplace publish preparation
- do not commit secrets or hardcode PAT values
- do not add VSCode product features unless required for listing quality

## Future: v1.18.0 Stability / Compatibility / Cleanup

Status: Planned

Goal:

Prepare the v2.0 release candidate by cleaning up documentation, compatibility notes, tests, and packaging checks.

Expected behavior:

- check all documentation links
- check Chinese and English docs consistency
- check README and README.zh-CN remain concise
- check PyPI installation instructions
- check VSCode Marketplace or VSIX installation instructions
- check examples and tutorials are still runnable
- check JSON contracts and API docs remain accurate
- check known limitations and troubleshooting are up to date
- check version metadata consistency
- check CI status
- check packaging and publishing docs
- check no ignored build artifacts are tracked
- run full Python tests
- run Python build/twine checks
- run VSCode extension compile/test/package checks
- verify PyPI install
- verify VSCode extension install path
- verify no-ROS-required behavior remains intact
- clarify stable, experimental, and internal surfaces
- remove stale roadmap promises
- do not add major features

## Future: v2.0.0-rc.1

Status: Planned

Goal:

Run a release candidate for the v2.0 stage-completion release.

Expected behavior:

- freeze product features
- do not add new commands
- do not add risky migration apply
- do not add automatic source-code conversion
- do not add ROS/ROS2 runtime execution
- do not add colcon/catkin execution
- only fix bugs, documentation issues, packaging issues, and release readiness issues
- validate the complete CLI workflow
- validate PyPI install
- validate VSCode extension install
- validate examples and tutorials
- validate English and Chinese docs
- prepare release notes

## Future: v2.0.0

Status: Planned

Goal:

Mark RoboPilot's static engineering and migration assistant workflow as a completed stage.

v2.0.0 is a stage-completion milestone, not necessarily a breaking rewrite. If no breaking changes are introduced, documentation should say: "v2.0.0 is a stage-completion release, not a breaking rewrite."

Expected behavior:

- PyPI-distributed CLI
- Python API layer
- JSON contracts
- VSCode extension
- English and Chinese documentation
- examples, tutorials, and demo pack
- static ROS1/ROS2 inspection
- dependency analysis
- ROS1-to-ROS2 migration planning
- migration scaffold preview / generate / validate / report workflow
- no-ROS-required safety model

Explicit non-goals before v2.0:

- no migration apply
- no automatic ROS1-to-ROS2 business logic conversion
- no automatic source patching
- no ROS runtime execution
- no ROS2 runtime execution
- no `catkin_make`
- no `colcon`
- no launch execution
- no generated node execution
- no new LLM agent behavior
- no complex Webview UI

## Long-term: VSCode Extension Expansion

Status: Long-term idea

After the VSCode MVP, possible future features include:

- persistent sidebar view
- command palette integration
- migration plan tree view
- dependency warning panel
- report preview
- ProjectSpec validation view
- guided beginner workflow
- one-click CLI command execution
- clear safety prompts for file-writing workflows

The extension should remain a UI wrapper over stable RoboPilot CLI/API functionality.

## Non-goals

RoboPilot will not focus on the following unless the project direction explicitly changes:

- real robot deployment
- heavy model training
- full ROS runtime execution
- automatic `catkin_make`
- automatic `colcon build`
- SLAM implementation
- reinforcement learning training
- large-scale VLA model inference
- embedded low-level driver development
- complex multi-agent orchestration
- replacing general-purpose coding agents
- automatic full project migration without manual review
- migration apply before v2.0
- automatic source code conversion before v2.0
- automatic ROS, ROS2, colcon, or launch execution before v2.0

## Development Priorities After v1.0.0

Priority order:

1. Keep the CLI runnable and stable.
2. Keep no-ROS-required usage as a core principle.
3. Improve installation and public distribution.
4. Prepare a clean API layer.
5. Make JSON outputs usable by VSCode and external tools.
6. Build a beginner-friendly VSCode extension as a thin wrapper.
7. Improve ROS/ROS2 static analysis.
8. Improve migration planning and scaffold workflows.
9. Preserve dry-run-first safety for file-writing operations.
10. Keep documentation concise and current.

## Recommended Path

```txt
v1.10.0 Migration Scaffold Report
  -> v1.11.0 VSCode Extension Migration Workflow Polish
  -> v1.12.0 VSCode Extension VSIX Packaging
  -> v1.13.0 VSCode Marketplace Publish Preparation
  -> v1.14.0 Examples / Tutorials / Demo Pack
  -> v1.15.0 Migration Workflow UX Polish
  -> v1.16.0 Chinese Documentation Expansion + Encoding Guardrails
  -> v1.17.0 VSCode Marketplace Publish
  -> v1.18.0 Stability / Compatibility / Cleanup
  -> v2.0.0-rc.1
  -> v2.0.0
```

v2.0.0 should mark stage completion for the v1.x static engineering toolchain. It is not intended to be a breaking rewrite unless a future release plan explicitly says so.

## Historical Path Through v1.8.0

```txt
v1.1.0 Packaging & Public Developer Experience
        ↓
v1.2.0 API Layer Refactor
        ↓
v1.3.0 Stable JSON Contracts / Schema Docs
        ↓
v1.4.0 VSCode Extension MVP
        ↓
v1.5.0 ROS2 Static Inspector
        ↓
v1.6.0 Dependency Analyzer Enhancement
        ↓
v1.7.0 Migration Scaffold Preview
        ↓
v1.8.0 Migration Scaffold Generate
```

Next planned milestone after v1.16.0: v1.17.0 VSCode Marketplace Publish.

RoboPilot should grow as a practical no-ROS-required ROS engineering toolchain, with CLI as the stable core and beginner-friendly interfaces layered on top.
