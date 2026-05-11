"""Shared helpers and light typing for the public RoboPilot API layer."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

PathLike = str | Path
StructuredResult = dict[str, Any]


def normalize_path(path: PathLike) -> Path:
    """Return a pathlib Path for API path arguments."""
    return path if isinstance(path, Path) else Path(path)


def to_structured_result(value: object) -> StructuredResult:
    """Convert RoboPilot result objects into plain Python dictionaries."""
    if hasattr(value, "to_dict"):
        result = value.to_dict()  # type: ignore[attr-defined]
        if isinstance(result, dict):
            return result
    if is_dataclass(value):
        return _stringify_paths(asdict(value))
    raise TypeError(f"Object cannot be converted to a structured result: {type(value)!r}")


def _stringify_paths(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _stringify_paths(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_stringify_paths(item) for item in value]
    if isinstance(value, list):
        return [_stringify_paths(item) for item in value]
    return value
