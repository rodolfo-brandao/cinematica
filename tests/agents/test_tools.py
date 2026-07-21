"""Unit tests for src.agents.tools (no real Neo4j, Ollama or TMDb)."""

import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union

from neo4j.exceptions import Neo4jError

from src.agents.tools import (
    _MAX_REVIEW_CONTENT_CHARS,
    _MAX_REVIEWS,
    _MAX_ROWS,
    _MAX_SEARCH_RESULTS,
    fetch_reviews,
    get_schema,
    ingest_movie,
    resolve_entity,
    run_cypher,
    save_movie_sentiment,
    search_external_movie,
    vector_search,
)
from src.models.tmdb import Genre, TmdbMovie, TmdbReview, TmdbSearchResult


class _FakeNeo4jClient:
    """A stand-in Neo4jClient replaying scripted `execute_read` outcomes."""

    def __init__(
        self, outcomes: Union[List[Dict[str, Any]], Exception]
    ) -> None:
        self._outcomes = outcomes
        self.calls: List[Tuple[str, Dict[str, Any]]] = []

    def execute_read(
        self, query: str, **parameters: Any
    ) -> List[Dict[str, Any]]:
        """Records the query/params and returns (or raises) the outcome."""

        self.calls.append((query, parameters))

        if isinstance(self._outcomes, Exception):
            raise self._outcomes

        return self._outcomes


class _FakeOllamaClient:
    """A stand-in OllamaClient returning a fixed embedding."""

    def __init__(self) -> None:
        self.embedded: List[str] = []

    async def embed(self, text: str) -> List[float]:
        """Records the text and returns a canned embedding."""

        self.embedded.append(text)
        return [0.1, 0.2, 0.3]


class _FakeWritableNeo4jClient:
    """A stand-in Neo4jClient recording both reads and writes."""

    def __init__(self, read_outcomes: List[Dict[str, Any]]) -> None:
        self._read_outcomes = read_outcomes
        self.read_calls: List[Tuple[str, Dict[str, Any]]] = []
        self.write_calls: List[Tuple[str, Dict[str, Any]]] = []

    def execute_read(
        self, query: str, **parameters: Any
    ) -> List[Dict[str, Any]]:
        """Records the query/params and returns the canned outcome."""

        self.read_calls.append((query, parameters))
        return self._read_outcomes

    def execute_write(self, query: str, **parameters: Any) -> None:
        """Records the query/params instead of running them."""

        self.write_calls.append((query, parameters))


class _FakeTmdbClient:
    """A stand-in TmdbClient replaying scripted search/details/reviews."""

    def __init__(
        self,
        search_results: Optional[List[TmdbSearchResult]] = None,
        movie_details: Optional[TmdbMovie] = None,
        reviews: Optional[List[TmdbReview]] = None
    ) -> None:
        self._search_results = search_results or []
        self._movie_details = movie_details
        self._reviews = reviews or []
        self.search_calls: List[Tuple[str, Optional[int]]] = []
        self.details_calls: List[int] = []
        self.reviews_calls: List[int] = []

    async def search_movies(
        self, query: str, year: Optional[int] = None
    ) -> List[TmdbSearchResult]:
        """Records the query/year and returns the canned candidates."""

        self.search_calls.append((query, year))
        return self._search_results

    async def get_movie_details(self, tmdb_id: int) -> TmdbMovie:
        """Records the id and returns the canned movie details."""

        self.details_calls.append(tmdb_id)
        return self._movie_details

    async def get_reviews(self, tmdb_id: int) -> List[TmdbReview]:
        """Records the id and returns the canned reviews."""

        self.reviews_calls.append(tmdb_id)
        return self._reviews


def _make_tmdb_movie(**overrides: Any) -> TmdbMovie:
    """Builds a minimal TMDb movie fixture for the ingestion tests."""

    fields: Dict[str, Any] = {
        "tmdb_id": 550,
        "imdb_id": "tt0137523",
        "is_adult": False,
        "budget": 0,
        "genres": [Genre(id=18, name="Drama")],
        "origin_country": ["US"],
        "original_language": "en",
        "original_title": "Fight Club",
        "overview": "An insomniac office worker...",
        "popularity": 50.0,
        "release_date": "1999-10-15",
        "revenue": 0,
        "runtime_min": 139,
        "spoken_languages": [],
        "status": "Released",
        "tagline": "",
        "title": "Fight Club",
        "has_video": False,
        "vote_average": 8.4,
        "vote_count": 25_000,
        "production_companies": [],
        "belongs_to_collection": None,
        "keywords": []
    }
    fields.update(overrides)
    return TmdbMovie(**fields)


