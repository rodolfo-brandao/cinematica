"""Frozen dataclasses modeling the `/query` request and response bodies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryRequest:
    """A natural-language question submitted to the agent."""
    question: str


@dataclass(frozen=True)
class QueryResponse:
    """The agent's synthesized answer to a submitted question."""
    question: str
    answer: str
