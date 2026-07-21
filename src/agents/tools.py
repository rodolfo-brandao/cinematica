"""Grounding tools the reasoning agent calls to query the film graph."""

import re
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from src.agents.schema import GRAPH_SCHEMA_DESCRIPTION
from src.clients.neo4j.client import Neo4jClient
from src.clients.ollama.client import OllamaClient
from src.clients.tmdb.client import TmdbClient
from src.pipeline.load import load_movie_record
from src.pipeline.serialize import to_external_movie_record


_DEFAULT_RESOLVE_LIMIT = 5
_DEFAULT_VECTOR_LIMIT = 10
_MAX_ROWS = 50
_MAX_SEARCH_RESULTS = 5
_MAX_REVIEWS = 20
_MAX_REVIEW_CONTENT_CHARS = 2000

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

_MOVIE_BY_TMDB_ID_QUERY = (
    "MATCH (m:Movie {tmdb_id: $tmdb_id}) "
    "RETURN m.tconst AS tconst LIMIT 1"
)
_REVIEW_MERGE_QUERY = (
    "MATCH (m:Movie {tmdb_id: $tmdb_id}) "
    "UNWIND $rows AS row "
    "MERGE (r:Review {review_id: row.review_id}) "
    "SET r += row "
    "MERGE (m)-[:HAS_REVIEW]->(r)"
)
_MOVIE_SENTIMENT_UPDATE_QUERY = (
    "MATCH (m:Movie {tmdb_id: $tmdb_id}) "
    "SET m.audience_sentiment_label = $label, "
    "m.audience_sentiment_score = $score, "
    "m.audience_sentiment_summary = $summary, "
    "m.audience_sentiment_reviewed_at = datetime()"
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


# TMDb-backed tools, for movies outside the ingested dataset. Use only
# after `resolve_entity`/`run_cypher` confirm the movie isn't already in
# the graph, since `ingest_movie`/`save_movie_sentiment` write to it.
async def search_external_movie(
    tmdb: TmdbClient, title: str, year: Optional[int] = None
) -> Dict[str, Any]:
    """
    Searches TMDb for a movie not found in the graph, so the model can
    identify the right `tmdb_id` to ingest.

    :param tmdb: The TMDb client to search with.
    :type tmdb: TmdbClient
    :param title: The free-text movie title to search for.
    :type title: str
    :param year: The release year, to disambiguate same-titled movies.
    :type year: Optional[int]

    :return: `{"candidates": [...]}`, most relevant first.
    :rtype: Dict[str, Any]
    """

    results = await tmdb.search_movies(title, year=year)
    return {
        "candidates": [
            asdict(result) for result in results[:_MAX_SEARCH_RESULTS]
        ]
    }


async def ingest_movie(
    tmdb: TmdbClient, neo4j: Neo4jClient, tmdb_id: int
) -> Dict[str, Any]:
    """
    Fetches a movie's full TMDb details and merges it into the graph, so
    a movie absent from the ingested dataset can be queried afterward.
    A no-op if the graph already has a movie with this `tmdb_id`, so it
    never overwrites a fuller, IMDb-sourced `Movie` node.

    :param tmdb: The TMDb client to fetch details from.
    :type tmdb: TmdbClient
    :param neo4j: The Neo4j client to write the movie into.
    :type neo4j: Neo4jClient
    :param tmdb_id: The TMDb id of the movie to ingest.
    :type tmdb_id: int

    :return: A confirmation dict, or `{"error": "..."}` if the movie has
        no linked IMDb id and can't be ingested.
    :rtype: Dict[str, Any]
    """

    existing = neo4j.execute_read(_MOVIE_BY_TMDB_ID_QUERY, tmdb_id=tmdb_id)
    if existing:
        return {
            "tconst": existing[0]["tconst"],
            "message": "Movie is already in the graph."
        }

    movie = await tmdb.get_movie_details(tmdb_id)
    if not movie.imdb_id:
        return {
            "error": (
                "This TMDb movie has no linked IMDb id and cannot be "
                "ingested."
            )
        }

    load_movie_record(to_external_movie_record(movie), neo4j)
    return {
        "tconst": movie.imdb_id,
        "primary_title": movie.title,
        "message": "Movie ingested into the graph."
    }


async def fetch_reviews(tmdb: TmdbClient, tmdb_id: int) -> Dict[str, Any]:
    """
    Fetches a movie's public TMDb reviews, for the model to read and
    judge audience sentiment from before calling `save_movie_sentiment`.
    Review content is truncated to bound the amount of text returned.

    :param tmdb: The TMDb client to fetch reviews from.
    :type tmdb: TmdbClient
    :param tmdb_id: The TMDb id of the movie whose reviews to fetch.
    :type tmdb_id: int

    :return: `{"reviews": [...]}`.
    :rtype: Dict[str, Any]
    """

    reviews = await tmdb.get_reviews(tmdb_id)
    return {
        "reviews": [
            _truncate_review(asdict(review))
            for review in reviews[:_MAX_REVIEWS]
        ]
    }


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
async def save_movie_sentiment(
    tmdb: TmdbClient,
    neo4j: Neo4jClient,
    tmdb_id: int,
    sentiment_label: str,
    sentiment_score: float,
    summary: str
) -> Dict[str, Any]:
    """
    Persists the model's audience-sentiment judgment for a movie: each
    of its TMDb reviews as a `Review` node, and the aggregate judgment on
    the `Movie` node itself. Re-fetches the same reviews `fetch_reviews`
    returned, so the model only has to pass its own conclusions rather
    than round-trip review text through tool arguments.

    :param tmdb: The TMDb client to re-fetch reviews from.
    :type tmdb: TmdbClient
    :param neo4j: The Neo4j client to persist the sentiment into.
    :type neo4j: Neo4jClient
    :param tmdb_id: The TMDb id of the movie being judged.
    :type tmdb_id: int
    :param sentiment_label: One of `"positive"`, `"mixed"`, `"negative"`.
    :type sentiment_label: str
    :param sentiment_score: A polarity score from -1.0 to 1.0.
    :type sentiment_score: float
    :param summary: A one-sentence rationale for the judgment.
    :type summary: str

    :return: A confirmation dict, or `{"error": "..."}` if the movie
        isn't in the graph yet.
    :rtype: Dict[str, Any]
    """

    existing = neo4j.execute_read(_MOVIE_BY_TMDB_ID_QUERY, tmdb_id=tmdb_id)
    if not existing:
        return {
            "error": (
                "No movie with this tmdb_id is in the graph yet; call "
                "ingest_movie first."
            )
        }

    reviews = await tmdb.get_reviews(tmdb_id)
    review_rows = [asdict(review) for review in reviews]
    if review_rows:
        neo4j.execute_write(
            _REVIEW_MERGE_QUERY, tmdb_id=tmdb_id, rows=review_rows
        )

    neo4j.execute_write(
        _MOVIE_SENTIMENT_UPDATE_QUERY,
        tmdb_id=tmdb_id,
        label=sentiment_label,
        score=sentiment_score,
        summary=summary
    )
    return {
        "tconst": existing[0]["tconst"],
        "reviews_saved": len(review_rows),
        "sentiment_label": sentiment_label,
        "sentiment_score": sentiment_score
    }


# Private helpers (module-level):
def _truncate_review(review: Dict[str, Any]) -> Dict[str, Any]:
    """Caps a review's `content` length, for what's returned to the model."""

    content = review["content"]
    if len(content) > _MAX_REVIEW_CONTENT_CHARS:
        review = {**review, "content": content[:_MAX_REVIEW_CONTENT_CHARS]}
    return review


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
    },
    {
        "name": "search_external_movie",
        "description": (
            "Search TMDb by free-text title for a movie not found in the "
            "graph. Only use this after `resolve_entity`/`run_cypher` "
            "confirm the movie is genuinely absent. Returns candidates "
            "with their `tmdb_id`, to pass to `ingest_movie`."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The free-text movie title to search."
                },
                "year": {
                    "type": "integer",
                    "description": (
                        "The release year, to disambiguate same-titled "
                        "movies."
                    )
                }
            },
            "required": ["title"]
        }
    },
    {
        "name": "ingest_movie",
        "description": (
            "Fetch a TMDb movie's full details and merge it into the "
            "graph as a `Movie` node, so it can then be queried via "
            "`run_cypher` like any other movie. A no-op if the movie is "
            "already in the graph. Note: movies ingested this way have "
            "no cast/crew relationships and no IMDb `average_rating`/"
            "`num_votes`."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tmdb_id": {
                    "type": "integer",
                    "description": (
                        "The TMDb id of the movie to ingest, from "
                        "`search_external_movie`."
                    )
                }
            },
            "required": ["tmdb_id"]
        }
    },
    {
        "name": "fetch_reviews",
        "description": (
            "Fetch a movie's public TMDb reviews to read and judge "
            "audience sentiment from. The movie must already be in the "
            "graph (via `ingest_movie` if needed). After reading the "
            "reviews, call `save_movie_sentiment` with your own "
            "judgment."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tmdb_id": {
                    "type": "integer",
                    "description": "The TMDb id of the movie to review."
                }
            },
            "required": ["tmdb_id"]
        }
    },
    {
        "name": "save_movie_sentiment",
        "description": (
            "Persist your own audience-sentiment judgment for a movie, "
            "formed from reading `fetch_reviews`' output: each review as "
            "a `Review` node, plus the aggregate verdict on the `Movie` "
            "node. Call `fetch_reviews` for this `tmdb_id` first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tmdb_id": {
                    "type": "integer",
                    "description": "The TMDb id of the movie judged."
                },
                "sentiment_label": {
                    "type": "string",
                    "enum": ["positive", "mixed", "negative"],
                    "description": "The overall audience sentiment."
                },
                "sentiment_score": {
                    "type": "number",
                    "description": (
                        "A polarity score from -1.0 (very negative) to "
                        "1.0 (very positive)."
                    )
                },
                "summary": {
                    "type": "string",
                    "description": (
                        "A one-sentence rationale for the judgment, "
                        "citing what the reviews actually said."
                    )
                }
            },
            "required": [
                "tmdb_id", "sentiment_label", "sentiment_score", "summary"
            ]
        }
    }
]

TOOL_NAMES = {
    "get_schema",
    "resolve_entity",
    "run_cypher",
    "vector_search",
    "search_external_movie",
    "ingest_movie",
    "fetch_reviews",
    "save_movie_sentiment"
}
