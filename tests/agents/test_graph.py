"""Unit tests for src.agents.graph (no real Claude, Neo4j or Ollama)."""

import asyncio
from types import SimpleNamespace
from typing import Any, Dict, List

from src.agents.graph import _FALLBACK_ANSWER, _MAX_QUERY_ATTEMPTS, build_graph
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
            "anthropic": anthropic, "neo4j": neo4j, "ollama": ollama
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
