# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- v1.18.0 stability, compatibility, documentation, packaging, and release-readiness cleanup before the v2.0 release candidate.
- v1.17.0 VSCode Marketplace publish readiness for extension id `j1angjj.robopilot-vscode`.
- Marketplace documentation for extension install, later updates, listing verification, and publishing failure recovery.
- v1.16.0 Chinese documentation expansion and encoding guardrails.
- `docs/zh-CN/` Chinese documentation index, tutorials, troubleshooting, VSCode, workflow, limitation, and demo walkthrough docs.
- `.editorconfig` UTF-8 defaults for common source and documentation files.
- `tests/test_docs_encoding.py` to verify Chinese Markdown UTF-8 decoding, no BOM, no replacement characters, and non-empty files.
- v1.15.0 migration workflow UX polish for the existing no-ROS-required scaffold review loop.
- `docs/troubleshooting.md` with CLI, VSCode, conda, Windows encoding, pytest temp, scaffold conflict, missing plan, missing scaffold, and Python version guidance.
- v1.14.0 examples, tutorials, and demo pack for the no-ROS-required migration scaffold workflow.
- `examples/ros1_migration_demo/` static ROS1-style catkin package for migration tutorials.
- `examples/ros2_scaffold_demo/` representative ROS2 scaffold-only demo with manual migration TODO notes.
- `examples/migration_outputs/` sample migration plan and scaffold report artifacts.
- `docs/tutorial_ros1_to_ros2_migration.md` CLI tutorial for detect, inspect, deps, plan, scaffold, validate, and report steps.
- `docs/tutorial_vscode_migration_workflow.md` VSCode-assisted migration workflow tutorial.
- `docs/demo_walkthrough.md` concise CLI and VSCode presentation script.
- v1.13.0 VSCode Marketplace publish preparation.
- `vscode-extension/CHANGELOG.md` with extension release notes from `0.1.0` through `0.5.0`.
- `docs/vscode_marketplace.md` with publisher-id, PAT, `VSCE_PAT`, manual publishing, GitHub Actions, listing verification, and rollback guidance.
- Manually triggered `.github/workflows/vscode-publish.yml` preparation workflow for future Marketplace publishing.
- v1.12.0 VSCode extension local VSIX packaging readiness.
- Project-local `@vscode/vsce` packaging script for generating a local `.vsix` without Marketplace publishing.
- `docs/vscode_packaging.md` with Node 20, build, package, local install, uninstall, configuration, and troubleshooting guidance.
- `.vscodeignore` for keeping local VSIX packages focused on compiled extension output and user-facing docs.
- v1.11.0 VSCode extension migration workflow polish.
- VSCode commands for migration scaffold preview, scaffold generation, scaffold validation, scaffold report generation, and opening scaffold reports.
- VSCode OutputChannel and TreeView summaries for migration scaffold target style, generated files, validation status, issues, warnings, and report path.
- v1.10.0 migration scaffold Markdown report workflow.
- `robopilot migrate-scaffold-report --plan migration_plan.yaml --scaffold path/to/ros2_scaffold` command for printing deterministic Markdown reports.
- `robopilot migrate-scaffold-report --output scaffold_report.md` file export with no overwrite by default and explicit `--overwrite` for report files.
- Markdown scaffold reports covering validation results, expected/present/missing/unexpected files, placeholder checks, ROS2 static inspection summary, manual migration items, interface and dependency review items, issues, warnings, next steps, and safety notes.
- `robopilot.api.migration.generate_migration_scaffold_report` API wrapper.
- v1.9.0 read-only migration scaffold validation workflow.
- `robopilot migrate-scaffold-validate --plan migration_plan.yaml --scaffold path/to/ros2_scaffold` command with readable terminal output.
- `robopilot migrate-scaffold-validate --json` deterministic JSON output for integrations.
- Static validation of generated scaffold files, missing files, placeholder safety wording, `MIGRATION_NOTES.md`, ROS2 scaffold inspection summary, unexpected files, and read-only safety notes.
- `robopilot.api.migration.validate_migration_scaffold` API wrapper.
- v1.8.0 conservative ROS2 migration scaffold generation workflow.
- `robopilot migrate-scaffold --plan migration_plan.yaml --output path/to/ros2_scaffold` command with readable terminal output.
- `robopilot migrate-scaffold --json` deterministic JSON output for integrations.
- Safe scaffold generation from migration plans with all-path preflight checks, no overwrite by default, and explicit `--overwrite` for intended scaffold files only.
- Placeholder ROS2 package metadata, build files, launch files, config files, TODO node files, and `MIGRATION_NOTES.md` generation.
- `robopilot.api.migration.generate_migration_scaffold` API wrapper.
- v1.7.0 read-only migration scaffold preview workflow.
- `robopilot migrate-scaffold-preview --plan migration_plan.yaml` command with readable terminal output.
- `robopilot migrate-scaffold-preview --json` deterministic JSON output for integrations.
- Static target-style inference for future ROS2 scaffold planning across `ament_python`, `ament_cmake`, and mixed Python/C++ review cases.
- `robopilot.api.migration.preview_migration_scaffold` API wrapper.
- v1.6.0 dependency analyzer enhancement for richer static ROS1/ROS2 dependency hints.
- Conservative ROS1-to-ROS2 dependency mapping hints for common packages such as `rospy`, `roscpp`, `catkin`, `message_generation`, `message_runtime`, `dynamic_reconfigure`, `actionlib`, `nodelet`, and launch-related dependencies.
- ROS/package-manager style hints for Python imports, C++ includes, and interface files.
- v1.5.0 no-ROS-required ROS2 static inspector for ament Python and ament CMake packages.
- `robopilot inspect-ros2 path/to/ros2_package` command with readable terminal output.
- `robopilot inspect-ros2 --json` deterministic JSON output for integrations.
- Static ROS2 package metadata, dependency, build-system, launch/config/interface, and node-candidate detection.
- `robopilot.api.static_analysis.inspect_ros2_project_static` API wrapper.
- JSON contract documentation and tests for `inspect-ros2 --json`.
- v1.4.0 VSCode Extension MVP source under `vscode-extension/`.
- VSCode commands for workspace detection, ROS1 inspection, dependency analysis, migration plan generation, migration preview, ProjectSpec validation, and output display.
- Thin TypeScript CLI runner that calls RoboPilot with argument arrays, parses JSON outputs, and reports missing CLI installation clearly.
- VSCode OutputChannel and simple Explorer TreeView summaries for RoboPilot results.
- `docs/vscode_extension.md` with local extension development and safety guidance.
- GitHub Actions workflow for VSCode extension compile and test checks.
- v1.3.0 stable JSON contract documentation and top-level key tests for integration-oriented CLI outputs.
- `docs/json_contracts.md` documenting JSON outputs for detection, inspection, dependency analysis, migration planning, migration validation/diff/preview, apply-preview, apply, rollback, history, and repair suggestions.
- `docs/integration_notes.md` with guidance for CLI `--json`, Python API use, VSCode extension direction, and file-writing safety.
- `tests/test_json_contracts.py` covering stable top-level JSON keys for key integration commands.
- v1.2.0 lightweight Python API layer for scripts, future VSCode integration, and possible UI wrappers.
- `robopilot.api.project` wrappers for ProjectSpec planning, refinement, diff, validation, and generation.
- `robopilot.api.static_analysis` wrappers for project detection, static inspection, ROS1 inspection, dependency analysis, and report export.
- `robopilot.api.migration` wrappers for ROS1-to-ROS2 migration plan creation, validation, diff, and preview.
- `robopilot.api.apply` wrappers for apply-preview, apply-plan export/validation, apply, rollback, and history.
- `docs/api.md` with API purpose, stability notes, and usage examples.
- v1.1.0 packaging and public developer experience polish.
- PyPI and TestPyPI publishing documentation, including Trusted Publishing guidance.
- Developer setup documentation for virtualenv, conda, editable installs, tests, CLI help, optional LLM extras, and packaging checks.
- Contributor and security policy documentation.
- GitHub issue templates for bugs, feature requests, and documentation updates.
- Pull request template with safety and testing checklist.
- GitHub Actions workflows for PyPI and TestPyPI Trusted Publishing.

