"""Unit tests for src.agents.graph (no real Claude, Neo4j or Ollama)."""

import asyncio
from types import SimpleNamespace
from typing import Any, Dict, List

import src.agents.tools as tools_module
from src.agents.graph import (
    _FALLBACK_ANSWER,
    _MAX_QUERY_ATTEMPTS,
    _dispatch_tool,
    _rows_from,
    build_graph
)
from src.agents.state import AgentState


def _text(content: str) -> SimpleNamespace:
    """Builds a text content block."""
    return SimpleNamespace(type="text", text=content)


def _tool_use(name: str, tool_input: Dict[str, Any]) -> SimpleNamespace:
    """Builds a tool_use content block."""
    return SimpleNamespace(
        type="tool_use", id="tool-1", name=name, input=tool_input
    )


def _reply(*blocks: SimpleNamespace) -> SimpleNamespace:
    """Builds a scripted assistant message, inferring the stop reason."""

    uses_tool = any(b.type == "tool_use" for b in blocks)
    return SimpleNamespace(
        content=list(blocks),
        stop_reason="tool_use" if uses_tool else "end_turn"
    )


class _FakeAnthropicClient:
    """A stand-in AnthropicClient replaying scripted messages in order."""

    def __init__(self, responses: List[SimpleNamespace]) -> None:
        self._responses = iter(responses)
        self.calls = 0

    async def complete(
        self, system: str, messages: List[Dict[str, Any]], tools=None
    ) -> SimpleNamespace:
        """Records the call count and replays the next scripted message."""

        self.calls += 1
        return next(self._responses)


class _FakeNeo4jClient:
    """A stand-in Neo4jClient returning canned rows for every read."""

    def __init__(self, rows: List[Dict[str, Any]]) -> None:
        self._rows = rows

    def execute_read(
        self, query: str, **parameters: Any
    ) -> List[Dict[str, Any]]:
        """Returns the canned rows for any query."""
        return self._rows


class _FakeOllamaClient:
    """A stand-in OllamaClient returning a fixed embedding."""

    async def embed(self, text: str) -> List[float]:
        """Returns a canned embedding."""
        return [0.0, 0.0]


def _initial_state(question: str) -> AgentState:
    """Builds a fresh initial state, mirroring `agent.answer_question`."""

    return {
        "question": question,
        "plan": "",
        "resolved": "",
        "rows": [],
        "query_notes": "",
        "verified": False,
        "verification_notes": "",
        "query_attempts": 0,
        "answer": ""
    }


def _run(anthropic, neo4j, ollama, question: str) -> AgentState:
    """Invokes a freshly compiled graph with the given fakes."""

    return asyncio.run(build_graph().ainvoke(
        _initial_state(question),
        config={"configurable": {
            "anthropic": anthropic, "neo4j": neo4j, "ollama": ollama,
            "tmdb": object()
        }}
    ))


def test_full_pipeline_happy_path():
    """A clean run flows plan→resolve→query→verify→compose to an answer."""

    anthropic = _FakeAnthropicClient(responses=[
        _reply(_text("Plan: multi-hop; resolve Coppola.")),   # plan
        _reply(_text("Resolved: Coppola = nm0000338.")),      # resolve
        _reply(_tool_use("run_cypher", {"query": "MATCH ..."})),  # query 1
        _reply(_text("Found 2 movies.")),                     # query 2
        _reply(_text("VERIFIED")),                            # verify
        _reply(_text("The Godfather and Part II."))           # compose
    ])
    neo4j = _FakeNeo4jClient(rows=[{"title": "The Godfather"}])

    result = _run(anthropic, neo4j, _FakeOllamaClient(), "Coppola's best?")

    assert result["answer"] == "The Godfather and Part II."
    assert result["rows"] == [{"title": "The Godfather"}]
    assert result["verified"] is True


def test_empty_result_is_rejected_and_falls_back():
    """Rows that stay empty fail the deterministic guard until fallback."""

    # plan + resolve, then each of _MAX_QUERY_ATTEMPTS query passes runs
    # one tool call (returning nothing) plus a text turn. Verify is
    # deterministic on empty rows, so it spends no scripted message.
    responses = [
        _reply(_text("Plan.")),
        _reply(_text("Resolved: none found."))
    ]
    for _ in range(_MAX_QUERY_ATTEMPTS):
        responses.append(_reply(_tool_use("run_cypher", {"query": "MATCH"})))
        responses.append(_reply(_text("No rows.")))

    anthropic = _FakeAnthropicClient(responses=responses)
    neo4j = _FakeNeo4jClient(rows=[])

    result = _run(anthropic, neo4j, _FakeOllamaClient(), "Movies by nobody?")

    assert result["answer"] == _FALLBACK_ANSWER
    assert result["query_attempts"] == _MAX_QUERY_ATTEMPTS
    assert result["verified"] is False


