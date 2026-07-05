"""Unit tests for src.pipeline.enrich (no real network calls)."""

import asyncio
import json
from pathlib import Path
from typing import Dict, List

from src.models.imdb import ImdbMovie
from src.pipeline.enrich import enrich_to_shards


def _make_movies(count: int) -> Dict[str, ImdbMovie]:
    return {
        f"tt{i:07d}": ImdbMovie(
            tconst=f"tt{i:07d}",
            primary_title=f"Title {i}",
            original_title=f"Title {i}",
            is_adult=False,
            start_year=2000 + i,
            runtime_min=90,
            genres=["Drama"]
        )
        for i in range(count)
    }


class _FakeClient:
    """A stand-in TmdbClient that returns no matches and makes no HTTP calls."""

    def __init__(self) -> None:
        self.calls: List[List[str]] = []

    async def find_by_imdb_ids(self, imdb_ids: List[str]) -> list:
        """Records the requested chunk and returns no TMDb matches."""

        self.calls.append(list(imdb_ids))
        return []

    async def close(self) -> None:
        """No-op close, matching TmdbClient's interface."""


def test_enrich_to_shards_chunks_and_writes_all_records(tmp_path: Path):
    movies = _make_movies(5)
    client = _FakeClient()

    asyncio.run(enrich_to_shards(
        movies, ratings={}, principals={}, names={},
        output_dir=tmp_path, chunk_size=2, client=client
    ))

    shards = sorted(tmp_path.glob("movies_*.jsonl"))
    assert len(shards) == 3
    assert len(client.calls) == 3

    total_records = sum(len(s.read_text().splitlines()) for s in shards)
    assert total_records == 5

    first_record = json.loads(shards[0].read_text().splitlines()[0])
    assert first_record["tconst"] == "tt0000000"
    assert first_record["tmdb"] is None


def test_enrich_to_shards_resumes_by_skipping_existing_shards(tmp_path: Path):
    movies = _make_movies(4)
    first_client = _FakeClient()

    asyncio.run(enrich_to_shards(
        movies, ratings={}, principals={}, names={},
        output_dir=tmp_path, chunk_size=2, client=first_client
    ))
    assert len(first_client.calls) == 2

    second_client = _FakeClient()
    asyncio.run(enrich_to_shards(
        movies, ratings={}, principals={}, names={},
        output_dir=tmp_path, chunk_size=2, client=second_client
    ))

    assert not second_client.calls


def test_enrich_to_shards_leaves_no_temporary_files(tmp_path: Path):
    movies = _make_movies(2)

    asyncio.run(enrich_to_shards(
        movies, ratings={}, principals={}, names={},
        output_dir=tmp_path, chunk_size=2, client=_FakeClient()
    ))

    assert not list(tmp_path.glob("*.tmp"))
