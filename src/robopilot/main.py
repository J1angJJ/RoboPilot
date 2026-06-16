"""Command-line interface for RoboPilot."""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from robopilot.api.apply import (
    preview_apply as api_preview_apply,
    read_project_history as api_read_project_history,
)
from robopilot.api.migration import (
    create_ros1_to_ros2_migration_plan as api_create_ros1_to_ros2_migration_plan,
    generate_migration_scaffold_report as api_generate_migration_scaffold_report,
    generate_migration_scaffold as api_generate_migration_scaffold,
    preview_migration_plan as api_preview_migration_plan,
    preview_migration_scaffold as api_preview_migration_scaffold,
    score_migration_readiness_api as api_score_migration_readiness,
    validate_migration_scaffold as api_validate_migration_scaffold,
    validate_migration_plan_file as api_validate_migration_plan_file,
)
from robopilot.api.static_analysis import (
    analyze_project_dependencies as api_analyze_project_dependencies,
    detect_project_type as api_detect_project_type,
    inspect_ros1_project_static as api_inspect_ros1_project_static,
    inspect_ros2_project_static as api_inspect_ros2_project_static,
    lint_project_api as api_lint_project,
)
from robopilot.apply.apply_plan import ApplySummary, apply_from_plan
from robopilot.apply_plan.plan import export_apply_plan, validate_apply_plan_file
from robopilot.apply_preview.preview import ApplyPreviewResult
from robopilot.debugger.log_analyzer import LogAnalysis, analyze_log
from robopilot.deps.analyzer import DependencyAnalysis
from robopilot.detector.project_detector import ProjectDetection
from robopilot.diff.spec_diff import SpecDiffResult, diff_spec_files
from robopilot.generator.project_generator import (
    generate_project,
    generate_project_from_spec,
)
from robopilot.graph.mermaid_generator import PipelineParseError, generate_mermaid
from robopilot.history.journal import HistoryReport
from robopilot.inspector.project_inspector import ProjectInspection, inspect_project
from robopilot.migration.ros1_to_ros2 import (
    ROS1ToROS2MigrationPlan,
)
from robopilot.migration.plan_diff import MigrationPlanDiffResult, diff_migration_plans
from robopilot.migration.plan_validator import (
    MigrationPlanValidationReport,
)
from robopilot.migration.preview import MigrationPreviewResult
from robopilot.migration.scaffold_generator import MigrationScaffoldGenerationResult
from robopilot.migration.scaffold_preview import MigrationScaffoldPreviewResult, ScaffoldFile
from robopilot.migration.scaffold_validator import MigrationScaffoldValidationResult
from robopilot.planner import (
    LLMProviderConfig,
    LLMPlanner,
    OpenAIPlannerClient,
    PlannerConfigurationError,
    PlannerError,
    RuleBasedPlanner,
)
from robopilot.repair.repair_suggester import RepairSuggestionReport, suggest_repairs
from robopilot.tutorial import (
    TutorialLesson,
    TutorialResult,
    get_lesson,
    list_lessons,
)
from robopilot.refiner.llm_refiner import LLMRefiner
from robopilot.refiner.spec_refiner import refine_spec
from robopilot.report.project_report import generate_project_report, write_project_report
from robopilot.rollback.rollback import RollbackSummary, rollback_project
from robopilot.ros1.inspector import ROS1Inspection
from robopilot.ros2.inspector import ROS2Inspection
from robopilot.spec.io import load_spec, spec_to_yaml, write_spec
from robopilot.spec.validator import validate_spec
from robopilot.utils.file_ops import OutputPathExistsError