def test_get_schema_returns_the_description():
    """`get_schema` surfaces the graph schema prompt."""

    assert "Node labels and properties" in get_schema()


def test_resolve_entity_queries_fulltext_and_escapes_lucene():
    """A person name is Lucene-escaped and run against the person index."""

    client = _FakeNeo4jClient(outcomes=[{"id": "nm1", "name": "Coppola"}])
    result = resolve_entity(client, name="Coppola (Sr.)", label="Person")

    assert result == [{"id": "nm1", "name": "Coppola"}]
    [(query, params)] = client.calls
    assert "person_name_ft" in query
    assert params["name"] == r"Coppola \(Sr.\)"
    assert params["limit"] == 5


def test_resolve_entity_returns_empty_for_unknown_label():
    """An unsupported label short-circuits without touching the database."""

    client = _FakeNeo4jClient(outcomes=[])
    assert resolve_entity(client, name="X", label="Genre") == []
    assert not client.calls


def test_run_cypher_explains_then_executes_and_caps_rows():
    """A valid query is EXPLAIN-validated, run, and its rows are capped."""

    rows = [{"n": i} for i in range(_MAX_ROWS + 10)]
    client = _FakeNeo4jClient(outcomes=rows)

    result = run_cypher(client, "MATCH (m:Movie) RETURN m LIMIT 500")

    assert len(result["rows"]) == _MAX_ROWS
    explain_query, _ = client.calls[0]
    assert explain_query.startswith("EXPLAIN ")


def test_run_cypher_rejects_write_query_without_touching_db():
    """A write clause is rejected by the denylist before any DB call."""

    client = _FakeNeo4jClient(outcomes=[])
    result = run_cypher(client, "MATCH (m:Movie) DETACH DELETE m")

    assert "error" in result
    assert not client.calls


def test_run_cypher_returns_error_on_neo4j_failure():
    """A Neo4j error is returned as a structured error, not raised."""

    client = _FakeNeo4jClient(outcomes=Neo4jError("bad query"))
    result = run_cypher(client, "MATCH (m:Movie) RETURN m LIMIT 1")

    assert "error" in result
    assert "bad query" in result["error"]


def test_vector_search_embeds_then_queries_the_index():
    """The text is embedded and passed to the vector index query."""

    client = _FakeNeo4jClient(outcomes=[{"tconst": "tt1", "title": "A"}])
    ollama = _FakeOllamaClient()

    result = asyncio.run(
        vector_search(client, ollama, text="isolation and memory", k=3)
    )

    assert result == [{"tconst": "tt1", "title": "A"}]
    assert ollama.embedded == ["isolation and memory"]
    [(query, params)] = client.calls
    assert "db.index.vector.queryNodes" in query
    assert params == {"k": 3, "embedding": [0.1, 0.2, 0.3]}


def test_search_external_movie_returns_candidates_capped():
    """Search results are capped and returned under a `candidates` key."""

    results = [
        TmdbSearchResult(
            tmdb_id=i, title=f"Movie {i}", original_title=f"Movie {i}",
            release_date="2020-01-01", overview="...", popularity=1.0
        )
        for i in range(_MAX_SEARCH_RESULTS + 3)
    ]
    tmdb = _FakeTmdbClient(search_results=results)

    result = asyncio.run(
        search_external_movie(tmdb, title="Dune", year=2021)
    )

    assert len(result["candidates"]) == _MAX_SEARCH_RESULTS
    assert tmdb.search_calls == [("Dune", 2021)]


def test_ingest_movie_is_a_noop_when_already_in_the_graph():
    """An existing `tmdb_id` short-circuits before any TMDb/write call."""

    neo4j = _FakeWritableNeo4jClient(read_outcomes=[{"tconst": "tt1"}])
    tmdb = _FakeTmdbClient()

    result = asyncio.run(ingest_movie(tmdb, neo4j, tmdb_id=1))

    assert result == {
        "tconst": "tt1", "message": "Movie is already in the graph."
    }
    assert not tmdb.details_calls
    assert not neo4j.write_calls


