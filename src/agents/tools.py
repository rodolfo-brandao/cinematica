"""Grounding tools the reasoning agent calls to query the film graph."""

import re
from typing import Any, Dict, List

from src.agents.schema import GRAPH_SCHEMA_DESCRIPTION
from src.clients.neo4j.client import Neo4jClient
from src.clients.ollama.client import OllamaClient


_DEFAULT_RESOLVE_LIMIT = 5
_DEFAULT_VECTOR_LIMIT = 10
_MAX_ROWS = 50

# Read-only guard: any query containing one of these clauses is rejected
# before it reaches the database. Neo4j's READ access mode is the
# authoritative backstop; this denylist just fails obvious writes fast
# and with a clearer message.
_WRITE_KEYWORDS = re.compile(
    r"\b(CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|"
    r"LOAD\s+CSV|CALL\s+apoc\.)\b",
    re.IGNORECASE
)

# Lucene reserves these characters; escape them so a raw name (e.g. one
# containing parentheses or a hyphen) is matched literally rather than
# parsed as query syntax.
_LUCENE_SPECIAL = re.compile(r'([+\-!(){}\[\]^"~*?:\\/&|])')

# Full-text-backed resolution, one projection per supported label:
_RESOLVE_QUERIES = {
    "Person": (
        "CALL db.index.fulltext.queryNodes('person_name_ft', $name) "
        "YIELD node, score "
        "RETURN node.nconst AS id, node.primary_name AS name, "
        "node.birth_year AS birth_year, node.death_year AS death_year, "
        "score "
        "ORDER BY score DESC LIMIT $limit"
    ),
    "Movie": (
        "CALL db.index.fulltext.queryNodes('movie_title_ft', $name) "
        "YIELD node, score "
        "RETURN node.tconst AS id, node.primary_title AS title, "
        "node.start_year AS start_year, score "
        "ORDER BY score DESC LIMIT $limit"
    ),
}

_VECTOR_SEARCH_QUERY = (
    "CALL db.index.vector.queryNodes('movie_overview', $k, $embedding) "
    "YIELD node, score "
    "RETURN node.tconst AS tconst, node.primary_title AS title, "
    "node.start_year AS start_year, node.overview AS overview, "
    "node.average_rating AS average_rating, node.num_votes AS num_votes, "
    "score "
    "ORDER BY score DESC"
)


def get_schema() -> str:
    """
    Returns the graph schema description, so the model queries against the
    real node labels, relationships and properties instead of guessing.

    :return: The schema description prompt.
    :rtype: str
    """

    return GRAPH_SCHEMA_DESCRIPTION


def resolve_entity(
    client: Neo4jClient,
    name: str,
    label: str,
    limit: int = _DEFAULT_RESOLVE_LIMIT
) -> List[Dict[str, Any]]:
    """
    Resolves a free-text name to candidate graph nodes via the full-text
    index, returning disambiguating fields so the model can pick the right
    one before building a query. Case- and spelling-tolerant, unlike an
    exact-match lookup.

    :param client: The Neo4j client to run the query against.
    :type client: Neo4jClient
    :param name: The free-text name to resolve.
    :type name: str
    :param label: The node label to resolve against; `"Person"` or
        `"Movie"`.
    :type label: str
    :param limit: The maximum number of candidates to return.
    :type limit: int

    :return: The candidate nodes, most relevant first; empty if the label
        is unsupported or nothing matched.
    :rtype: List[Dict[str, Any]]
    """

    query = _RESOLVE_QUERIES.get(label)

    if query is None:
        return []

    return client.execute_read(
        query, name=_lucene_escape(name), limit=limit
    )


def run_cypher(
    client: Neo4jClient, query: str, max_rows: int = _MAX_ROWS
) -> Dict[str, Any]:
    """
    Validates and runs a read-only Cypher query, returning either its rows
    or a structured error the model can react to and repair.

    The query is rejected outright if it contains a write clause, then
    validated with `EXPLAIN` (catching syntax/semantic errors before any
    execution), then run via `Neo4jClient.execute_read` (whose READ access
    mode rejects any write that slips past the denylist). Rows are capped.

    :param client: The Neo4j client to run the query against.
    :type client: Neo4jClient
    :param query: The read-only Cypher query to run.
    :type query: str
    :param max_rows: The maximum number of rows to return.
    :type max_rows: int

    :return: `{"rows": [...]}` on success, or `{"error": "..."}` when the
        query is rejected, fails to plan, or fails to execute.
    :rtype: Dict[str, Any]
    """

    if _WRITE_KEYWORDS.search(query):
        return {"error": "Query contains a disallowed write clause."}

    try:
        client.execute_read(f"EXPLAIN {query}")
        rows = client.execute_read(query)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # The model, not this codebase, authored the query; any Neo4j
        # error is expected input for it to recover from, not a bug here.
        return {"error": str(exc)}

    return {"rows": rows[:max_rows]}


async def vector_search(
    client: Neo4jClient,
    ollama: OllamaClient,
    text: str,
    k: int = _DEFAULT_VECTOR_LIMIT
) -> List[Dict[str, Any]]:
    """
    Finds movies whose overview is semantically closest to `text`, for
    thematic questions plain Cypher can't express (e.g. "movies about
    isolation and memory").

    :param client: The Neo4j client holding the vector index.
    :type client: Neo4jClient
    :param ollama: The Ollama client producing the query embedding.
    :type ollama: OllamaClient
    :param text: The free-text theme to search for.
    :type text: str
    :param k: The number of nearest movies to return.
    :type k: int

    :return: The nearest movies, most similar first.
    :rtype: List[Dict[str, Any]]
    """

    embedding = await ollama.embed(text)
    return client.execute_read(
        _VECTOR_SEARCH_QUERY, k=k, embedding=embedding
    )


# Private helper (module-level):
def _lucene_escape(value: str) -> str:
    """Escapes Lucene's reserved characters in a full-text query string."""

    return _LUCENE_SPECIAL.sub(r"\\\1", value)


# Anthropic tool schemas, in the same order as `TOOL_NAMES`:
TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "get_schema",
        "description": (
            "Return the film graph's schema: node labels, properties, "
            "relationships, and usage notes. Call this first to ground "
            "every query in the real schema instead of guessing names."
        ),
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "resolve_entity",
        "description": (
            "Resolve a person or movie name to candidate graph nodes via "
            "fuzzy full-text search. Use this to find the canonical node "
            "(and its id) before referencing an entity in a query, rather "
            "than matching names exactly."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The free-text name to resolve."
                },
                "label": {
                    "type": "string",
                    "enum": ["Person", "Movie"],
                    "description": "Which node label to resolve against."
                }
            },
            "required": ["name", "label"]
        }
    },
    {
        "name": "run_cypher",
        "description": (
            "Run a read-only Cypher query against the film graph and get "
            "its rows back. Returns a structured error (schema/syntax/"
            "execution) to fix and retry when the query is invalid. Only "
            "MATCH/WHERE/WITH/RETURN/ORDER BY/LIMIT read clauses are "
            "allowed; always include a LIMIT."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The read-only Cypher query to run."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "vector_search",
        "description": (
            "Find movies whose plot/overview is semantically closest to a "
            "free-text theme. Use for thematic or conceptual questions "
            "that can't be expressed as exact graph filters (e.g. 'movies "
            "about grief and memory')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The free-text theme to search for."
                }
            },
            "required": ["text"]
        }
    }
]

TOOL_NAMES = {"get_schema", "resolve_entity", "run_cypher", "vector_search"}
