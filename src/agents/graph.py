"""LangGraph pipeline answering questions over the film graph with Claude."""

import json
from typing import Any, Dict, List, Tuple

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.agents import tools as tool_module
from src.agents.state import AgentState
from src.logger import get_logger


_MAX_QUERY_ATTEMPTS = 3
_MAX_TOOL_ITERATIONS = 8

_FALLBACK_ANSWER = (
    "I couldn't find a confident answer to that question in the "
    "film knowledge graph."
)

_PLAN_SYSTEM_PROMPT = (
    "You are the planning stage of Cinematica, an assistant answering "
    "questions over a film knowledge graph. Classify the question as "
    "multi-hop (graph traversal), analytical (aggregation/ranking), "
    "thematic (semantic/plot-based), or a hybrid, and list the specific "
    "people and movies named that will need resolving to canonical graph "
    "nodes. Reply with a short plan. Do not answer the question."
)
_RESOLVE_SYSTEM_PROMPT = (
    "You are the entity-resolution stage of Cinematica. Using the "
    "`resolve_entity` tool, resolve every person and movie named in the "
    "question to its canonical graph node, and report each one's id "
    "(nconst/tconst) alongside its name. If a name is ambiguous, say so. "
    "Do not attempt to answer the question itself."
)
_QUERY_SYSTEM_PROMPT = (
    "You are the querying stage of Cinematica, running against Neo4j. "
    "Gather exactly the rows needed to answer the question, using the "
    "tools: call `get_schema` before writing Cypher, prefer the resolved "
    "entity ids you were given, use `run_cypher` for structured filters "
    "and traversals (react to its errors and fix them), and "
    "`vector_search` for thematic/plot questions. When you have the rows "
    "that answer the question, stop and briefly state what you found.\n\n"
    + tool_module.GRAPH_SCHEMA_DESCRIPTION
)
_VERIFY_SYSTEM_PROMPT = (
    "You are the verification stage of Cinematica. Given a question and "
    "the rows gathered for it, judge whether those rows actually satisfy "
    "every constraint in the question, not just some of them. A result "
    "that silently drops a constraint (ignores a named person, a "
    "relationship, a year, or a rating threshold the question asked for) "
    "must be rejected. A constraint can be satisfied by a node-property "
    "filter inside a MATCH pattern, so do not reject a query merely for "
    "lacking a WHERE clause if the pattern already encodes the "
    "constraint. Reply with a single line: \"VERIFIED\" if the rows "
    "fully satisfy the question, or \"REJECTED: <reason>\" otherwise."
)
_COMPOSE_SYSTEM_PROMPT = (
    "You are the answer-composition stage of Cinematica. Given a "
    "question and the rows retrieved for it, write a clear, "
    "natural-language answer using only facts present in the rows. Never "
    "state a fact, name or relationship that isn't in the rows."
)

_logger = get_logger(__name__)


