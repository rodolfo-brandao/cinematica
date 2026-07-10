"""Entry point for the Cinematica knowledge graph pipeline."""

import argparse
import asyncio
from pathlib import Path
from typing import Optional

from src.clients.neo4j.client import Neo4jClient
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
from src.pipeline.load import load_movies


_DATASETS_DIR = Path("datasets")
_CHUNKS_DIR = Path("data/chunks")
_CONSOLIDATED_PATH = Path("data/movies.jsonl")

_logger = get_logger(__name__)


async def run_pipeline(max_chunks: Optional[int] = None) -> None:
    """
    Runs the enrichment pipeline: compiles the IMDb datasets into in-memory
    indexes, enriches movies with TMDb data into resumable JSONL shards,
    consolidates the existing shards into a single output file, then loads
    that file into Neo4j.

    :param max_chunks: Maximum number of new shards to write this run;
        `None` runs until every chunk is enriched.
    :type max_chunks: Optional[int]
    """

    movies = build_movie_index(_DATASETS_DIR / "title.basics.tsv.gz")
    movie_ids = set(movies)

    ratings = build_ratings_index(_DATASETS_DIR / "title.ratings.tsv.gz", movie_ids)
    principals = build_principals_index(_DATASETS_DIR / "title.principals.tsv.gz", movie_ids)
    names = build_names_index(_DATASETS_DIR / "name.basics.tsv.gz", collect_nconsts(principals))

    await enrich_to_shards(
        movies, ratings, principals, names, _CHUNKS_DIR,
        max_chunks=max_chunks
    )
    consolidate_shards(_CHUNKS_DIR, _CONSOLIDATED_PATH)

    with Neo4jClient() as client:
        client.ensure_constraints()
        load_movies(_CONSOLIDATED_PATH, client)

    _logger.info("Pipeline finished. Output written to %s", _CONSOLIDATED_PATH)


def _parse_args() -> argparse.Namespace:
    """Parses the command-line arguments for the pipeline run."""

    parser = argparse.ArgumentParser(
        description="Cinematica IMDb/TMDb enrichment pipeline."
    )
    parser.add_argument(
        "max_chunks",
        nargs="?",
        type=int,
        default=None,
        help=(
            "maximum number of new shards to write this run "
            "(e.g. 200 = one 100k-movie batch); omit to run to completion"
        )
    )
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(run_pipeline(max_chunks=_parse_args().max_chunks))
