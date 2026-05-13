# Integration Notes

This document is for tools that want to consume RoboPilot output, including future editor integrations.

## Recommended Interfaces

Use one of two integration surfaces:

- Non-Python tools should call the CLI with documented `--json` outputs.
- Python tools can use `robopilot.api`.

Do not parse Rich human-readable output. Terminal prose is for people and may change.

## CLI JSON

For external tools such as a VSCode extension, prefer commands like:

```bash
robopilot detect path/to/project --json
robopilot inspect-ros2 path/to/project --json
robopilot deps path/to/project --json
robopilot migrate-preview --plan migration_plan.yaml --project path/to/project --json
robopilot migrate-scaffold-preview --plan migration_plan.yaml --json
robopilot migrate-scaffold --plan migration_plan.yaml --output path/to/ros2_scaffold --json
robopilot migrate-scaffold-validate --plan migration_plan.yaml --scaffold path/to/ros2_scaffold --json
```

The documented top-level keys in [JSON Contracts](json_contracts.md) are intended for integration use. Treat undocumented keys, deeply nested heuristic details, and dependency hint wording as unstable unless a future schema document marks them stable.

Consumers should:

- tolerate additional keys
- handle missing optional fields defensively
- treat advisory text as display text, not control flow
- rely on boolean/status fields where documented
- show safety notes when file-writing workflows are involved

## Python API

Python integrations can call the API layer directly:

```python
from robopilot.api.static_analysis import detect_project_type

result = detect_project_type("path/to/project")
```

The API avoids Rich rendering and direct stdout printing. It is newer than the CLI and should be treated as maturing until a future stable API contract is published.

Markdown report commands such as `migrate-scaffold-report` are intended for human review. External tools should display or save the Markdown directly and continue using documented `--json` commands for machine-readable control flow.

## File-Writing Workflows

External tools must keep RoboPilot's safety model visible:

- Invoke file-writing commands only after explicit user intent.
- Use dry-run commands before confirmed writes.
- For `migrate-scaffold`, show the output directory and conflict list before treating generation as successful.
- For `migrate-scaffold-validate`, show missing files, failed placeholder checks, warnings, and the safety note before presenting the scaffold as ready for manual migration.
- For `migrate-scaffold-report`, write only to an explicit user-selected report path and avoid overwriting existing reports unless the user requests `--overwrite`.
- Do not call `apply --confirm` or `rollback --confirm` without an explicit user confirmation step.
- Surface conflicts, skipped files, backup paths, and safety notes to users.
- Do not bypass ProjectSpec validation, apply-preview, apply-plan, or rollback safety checks.

## VSCode Extension

The VSCode extension under `vscode-extension/` is thin:

```txt
VSCode command
  -> spawn robopilot CLI with --json
  -> parse JSON
  -> render TreeView / Webview / OutputChannel
```

This keeps the extension decoupled from RoboPilot internals and avoids duplicating static analysis, migration, or apply logic.

The extension should continue to use documented JSON contracts and should not parse Rich human-readable output.

For the migration scaffold workflow, the extension should consume JSON from `migrate-scaffold-preview --json`, `migrate-scaffold --json`, and `migrate-scaffold-validate --json`. `migrate-scaffold-report` is a Markdown report command; integrations should treat its stdout as human text and use the explicit report file path for opening or displaying the report.