### Changed

- Updated package and generated demo metadata to `1.18.0`.
- Updated roadmap and guidance documents to mark Marketplace publishing as completed and set v1.18.0 as the current cleanup milestone.
- Refreshed VSCode Marketplace availability wording across English and Chinese docs.
- Updated documentation to reflect that the VSCode extension is available from Visual Studio Marketplace as `j1angjj.robopilot-vscode`.
- Updated VSCode extension package metadata to `0.5.0` for the first Marketplace-ready release.
- Updated extension README and changelog for Marketplace suitability while preserving CLI-backed, no-ROS-required safety boundaries.
- Updated package and generated demo metadata to `1.17.0`.
- Rewrote `README.zh-CN.md` as a concise UTF-8 Chinese homepage that links to `docs/zh-CN/README.md`.
- Updated README, developer setup, testing docs, roadmap, and agent guidance for v1.16.0 Chinese documentation and encoding checks.
- Updated package and generated demo metadata to `1.16.0`.
- Improved migration plan, scaffold preview, scaffold generation, scaffold validation, and scaffold report next-step guidance.
- Improved migration scaffold report readability with a recommended next action and `What To Do Next` section.
- Updated migration tutorials, demo walkthrough, command reference, README links, roadmap, and agent guidance for v1.15.0 UX polish.
- Updated package and generated demo metadata to `1.15.0`.
- Updated README, workflow docs, roadmap, and project guidance for the v1.14.0 tutorial/demo milestone.
- Updated package and generated demo metadata to `1.14.0`.
- Updated VSCode extension package metadata to `0.4.0` with homepage, bugs URL, and Marketplace-ready publisher documentation.
- Updated package and generated demo metadata to `1.13.0`.
- Updated README, VSCode docs, developer setup, testing docs, roadmap, and agent guidance with Marketplace preparation notes.
- Updated VSCode extension package metadata to `0.3.0` with repository, license, keywords, and local packaging publisher metadata.
- Updated package and generated demo metadata to `1.12.0`.
- Updated VSCode extension CI to run local VSIX packaging checks without publishing.
- Updated VSCode extension package metadata to `0.2.0`.
- Updated package and generated demo metadata to `1.11.0`.
- Updated README, workflow, integration, VSCode extension, roadmap, and agent guidance with VSCode migration scaffold workflow polish.
- Updated package and generated demo metadata to `1.10.0`.
- Updated README, command reference, workflow, architecture, API, roadmap, and agent guidance with migration scaffold reports.
- Updated package and generated demo metadata to `1.9.0`.
- Updated README, command reference, workflow, architecture, API, JSON contract, roadmap, and agent guidance with migration scaffold validation.
- Tightened mixed scaffold package metadata so conservative mixed-review scaffolds do not claim a specific ROS2 build system before manual review.
- Updated package and generated demo metadata to `1.8.0`.
- Updated README, command reference, workflow, architecture, API, JSON contract, roadmap, and agent guidance with migration scaffold generation.
- Updated package and generated demo metadata to `1.7.0`.
- Updated README, command reference, workflow, architecture, API, JSON contract, roadmap, and agent guidance with migration scaffold preview.
- Updated package and generated demo metadata to `1.6.0`.
- Updated `robopilot deps --json` documentation and tests with stable `migration_hints` and `rosdep_hints` top-level keys; nested heuristic wording remains experimental.
- Improved conservative `possibly_unused` behavior to avoid overclaiming common buildtool, runtime, and interface dependencies.
- Updated package and generated demo metadata to `1.5.0`.
- Updated README, command reference, workflow, architecture, API, JSON contract, roadmap, and agent guidance with ROS2 static inspection.
- Updated package and generated demo metadata to `1.4.0`.
- Updated integration and developer documentation with VSCode extension MVP guidance.
- Updated package and generated demo metadata to `1.3.0`.
- Clarified stability policy for documented JSON top-level keys, human-readable Rich output, and maturing API surface.
- Updated package and generated demo metadata to `1.2.0`.
- Routed selected CLI commands through the new thin API wrappers while preserving CLI output behavior.
- Updated package and generated demo metadata to `1.1.0`.
- Audited `pyproject.toml` package metadata, optional dependencies, project URLs, license metadata, build backend requirements, and console script configuration.
- Tightened Python package support metadata to `>=3.10,<3.12` to match the tested 3.10/3.11 support matrix; Python 3.12 is not claimed until tested, and Python 3.13 remains unsupported due to known Typer / CLI compatibility issues.
- Added README installation wording for source installs now and PyPI installs after release.
- Expanded release and testing docs with local build and `twine check` commands.

