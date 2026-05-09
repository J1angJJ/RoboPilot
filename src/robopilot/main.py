"""Command-line interface for RoboPilot."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from robopilot.generator.project_generator import generate_project
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


if __name__ == "__main__":
    app()
