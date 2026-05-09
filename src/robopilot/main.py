"""Command-line interface for RoboPilot."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from robopilot.debugger.log_analyzer import LogAnalysis, analyze_log
from robopilot.generator.project_generator import generate_project
from robopilot.graph.mermaid_generator import PipelineParseError, generate_mermaid
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
    name: Annotated[str, typer.Option("--name", "-n", help="Package name to create.")],
    task: Annotated[
        str,
        typer.Option("--task", "-t", help="Natural language robotics task."),
    ],
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

    table = Table(title="Created files")
    table.add_column("Path", style="cyan")
    for file_path in project.files:
        table.add_row(str(file_path.relative_to(project.output_dir)))
    console.print(table)


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
