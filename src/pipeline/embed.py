"""Embedding of movie overviews into the Neo4j vector index."""

from typing import Any, Dict, List

from src.clients.neo4j.client import Neo4jClient
from src.clients.ollama.client import OllamaClient
from src.logger import get_logger


_logger = get_logger(__name__)

_DEFAULT_PAGE_SIZE = 100

# Selects a page of movies that have an overview but no embedding yet, so
# the process is naturally resumable and idempotent: already-embedded
# movies are never re-fetched, and re-running only fills the gaps.
_PENDING_MOVIES_QUERY = (
    "MATCH (m:Movie) "
    "WHERE m.overview IS NOT NULL AND m.overview <> '' "
    "AND m.overview_embedding IS NULL "
    "RETURN m.tconst AS tconst, m.overview AS overview "
    "LIMIT $limit"
)
_SET_EMBEDDING_QUERY = (
    "UNWIND $rows AS row "
    "MATCH (m:Movie {tconst: row.tconst}) "
    "SET m.overview_embedding = row.embedding"
)


async def embed_movie_overviews(
    neo4j: Neo4jClient,
    ollama: OllamaClient,
    page_size: int = _DEFAULT_PAGE_SIZE
) -> int:
    """
    Embeds every movie overview that isn't embedded yet and stores the
    vectors on `Movie.overview_embedding`, then ensures the backing vector
    index exists (its dimension is taken from the embeddings produced).

    Movies are processed in resumable pages: each page fetches only movies
    still missing an embedding, so a re-run picks up exactly where a prior
    run stopped and finished runs are no-ops.

    :param neo4j: The Neo4j client holding the movie graph.
    :type neo4j: Neo4jClient
    :param ollama: The Ollama client producing the embeddings.
    :type ollama: OllamaClient
    :param page_size: Number of movies embedded per write batch.
    :type page_size: int

    :return: The total number of movie overviews embedded this run.
    :rtype: int
    """

    embedded_count = 0
    dimensions = 0

    while True:
        pending = neo4j.execute_read(_PENDING_MOVIES_QUERY, limit=page_size)

        if not pending:
            break

        rows: List[Dict[str, Any]] = []
        for movie in pending:
            embedding = await ollama.embed(movie["overview"])
            dimensions = dimensions or len(embedding)
            rows.append(
                {"tconst": movie["tconst"], "embedding": embedding}
            )

        neo4j.execute_write(_SET_EMBEDDING_QUERY, rows=rows)
        embedded_count += len(rows)
        _logger.info("Embedded %d movie overview(s) so far.", embedded_count)

    if dimensions:
        neo4j.ensure_vector_index(dimensions)

    _logger.info("Embedded %d movie overview(s) in total.", embedded_count)
    return embedded_count
