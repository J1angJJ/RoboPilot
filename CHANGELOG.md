# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
