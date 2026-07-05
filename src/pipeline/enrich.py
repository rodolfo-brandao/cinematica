"""TMDb enrichment of compiled IMDb movies into JSONL shards."""

import json
import os
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence

from src.clients.tmdb.client import TmdbClient
from src.logger import get_logger
from src.models.imdb import ImdbMovie, ImdbRating, ImdbPrincipal, ImdbPerson
from src.pipeline.serialize import to_movie_record


_logger = get_logger(__name__)

_DEFAULT_CHUNK_SIZE = 500
_SHARD_PREFIX = "movies_"
_SHARD_SUFFIX = ".jsonl"


# The four IMDb indexes are each required and semantically distinct, so they
# are kept as separate named arguments rather than bundled into a container:
# pylint: disable-next=too-many-arguments,too-many-positional-arguments
async def enrich_to_shards(
    movies: Dict[str, ImdbMovie],
    ratings: Dict[str, ImdbRating],
    principals: Dict[str, List[ImdbPrincipal]],
    names: Dict[str, ImdbPerson],
    output_dir: Path,
    chunk_size: int = _DEFAULT_CHUNK_SIZE,
    client: Optional[TmdbClient] = None
) -> None:
    """
    Enriches the compiled IMDb movies with TMDb data and writes the result as
    per-chunk JSONL shards. Chunks are derived from the sorted `tconst`s, so a
    given chunk always maps to the same movies; shards that already exist are
    skipped, making the whole process resumable.

    :param movies: The movie index (the pipeline spine).
    :type movies: Dict[str, ImdbMovie]
    :param ratings: The ratings index, keyed by `tconst`.
    :type ratings: Dict[str, ImdbRating]
    :param principals: The principals index, keyed by `tconst`.
    :type principals: Dict[str, List[ImdbPrincipal]]
    :param names: The names index, keyed by `nconst`.
    :type names: Dict[str, ImdbPerson]
    :param output_dir: Directory where the JSONL shards are written.
    :type output_dir: Path
    :param chunk_size: Number of movies per shard.
    :type chunk_size: int
    :param client: An existing TMDb client; one is created (and closed) if omitted.
    :type client: Optional[TmdbClient]
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    tconsts = sorted(movies)
    chunks = list(_chunked(tconsts, chunk_size))
    _logger.info(
        "Enriching %d movie(s) in %d chunk(s) of up to %d.",
        len(tconsts), len(chunks), chunk_size
    )

    owns_client = client is None
    client = client or TmdbClient()

    try:
        for chunk_index, chunk in enumerate(chunks):
            shard_path = output_dir / f"{_SHARD_PREFIX}{chunk_index:05d}{_SHARD_SUFFIX}"

            if shard_path.exists():
                _logger.info("Skipping chunk %d (shard already exists).", chunk_index)
                continue

            _logger.info("Processing chunk %d/%d.", chunk_index + 1, len(chunks))
            records = await _enrich_chunk(chunk, movies, ratings, principals, names, client)

            _write_shard(shard_path, records)
            _logger.info("Wrote %d record(s) to %s", len(records), shard_path)
    finally:
        if owns_client:
            await client.close()


# Private helpers (module-level):
# pylint: disable-next=too-many-arguments,too-many-positional-arguments
async def _enrich_chunk(
    chunk: List[str],
    movies: Dict[str, ImdbMovie],
    ratings: Dict[str, ImdbRating],
    principals: Dict[str, List[ImdbPrincipal]],
    names: Dict[str, ImdbPerson],
    client: TmdbClient
) -> List[dict]:
    """Resolves TMDb data for one chunk and joins it into movie records."""

    tmdb_movies = await client.find_by_imdb_ids(chunk)
    tmdb_by_imdb_id = {movie.imdb_id: movie for movie in tmdb_movies}

    return [
        to_movie_record(
            movie=movies[tconst],
            rating=ratings.get(tconst),
            principals=principals.get(tconst, []),
            names=names,
            tmdb=tmdb_by_imdb_id.get(tconst)
        )
        for tconst in chunk
    ]


def _chunked(sequence: Sequence[str], size: int) -> Iterator[List[str]]:
    """Yields successive `size`-length chunks from `sequence`."""

    for start in range(0, len(sequence), size):
        yield list(sequence[start:start + size])


def _write_shard(shard_path: Path, records: List[dict]) -> None:
    """
    Writes `records` as JSONL to `shard_path` atomically: the data is written to
    a temporary file first and then moved into place, so a crash mid-write can
    never leave a partial shard behind.
    """

    tmp_path = shard_path.with_suffix(shard_path.suffix + ".tmp")
    lines = (json.dumps(record, ensure_ascii=False) for record in records)
    tmp_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(tmp_path, shard_path)
