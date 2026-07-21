"""Unit tests for src.pipeline.load (no real Neo4j instance)."""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.pipeline.load import load_movie_record, load_movies


class _FakeClient:
    """A stand-in Neo4jClient that records writes instead of executing them."""

    def __init__(self) -> None:
        self.calls: List[Tuple[str, Dict[str, Any]]] = []

    def execute_write(self, query: str, **parameters: Any) -> None:
        """Records the query and its parameters instead of running them."""

        self.calls.append((query, parameters))

    def close(self) -> None:
        """No-op close, matching Neo4jClient's interface."""


def _write_records(path: Path, records: List[Dict[str, Any]]) -> None:
    """Writes `records` as a JSONL file at `path`."""

    lines = (json.dumps(record) for record in records)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _make_record(tconst: str, **overrides: Any) -> Dict[str, Any]:
    """Builds a minimal, schema-shaped movie record with sane defaults."""

    record = {
        "tconst": tconst,
        "primary_title": "Title",
        "original_title": "Title",
        "is_adult": False,
        "start_year": 2000,
        "runtime_min": 90,
        "genres": ["Drama"],
        "rating": {"average_rating": 7.5, "num_votes": 100},
        "principals": [],
        "tmdb": None
    }
    record.update(overrides)
    return record


def _movie_upsert_calls(
    client: _FakeClient
) -> List[Tuple[str, Dict[str, Any]]]:
    """Filters `client.calls` down to `Movie` upsert queries."""

    return [(q, p) for q, p in client.calls if "MERGE (m:Movie" in q]


def _calls_matching(
    client: _FakeClient, fragment: str
) -> List[Tuple[str, Dict[str, Any]]]:
    """Filters `client.calls` down to queries containing `fragment`."""

    return [(q, p) for q, p in client.calls if fragment in q]


def test_load_movies_flattens_rating_and_tmdb_onto_movie(tmp_path: Path):
    """A movie with TMDb data gets its rating/TMDb fields flattened."""

    tmdb = {
        "tmdb_id": 42,
        "imdb_id": "tt0000001",
        "overview": "A film.",
        "tagline": "",
        "status": "Released",
        "budget": 1000,
        "revenue": 2000,
        "popularity": 1.2,
        "release_date": "2000-01-01",
        "original_language": "en",
        "vote_average": 7.0,
        "vote_count": 10,
        "has_video": False,
        "genres": [{"id": 18, "name": "Drama"}],
        "spoken_languages": [{"english_name": "English", "iso_639_1": "en", "name": "English"}],
        "origin_country": ["US"]
    }
    record = _make_record("tt0000001", tmdb=tmdb)
    input_path = tmp_path / "movies.jsonl"
    _write_records(input_path, [record])

    client = _FakeClient()
    count = load_movies(input_path, client=client, batch_size=10)

    assert count == 1
    [(_, params)] = _movie_upsert_calls(client)
    [row] = params["rows"]
    assert row["tconst"] == "tt0000001"
    assert row["average_rating"] == 7.5
    assert row["num_votes"] == 100
    assert row["tmdb_id"] == 42
    # Languages and countries are now first-class nodes, not Movie props.
    assert "spoken_languages" not in row
    assert "origin_countries" not in row

    [(_, language_params)] = _calls_matching(client, "MERGE (l:Language")
    assert language_params["rows"] == [
        {"tconst": "tt0000001", "name": "English"}
    ]
    [(_, country_params)] = _calls_matching(client, "MERGE (c:Country")
    assert country_params["rows"] == [{"tconst": "tt0000001", "code": "US"}]


def test_load_movies_handles_missing_rating_and_tmdb(tmp_path: Path):
    """A movie with no rating/TMDb match still gets a Movie row (all null)."""

    input_path = tmp_path / "movies.jsonl"
    _write_records(input_path, [_make_record("tt0000002", rating=None)])

    client = _FakeClient()
    load_movies(input_path, client=client, batch_size=10)

    [(_, params)] = _movie_upsert_calls(client)
    [row] = params["rows"]
    assert row["average_rating"] is None
    assert row["tmdb_id"] is None
    # No TMDb data means no language/country dimension writes at all.
    assert not _calls_matching(client, "MERGE (l:Language")
    assert not _calls_matching(client, "MERGE (c:Country")


