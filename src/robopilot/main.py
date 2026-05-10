"""Command-line interface for RoboPilot."""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from robopilot.debugger.log_analyzer import LogAnalysis, analyze_log
from robopilot.generator.project_generator import (
    generate_project,
    generate_project_from_spec,
)
from robopilot.graph.mermaid_generator import PipelineParseError, generate_mermaid
from robopilot.inspector.project_inspector import ProjectInspection, inspect_project
from robopilot.planner import (
    LLMProviderConfig,
    LLMPlanner,
    OpenAIPlannerClient,
    PlannerConfigurationError,
    PlannerError,
    RuleBasedPlanner,
)
from robopilot.repair.repair_suggester import RepairSuggestionReport, suggest_repairs
from robopilot.refiner.spec_refiner import refine_spec
from robopilot.report.project_report import generate_project_report, write_project_report
from robopilot.spec.io import load_spec, spec_to_yaml, write_spec
from robopilot.spec.validator import validate_spec
from robopilot.utils.file_ops import OutputPathExistsError


app = typer.Typer(
    help="RoboPilot: lightweight ROS-style robotics development assistant.",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def main() -> None:
    """Run RoboPilot commands."""


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
        typer.Option("--planner", help="Refinement backend to use. Only 'rule' is supported."),
    ] = "rule",
) -> None:
    """Refine an existing ProjectSpec and write a new spec file."""
    try:
        original_spec = load_spec(spec)
        refined_spec = refine_spec(original_spec, instruction, planner=planner)
        write_spec(refined_spec, output)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Wrote refined ProjectSpec to[/green] {output}")


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
