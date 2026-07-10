"""Asynchronous client for the TMDb REST API v3."""

import asyncio
import logging
import os
import httpx
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from src.logger import get_logger
from src.models.tmdb import (
    Genre,
    SpokenLanguage,
    TmdbMovie
)


load_dotenv()
TMDB_API_BASE_URL = "https://api.themoviedb.org/3"
TMDB_API_READ_ACCESS_TOKEN: Optional[str] = os.getenv(key="TMDB_API_READ_ACCESS_TOKEN")

# [TMDb] 20 simultaneous connections per IP:
_MAX_CONCURRENT_REQUESTS = 20

# Retry Policy constants:
_MAX_ATTEMPTS = 4
_WAIT_MIN_SECONDS = 1
_WAIT_MAX_SECONDS = 30
_RETRYABLE_STATUS_CODES = {
    429,    # Too Many Requests
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
    `httpx.HTTPStatusError` with status code 429, 500, 502, 503 or\n
    504, or a `httpx.TransportError` (timeouts, connection resets,\n
    and other transient network failures).
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


class TmdbClient:
    """
    Async HTTP client for the TMDb REST API v3.\n
    Currently handles only search for movies based on IMDb IDs.\n
    Authentication is handled via Bearer Token (_Read Access Token_).\n

    Uses:
    - `httpx.AsyncClient` for non-blocking I/O
    - `asyncio.Semaphore` to stay within TMDb's limit of 20 simultaneous
    connections per IP
    """

    def __init__(self, read_access_token: Optional[str] = None) -> None:
        """
        Initializes the async HTTP client and concurrency semaphore.

        :param read_access_token: TMDb Read Access Token; falls back to
            the `TMDB_API_READ_ACCESS_TOKEN` env var when omitted.
        :type read_access_token: Optional[str]

        :raises ValueError: If no Read Access Token can be resolved.
        """

        token = read_access_token or TMDB_API_READ_ACCESS_TOKEN

        if not token:
            raise ValueError("TMDb 'Read Access Token' is required.")

        self._http = httpx.AsyncClient(
            base_url=TMDB_API_BASE_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
        )
        self._semaphore = asyncio.Semaphore(_MAX_CONCURRENT_REQUESTS)

    async def __aenter__(self) -> "TmdbClient":
        """Enters the async context, returning this client instance."""
        return self

    async def __aexit__(self, *_) -> None:
        """Exits the async context, closing the connection pool."""
        await self.close()

    async def close(self) -> None:
        """Closes the underlying async HTTP connection pool."""
        await self._http.aclose()


    async def find_by_imdb_id(self, imdb_id: str) -> Optional[TmdbMovie]:
        """
        Resolves a single TMDb movie record from a IMDb ID (e.g. "tt0137523").

        :param imdb_id: The IMDb title unique identifier (`tt` --prefixed string).
        :type imdb_id: str

        :return: A :class:`~src.models.tmdb.TmdbMovie` instance or `None`.
        :rtype: src.models.tmdb.TmdbMovie

        :raises urllib.error.HTTPError: On non-retryable HTTP errors.
        """

        _logger.debug("Resolving IMDb ID %s via TMDb /find endpoint", imdb_id)
        find_response = await self._get(
            path=f"/find/{imdb_id}",
            params={ "external_source": "imdb_id" }
        )
        movie_results = (find_response or {}).get("movie_results") or []

        if not movie_results:
            _logger.warning("No TMDb match found for IMDb ID %s", imdb_id)
            return None

        tmdb_id: int = movie_results[0]["id"]
        _logger.debug("Resolved IMDb ID %s -> TMDb ID %d", imdb_id, tmdb_id)

        # Complete TmdbMovie (budget, revenue, runtime, genres, etc.):
        details = await self._get(path=f"/movie/{tmdb_id}")
        return _parse_movie_details(details)


    async def find_by_imdb_ids(self, imdb_ids: List[str]) -> List[TmdbMovie]:
        """
        Concurrently resolves a list of IMDb IDs into TMDb records.

        :param imdb_ids: A list of IMDb IDs (`tt` --prefixed string).
        :type imdb_ids: List[str]

        :return: A list with instances of :class:`~src.models.tmdb.TmdbMovie` if
        any movie is found. Otherwise, `[]`.
        :rtype: List[TmdbMovie]
        """

        _logger.info("Resolving %d IMDb ID(s) concurrently.", len(imdb_ids))
        tasks = [self.find_by_imdb_id(imdb_id) for imdb_id in imdb_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        movies: List[TmdbMovie] = []
        failed = 0

        for imdb_id, result in zip(imdb_ids, results):
            if isinstance(result, TmdbMovie):
                movies.append(result)
            elif isinstance(result, BaseException):
                # `None` means "no TMDb match", already logged as a
                # warning by `find_by_imdb_id`; only real exceptions
                # are logged here.
                failed += 1
                _logger.error("Failed to resolve %s: %r", imdb_id, result)

        not_found = len(imdb_ids) - len(movies) - failed
        _logger.info(
            "Resolved %d/%d record(s) (%d not found on TMDb, %d failed).",
            len(movies), len(imdb_ids), not_found, failed
        )
        return movies


    @_retry_policy
    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Performs a `GET` HTTP request on the TMDb REST API, on the given endpoint.

        :param path: A TMDb REST API endpoint.
        :type path: str
        :param params: The query params for the request.
        :type params: Optional[Dict[str, Any]]

        :returns: Movie details.
        :rtype: Dict[str, Any]

        :raises httpx.HTTPStatusError: If the request is unsuccessful.
        """

        async with self._semaphore:
            _logger.debug("GET %s%s", TMDB_API_BASE_URL, path)
            response = await self._http.get(path, params=params)
            response.raise_for_status()
            return response.json()


# Private parser (module-level):
def _parse_movie_details(data: Dict[str, Any]) -> TmdbMovie:
    """
    Parses a given movie data into :class:`~src.models.tmdb.TmdbMovie`.

    :param data: The movie details object from the TMDb API response.
    :type data: Dict[str, Any]

    :return: An instance of :class:`~src.models.tmdb.TmdbMovie`.
    :rtype: src.models.tmdb.Movie
    """

    genres = [
        Genre(
            id=g["id"],
            name=g["name"]
        ) for g in data.get("genres") or []
    ]

    spoken_languages = [
        SpokenLanguage(
            english_name=sl["english_name"],
            iso_639_1=sl["iso_639_1"],
            name=sl["name"]
        ) for sl in data.get("spoken_languages") or []
    ]

    origin_countries = [
        str(oc) for oc in data.get("origin_country") or []
    ]

    return TmdbMovie(
        tmdb_id=data["id"],
        imdb_id=data["imdb_id"],
        is_adult=data["adult"],
        budget=data["budget"],
        genres=genres,
        origin_country=origin_countries,
        original_language=data["original_language"],
        original_title=data["original_title"],
        overview=data["overview"],
        popularity=data["popularity"],
        release_date=data["release_date"],
        revenue=data["revenue"],
        runtime_min=data["runtime"],
        spoken_languages=spoken_languages,
        status=data["status"],
        tagline=data["tagline"],
        title=data["title"],
        has_video=data["video"],
        vote_average=data["vote_average"],
        vote_count=data["vote_count"]
    )
