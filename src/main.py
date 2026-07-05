"""Entry point for the Cinematica knowledge graph pipeline."""

import asyncio
from pathlib import Path

from src.logger import get_logger
from src.pipeline.compile import (
    build_movie_index,
    build_ratings_index,
    build_principals_index,
    collect_nconsts,
    build_names_index
)
from src.pipeline.consolidate import consolidate_shards
from src.pipeline.enrich import enrich_to_shards


_DATASETS_DIR = Path("datasets")
_CHUNKS_DIR = Path("data/chunks")
_CONSOLIDATED_PATH = Path("data/movies.jsonl")

_logger = get_logger(__name__)


async def run_pipeline() -> None:
    """
    Runs the full enrichment pipeline: compiles the IMDb datasets into
    in-memory indexes, enriches every movie with TMDb data into resumable
    JSONL shards, then consolidates the shards into a single output file.
    """

    movies = build_movie_index(_DATASETS_DIR / "title.basics.tsv.gz")
    movie_ids = set(movies)

    ratings = build_ratings_index(_DATASETS_DIR / "title.ratings.tsv.gz", movie_ids)
    principals = build_principals_index(_DATASETS_DIR / "title.principals.tsv.gz", movie_ids)
    names = build_names_index(_DATASETS_DIR / "name.basics.tsv.gz", collect_nconsts(principals))

    await enrich_to_shards(movies, ratings, principals, names, _CHUNKS_DIR)
    consolidate_shards(_CHUNKS_DIR, _CONSOLIDATED_PATH)

    _logger.info("Pipeline finished. Output written to %s", _CONSOLIDATED_PATH)


if __name__ == "__main__":
    asyncio.run(run_pipeline())
