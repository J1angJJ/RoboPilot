"""Optional OpenAI provider client for ProjectSpec-only planning."""

from __future__ import annotations

from typing import Any

from robopilot.planner.base import PlannerConfigurationError, PlannerProviderError
from robopilot.planner.provider_config import LLMProviderConfig


class OpenAIPlannerClient:
    """Minimal OpenAI Responses API client wrapper for LLMPlanner."""

    def __init__(
        self,
        config: LLMProviderConfig,
        *,
        sdk_client: Any | None = None,
    ) -> None:
        self.config = config
        self._client = sdk_client or self._build_sdk_client(config.api_key)

    def complete(self, prompt: str) -> str:
        """Return provider text output for a ProjectSpec prompt."""
        try:
            response = self._client.responses.create(
                model=self.config.model,
                input=prompt,
            )
        except Exception as exc:  # pragma: no cover - exercised with fake clients
            raise PlannerProviderError(f"OpenAI provider call failed: {exc}") from exc

        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text
        extracted = _extract_output_text(response)
        if extracted.strip():
            return extracted
        raise PlannerProviderError("OpenAI provider returned empty text output.")

    @staticmethod
    def _build_sdk_client(api_key: str) -> Any:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise PlannerConfigurationError(
                "OpenAI SDK is not installed. Install RoboPilot with the optional "
                "LLM extra, for example: pip install -e \".[llm]\""
            ) from exc
        return OpenAI(api_key=api_key)


def _extract_output_text(response: Any) -> str:
    output = getattr(response, "output", None)
    if not isinstance(output, list):
        return ""

    chunks: list[str] = []
    for item in output:
        content = getattr(item, "content", None)
        if not isinstance(content, list):
            continue
        for content_item in content:
            text = getattr(content_item, "text", None)
            if isinstance(text, str):
                chunks.append(text)
    return "\n".join(chunks)
