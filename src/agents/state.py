"""Shared state schema threaded through the agent's LangGraph pipeline."""

from typing import Any, Dict, List, TypedDict


class AgentState(TypedDict):
    """
    The working state passed between LangGraph nodes while answering one
    question. The `Neo4jClient`/`AnthropicClient`/`OllamaClient`
    dependencies are not part of this state; they're injected
    per-invocation via LangGraph's `RunnableConfig` instead.

    :param question: The original natural-language question.
    :type question: str
    :param plan: The strategy produced by `plan`: which entities to
        resolve and whether semantic search is needed.
    :type plan: str
    :param resolved: A summary of the canonical entities resolved by
        `resolve`, fed into the query stage.
    :type resolved: str
    :param rows: The most recent data rows gathered by `query`.
    :type rows: List[Dict[str, Any]]
    :param query_notes: The query stage's own account of what it ran and
        found, used by `verify`.
    :type query_notes: str
    :param verified: Whether `verify` judged `rows` to actually answer
        `question`.
    :type verified: bool
    :param verification_notes: The verifier's reasoning, especially when
        rejecting a result; fed back into a query retry.
    :type verification_notes: str
    :param query_attempts: Number of `query` passes made so far.
    :type query_attempts: int
    :param answer: The final synthesized answer.
    :type answer: str
    """

    question: str
    plan: str
    resolved: str
    rows: List[Dict[str, Any]]
    query_notes: str
    verified: bool
    verification_notes: str
    query_attempts: int
    answer: str
