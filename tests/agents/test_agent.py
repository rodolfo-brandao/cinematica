"""Unit tests for src.agents.agent (no real Claude, Neo4j or Ollama)."""

import asyncio
from typing import Any, Dict, List, Tuple

from src.agents import agent as agent_module


class _FakeCompiledGraph:
    """A stand-in compiled LangGraph replaying one canned `ainvoke` result."""

    def __init__(self, result: Dict[str, Any]) -> None:
        self._result = result
        self.calls: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []

    async def ainvoke(
        self, state: Dict[str, Any], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Records the initial state/config and replays the canned result."""

        self.calls.append((state, config))
        return self._result


def test_answer_question_invokes_the_graph_with_a_fresh_state(monkeypatch):
    """The graph is invoked with a full initial state and three clients."""

    fake_graph = _FakeCompiledGraph(result={"answer": "Two movies."})
    monkeypatch.setattr(agent_module, "_GRAPH", fake_graph)

    neo4j, anthropic, ollama = object(), object(), object()
    answer = asyncio.run(
        agent_module.answer_question("Which?", neo4j, anthropic, ollama)
    )

    assert answer == "Two movies."
    [(state, config)] = fake_graph.calls
    assert state == {
        "question": "Which?",
        "plan": "",
        "resolved": "",
        "rows": [],
        "query_notes": "",
        "verified": False,
        "verification_notes": "",
        "query_attempts": 0,
        "answer": ""
    }
    assert config == {"configurable": {
        "neo4j": neo4j, "anthropic": anthropic, "ollama": ollama
    }}


def test_answer_question_returns_the_graphs_final_answer(monkeypatch):
    """Whatever `answer` the graph settles on is returned as-is."""

    fake_graph = _FakeCompiledGraph(
        result={"answer": "I couldn't find a confident answer."}
    )
    monkeypatch.setattr(agent_module, "_GRAPH", fake_graph)

    answer = asyncio.run(
        agent_module.answer_question(
            "Anything?", object(), object(), object()
        )
    )

    assert answer == "I couldn't find a confident answer."