## [1.0.0] - 2026-05-11

### Changed

- Promoted RoboPilot from `v1.0.0-rc.1` to the first stable `v1.0.0` release.
- Updated package metadata and generated demo metadata from `1.0.0rc1` to `1.0.0`.
- Confirmed `v1.0.0-rc.1` validation passed with no blocking issues.
- Confirmed no new product capabilities were added after the release candidate.
- Updated README, roadmap, AGENTS, and v1 scope wording from release-candidate status to stable release status.

### Stable Scope

- No-ROS-required static engineering workflow for ROS-style projects.
- ProjectSpec planning, validation, generation, refinement, and diff.
- Static detect, inspect, dependency analysis, repair suggestion, and report workflows.
- Safe apply, rollback, and project-local history loop.
- ROS1 static inspection without requiring ROS.
- ROS1-to-ROS2 migration plan, validation, diff, and preview workflows.
- Optional LLM planner/refiner boundaries constrained to validated ProjectSpec data.

## [1.0.0-rc.1] - 2026-05-11

### Changed

- Prepared RoboPilot `v1.0.0-rc.1` as a release candidate stabilization pass.
- Updated package metadata to the valid Python package version `1.0.0rc1`; the corresponding git tag should be `v1.0.0-rc.1`.
- Reviewed CLI help positioning for the no-ROS-required static engineering toolchain.
- Audited README and documentation links for release-candidate readiness.
- Audited stability policy, known limitations, compatibility, testing, release process, command reference, workflows, and architecture docs.
- Confirmed no new product capabilities, CLI commands, migration file generation, migration apply, ROS runtime execution, ROS2 runtime execution, catkin/colcon execution, RAG, Streamlit, Gradio, VSCode extension, real robot integration, or new LLM behavior were added in this RC pass.

### Verified

- Full pytest suite passes with the documented Windows temp workaround.
- Major CLI help pages were manually checked for release-candidate readiness.

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
