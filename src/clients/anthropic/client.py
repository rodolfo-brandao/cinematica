"""Asynchronous client for the Anthropic Messages API."""

import os
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic
from anthropic.types import Message
from dotenv import load_dotenv

from src.logger import get_logger


load_dotenv()
# Sonnet is the default: the grounding tools (schema introspection, entity
# resolution, error-repair loops) carry most of the reasoning load, so the
# Opus tier is an escalation to justify with evidence, not a starting
# assumption. Raise to `claude-opus-4-8` via `ANTHROPIC_MODEL` if a class
# of questions is shown to need it.
_DEFAULT_MODEL = "claude-sonnet-5"
ANTHROPIC_MODEL: str = os.getenv(key="ANTHROPIC_MODEL") or _DEFAULT_MODEL

# Roomy but under the SDK's non-streaming timeout guard; the reasoning
# stages produce short answers, not long documents:
_MAX_TOKENS = 16000


_logger = get_logger(__name__)


class AnthropicClient:
    """
    Async client for the Anthropic Messages API, driving every reasoning
    stage of the agent pipeline.\n

    Thin wrapper over the official `AsyncAnthropic` SDK: it runs one
    chat turn (optionally with tool schemas) and returns the raw
    `Message`, leaving the tool-use loop to the caller. Adaptive thinking
    and high effort are enabled by default for reasoning quality. The SDK
    resolves credentials from `ANTHROPIC_API_KEY` and auto-retries
    transient failures, so no bespoke retry policy is layered on top.
    """

    def __init__(self, model: Optional[str] = None) -> None:
        """
        Initializes the async Anthropic client.

        :param model: The Claude model ID to call; falls back to the
            `ANTHROPIC_MODEL` env var, then to `claude-opus-4-8`.
        :type model: Optional[str]
        """

        self._model = model or ANTHROPIC_MODEL
        self._client = AsyncAnthropic()

    async def __aenter__(self) -> "AnthropicClient":
        """Enters the async context, returning this client instance."""
        return self

    async def __aexit__(self, *_) -> None:
        """Exits the async context, closing the underlying client."""
        await self.close()

    async def close(self) -> None:
        """Closes the underlying async Anthropic client."""
        await self._client.close()

    async def complete(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Message:
        """
        Runs one Messages API turn and returns the assistant's response.

        :param system: The system prompt grounding this turn.
        :type system: str
        :param messages: The conversation so far, in the Messages API
            `role`/`content` format.
        :type messages: List[Dict[str, Any]]
        :param tools: The tool schemas available to the model this turn;
            omit for a plain (no tool-use) turn.
        :type tools: Optional[List[Dict[str, Any]]]

        :return: The assistant's response message (`content` blocks plus
            `stop_reason`).
        :rtype: anthropic.types.Message
        """

        _logger.debug(
            "Anthropic messages.create (model=%s, tools=%d)",
            self._model, len(tools or [])
        )
        return await self._client.messages.create(
            model=self._model,
            max_tokens=_MAX_TOKENS,
            thinking={"type": "adaptive"},
            output_config={"effort": "high"},
            system=system,
            messages=messages,
            tools=tools or []
        )
