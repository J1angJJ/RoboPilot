"""Provider configuration for optional LLM planning."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

from robopilot.planner.base import PlannerConfigurationError


DEFAULT_LLM_MODEL = "gpt-4.1-mini"


@dataclass(frozen=True)
class LLMProviderConfig:
    """Configuration for an optional LLM provider."""

    api_key: str
    model: str

    @classmethod
    def from_env(
        cls,
        *,
        model_override: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> "LLMProviderConfig":
        """Create provider config from environment variables."""
        values = os.environ if env is None else env
        api_key = values.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise PlannerConfigurationError(
                "LLM planner requested, but OPENAI_API_KEY is not set. "
                "Set OPENAI_API_KEY or use --planner rule for offline planning."
            )

        model = (
            model_override
            or values.get("ROBOPILOT_LLM_MODEL", "")
            or DEFAULT_LLM_MODEL
        ).strip()
        return cls(api_key=api_key, model=model or DEFAULT_LLM_MODEL)