def test_load_movies_maps_tmdb_dimensions_to_nodes(tmp_path: Path):
    """Companies, keywords and the collection become linked nodes."""

    tmdb = {
        "production_companies": [
            {"id": 7, "name": "Zoetrope", "origin_country": "US"}
        ],
        "keywords": [{"id": 1, "name": "mafia"}, {"id": 2, "name": "family"}],
        "belongs_to_collection": {"id": 230, "name": "The Godfather Collection"}
    }
    record = _make_record("tt0000005", tmdb=tmdb)
    input_path = tmp_path / "movies.jsonl"
    _write_records(input_path, [record])

    client = _FakeClient()
    load_movies(input_path, client=client, batch_size=10)

    [(_, company_params)] = _calls_matching(client, "MERGE (pc:ProductionCompany")
    assert company_params["rows"] == [
        {"tconst": "tt0000005", "tmdb_id": 7, "name": "Zoetrope"}
    ]

    [(_, keyword_params)] = _calls_matching(client, "MERGE (k:Keyword")
    assert {row["name"] for row in keyword_params["rows"]} == {"mafia", "family"}

    [(_, collection_params)] = _calls_matching(client, "MERGE (col:Collection")
    assert collection_params["rows"] == [
        {"tconst": "tt0000005", "tmdb_id": 230,
         "name": "The Godfather Collection"}
    ]

    # The company's origin country is folded into the Country dimension.
    [(_, country_params)] = _calls_matching(client, "MERGE (c:Country")
    assert country_params["rows"] == [{"tconst": "tt0000005", "code": "US"}]


def test_load_movies_merges_and_deduplicates_genres(tmp_path: Path):
    """IMDb and TMDb genres are combined into one deduplicated set."""

    record = _make_record(
        "tt0000003",
        genres=["Drama", "Romance"],
        tmdb={"genres": [{"id": 18, "name": "Drama"}, {"id": 35, "name": "Comedy"}]}
    )
    input_path = tmp_path / "movies.jsonl"
    _write_records(input_path, [record])

    client = _FakeClient()
    load_movies(input_path, client=client, batch_size=10)

    [(_, params)] = [
        (q, p) for q, p in client.calls if "MERGE (g:Genre" in q
    ]
    names = {row["name"] for row in params["rows"]}
    assert names == {"Drama", "Romance", "Comedy"}


def test_load_movies_maps_principal_categories_to_relationship_types(
    tmp_path: Path
):
    """Known IMDb categories map to their documented relationship type."""

    record = _make_record("tt0000004", principals=[
        {
            "nconst": "nm001", "ordering": 1, "category": "actor",
            "job": None, "characters": ["Hero"],
            "person": {
                "primary_name": "Actor One", "birth_year": 1970,
                "death_year": None, "primary_profession": ["actor"]
            }
        },
        {
            "nconst": "nm002", "ordering": 2, "category": "director",
            "job": None, "characters": [],
            "person": {
                "primary_name": "Director One", "birth_year": 1960,
                "death_year": None, "primary_profession": ["director"]
            }
        },
        {
            "nconst": "nm003", "ordering": 3, "category": "puppeteer",
            "job": "Puppets", "characters": [],
            "person": None
        }
    ])
    input_path = tmp_path / "movies.jsonl"
    _write_records(input_path, [record])

    client = _FakeClient()
    load_movies(input_path, client=client, batch_size=10)

    relationship_queries = {
        q for q, _ in client.calls if "MERGE (p:Person" in q
    }
    assert any("ACTED_IN" in q for q in relationship_queries)
    assert any("DIRECTED" in q for q in relationship_queries)
    assert any("WORKED_ON" in q for q in relationship_queries)

    [(_, fallback_params)] = [
        (q, p) for q, p in client.calls if "WORKED_ON" in q
    ]
    [fallback_row] = fallback_params["rows"]
    assert fallback_row["nconst"] == "nm003"
    assert fallback_row["rel"]["category"] == "puppeteer"
    assert fallback_row["person"]["primary_name"] is None


def test_load_movies_splits_batches_at_batch_size(tmp_path: Path):
    """Movie upserts are split into one batch per `batch_size` records."""

    records = [_make_record(f"tt{i:07d}") for i in range(5)]
    input_path = tmp_path / "movies.jsonl"
    _write_records(input_path, records)

    client = _FakeClient()
    count = load_movies(input_path, client=client, batch_size=2)

    assert count == 5
    upsert_calls = _movie_upsert_calls(client)
    assert len(upsert_calls) == 3
    assert [len(params["rows"]) for _, params in upsert_calls] == [2, 2, 1]


def test_load_movie_record_upserts_a_single_record():
    """`load_movie_record` runs the same batch path as `load_movies`."""

    client = _FakeClient()
    record = _make_record("tt0000009", principals=[])

    load_movie_record(record, client)

    [(_, params)] = _movie_upsert_calls(client)
    [row] = params["rows"]
    assert row["tconst"] == "tt0000009"
    # An empty `principals` list writes no relationship-merge queries.
    assert not _calls_matching(client, "MERGE (p:Person")
