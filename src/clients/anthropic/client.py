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
_DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-5"
# OpenRouter names models as `<provider>/<model>`:
_DEFAULT_OPENROUTER_MODEL = f"anthropic/{_DEFAULT_ANTHROPIC_MODEL}"
ANTHROPIC_MODEL: Optional[str] = os.getenv(key="ANTHROPIC_MODEL") or None

# Fallback route when `ANTHROPIC_API_KEY` is empty: OpenRouter's
# Anthropic-compatible Messages endpoint (the SDK appends `/v1/messages`):
_OPENROUTER_BASE_URL = "https://openrouter.ai/api"

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
    and high effort are enabled by default for reasoning quality.
    Requests go straight to Anthropic when `ANTHROPIC_API_KEY` is set;
    when it is empty, they go through OpenRouter, authenticated with
    `OPENROUTER_API_KEY` as a bearer token. The SDK auto-retries
    transient failures, so no bespoke retry policy is layered on top.
    """

    def __init__(self, model: Optional[str] = None) -> None:
        """
        Initializes the async Anthropic client.

        :param model: The Claude model ID to call; falls back to the
            `ANTHROPIC_MODEL` env var, then to `claude-sonnet-5` (or
            `anthropic/claude-sonnet-5` when routed through OpenRouter).
        :type model: Optional[str]

        :raises RuntimeError: If neither `ANTHROPIC_API_KEY` nor
            `OPENROUTER_API_KEY` is set.
        """

        anthropic_key = os.getenv(key="ANTHROPIC_API_KEY")
        openrouter_key = os.getenv(key="OPENROUTER_API_KEY")

        if anthropic_key:
            self._model = (
                model or ANTHROPIC_MODEL or _DEFAULT_ANTHROPIC_MODEL
            )
            self._client = AsyncAnthropic(api_key=anthropic_key)
        elif openrouter_key:
            chosen = model or ANTHROPIC_MODEL or _DEFAULT_OPENROUTER_MODEL
            # Accept bare Anthropic IDs too, so one `ANTHROPIC_MODEL`
            # works on both routes:
            self._model = (
                chosen if "/" in chosen else f"anthropic/{chosen}"
            )
            # OpenRouter expects `Authorization: Bearer`, which the SDK
            # sends for `auth_token` (`api_key` goes as `x-api-key`):
            self._client = AsyncAnthropic(
                api_key=None,
                auth_token=openrouter_key,
                base_url=_OPENROUTER_BASE_URL
            )
        else:
            raise RuntimeError(
                "Set ANTHROPIC_API_KEY or OPENROUTER_API_KEY"
            )

        _logger.info(
            "Reasoning via %s (model=%s)",
            "Anthropic" if anthropic_key else "OpenRouter", self._model
        )

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