def test_verification_rejection_then_success():
    """A rejected result retries the query stage, then composes an answer."""

    anthropic = _FakeAnthropicClient(responses=[
        _reply(_text("Plan.")),                               # plan
        _reply(_text("Resolved.")),                           # resolve
        _reply(_tool_use("run_cypher", {"query": "MATCH a"})),  # query 1
        _reply(_text("Some rows.")),
        _reply(_text("REJECTED: ignores the director.")),     # verify 1
        _reply(_tool_use("run_cypher", {"query": "MATCH b"})),  # query 2
        _reply(_text("Better rows.")),
        _reply(_text("VERIFIED")),                            # verify 2
        _reply(_text("Here is the corrected answer."))        # compose
    ])
    neo4j = _FakeNeo4jClient(rows=[{"title": "A"}])

    result = _run(anthropic, neo4j, _FakeOllamaClient(), "Which movies?")

    assert result["answer"] == "Here is the corrected answer."
    assert result["query_attempts"] == 2


def test_dispatch_tool_routes_the_tmdb_backed_tools_by_name(monkeypatch):
    """Each new tool name is routed to its `tools` module counterpart."""

    calls: List[Any] = []

    async def _fake_search(tmdb, **kwargs):
        calls.append(("search_external_movie", tmdb, kwargs))
        return {"candidates": []}

    async def _fake_ingest(tmdb, neo4j, **kwargs):
        calls.append(("ingest_movie", tmdb, neo4j, kwargs))
        return {"message": "ingested"}

    async def _fake_fetch(tmdb, **kwargs):
        calls.append(("fetch_reviews", tmdb, kwargs))
        return {"reviews": []}

    async def _fake_save(tmdb, neo4j, **kwargs):
        calls.append(("save_movie_sentiment", tmdb, neo4j, kwargs))
        return {"sentiment_label": "positive"}

    monkeypatch.setattr(
        tools_module, "search_external_movie", _fake_search
    )
    monkeypatch.setattr(tools_module, "ingest_movie", _fake_ingest)
    monkeypatch.setattr(tools_module, "fetch_reviews", _fake_fetch)
    monkeypatch.setattr(
        tools_module, "save_movie_sentiment", _fake_save
    )

    neo4j, ollama, tmdb = object(), object(), object()

    search_result = asyncio.run(_dispatch_tool(
        "search_external_movie", {"title": "Dune"}, neo4j, ollama, tmdb
    ))
    ingest_result = asyncio.run(_dispatch_tool(
        "ingest_movie", {"tmdb_id": 1}, neo4j, ollama, tmdb
    ))
    fetch_result = asyncio.run(_dispatch_tool(
        "fetch_reviews", {"tmdb_id": 1}, neo4j, ollama, tmdb
    ))
    save_result = asyncio.run(_dispatch_tool(
        "save_movie_sentiment",
        {
            "tmdb_id": 1, "sentiment_label": "positive",
            "sentiment_score": 0.5, "summary": "Mostly positive."
        },
        neo4j, ollama, tmdb
    ))

    assert search_result == {"candidates": []}
    assert ingest_result == {"message": "ingested"}
    assert fetch_result == {"reviews": []}
    assert save_result == {"sentiment_label": "positive"}
    assert [call[0] for call in calls] == [
        "search_external_movie", "ingest_movie", "fetch_reviews",
        "save_movie_sentiment"
    ]
    assert all(call[1] is tmdb for call in calls)


def test_rows_from_ignores_candidates_and_reviews_keys():
    """
    Search/review tool output must never be promoted into answer rows —
    only a real `run_cypher` result should ever populate `AgentState["rows"]`.
    """

    assert _rows_from({"candidates": [{"tmdb_id": 1}]}) == []
    assert _rows_from({"reviews": [{"review_id": "r1"}]}) == []
    assert _rows_from({"rows": [{"tconst": "tt1"}]}) == [{"tconst": "tt1"}]