def test_ingest_movie_writes_a_new_movie_record():
    """A movie absent from the graph is fetched and merged in."""

    neo4j = _FakeWritableNeo4jClient(read_outcomes=[])
    tmdb = _FakeTmdbClient(movie_details=_make_tmdb_movie())

    result = asyncio.run(ingest_movie(tmdb, neo4j, tmdb_id=550))

    assert result == {
        "tconst": "tt0137523",
        "primary_title": "Fight Club",
        "message": "Movie ingested into the graph."
    }
    assert tmdb.details_calls == [550]
    [(_, movie_params)] = [
        (q, p) for q, p in neo4j.write_calls if "MERGE (m:Movie" in q
    ]
    [row] = movie_params["rows"]
    assert row["tconst"] == "tt0137523"


def test_ingest_movie_rejects_a_movie_with_no_imdb_id():
    """A TMDb movie with no linked IMDb id is refused, not silently merged."""

    neo4j = _FakeWritableNeo4jClient(read_outcomes=[])
    tmdb = _FakeTmdbClient(movie_details=_make_tmdb_movie(imdb_id=""))

    result = asyncio.run(ingest_movie(tmdb, neo4j, tmdb_id=550))

    assert "error" in result
    assert not neo4j.write_calls


def test_fetch_reviews_caps_count_and_truncates_content():
    """Reviews are capped in count and each has its content truncated."""

    reviews = [
        TmdbReview(
            review_id=str(i), author="A", content="x" * 5000,
            tmdb_rating=8.0, created_at="2020-01-01", url="http://x"
        )
        for i in range(_MAX_REVIEWS + 5)
    ]
    tmdb = _FakeTmdbClient(reviews=reviews)

    result = asyncio.run(fetch_reviews(tmdb, tmdb_id=1))

    assert len(result["reviews"]) == _MAX_REVIEWS
    assert all(
        len(review["content"]) <= _MAX_REVIEW_CONTENT_CHARS
        for review in result["reviews"]
    )


def test_save_movie_sentiment_errors_when_movie_not_ingested():
    """A `tmdb_id` absent from the graph is refused before any TMDb call."""

    neo4j = _FakeWritableNeo4jClient(read_outcomes=[])
    tmdb = _FakeTmdbClient()

    result = asyncio.run(save_movie_sentiment(
        tmdb, neo4j, tmdb_id=1, sentiment_label="positive",
        sentiment_score=0.8, summary="Well received."
    ))

    assert "error" in result
    assert not tmdb.reviews_calls
    assert not neo4j.write_calls


def test_save_movie_sentiment_persists_reviews_and_aggregate():
    """Reviews are merged and the aggregate judgment is set on the movie."""

    neo4j = _FakeWritableNeo4jClient(read_outcomes=[{"tconst": "tt1"}])
    reviews = [
        TmdbReview(
            review_id="r1", author="A", content="Great film.",
            tmdb_rating=9.0, created_at="2020-01-01", url="http://x"
        )
    ]
    tmdb = _FakeTmdbClient(reviews=reviews)

    result = asyncio.run(save_movie_sentiment(
        tmdb, neo4j, tmdb_id=1, sentiment_label="positive",
        sentiment_score=0.8, summary="Well received."
    ))

    assert result == {
        "tconst": "tt1", "reviews_saved": 1,
        "sentiment_label": "positive", "sentiment_score": 0.8
    }
    [(_, review_params)] = [
        (q, p) for q, p in neo4j.write_calls if "MERGE (r:Review" in q
    ]
    assert review_params["rows"] == [{
        "review_id": "r1", "author": "A", "content": "Great film.",
        "tmdb_rating": 9.0, "created_at": "2020-01-01", "url": "http://x"
    }]
    [(_, sentiment_params)] = [
        (q, p) for q, p in neo4j.write_calls
        if "audience_sentiment_label" in q
    ]
    assert sentiment_params == {
        "tmdb_id": 1, "label": "positive", "score": 0.8,
        "summary": "Well received."
    }
