"""Unit tests for src.agents.tools (no real Neo4j or Ollama instance)."""

import asyncio
from typing import Any, Dict, List, Tuple, Union

from neo4j.exceptions import Neo4jError

from src.agents.tools import (
    _MAX_ROWS,
    get_schema,
    resolve_entity,
    run_cypher,
    vector_search,
)


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