app = typer.Typer(
    help="RoboPilot: no-ROS-required static tooling for ROS-style projects.",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def main() -> None:
    """Run RoboPilot CLI commands."""


@app.command()
def generate(
    name: Annotated[
        str | None,
        typer.Option("--name", "-n", help="Package name to create."),
    ] = None,
    task: Annotated[
        str | None,
        typer.Option("--task", "-t", help="Natural language robotics task."),
    ] = None,
    spec: Annotated[
        Path | None,
        typer.Option("--spec", "-s", help="Path to a robopilot.yaml ProjectSpec."),
    ] = None,
    output_root: Annotated[
        Path,
        typer.Option(
            "--output-root",
            "-o",
            help="Directory where generated projects are written.",
        ),
    ] = Path("outputs"),
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Allow overwriting files inside an existing generated project.",
        ),
    ] = False,
) -> None:
    """Generate an offline ROS-style Python package skeleton."""
    try:
        if spec is not None:
            if name is not None or task is not None:
                raise ValueError("Use either --spec or --name/--task, not both.")
            project_spec = load_spec(spec)
            project = generate_project_from_spec(
                spec=project_spec,
                output_root=output_root,
                overwrite=overwrite,
            )
        else:
            if name is None or task is None:
                raise ValueError("Provide --name and --task, or provide --spec.")
            project = generate_project(
                name=name,
                task=task,
                output_root=output_root,
                overwrite=overwrite,
            )
    except (OutputPathExistsError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Generated[/green] {project.package_name}")
    console.print(f"Output: [bold]{project.output_dir}[/bold]")
    console.print(f"Selected template: [bold]{project.selected_template}[/bold]")

    table = Table(title="Created files")
    table.add_column("Path", style="cyan")
    for file_path in project.files:
        table.add_row(str(file_path.relative_to(project.output_dir)))
    console.print(table)


@app.command()
def plan(
    name: Annotated[str, typer.Option("--name", "-n", help="Package name to plan.")],
    task: Annotated[
        str,
        typer.Option("--task", "-t", help="Natural language robotics task."),
    ],
    planner: Annotated[
        str,
        typer.Option(
            "--planner",
            help="Planner backend to use: rule or llm.",
        ),
    ] = "rule",
    model: Annotated[
        str | None,
        typer.Option(
            "--model",
            help="Optional model name for --planner llm.",
        ),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Optional path to write the ProjectSpec."),
    ] = None,
) -> None:
    """Create and print a robopilot.yaml ProjectSpec without generating files."""
    try:
        selected_planner = _build_planner(planner, model=model)
        project_spec = selected_planner.plan(package_name=name, task=task)
    except (PlannerError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    yaml_text = spec_to_yaml(project_spec)
    console.print(yaml_text)

    if output is not None:
        write_spec(project_spec, output)
        console.print(f"[green]Wrote ProjectSpec to[/green] {output}")


def _build_planner(
    planner_name: str,
    *,
    model: str | None = None,
) -> RuleBasedPlanner | LLMPlanner:
    normalized = planner_name.strip().lower()
    if normalized == "rule":
        return RuleBasedPlanner()
    if normalized == "llm":
        config = LLMProviderConfig.from_env(model_override=model)
        return LLMPlanner(client=OpenAIPlannerClient(config))
    raise PlannerConfigurationError(
        f"Unknown planner: {planner_name}. Use 'rule' or 'llm'."
    )


@app.command()
def refine(
    spec: Annotated[
        Path,
        typer.Option("--spec", "-s", help="Path to an existing robopilot.yaml ProjectSpec."),
    ],
    instruction: Annotated[
        str,
        typer.Option("--instruction", "-i", help="Instruction for refining the ProjectSpec."),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Path to write the refined ProjectSpec."),
    ],
    planner: Annotated[
        str,
        typer.Option("--planner", help="Refinement backend to use: rule or llm."),
    ] = "rule",
    model: Annotated[
        str | None,
        typer.Option(
            "--model",
            help="Optional model name for --planner llm.",
        ),
    ] = None,
) -> None:
    """Refine an existing ProjectSpec and write a new spec file."""
    try:
        original_spec = load_spec(spec)
        refined_spec = _refine_with_selected_planner(
            original_spec,
            instruction,
            planner_name=planner,
            model=model,
        )
        write_spec(refined_spec, output)
    except (OSError, PlannerError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Wrote refined ProjectSpec to[/green] {output}")


def _refine_with_selected_planner(
    project_spec,
    instruction: str,
    *,
    planner_name: str,
    model: str | None = None,
):
    normalized = planner_name.strip().lower()
    if normalized == "rule":
        return refine_spec(project_spec, instruction, planner="rule")
    if normalized == "llm":
        config = LLMProviderConfig.from_env(model_override=model)
        refiner = LLMRefiner(client=OpenAIPlannerClient(config))
        return refiner.refine(project_spec, instruction)
    raise PlannerConfigurationError(
        f"Unknown refinement planner: {planner_name}. Use 'rule' or 'llm'."
    )


@app.command()
def diff(
    old: Annotated[
        Path,
        typer.Option("--old", help="Path to the baseline ProjectSpec."),
    ],
    new: Annotated[
        Path,
        typer.Option("--new", help="Path to the updated ProjectSpec."),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Compare two ProjectSpec files without modifying either one."""
    try:
        result = diff_spec_files(old, new)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    _print_spec_diff(result)


def _print_spec_diff(result: SpecDiffResult) -> None:
    console.print(Panel.fit("Spec Summary", style="bold cyan"))
    console.print(f"[bold]Old spec:[/bold] {result.old_spec}")
    console.print(f"[bold]New spec:[/bold] {result.new_spec}")
    console.print(f"[bold]Valid:[/bold] {result.valid}")
    console.print(f"[bold]Has changes:[/bold] {result.has_changes}")

    console.print(Panel.fit("Changed Fields", style="bold cyan"))
    if result.changed_fields:
        table = Table()
        table.add_column("Field")
        table.add_column("Old")
        table.add_column("New")
        for field, values in result.changed_fields.items():
            table.add_row(field, values["old"], values["new"])
        console.print(table)
    else:
        console.print("[green]No scalar field changes.[/green]")

    _print_named_items("Added Nodes", result.added_nodes)
    _print_named_items("Removed Nodes", result.removed_nodes)
    _print_named_items("Added Topics", result.added_topics)
    _print_named_items("Removed Topics", result.removed_topics)

    console.print(Panel.fit("Added Files", style="bold cyan"))
    _print_scalar_group("Config files", result.added_config_files)
    _print_scalar_group("Launch files", result.added_launch_files)

    console.print(Panel.fit("Removed Files", style="bold cyan"))
    _print_scalar_group("Config files", result.removed_config_files)
    _print_scalar_group("Launch files", result.removed_launch_files)

    console.print(Panel.fit("Added Notes", style="bold cyan"))
    _print_scalar_values(result.added_notes)

    console.print(Panel.fit("Removed Notes", style="bold cyan"))
    _print_scalar_values(result.removed_notes)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(
        "This diff is generated from static ProjectSpec comparison only. "
        "RoboPilot did not modify either spec file."
    )


def _print_named_items(title: str, items: tuple[dict[str, str], ...]) -> None:
    console.print(Panel.fit(title, style="bold cyan"))
    if not items:
        console.print("[green]None.[/green]")
        return
    for item in items:
        console.print(f"- {item.get('name', 'unknown')}")


def _print_scalar_group(label: str, values: tuple[str, ...]) -> None:
    console.print(f"[bold]{label}:[/bold]")
    _print_scalar_values(values)


def _print_scalar_values(values: tuple[str, ...]) -> None:
    if not values:
        console.print("- none")
        return
    for value in values:
        console.print(f"- {value}")


@app.command("apply-preview")
def apply_preview(
    spec: Annotated[
        Path,
        typer.Option("--spec", "-s", help="Path to a robopilot.yaml ProjectSpec."),
    ],
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Existing project directory to preview."),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Preview applying a ProjectSpec to a project without modifying files."""
    try:
        result = api_preview_apply(spec, project, as_dict=False)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    _print_apply_preview(result)


def _print_apply_preview(result: ApplyPreviewResult) -> None:
    console.print(Panel.fit("Apply Preview Summary", style="bold cyan"))
    console.print(f"[bold]Spec path:[/bold] {result.spec_path}")
    console.print(f"[bold]Project path:[/bold] {result.project_path}")
    console.print(f"[bold]Package name:[/bold] {result.package_name}")
    console.print(f"[bold]Selected template:[/bold] {result.selected_template}")
    console.print(f"[bold]Missing project:[/bold] {result.missing_project}")

    console.print(Panel.fit("Files to Create", style="bold cyan"))
    _print_scalar_values(result.files_to_create)

    console.print(Panel.fit("Files to Update", style="bold cyan"))
    _print_scalar_values(result.files_to_update)

    console.print(Panel.fit("Files to Keep", style="bold cyan"))
    _print_scalar_values(result.files_to_keep)

    console.print(Panel.fit("Conflicts", style="bold cyan"))
    _print_scalar_values(result.conflicts)

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    _print_scalar_values(result.suggested_next_steps)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(result.safety_note)


@app.command("apply-plan")
def apply_plan(
    spec: Annotated[
        Path,
        typer.Option("--spec", "-s", help="Path to a robopilot.yaml ProjectSpec."),
    ],
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Existing project directory to preview."),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Path to write the apply plan."),
    ],
    output_format: Annotated[
        str,
        typer.Option("--format", help="Apply plan output format: yaml or json."),
    ] = "yaml",
) -> None:
    """Export a read-only apply plan from an apply-preview result."""
    try:
        export_apply_plan(
            spec_path=spec,
            project_path=project,
            output_path=output,
            output_format=output_format,
        )
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Wrote apply plan to[/green] {output}")


@app.command("apply-plan-validate")
def apply_plan_validate(
    plan: Annotated[
        Path,
        typer.Option("--plan", "-p", help="Path to an apply plan file."),
    ],
) -> None:
    """Validate a serialized apply plan without executing it."""
    result = validate_apply_plan_file(plan)
    if result.is_valid:
        console.print(f"[green]Valid apply plan:[/green] {plan}")
        return

    console.print(f"[red]Invalid apply plan:[/red] {plan}")
    for error in result.errors:
        console.print(f"- {error}")
    raise typer.Exit(code=1)


@app.command()
def apply(
    plan: Annotated[
        Path,
        typer.Option("--plan", "-p", help="Path to a validated apply plan file."),
    ],
    confirm: Annotated[
        bool,
        typer.Option("--confirm", help="Actually write planned create/update files."),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Dry-run or safely apply a previously exported apply plan."""
    try:
        summary = apply_from_plan(plan, confirm=confirm)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        print(json.dumps(summary.to_dict(), indent=2))
        return

    _print_apply_summary(summary)


def _print_apply_summary(summary: ApplySummary) -> None:
    console.print(Panel.fit("Apply Summary", style="bold cyan"))
    console.print(f"[bold]Plan path:[/bold] {summary.plan_path}")
    console.print(f"[bold]Project path:[/bold] {summary.project_path}")
    console.print(f"[bold]Dry run:[/bold] {summary.dry_run}")

    console.print(Panel.fit("Files Created", style="bold cyan"))
    _print_scalar_values(summary.files_created)

    console.print(Panel.fit("Files Updated", style="bold cyan"))
    _print_scalar_values(summary.files_updated)

    console.print(Panel.fit("Files Kept", style="bold cyan"))
    _print_scalar_values(summary.files_kept)

    console.print(Panel.fit("Backups Created", style="bold cyan"))
    _print_scalar_values(summary.backups_created)

    console.print(Panel.fit("Skipped Files", style="bold cyan"))
    _print_scalar_values(summary.skipped_files)

    console.print(Panel.fit("Conflicts", style="bold cyan"))
    _print_scalar_values(summary.conflicts)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(summary.safety_note)


@app.command()
def rollback(
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project directory to restore into."),
    ],
    backup: Annotated[
        Path,
        typer.Option("--backup", "-b", help="RoboPilot backup directory to restore from."),
    ],
    confirm: Annotated[
        bool,
        typer.Option("--confirm", help="Actually restore files from backup."),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Dry-run or restore files from a RoboPilot backup directory."""
    try:
        summary = rollback_project(
            project_path=project,
            backup_path=backup,
            confirm=confirm,
        )
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        print(json.dumps(summary.to_dict(), indent=2))
        return

    _print_rollback_summary(summary)


def _print_rollback_summary(summary: RollbackSummary) -> None:
    console.print(Panel.fit("Rollback Summary", style="bold cyan"))
    console.print(f"[bold]Project path:[/bold] {summary.project_path}")
    console.print(f"[bold]Backup path:[/bold] {summary.backup_path}")
    console.print(f"[bold]Dry run:[/bold] {summary.dry_run}")

    console.print(Panel.fit("Files to Restore", style="bold cyan"))
    _print_scalar_values(summary.files_to_restore)

    console.print(Panel.fit("Files Restored", style="bold cyan"))
    _print_scalar_values(summary.files_restored)

    console.print(Panel.fit("Skipped Files", style="bold cyan"))
    _print_scalar_values(summary.skipped_files)

    console.print(Panel.fit("Errors", style="bold cyan"))
    _print_scalar_values(summary.errors)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(summary.safety_note)


@app.command()
def history(
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project directory to read history from."),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Show project-local RoboPilot apply and rollback history."""
    try:
        report = api_read_project_history(project, as_dict=False)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
        return

    _print_history(report)


def _print_history(report: HistoryReport) -> None:
    console.print(Panel.fit("History Summary", style="bold cyan"))
    console.print(f"[bold]Project path:[/bold] {report.project_path}")
    console.print(f"[bold]History dir:[/bold] {report.history_dir}")
    console.print(f"[bold]Number of entries:[/bold] {len(report.entries)}")

    console.print(Panel.fit("Recent Entries", style="bold cyan"))
    if not report.entries:
        console.print("[green]No RoboPilot history entries found.[/green]")
        return

    table = Table()
    table.add_column("Operation")
    table.add_column("Timestamp")
    table.add_column("Summary")
    table.add_column("Files changed/restored")
    for entry in report.entries[-10:]:
        changed_count = (
            len(entry.files_created)
            + len(entry.files_updated)
            + len(entry.files_restored)
        )
        table.add_row(
            entry.operation,
            entry.timestamp,
            entry.summary,
            str(changed_count),
        )
    console.print(table)


@app.command()
def detect(
    project_path: Annotated[Path, typer.Argument(help="Project directory to detect.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Detect ROS-style project type without requiring ROS."""
    result = api_detect_project_type(project_path, as_dict=False)
    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    _print_detection(result)


def _print_detection(result: ProjectDetection) -> None:
    console.print(Panel.fit("Detection Summary", style="bold cyan"))
    console.print(f"[bold]Project path:[/bold] {result.project_path}")
    console.print(f"[bold]Exists:[/bold] {result.exists}")
    console.print(f"[bold]Project type:[/bold] {result.project_type}")
    console.print(f"[bold]Confidence:[/bold] {result.confidence}")

    console.print(Panel.fit("Detected Signals", style="bold cyan"))
    _print_scalar_values(result.detected_signals)

    console.print(Panel.fit("Missing Common Files", style="bold cyan"))
    _print_scalar_values(result.missing_common_files)

    console.print(Panel.fit("Notes", style="bold cyan"))
    _print_scalar_values(result.notes)

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    _print_scalar_values(result.suggested_next_steps)


@app.command("inspect-ros1")
def inspect_ros1(
    project_path: Annotated[Path, typer.Argument(help="ROS1 catkin package directory to inspect.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Statically inspect a ROS1 catkin package without requiring ROS."""
    result = api_inspect_ros1_project_static(project_path, as_dict=False)
    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    _print_ros1_inspection(result)


def _print_ros1_inspection(result: ROS1Inspection) -> None:
    console.print(Panel.fit("ROS1 Inspection Summary", style="bold cyan"))
    console.print(f"[bold]Project path:[/bold] {result.project_path}")
    console.print(f"[bold]Exists:[/bold] {result.exists}")
    console.print(f"[bold]Detected project type:[/bold] {result.detected_project_type}")

    console.print(Panel.fit("Package Metadata", style="bold cyan"))
    console.print(f"[bold]Package name:[/bold] {result.package_name or 'unknown'}")
    console.print(f"[bold]Package format:[/bold] {result.package_format or 'unknown'}")

    console.print(Panel.fit("Dependencies", style="bold cyan"))
    _print_scalar_group("Buildtool", result.dependencies.buildtool)
    _print_scalar_group("Build", result.dependencies.build)
    _print_scalar_group("Exec", result.dependencies.exec)
    _print_scalar_group("Run", result.dependencies.run)

    console.print(Panel.fit("CMake / Catkin Signals", style="bold cyan"))
    console.print(f"[bold]find_package(catkin):[/bold] {result.catkin.find_package_catkin}")
    console.print(f"[bold]catkin_package():[/bold] {result.catkin.catkin_package}")
    _print_scalar_group("Catkin components", result.catkin.catkin_components)

    console.print(Panel.fit("Detected Files", style="bold cyan"))
    _print_scalar_group("Launch files", result.files.launch_files)
    _print_scalar_group("Message files", result.files.msg_files)
    _print_scalar_group("Service files", result.files.srv_files)
    _print_scalar_group("Action files", result.files.action_files)
    _print_scalar_group("Python files", result.files.python_files)
    _print_scalar_group("C++ files", result.files.cpp_files)

    console.print(Panel.fit("Node Candidates", style="bold cyan"))
    _print_scalar_group("Python ROS1 nodes", result.nodes.python_node_candidates)
    _print_scalar_group("C++ ROS1 nodes", result.nodes.cpp_node_candidates)
    console.print(f"[bold]rospy usage:[/bold] {result.rospy_usage}")
    console.print(f"[bold]roscpp usage:[/bold] {result.roscpp_usage}")

    console.print(Panel.fit("Potential Issues", style="bold cyan"))
    _print_scalar_values(result.issues)

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    _print_scalar_values(result.suggested_next_steps)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(result.safety_note)


@app.command("inspect-ros2")
def inspect_ros2(
    project_path: Annotated[Path, typer.Argument(help="ROS2 ament package directory to inspect.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Statically inspect a ROS2 ament package without requiring ROS2."""
    result = api_inspect_ros2_project_static(project_path, as_dict=False)
    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    _print_ros2_inspection(result)


def _print_ros2_inspection(result: ROS2Inspection) -> None:
    console.print(Panel.fit("ROS2 Inspection Summary", style="bold cyan"))
    console.print(f"[bold]Project path:[/bold] {result.project_path}")
    console.print(f"[bold]Exists:[/bold] {result.exists}")
    console.print(f"[bold]Detected project type:[/bold] {result.detected_project_type}")

    console.print(Panel.fit("Package Metadata", style="bold cyan"))
    console.print(f"[bold]Package name:[/bold] {result.package_name or 'unknown'}")
    console.print(f"[bold]Package format:[/bold] {result.package_format or 'unknown'}")

    console.print(Panel.fit("Dependencies", style="bold cyan"))
    _print_scalar_group("Buildtool", result.dependencies.buildtool)
    _print_scalar_group("Build", result.dependencies.build)
    _print_scalar_group("Exec", result.dependencies.exec)
    _print_scalar_group("Test", result.dependencies.test)

    console.print(Panel.fit("Build System Signals", style="bold cyan"))
    console.print(f"[bold]ament_cmake:[/bold] {result.build_system.ament_cmake}")
    console.print(f"[bold]ament_python:[/bold] {result.build_system.ament_python}")
    console.print(f"[bold]ament_package():[/bold] {result.build_system.ament_package}")
    console.print(f"[bold]setup.py:[/bold] {result.build_system.setup_py}")
    console.print(f"[bold]setup.cfg:[/bold] {result.build_system.setup_cfg}")
    console.print(f"[bold]resource marker:[/bold] {result.build_system.resource_marker}")

    console.print(Panel.fit("Detected Files", style="bold cyan"))
    _print_scalar_group("Launch files", result.files.launch_files)
    _print_scalar_group("Config files", result.files.config_files)
    _print_scalar_group("Message files", result.files.msg_files)
    _print_scalar_group("Service files", result.files.srv_files)
    _print_scalar_group("Action files", result.files.action_files)
    _print_scalar_group("Python files", result.files.python_files)
    _print_scalar_group("C++ files", result.files.cpp_files)

    console.print(Panel.fit("Node Candidates", style="bold cyan"))
    _print_scalar_group("Python ROS2 nodes", result.nodes.python_node_candidates)
    _print_scalar_group("C++ ROS2 nodes", result.nodes.cpp_node_candidates)
    console.print(f"[bold]rclpy usage:[/bold] {result.rclpy_usage}")
    console.print(f"[bold]rclcpp usage:[/bold] {result.rclcpp_usage}")

    console.print(Panel.fit("Potential Issues", style="bold cyan"))
    _print_scalar_values(result.issues)

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    _print_scalar_values(result.suggested_next_steps)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(result.safety_note)


@app.command()
def deps(
    project_path: Annotated[Path, typer.Argument(help="Project directory to analyze.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Analyze ROS-style dependencies without requiring ROS."""
    result = api_analyze_project_dependencies(project_path, as_dict=False)
    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    _print_dependency_analysis(result)


def _print_dependency_analysis(result: DependencyAnalysis) -> None:
    console.print(Panel.fit("Dependency Analysis Summary", style="bold cyan"))
    console.print(f"[bold]Project path:[/bold] {result.project_path}")
    console.print(f"[bold]Exists:[/bold] {result.exists}")
    console.print(f"[bold]Project type:[/bold] {result.project_type}")

    console.print(Panel.fit("Declared Dependencies", style="bold cyan"))
    _print_scalar_group("Buildtool", result.declared_dependencies.buildtool)
    _print_scalar_group("Build", result.declared_dependencies.build)
    _print_scalar_group("Exec", result.declared_dependencies.exec)
    _print_scalar_group("Run", result.declared_dependencies.run)
    _print_scalar_group("Test", result.declared_dependencies.test)

    console.print(Panel.fit("Detected Usage", style="bold cyan"))
    _print_scalar_group("Python imports", result.detected_usage.python_imports)
    _print_scalar_group("C++ includes", result.detected_usage.cpp_includes)
    _print_scalar_group("CMake find_package", result.detected_usage.cmake_find_package)
    _print_scalar_group("Catkin components", result.detected_usage.catkin_components)
    _print_scalar_group("Launch references", result.detected_usage.launch_references)

    console.print(Panel.fit("Possibly Missing Dependencies", style="bold cyan"))
    _print_scalar_values(result.possibly_missing)

    console.print(Panel.fit("Possibly Unused Dependencies", style="bold cyan"))
    _print_scalar_values(result.possibly_unused)

    console.print(Panel.fit("Dependency Hints", style="bold cyan"))
    _print_scalar_values(result.hints)

    console.print(Panel.fit("Migration Hints", style="bold cyan"))
    _print_scalar_values(result.migration_hints)

    console.print(Panel.fit("Rosdep Hints", style="bold cyan"))
    _print_scalar_values(result.rosdep_hints)

    console.print(Panel.fit("Warnings", style="bold cyan"))
    _print_scalar_values(result.warnings)

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    _print_scalar_values(result.suggested_next_steps)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(result.safety_note)


@app.command()
def lint(
    project_path: Annotated[Path, typer.Argument(help="Project directory to lint.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Run static lint checks on a ROS-style project without modifying files."""
    try:
        result = api_lint_project(project_path, as_dict=False)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        if result.error_count > 0:
            raise typer.Exit(code=1)
        return

    _print_lint_result(result)
    if result.error_count > 0:
        raise typer.Exit(code=1)


def _print_lint_result(result: "LintResult") -> None:
    console.print(Panel.fit("Lint Summary", style="bold cyan"))
    console.print(f"[bold]Project path:[/bold] {result.project_path}")
    console.print(f"[bold]Package name:[/bold] {result.package_name or 'unknown'}")
    console.print(f"[bold]Project type:[/bold] {result.project_type}")
    console.print(
        f"[bold]Issues:[/bold] "
        f"[red]{result.error_count} errors[/red], "
        f"[yellow]{result.warning_count} warnings[/yellow], "
        f"[cyan]{result.info_count} info[/cyan]"
    )

    if not result.issues:
        console.print("[green]No issues found.[/green]")
        return

    table = Table(title="Lint Issues")
    table.add_column("Severity", style="bold")
    table.add_column("File")
    table.add_column("Rule")
    table.add_column("Message")
    for issue in result.issues:
        sev_style = {"error": "red", "warning": "yellow", "info": "cyan"}.get(issue.severity, "")
        table.add_row(
            f"[{sev_style}]{issue.severity}[/{sev_style}]",
            issue.file,
            issue.rule,
            issue.message,
        )
    console.print(table)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    from robopilot.lint import SAFETY_NOTE
    console.print(SAFETY_NOTE)


@app.command("migrate-plan")
def migrate_plan(
    source_path: Annotated[
        Path,
        typer.Option("--from", help="Source ROS1 package directory."),
    ],
    target: Annotated[
        str,
        typer.Option("--to", help="Migration target. Currently only 'ros2' is supported."),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Path to write the migration plan."),
    ],
    output_format: Annotated[
        str,
        typer.Option("--format", help="Migration plan output format: yaml or json."),
    ] = "yaml",
) -> None:
    """Create a static ROS1-to-ROS2 migration plan without modifying files."""
    try:
        plan = api_create_ros1_to_ros2_migration_plan(
            source_path=source_path,
            target=target,
            output_path=output,
            output_format=output_format,
            as_dict=False,
        )
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Wrote migration plan to[/green] {output}")
    _print_migration_plan(plan)


def _print_migration_plan(plan: ROS1ToROS2MigrationPlan) -> None:
    console.print(Panel.fit("Migration Plan Summary", style="bold cyan"))
    console.print(f"[bold]Source Project:[/bold] {plan.source_path}")
    console.print(f"[bold]Package:[/bold] {plan.package_name or 'unknown'}")
    console.print(f"[bold]Target:[/bold] {plan.target}")
    console.print(f"[bold]Source project type:[/bold] {plan.source_project_type}")
    console.print(f"[bold]Confidence:[/bold] {plan.confidence}")
    console.print(plan.summary)

    console.print(Panel.fit("Package XML Migration", style="bold cyan"))
    _print_scalar_values(plan.package_xml_migration)

    console.print(Panel.fit("Build System Migration", style="bold cyan"))
    _print_scalar_values(plan.build_system_migration)

    console.print(Panel.fit("Source Code Migration", style="bold cyan"))
    _print_scalar_values(plan.source_code_migration)

    console.print(Panel.fit("Launch Migration", style="bold cyan"))
    _print_scalar_values(plan.launch_migration)

    console.print(Panel.fit("Interface Migration", style="bold cyan"))
    _print_scalar_values(plan.interface_migration)

    console.print(Panel.fit("Dependency Migration", style="bold cyan"))
    dependency = plan.dependency_migration
    for key in (
        "possibly_missing",
        "possibly_unused",
        "ros2_equivalent_hints",
        "manual_review_dependencies",
    ):
        value = dependency.get(key, [])
        console.print(f"[bold]{key}:[/bold]")
        _print_scalar_values(tuple(str(item) for item in value) if isinstance(value, list) else ())

    console.print(Panel.fit("Suggested File Changes", style="bold cyan"))
    _print_scalar_values(plan.suggested_file_changes)

    console.print(Panel.fit("Manual Review Items", style="bold cyan"))
    _print_scalar_values(plan.manual_review_items)

    console.print(Panel.fit("Risks", style="bold cyan"))
    _print_scalar_values(plan.risks)

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    _print_scalar_values(plan.suggested_next_steps)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(plan.safety_note)


@app.command("migrate-plan-validate")
def migrate_plan_validate(
    plan: Annotated[
        Path,
        typer.Option("--plan", "-p", help="Path to a ROS1-to-ROS2 migration plan."),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Validate a ROS1-to-ROS2 migration plan without modifying files."""
    report = api_validate_migration_plan_file(plan, as_dict=False)
    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
        if not report.valid:
            raise typer.Exit(code=1)
        return

    _print_migration_plan_validation(report)
    if not report.valid:
        raise typer.Exit(code=1)


def _print_migration_plan_validation(report: MigrationPlanValidationReport) -> None:
    console.print(Panel.fit("Migration Plan Validation Summary", style="bold cyan"))
    console.print(f"[bold]Plan path:[/bold] {report.plan_path}")
    console.print(f"[bold]Valid:[/bold] {report.valid}")

    console.print(Panel.fit("Missing Fields", style="bold cyan"))
    _print_scalar_values(report.missing_fields)

    console.print(Panel.fit("Invalid Fields", style="bold cyan"))
    _print_scalar_values(report.invalid_fields)

    console.print(Panel.fit("Warnings", style="bold cyan"))
    _print_scalar_values(report.warnings)

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    _print_scalar_values(report.suggested_next_steps)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(report.safety_note)


@app.command("migrate-plan-diff")
def migrate_plan_diff(
    old: Annotated[
        Path,
        typer.Option("--old", help="Path to the baseline migration plan."),
    ],
    new: Annotated[
        Path,
        typer.Option("--new", help="Path to the updated migration plan."),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Diff two ROS1-to-ROS2 migration plans without modifying files."""
    try:
        result = diff_migration_plans(old, new)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    _print_migration_plan_diff(result)


def _print_migration_plan_diff(result: MigrationPlanDiffResult) -> None:
    console.print(Panel.fit("Migration Plan Diff Summary", style="bold cyan"))
    console.print(f"[bold]Old plan:[/bold] {result.old_plan}")
    console.print(f"[bold]New plan:[/bold] {result.new_plan}")
    console.print(f"[bold]Valid:[/bold] {result.valid}")
    console.print(f"[bold]Has changes:[/bold] {result.has_changes}")

    console.print(Panel.fit("Changed Fields", style="bold cyan"))
    if result.changed_fields:
        table = Table()
        table.add_column("Field")
        table.add_column("Old")
        table.add_column("New")
        for field, values in result.changed_fields.items():
            table.add_row(field, values["old"], values["new"])
        console.print(table)
    else:
        console.print("[green]No scalar field changes.[/green]")

    console.print(Panel.fit("Added Items", style="bold cyan"))
    _print_mapping_values(result.added_items)

    console.print(Panel.fit("Removed Items", style="bold cyan"))
    _print_mapping_values(result.removed_items)

    console.print(Panel.fit("Unchanged Summary", style="bold cyan"))
    _print_scalar_values(result.unchanged_fields)

    console.print(Panel.fit("Warnings", style="bold cyan"))
    _print_scalar_values(result.warnings)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(result.safety_note)


def _print_mapping_values(values: dict[str, list[str]]) -> None:
    if not values:
        console.print("- none")
        return
    for key, items in values.items():
        console.print(f"[bold]{key}:[/bold]")
        _print_scalar_values(tuple(items))


@app.command("migrate-score")
def migrate_score(
    source_path: Annotated[
        Path,
        typer.Argument(help="Source ROS1 package directory to score."),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Score a ROS1 package on ROS2 migration readiness (0-100) without modifying files."""
    try:
        result = api_score_migration_readiness(source_path, as_dict=False)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    _print_migrate_score(result)


def _print_migrate_score(result: "MigrationScoreResult") -> None:
    score_color = (
        "green" if result.overall_score >= 80
        else "yellow" if result.overall_score >= 60
        else "red" if result.overall_score >= 40
        else "bright_red"
    )
    console.print(Panel.fit("Migration Readiness Score", style="bold cyan"))
    console.print(f"[bold]Source path:[/bold] {result.source_path}")
    console.print(f"[bold]Package name:[/bold] {result.package_name or 'unknown'}")
    console.print(f"[bold]Project type:[/bold] {result.source_project_type}")
    console.print(
        f"[bold]Overall score:[/bold] [{score_color}]{result.overall_score}/100[/{score_color}]"
    )
    console.print(f"[bold]Summary:[/bold] {result.summary}")

    cat_table = Table(title="Category Breakdown")
    cat_table.add_column("Category")
    cat_table.add_column("Score", justify="right")
    cat_table.add_column("Weight", justify="right")
    cat_table.add_column("Weighted", justify="right")
    cat_table.add_column("Findings")
    for cat in result.categories:
        weighted = round(cat.score / cat.max_score * cat.weight * 100) if cat.max_score > 0 else 0
        sc = f"[{'green' if cat.score >= 80 else 'yellow' if cat.score >= 50 else 'red'}]{cat.score}[/]"
        cat_table.add_row(cat.label, sc, f"{cat.weight:.0%}", str(weighted),
                          cat.findings[0] if cat.findings else "")
    console.print(cat_table)

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    for step in result.suggested_next_steps:
        console.print(f"- {step}")

    from robopilot.migrate_score import SAFETY_NOTE
    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(SAFETY_NOTE)


@app.command("migrate-preview")
def migrate_preview(
    plan: Annotated[
        Path,
        typer.Option("--plan", "-p", help="Path to a ROS1-to-ROS2 migration plan."),
    ],
    project: Annotated[
        Path,
        typer.Option("--project", help="Source ROS1 package directory to preview."),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Preview file-level ROS1-to-ROS2 migration actions without modifying files."""
    try:
        result = api_preview_migration_plan(plan, project, as_dict=False)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    _print_migration_preview(result)


def _print_migration_preview(result: MigrationPreviewResult) -> None:
    console.print(Panel.fit("Migration Preview Summary", style="bold cyan"))
    console.print(f"[bold]Plan path:[/bold] {result.plan_path}")
    console.print(f"[bold]Source Project:[/bold] {result.project_path}")
    console.print(f"[bold]Target:[/bold] {result.target}")
    console.print(f"[bold]Package:[/bold] {result.package_name or 'unknown'}")
    console.print(f"[bold]Source project type:[/bold] {result.source_project_type}")

    console.print(Panel.fit("Files to Create", style="bold cyan"))
    _print_scalar_values(result.files_to_create)

    console.print(Panel.fit("Files to Update", style="bold cyan"))
    _print_scalar_values(result.files_to_update)

    console.print(Panel.fit("Files to Keep", style="bold cyan"))
    _print_scalar_values(result.files_to_keep)

    console.print(Panel.fit("Files Requiring Manual Migration", style="bold cyan"))
    _print_scalar_values(result.files_requiring_manual_migration)

    console.print(Panel.fit("Interface Files to Review", style="bold cyan"))
    _print_scalar_values(result.interface_files_to_review)

    console.print(Panel.fit("Dependency Items to Review", style="bold cyan"))
    _print_scalar_values(result.dependency_items_to_review)

    console.print(Panel.fit("Conflicts", style="bold cyan"))
    _print_scalar_values(result.conflicts)

    console.print(Panel.fit("Risks", style="bold cyan"))
    _print_scalar_values(result.risks)

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    _print_scalar_values(result.suggested_next_steps)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(result.safety_note)


@app.command("migrate-scaffold-preview")
def migrate_scaffold_preview(
    plan: Annotated[
        Path,
        typer.Option("--plan", "-p", help="Path to a ROS1-to-ROS2 migration plan."),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Preview a future ROS2 scaffold from a migration plan without writing files."""
    try:
        result = api_preview_migration_scaffold(plan, as_dict=False)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    _print_migration_scaffold_preview(result)


def _print_migration_scaffold_preview(result: MigrationScaffoldPreviewResult) -> None:
    console.print(Panel.fit("Migration Scaffold Preview Summary", style="bold cyan"))
    console.print(f"[bold]Plan path:[/bold] {result.plan_path}")
    console.print(f"[bold]Source Project:[/bold] {result.source_path or 'unknown'}")
    console.print(f"[bold]Target:[/bold] {result.target}")
    console.print(f"[bold]Package:[/bold] {result.package_name or 'unknown'}")
    console.print(f"[bold]Target Style:[/bold] {result.target_style}")

    console.print(Panel.fit("Scaffold Files to Create", style="bold cyan"))
    _print_scaffold_items(result.scaffold_files_to_create)

    console.print(Panel.fit("Placeholder Files", style="bold cyan"))
    _print_scaffold_items(result.placeholder_files)

    console.print(Panel.fit("Files Requiring Manual Migration", style="bold cyan"))
    _print_scalar_values(result.files_requiring_manual_migration)

    console.print(Panel.fit("Interface Files to Review", style="bold cyan"))
    _print_scalar_values(result.interface_files_to_review)

    console.print(Panel.fit("Dependency Items to Review", style="bold cyan"))
    _print_scalar_values(result.dependency_items_to_review)

    console.print(Panel.fit("Build System Notes", style="bold cyan"))
    _print_scalar_values(result.build_system_notes)

    console.print(Panel.fit("Launch Notes", style="bold cyan"))
    _print_scalar_values(result.launch_notes)

    console.print(Panel.fit("Risks", style="bold cyan"))
    _print_scalar_values(result.risks)

    console.print(Panel.fit("Conflicts", style="bold cyan"))
    _print_scalar_values(result.conflicts)

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    _print_scalar_values(result.suggested_next_steps)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(result.safety_note)


def _print_scaffold_items(items: tuple[ScaffoldFile, ...]) -> None:
    if not items:
        console.print("- none")
        return
    for item in items:
        console.print(f"- {item.path} ({item.status})")
        console.print(f"  purpose: {item.purpose}")
        console.print(f"  source_basis: {item.source_basis}")


@app.command("migrate-scaffold")
def migrate_scaffold(
    plan: Annotated[
        Path,
        typer.Option("--plan", "-p", help="Path to a ROS1-to-ROS2 migration plan."),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Directory where the ROS2 scaffold should be generated."),
    ],
    overwrite: Annotated[
        bool,
        typer.Option("--overwrite", help="Overwrite only intended scaffold files if they already exist."),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Generate a conservative ROS2 scaffold from a migration plan."""
    try:
        result = api_generate_migration_scaffold(plan, output, overwrite=overwrite, as_dict=False)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        _print_migration_scaffold_generation(result)

    if result.conflicts:
        raise typer.Exit(code=1)


def _print_migration_scaffold_generation(result: MigrationScaffoldGenerationResult) -> None:
    console.print(Panel.fit("Migration Scaffold Generation Summary", style="bold cyan"))
    console.print(f"[bold]Plan path:[/bold] {result.plan_path}")
    console.print(f"[bold]Output path:[/bold] {result.output_path}")
    console.print(f"[bold]Source Project:[/bold] {result.source_path or 'unknown'}")
    console.print(f"[bold]Target:[/bold] {result.target}")
    console.print(f"[bold]Package:[/bold] {result.package_name or 'unknown'}")
    console.print(f"[bold]Target Style:[/bold] {result.target_style}")

    console.print(Panel.fit("Files to Create", style="bold cyan"))
    _print_scalar_values(result.files_to_create)

    console.print(Panel.fit("Files Created", style="bold cyan"))
    _print_scalar_values(result.files_created)

    console.print(Panel.fit("Conflicts", style="bold cyan"))
    _print_scalar_values(result.conflicts)

    console.print(Panel.fit("Skipped Files", style="bold cyan"))
    _print_scalar_values(result.skipped_files)

    console.print(Panel.fit("Manual Migration Required", style="bold cyan"))
    _print_scalar_values(result.manual_migration_required)

    console.print(Panel.fit("Interface Files to Review", style="bold cyan"))
    _print_scalar_values(result.interface_files_to_review)

    console.print(Panel.fit("Dependency Items to Review", style="bold cyan"))
    _print_scalar_values(result.dependency_items_to_review)

    console.print(Panel.fit("Risks", style="bold cyan"))
    _print_scalar_values(result.risks)

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    _print_scalar_values(result.suggested_next_steps)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(result.safety_note)


@app.command("migrate-scaffold-validate")
def migrate_scaffold_validate(
    plan: Annotated[
        Path,
        typer.Option("--plan", "-p", help="Path to a ROS1-to-ROS2 migration plan."),
    ],
    scaffold: Annotated[
        Path,
        typer.Option("--scaffold", "-s", help="Generated ROS2 scaffold directory to validate."),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Validate a generated migration scaffold without modifying files."""
    try:
        result = api_validate_migration_scaffold(plan, scaffold, as_dict=False)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        _print_migration_scaffold_validation(result)

    if not result.valid:
        raise typer.Exit(code=1)


def _print_migration_scaffold_validation(result: MigrationScaffoldValidationResult) -> None:
    console.print(Panel.fit("Migration Scaffold Validation Summary", style="bold cyan"))
    console.print(f"[bold]Plan path:[/bold] {result.plan_path}")
    console.print(f"[bold]Scaffold path:[/bold] {result.scaffold_path}")
    console.print(f"[bold]Package:[/bold] {result.package_name or 'unknown'}")
    console.print(f"[bold]Target Style:[/bold] {result.target_style}")
    console.print(f"[bold]Valid:[/bold] {result.valid}")

    console.print(Panel.fit("Missing Files", style="bold cyan"))
    _print_scalar_values(result.missing_files)

    console.print(Panel.fit("Placeholder Checks", style="bold cyan"))
    if not result.placeholder_checks:
        console.print("- none")
    for check in result.placeholder_checks:
        status = "pass" if check.passed else "fail"
        console.print(f"- {check.path}: {status}")
        if check.missing_concepts:
            console.print(f"  missing: {', '.join(check.missing_concepts)}")

    console.print(Panel.fit("Issues", style="bold cyan"))
    _print_scalar_values(result.issues)

    console.print(Panel.fit("Warnings", style="bold cyan"))
    _print_scalar_values(result.warnings)

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    _print_scalar_values(result.suggested_next_steps)

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(result.safety_note)


@app.command("migrate-scaffold-report")
def migrate_scaffold_report(
    plan: Annotated[
        Path,
        typer.Option("--plan", "-p", help="Path to a ROS1-to-ROS2 migration plan."),
    ],
    scaffold: Annotated[
        Path,
        typer.Option("--scaffold", "-s", help="Generated ROS2 scaffold directory to report on."),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Optional Markdown report output path."),
    ] = None,
    overwrite: Annotated[
        bool,
        typer.Option("--overwrite", help="Overwrite an existing report output file."),
    ] = False,
) -> None:
    """Export a Markdown report for a generated migration scaffold."""
    try:
        markdown = api_generate_migration_scaffold_report(
            plan,
            scaffold,
            output_path=output,
            overwrite=overwrite,
        )
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if output is None:
        print(markdown)
        return

    result = api_validate_migration_scaffold(plan, scaffold, as_dict=False)
    console.print(Panel.fit("Migration Scaffold Report", style="bold cyan"))
    console.print(f"[bold]Report path:[/bold] {output}")
    console.print(f"[bold]Validation status:[/bold] {result.valid}")
    console.print(f"[bold]Issue count:[/bold] {len(result.issues)}")
    console.print(f"[bold]Warning count:[/bold] {len(result.warnings)}")
    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    console.print("- Open and review the generated scaffold report.")
    console.print("- Review MIGRATION_NOTES.md before manual migration work.")
    if not result.valid:
        console.print("- Fix validation issues and rerun migrate-scaffold-validate.")
    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(result.safety_note)


@app.command()
def validate(
    spec: Annotated[
        Path,
        typer.Option("--spec", "-s", help="Path to a robopilot.yaml ProjectSpec."),
    ],
) -> None:
    """Validate a robopilot.yaml ProjectSpec."""
    try:
        project_spec = load_spec(spec)
        result = validate_spec(project_spec)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Invalid ProjectSpec:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if result.is_valid:
        console.print(f"[green]Valid ProjectSpec:[/green] {spec}")
        return

    console.print(f"[red]Invalid ProjectSpec:[/red] {spec}")
    for error in result.errors:
        console.print(f"- {error}")
    raise typer.Exit(code=1)


@app.command()
def inspect(
    project_path: Annotated[Path, typer.Argument(help="Project directory to inspect.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Statically inspect a RoboPilot-generated or ROS-style project."""
    report = inspect_project(project_path)
    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
        return

    _print_inspection(report)


def _print_inspection(report: ProjectInspection) -> None:
    console.print(Panel.fit("Project Summary", style="bold cyan"))
    console.print(f"[bold]Project path:[/bold] {report.project_path}")
    console.print(f"[bold]Exists:[/bold] {report.exists}")
    console.print(f"[bold]Empty:[/bold] {report.is_empty}")
    console.print(f"[bold]Package name:[/bold] {report.package_name or 'unknown'}")

    console.print(Panel.fit("Spec Status", style="bold cyan"))
    console.print(f"[bold]robopilot.yaml exists:[/bold] {report.spec.exists}")
    console.print(f"[bold]Valid spec:[/bold] {report.spec.valid}")
    console.print(
        f"[bold]Selected template:[/bold] {report.spec.selected_template or 'unknown'}"
    )
    if report.spec.errors:
        for error in report.spec.errors:
            console.print(f"- {error}")

    files_table = Table(title="Detected Files")
    files_table.add_column("Type")
    files_table.add_column("Detected")
    files_table.add_row("package.xml", str(report.files.package_xml))
    files_table.add_row("setup.py", str(report.files.setup_py))
    files_table.add_row("setup.cfg", str(report.files.setup_cfg))
    files_table.add_row("README.md", str(report.files.readme))
    files_table.add_row("Launch files", _join_or_none(report.files.launch_files))
    files_table.add_row("Config files", _join_or_none(report.files.config_files))
    files_table.add_row("Python node files", _join_or_none(report.files.python_node_files))
    console.print(files_table)

    console.print(Panel.fit("Potential Issues", style="bold cyan"))
    if report.issues:
        for issue in report.issues:
            console.print(f"- {issue}")
    else:
        console.print("[green]No obvious structural issues detected.[/green]")

    console.print(Panel.fit("Suggested Next Steps", style="bold cyan"))
    for step in report.suggested_next_steps:
        console.print(f"- {step}")


def _join_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


@app.command("repair-suggest")
def repair_suggest(
    project_path: Annotated[Path, typer.Argument(help="Project directory to inspect.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print deterministic JSON output."),
    ] = False,
) -> None:
    """Suggest safe offline repairs for an inspected project."""
    report = suggest_repairs(project_path)
    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
        return

    _print_repair_suggestions(report)


def _print_repair_suggestions(report: RepairSuggestionReport) -> None:
    console.print(Panel.fit("Repair Suggestion Report", style="bold cyan"))
    console.print(f"[bold]Project path:[/bold] {report.project_path}")

    console.print(Panel.fit("Detected Issues", style="bold cyan"))
    if report.issues:
        for issue in report.issues:
            console.print(f"- {issue}")
    else:
        console.print("[green]No structural issues detected.[/green]")

    console.print(Panel.fit("Repair Suggestions", style="bold cyan"))
    if report.repair_suggestions:
        table = Table()
        table.add_column("Severity")
        table.add_column("Issue")
        table.add_column("Suggestion")
        for suggestion in report.repair_suggestions:
            table.add_row(
                suggestion.severity,
                suggestion.issue,
                suggestion.suggestion,
            )
        console.print(table)
    else:
        console.print("[green]No repair suggestions needed.[/green]")

    console.print(Panel.fit("Suggested Commands", style="bold cyan"))
    for command in report.suggested_commands:
        console.print(f"- {command}")

    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(report.safety_note)


@app.command()
def report(
    project_path: Annotated[Path, typer.Argument(help="Project directory to report on.")],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Optional Markdown report output path."),
    ] = None,
) -> None:
    """Export a static Markdown report for a project inspection."""
    try:
        if output is None:
            print(generate_project_report(project_path))
            return

        write_project_report(project_path, output)
    except OSError as exc:
        console.print(f"[red]Error:[/red] Could not write report: {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Wrote project report to[/green] {output}")


@app.command()
def debug(
    log: Annotated[
        Path | None,
        typer.Option("--log", "-l", help="Path to a robotics error log file."),
    ] = None,
    text: Annotated[
        str | None,
        typer.Option("--text", "-t", help="Inline error log text to analyze."),
    ] = None,
) -> None:
    """Analyze a robotics error log using offline rules."""
    if (log is None and text is None) or (log is not None and text is not None):
        console.print("[red]Error:[/red] Provide exactly one of --log or --text.")
        raise typer.Exit(code=1)

    try:
        log_text = log.read_text(encoding="utf-8") if log is not None else text or ""
    except OSError as exc:
        console.print(f"[red]Error:[/red] Could not read log file: {exc}")
        raise typer.Exit(code=1) from exc

    _print_analysis(analyze_log(log_text))


def _print_analysis(analysis: LogAnalysis) -> None:
    console.print(Panel.fit("Robotics Error Log Diagnosis", style="bold cyan"))
    console.print(f"[bold]Error type:[/bold] {analysis.error_type}")
    console.print(f"[bold]Confidence level:[/bold] {analysis.confidence}")
    console.print(f"[bold]Diagnosis:[/bold] {analysis.diagnosis}")

    console.print("[bold]Possible causes:[/bold]")
    for cause in analysis.possible_causes:
        console.print(f"- {cause}")

    console.print("[bold]Suggested fixes:[/bold]")
    for fix in analysis.suggested_fixes:
        console.print(f"- {fix}")


@app.command()
def tutorial(
    lesson: Annotated[
        str | None,
        typer.Option("--lesson", "-l", help="Run a specific lesson by ID."),
    ] = None,
    list_lessons_flag: Annotated[
        bool,
        typer.Option("--list", help="List available lessons."),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print lesson metadata as JSON."),
    ] = False,
) -> None:
    """Run a step-by-step interactive RoboPilot tutorial for beginners."""
    if list_lessons_flag:
        _print_lesson_list()
        return

    if json_output:
        lessons_data = [l.to_dict() for l in list_lessons()]
        if lesson:
            selected = get_lesson(lesson)
            if selected is None:
                print(json.dumps({"error": f"Unknown lesson: {lesson}"}))
                raise typer.Exit(code=1)
            print(json.dumps(selected.to_dict(), indent=2))
            return
        print(json.dumps(lessons_data, indent=2))
        return

    if lesson is None:
        console.print(Panel.fit("RoboPilot Tutorial", style="bold cyan"))
        console.print("Welcome! Run a lesson with --lesson, or --list to see available lessons.\n")
        console.print("[bold]Quick start:[/bold]")
        console.print("  robopilot tutorial --lesson demo_detector")
        console.print("  robopilot tutorial --lesson migration_basics")
        console.print("\n[bold]List all lessons:[/bold]")
        console.print("  robopilot tutorial --list")
        return

    selected = get_lesson(lesson)
    if selected is None:
        console.print(f"[red]Unknown lesson:[/red] {lesson}")
        console.print("Run [bold]robopilot tutorial --list[/bold] to see available lessons.")
        raise typer.Exit(code=1)

    _run_tutorial_lesson(selected)


def _print_lesson_list() -> None:
    lessons = list_lessons()
    console.print(Panel.fit("Available Tutorials", style="bold cyan"))
    table = Table()
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Duration")
    for les in lessons:
        table.add_row(les.id, les.title, f"~{les.estimated_minutes} min")
    console.print(table)
    console.print("\nRun: [bold]robopilot tutorial --lesson <id>[/bold]")


def _run_tutorial_lesson(lesson: TutorialLesson) -> None:
    console.print(Panel.fit(f"Tutorial: {lesson.title}", style="bold cyan"))
    console.print(f"[bold]Summary:[/bold] {lesson.summary}")
    console.print(f"[bold]Estimated time:[/bold] ~{lesson.estimated_minutes} minutes")
    console.print(f"[bold]Steps:[/bold] {len(lesson.steps)}\n")
    console.print("Press [bold]Enter[/bold] after each step to continue...\n")

    for i, step in enumerate(lesson.steps, 1):
        input(f"  [{i}/{len(lesson.steps)}] Press Enter to continue...")
        console.print()

        if step.action == "explain":
            console.print(Panel.fit(f"[bold cyan]Step {i}: {step.title}[/bold cyan]"))
            console.print(step.description)
            console.print()
        elif step.action == "run" and step.command:
            console.print(Panel.fit(f"[bold cyan]Step {i}: {step.title}[/bold cyan]"))
            console.print(step.description)
            if step.expected:
                console.print(f"\n[dim]Expected: {step.expected}[/dim]")
            console.print()
            _run_step_command(step)
        console.print()

    console.print(Panel.fit("[green]Tutorial Complete![/green]", style="bold green"))
    console.print(f"You finished '{lesson.title}' — all {len(lesson.steps)} steps.\n")
    console.print("[bold]Next:[/bold]")
    console.print("  - Try another lesson: robopilot tutorial --lesson migration_basics")
    console.print("  - Explore all commands: robopilot --help")
    console.print("  - Read the docs: docs/")

    from robopilot.tutorial import SAFETY_NOTE
    console.print(Panel.fit("Safety Note", style="bold cyan"))
    console.print(SAFETY_NOTE)


def _run_step_command(step: "TutorialStep") -> None:
    import subprocess
    import sys

    if not step.command:
        return

    console.print(f"[dim]$ {step.command}[/dim]\n")
    try:
        result = subprocess.run(
            step.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(Path.cwd()),
        )
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        console.print(output)
        if step.verification:
            if step.verification in output:
                console.print(f"[green]✓ Verified: '{step.verification}' found in output.[/green]")
            else:
                console.print(f"[yellow]⚠ Warning: Expected '{step.verification}' not found. Results may still be valid.[/yellow]")
    except Exception as exc:
        console.print(f"[red]Command failed:[/red] {exc}")


@app.command()
def graph(
    pipeline: Annotated[
        str,
        typer.Option(
            "--pipeline",
            "-p",
            help="Arrow-based robotics pipeline, such as 'camera -> detector'.",
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Optional Mermaid output file path."),
    ] = None,
) -> None:
    """Generate a Mermaid graph from a robotics workflow pipeline."""
    try:
        mermaid = generate_mermaid(pipeline)
    except PipelineParseError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(mermaid)

    if output is not None:
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(f"{mermaid}\n", encoding="utf-8")
        except OSError as exc:
            console.print(f"[red]Error:[/red] Could not write graph file: {exc}")
            raise typer.Exit(code=1) from exc

        console.print(f"[green]Wrote Mermaid graph to[/green] {output}")


if __name__ == "__main__":
    app()