async def plan(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    """Classifies the question and names the entities to resolve."""

    anthropic = config["configurable"]["anthropic"]
    message = await anthropic.complete(
        _PLAN_SYSTEM_PROMPT,
        [{"role": "user", "content": f"Question: {state['question']}"}]
    )
    return {"plan": _message_text(message)}


async def resolve(
    state: AgentState, config: RunnableConfig
) -> Dict[str, Any]:
    """Resolves named entities to canonical graph nodes via full-text."""

    text, _ = await _run_tool_loop(
        config,
        _RESOLVE_SYSTEM_PROMPT,
        f"Question: {state['question']}\n\nPlan: {state['plan']}",
        [_schema_for("resolve_entity")]
    )
    return {"resolved": text}


async def query(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    """Gathers the rows that answer the question via a bounded tool loop."""

    text, rows = await _run_tool_loop(
        config,
        _QUERY_SYSTEM_PROMPT,
        _query_user_prompt(state),
        tool_module.TOOL_SCHEMAS
    )
    return {
        "rows": rows,
        "query_notes": text,
        "query_attempts": state["query_attempts"] + 1
    }


async def verify(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    """Judges whether the gathered rows actually satisfy the question."""

    # Deterministic guard: an empty result can never satisfy a question
    # that asked for movies/people, so it is rejected without spending an
    # LLM call — this alone catches the "silently returned nothing" case.
    if not state["rows"]:
        return {
            "verified": False,
            "verification_notes": "REJECTED: the query returned no rows."
        }

    anthropic = config["configurable"]["anthropic"]
    message = await anthropic.complete(
        _VERIFY_SYSTEM_PROMPT,
        [{"role": "user", "content": _verify_user_prompt(state)}]
    )
    content = _message_text(message)
    return {
        "verified": content.strip().upper().startswith("VERIFIED"),
        "verification_notes": content
    }


async def compose(
    state: AgentState, config: RunnableConfig
) -> Dict[str, Any]:
    """Writes the final answer strictly from the verified rows."""

    anthropic = config["configurable"]["anthropic"]
    message = await anthropic.complete(
        _COMPOSE_SYSTEM_PROMPT,
        [{"role": "user", "content": _compose_user_prompt(state)}]
    )
    return {"answer": _message_text(message)}


def fallback(_state: AgentState) -> Dict[str, Any]:
    """Sets the canonical answer once the retry budget is exhausted."""
    return {"answer": _FALLBACK_ANSWER}


def build_graph() -> CompiledStateGraph:
    """
    Wires the plan/resolve/query/verify/compose nodes into a compiled
    LangGraph pipeline.

    :return: The compiled state graph.
    :rtype: CompiledStateGraph
    """

    graph = StateGraph(AgentState)
    graph.add_node("plan", plan)
    graph.add_node("resolve", resolve)
    graph.add_node("query", query)
    graph.add_node("verify", verify)
    graph.add_node("compose", compose)
    graph.add_node("fallback", fallback)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "resolve")
    graph.add_edge("resolve", "query")
    graph.add_edge("query", "verify")
    graph.add_conditional_edges(
        "verify",
        _route_after_verify,
        {
            "query": "query",
            "compose": "compose",
            "fallback": "fallback"
        }
    )
    graph.add_edge("compose", END)
    graph.add_edge("fallback", END)

    return graph.compile()


# Private helpers (module-level):
async def _run_tool_loop(
    config: RunnableConfig,
    system: str,
    user: str,
    tools: List[Dict[str, Any]]
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Runs a bounded Claude tool-use loop, dispatching each requested tool
    against the graph clients until the model stops calling tools (or the
    iteration budget is hit). Returns the model's final text and the most
    recent non-empty rows any data tool returned.
    """

    anthropic = config["configurable"]["anthropic"]
    neo4j = config["configurable"]["neo4j"]
    ollama = config["configurable"]["ollama"]

    messages: List[Dict[str, Any]] = [{"role": "user", "content": user}]
    rows: List[Dict[str, Any]] = []

    for _ in range(_MAX_TOOL_ITERATIONS):
        message = await anthropic.complete(system, messages, tools=tools)

        if message.stop_reason != "tool_use":
            return _message_text(message), rows

        messages.append({"role": "assistant", "content": message.content})
        results = []

        for block in message.content:
            if getattr(block, "type", None) != "tool_use":
                continue

            output = await _dispatch_tool(block.name, block.input, neo4j, ollama)
            rows = _rows_from(output) or rows
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(output)
            })

        messages.append({"role": "user", "content": results})

    _logger.warning("Tool loop exhausted %d iterations.", _MAX_TOOL_ITERATIONS)
    return "", rows


async def _dispatch_tool(
    name: str, tool_input: Dict[str, Any], neo4j: Any, ollama: Any
) -> Any:
    """Runs one requested tool against the clients, by name."""

    if name == "get_schema":
        return tool_module.get_schema()
    if name == "resolve_entity":
        return tool_module.resolve_entity(neo4j, **tool_input)
    if name == "run_cypher":
        return tool_module.run_cypher(neo4j, **tool_input)
    if name == "vector_search":
        return await tool_module.vector_search(neo4j, ollama, **tool_input)

    return {"error": f"Unknown tool: {name}"}


def _rows_from(output: Any) -> List[Dict[str, Any]]:
    """Extracts data rows from a tool result, or `[]` when it has none."""

    if isinstance(output, dict) and isinstance(output.get("rows"), list):
        return output["rows"]
    if isinstance(output, list):
        return output
    return []


def _message_text(message: Any) -> str:
    """Concatenates the text blocks of an Anthropic message."""

    return "".join(
        block.text
        for block in message.content
        if getattr(block, "type", None) == "text"
    )


def _schema_for(tool_name: str) -> Dict[str, Any]:
    """Returns the Anthropic tool schema for a single tool by name."""

    return next(
        schema for schema in tool_module.TOOL_SCHEMAS
        if schema["name"] == tool_name
    )


def _query_user_prompt(state: AgentState) -> str:
    """Builds the query-stage user prompt, with retry feedback."""

    parts = [
        f"Question: {state['question']}",
        f"Plan: {state['plan']}",
        f"Resolved entities: {state['resolved']}"
    ]

    if state["verification_notes"] and not state["verified"]:
        parts.append(
            "A previous attempt was rejected in verification: "
            f"{state['verification_notes']}\nGather corrected rows."
        )

    return "\n\n".join(parts)


def _verify_user_prompt(state: AgentState) -> str:
    """Builds the verification user prompt."""

    return (
        f"Question: {state['question']}\n\n"
        f"Query notes: {state['query_notes']}\n\n"
        f"Rows: {json.dumps(state['rows'])}"
    )


def _compose_user_prompt(state: AgentState) -> str:
    """Builds the answer-composition user prompt."""

    return (
        f"Question: {state['question']}\n\nRows: {json.dumps(state['rows'])}"
    )


def _route_after_verify(state: AgentState) -> str:
    """Routes to the answer, a query retry, or the fallback, after verify."""

    if state["verified"]:
        return "compose"
    if state["query_attempts"] < _MAX_QUERY_ATTEMPTS:
        return "query"
    return "fallback"
