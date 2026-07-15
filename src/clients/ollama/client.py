"""Asynchronous client for the local Ollama embeddings API."""

import logging
import os
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from src.logger import get_logger


load_dotenv()
_DEFAULT_BASE_URL = "http://localhost:11434"
_DEFAULT_EMBED_MODEL = "nomic-embed-text"
OLLAMA_BASE_URL: str = os.getenv(key="OLLAMA_BASE_URL") or _DEFAULT_BASE_URL
OLLAMA_EMBED_MODEL: str = (
    os.getenv(key="OLLAMA_EMBED_MODEL") or _DEFAULT_EMBED_MODEL
)

# Local inference can run well past httpx's 5-second default timeout,
# particularly on a cold model load:
_REQUEST_TIMEOUT_SECONDS = 120.0

# Retry Policy constants:
_MAX_ATTEMPTS = 4
_WAIT_MIN_SECONDS = 1
_WAIT_MAX_SECONDS = 30
_RETRYABLE_STATUS_CODES = {
    500,    # Internal Server Error
    502,    # Bad Gateway
    503,    # Service Unavailable
    504     # Gateway Timeout
}


_logger = get_logger(__name__)


# Private retry policy functions:
def _is_retryable(e: BaseException) -> bool:
    """
    Verifies if the given exception is retryable: either a\n
    `httpx.HTTPStatusError` with status code 500, 502, 503 or 504, or\n
    a `httpx.TransportError` (timeouts, connection resets, and other\n
    transient network failures).
    """

    if isinstance(e, httpx.HTTPStatusError):
        return e.response.status_code in _RETRYABLE_STATUS_CODES

    return isinstance(e, httpx.TransportError)

def _retry_policy(func):
    """A simple decorator function to apply shared tenacity retry policy."""

    return retry(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(_MAX_ATTEMPTS),
        wait=wait_exponential(
            multiplier=1,
            min=_WAIT_MIN_SECONDS,
            max=_WAIT_MAX_SECONDS
        ),
        before_sleep=before_sleep_log(_logger, logging.WARNING),
        reraise=True
    )(func)


class OllamaClient:
    """
    Async HTTP client for the local Ollama embeddings API.\n
    Produces dense vector embeddings for a single text at a time, used to
    populate and query the Neo4j vector index backing semantic search.\n

    Uses `httpx.AsyncClient` for non-blocking I/O. No `asyncio.Semaphore`
    is needed: embedding at load time is driven sequentially, and at query
    time serves one question at a time.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ) -> None:
        """
        Initializes the async HTTP client.

        :param base_url: The Ollama server base URL; falls back to the
            `OLLAMA_BASE_URL` env var, then to `http://localhost:11434`.
        :type base_url: Optional[str]
        :param model: The Ollama embedding model name; falls back to the
            `OLLAMA_EMBED_MODEL` env var, then to `nomic-embed-text`.
        :type model: Optional[str]
        """

        self._model = model or OLLAMA_EMBED_MODEL
        self._http = httpx.AsyncClient(
            base_url=base_url or OLLAMA_BASE_URL,
            # Local inference is far slower than a typical HTTP call,
            # especially on the first request while the model loads:
            timeout=httpx.Timeout(_REQUEST_TIMEOUT_SECONDS)
        )

    async def __aenter__(self) -> "OllamaClient":
        """Enters the async context, returning this client instance."""
        return self

    async def __aexit__(self, *_) -> None:
        """Exits the async context, closing the connection pool."""
        await self.close()

    async def close(self) -> None:
        """Closes the underlying async HTTP connection pool."""
        await self._http.aclose()

    async def embed(self, text: str) -> List[float]:
        """
        Embeds a single text into a dense vector via the Ollama
        `/api/embed` endpoint.

        :param text: The text to embed.
        :type text: str

        :return: The embedding vector.
        :rtype: List[float]

        :raises httpx.HTTPStatusError: If the request is unsuccessful.
        """

        response = await self._post(
            path="/api/embed",
            json={"model": self._model, "input": text}
        )
        return response["embeddings"][0]

    @_retry_policy
    async def _post(
        self, path: str, json: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Performs a `POST` HTTP request on the Ollama API, on the given
        endpoint.

        :param path: An Ollama REST API endpoint.
        :type path: str
        :param json: The JSON request body.
        :type json: Dict[str, Any]

        :returns: The parsed JSON response body.
        :rtype: Dict[str, Any]

        :raises httpx.HTTPStatusError: If the request is unsuccessful.
        """

        _logger.debug("POST %s%s", self._http.base_url, path)
        response = await self._http.post(path, json=json)
        response.raise_for_status()
        return response.json()
