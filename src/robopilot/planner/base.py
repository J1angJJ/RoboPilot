"""Shared planner interface and planner errors."""

from __future__ import annotations

from typing import Protocol

from robopilot.generator.project_spec import ProjectSpec


class Planner(Protocol):
    """Interface for ProjectSpec planners."""

    def plan(self, *, package_name: str, task: str) -> ProjectSpec:
        """Return a ProjectSpec for a package name and robotics task."""


class PlannerError(ValueError):
    """Base error for planner failures."""


class PlannerConfigurationError(PlannerError):
    """Raised when a requested planner is not configured."""


class PlannerValidationError(PlannerError):
    """Raised when a planner returns an invalid ProjectSpec."""


class PlannerProviderError(PlannerError):
    """Raised when a configured LLM provider call fails."""
