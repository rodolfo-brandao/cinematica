"""Unit tests for src.api.app (no real Neo4j or Ollama instance)."""

from typing import Any, Iterator

import pytest
from fastapi.testclient import TestClient

import src.api.app as app_module


class _FakeNeo4jClient:
    """A stand-in Neo4jClient requiring no real connection."""

    def close(self) -> None:
        """No-op close, matching Neo4jClient's interface."""


class _FakeAnthropicClient:
    """A stand-in AnthropicClient requiring no real credentials."""

    async def close(self) -> None:
        """No-op close, matching AnthropicClient's interface."""


class _FakeOllamaClient:
    """A stand-in OllamaClient requiring no real connection."""

    async def close(self) -> None:
        """No-op close, matching OllamaClient's interface."""


async def _fake_answer_question(question: str, **_: Any) -> str:
    """A stand-in answer_question that echoes the question back."""

    return f"Answer to: {question}"


@pytest.fixture(name="client")
def _client_fixture(
    monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    """A TestClient wired to fake Neo4j/Ollama clients and a stub agent."""

    monkeypatch.setattr(app_module, "Neo4jClient", _FakeNeo4jClient)
    monkeypatch.setattr(
        app_module, "AnthropicClient", _FakeAnthropicClient
    )
    monkeypatch.setattr(app_module, "OllamaClient", _FakeOllamaClient)
    monkeypatch.setattr(
        app_module, "answer_question", _fake_answer_question
    )

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_query_endpoint_returns_the_agents_answer(client: TestClient):
    """The route wires the request question to the agent's answer."""

    response = client.post(
        "/query", json={"question": "Who directed Inception?"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "question": "Who directed Inception?",
        "answer": "Answer to: Who directed Inception?"
    }
