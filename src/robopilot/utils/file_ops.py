"""Safe file operation helpers for generated RoboPilot projects."""

from pathlib import Path


class OutputPathExistsError(FileExistsError):
    """Raised when a generated output path already exists."""


def ensure_new_directory(path: Path, *, overwrite: bool = False) -> None:
    """Create a directory, refusing to reuse an existing path by default."""
    if path.exists() and not overwrite:
        raise OutputPathExistsError(
            f"Output directory already exists: {path}. "
            "Choose another name or pass overwrite=True."
        )

    path.mkdir(parents=True, exist_ok=overwrite)


def write_text_file(path: Path, content: str, *, overwrite: bool = False) -> None:
    """Write a UTF-8 text file, protecting existing files by default."""
    if path.exists() and not overwrite:
        raise OutputPathExistsError(
            f"Refusing to overwrite existing file: {path}."
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

