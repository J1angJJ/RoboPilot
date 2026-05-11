# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- v0.24.0 v1.0 release candidate preparation documentation.
- `docs/testing.md` covering dev dependency installation, full and selected test runs, Windows pytest temp workaround, manual workflow checks, and no-ROS/no-network expectations.
- `docs/release_process.md` covering version bumps, changelog updates, tests, manual CLI checks, commit conventions, tags, GitHub Releases, and rollback planning.
- `docs/compatibility.md` covering supported Python versions, expected operating systems, no-ROS runtime boundaries, supported project categories, and heuristic areas.
- `docs/known_limitations.md` covering static analysis limits, migration limits, apply/rollback constraints, LLM validation caveats, and unimplemented VSCode integration.
- `docs/stability_policy.md` defining stable, experimental, and internal areas before v1.0 final.
- v0.23.0 stability and CLI polish pass.
- `docs/command_reference.md` with command purpose, examples, read-only/file-writing mode, and safety notes.
- `docs/workflows.md` with the main spec-first, apply/rollback, inspection, static analysis, and migration workflows.
- `docs/architecture.md` with the no-ROS-required design, ProjectSpec workflow, deterministic rendering, safety chain, static analysis modules, migration modules, and LLM boundaries.
- `docs/v1_scope.md` with proposed v1.0.0 scope and non-goals.
- v0.22.0 static migration plan validation and diff review.
- `robopilot migrate-plan-validate --plan ...` command.
- `robopilot migrate-plan-validate --json` deterministic JSON output.
- `robopilot migrate-plan-diff --old ... --new ...` command.
- `robopilot migrate-plan-diff --json` deterministic JSON output.
- Validation reports for missing fields, invalid fields, unsupported migration targets, warnings, suggested next steps, and safety notes.
- Migration plan diffs for scalar fields, list-like sections, dependency migration items, added items, removed items, unchanged fields, warnings, and safety notes.
- Reuse of the existing migration plan JSON and RoboPilot YAML-like loader for validation, diff, and preview workflows.
- v0.21.0 no-ROS-required static migration apply preview.
- `robopilot migrate-preview --plan ... --project ...` command.
- `robopilot migrate-preview --json` deterministic JSON output.
- Migration preview loading and validation for JSON and RoboPilot YAML-like migration plans.
- File-level migration classifications for planned ROS2 files to create, files to keep, files requiring manual migration, interface files to review, dependency items to review, conflicts, risks, and suggested next steps.
- Conservative conflict detection for unsupported targets, missing source projects, source path mismatches, mixed ROS signals, and planned ROS2 files that already exist in the source tree.
- Migration preview reuse of migration plans, static project detection, ROS1 inspection, and dependency analysis.
- v0.20.0 no-ROS-required static ROS1-to-ROS2 migration planning.
- `robopilot migrate-plan --from ... --to ros2 --output ...` command.
- `robopilot migrate-plan --format json` deterministic JSON output.
- Migration plan sections for package.xml migration, build system migration, source code migration, launch migration, interface migration, dependency migration, suggested file changes, manual review items, risks, and suggested next steps.
- Migration planning reuse of static project detection, ROS1 inspection, and dependency analysis.
- Conservative ROS1-to-ROS2 hints for catkin to ament, `rospy` to `rclpy`, `roscpp` to `rclcpp`, ROS1 launch XML to ROS2 Python launch files, and catkin message generation to ROS2 interface generation.
- v0.19.0 no-ROS-required static dependency analyzer for ROS-style projects.
- `robopilot deps path/to/project` command.
- `robopilot deps --json` deterministic JSON output.
- Static extraction of `package.xml` buildtool, build, exec, run, and test dependencies.
- Static extraction of CMake `find_package(...)` dependencies and catkin components.
- Static detection of Python imports, C++ includes, and launch file package references.
- Conservative inferred dependency hints for common ROS and robotics imports/includes such as `rospy`, `roscpp`, `rclpy`, `rclcpp`, `sensor_msgs`, `geometry_msgs`, `std_msgs`, `cv_bridge`, `image_transport`, `numpy`, and `cv2`.
- Reporting for possibly missing and possibly unused dependencies with conservative wording.
- v0.18.0 no-ROS-required static ROS1 catkin package inspector.
- `robopilot inspect-ros1 path/to/ros1_package` command.
- `robopilot inspect-ros1 --json` deterministic JSON output.
- Static ROS1 metadata extraction from `package.xml`, including package name, package format, buildtool dependencies, build dependencies, exec dependencies, and run dependencies.
- Static CMake/catkin signal extraction from `CMakeLists.txt`, including `find_package(catkin REQUIRED COMPONENTS ...)` components and `catkin_package()`.
- Detection of launch, msg, srv, action, Python, and C++ files in ROS1 package directories.
- ROS1 node candidate detection for `rospy` Python files and `roscpp` C++ files without importing or executing user code.
- ROS1 package issue reporting for missing core files, missing catkin metadata, missing launch/scripts directories, missing message generation hints, and non-ROS or ROS2 detector warnings.
- v0.17.0 no-ROS-required static ROS project detector.
- `robopilot detect path/to/project` command.
- `robopilot detect --json` deterministic JSON output.
- Detection categories for RoboPilot projects, ROS1 catkin packages, ROS2 ament Python packages, ROS2 ament CMake packages, mixed ROS-style projects, non-ROS projects, and unknown projects.
- Static signal detection for `robopilot.yaml`, `package.xml`, `CMakeLists.txt`, `setup.py`, `setup.cfg`, ROS-style directories, catkin, ament, `rclpy`, `rclcpp`, `rospy`, and `roscpp`.
- v0.16.0 project-local apply history / workspace journal.
- `robopilot history --project ...` command.
- `robopilot history --json` deterministic JSON output.
- History entries under `.robopilot_history/` for confirmed apply operations.
- History entries under `.robopilot_history/` for confirmed rollback operations.
- Apply-preview conflict ignoring for RoboPilot metadata directories such as `.robopilot_history/` and `.robopilot_backups/`.
- v0.15.0 safe apply rollback workflow.
- `robopilot rollback --project ... --backup ...` dry-run command.
- `robopilot rollback --confirm` confirmed restore mode for RoboPilot backups.
- `robopilot rollback --json` deterministic JSON summary output.
- Safety checks for missing project paths, invalid backup paths, unsafe relative paths, path traversal, and non-RoboPilot backup locations.
- Rollback behavior that restores only files contained in the backup directory and does not delete newly created files.
- v0.14.0 safe apply-from-plan workflow.
- `robopilot apply --plan ...` dry-run command.
- `robopilot apply --plan ... --confirm` confirmed file-writing mode.
- `robopilot apply --json` deterministic JSON summary output.
- Stale-plan, conflict, unsafe-path, and unexpected-file safety checks before writing.
- Backup creation under `.robopilot_backups/<timestamp>/` before updating existing files.
- v0.13.0 read-only apply plan export workflow.
- `robopilot apply-plan --spec ... --project ... --output ...` command.
- `robopilot apply-plan --format json` support.
- `robopilot apply-plan-validate --plan ...` command.
- Deterministic YAML-like and JSON apply plan serialization.
- Apply plan validation for required stable fields.
- v0.12.0 read-only apply preview workflow.
- `robopilot apply-preview --spec ... --project ...` command.
- `robopilot apply-preview --json` deterministic JSON output.
- Preview classification for files to create, update, keep, and conflicts.
- In-memory project rendering shared with deterministic generation.
- Multi-node ProjectSpec rendering for expected Python node files.
- v0.11.0 optional LLM-assisted ProjectSpec refinement workflow.
- `robopilot refine --planner llm --model ...` support.
- LLM refiner prompt that includes the current ProjectSpec, user instruction, allowed schema, and safety constraints.
- Validation of LLM-refined ProjectSpec output before writing.
- Guardrails preventing unrequested `package_name` and `task` changes.
- Reuse of existing provider configuration, OpenAI client, ProjectSpec parsing, and validation.
- v0.10.0 static ProjectSpec diff workflow.
- `robopilot diff --old ... --new ...` command.
- `robopilot diff --json` deterministic JSON output for tests and integrations.
- Diff reporting for scalar fields, nodes, topics, config files, launch files, and notes.
- Validation of both ProjectSpec files before diffing.
- Read-only diff behavior that never modifies either spec file.
- v0.9.0 rule-based ProjectSpec refinement workflow.
- `robopilot refine --spec ... --instruction ... --output ...` command.
- Deterministic refinements for tracker, camera, controller, notes, and explicit topic additions.
- Duplicate node/topic avoidance during refinement.
- Refined ProjectSpec validation before writing output.
- Initial rule-only refinement path before optional LLM refinement support.
- v0.8.0 real OpenAI provider integration for optional ProjectSpec-only planning.
- Provider configuration from `OPENAI_API_KEY` and `ROBOPILOT_LLM_MODEL`.
- `robopilot plan --planner llm --model ...` model override support.
- Optional `llm` extra for installing the official OpenAI Python package.
- OpenAI provider wrapper with clear missing-key, missing-SDK, and provider-call errors.
- Parsing of LLM ProjectSpec output from JSON or RoboPilot's limited YAML schema.
- Minimal `.env.example` with placeholder LLM environment variables.
- v0.7.0 planner interface for ProjectSpec generation.
- Rule-based planner wrapper for the existing offline task classification flow.
- Optional ProjectSpec-only LLM planner with injectable client support for tests and integrations.
- `robopilot plan --planner rule` and `robopilot plan --planner llm` planner selection.
- Validation of LLM-produced ProjectSpec data before generation.
- Clear CLI error when the optional LLM planner is requested without a configured client.
- v0.6.0 project report export workflow combining inspection and repair suggestions.
- `robopilot report` command for printing deterministic Markdown reports.
- `robopilot report --output` support for writing Markdown reports to disk.
- Static report sections for project summary, spec status, detected files, potential issues, repair suggestions, suggested commands, and safety notes.
- v0.5.0 project repair suggestion workflow based on the Project Inspector.
- `robopilot repair-suggest` command with structured terminal output.
- `robopilot repair-suggest --json` deterministic JSON output for tests and integrations.
- Safe issue-to-suggestion mapping for missing package files, missing directories, missing or invalid `robopilot.yaml`, empty directories, and non-existent paths.
- Read-only repair guidance with no automatic file modification and no `--apply` mode.
- v0.4.0 project inspector for RoboPilot-generated and ROS-style project directories.
- `robopilot inspect` command with structured terminal output.
- `robopilot inspect --json` deterministic JSON output for tests and integrations.
- Static checks for missing package files, launch/config directories, Python package directories, and `robopilot.yaml`.
- Inspector reuse of existing ProjectSpec loader and validator.
- v0.3.0 spec-first generation workflow.
- `robopilot plan` command for creating and printing `robopilot.yaml` specs.
- `robopilot validate --spec` command for checking ProjectSpec files before generation.
- `robopilot generate --spec` support for generating packages from saved specs.
- Lightweight built-in ProjectSpec YAML serialization and validation.
- v0.2.0 prompt-driven template selection for `robopilot generate`.
- Offline task classification for `camera_subscriber`, `object_detection`,
  `velocity_controller`, `perception_pipeline`, and `generic_node` templates.
- Generated `robopilot.yaml` metadata with package name, task, selected template,
  generator name, and notes.
- Template registry and project specification layer for deterministic generation.

### Changed

- Simplified `README.md` and `README.zh-CN.md` into concise project overview pages that link to detailed docs.
- Updated CLI top-level help text to emphasize no-ROS-required static tooling.
- Updated `.gitignore` coverage for RoboPilot local backup and history metadata.
- Updated package metadata and generated demo package version to `0.23.0`.
- Updated README documentation links and v1.0 scope notes for release-candidate readiness.
- Updated package metadata and generated demo package version to `0.24.0`.

## [0.1.0] - 2026-05-09

### Added

- Offline ROS-style package generator with safe default output behavior.
- Offline robotics error log debugger for common development errors.
- Pipeline-to-Mermaid workflow graph generator.
- English and Chinese README files.
- Demo script for project walkthroughs.
- Static generated example project for GitHub showcase demos.
- Example prompts, error logs, and Mermaid graph assets.
- Pytest coverage for generator, debugger, and graph modules.
