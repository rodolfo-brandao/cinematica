"""Synchronous client for the Neo4j Bolt protocol."""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from neo4j import GraphDatabase, ManagedTransaction

from src.logger import get_logger


load_dotenv()
NEO4J_URI: Optional[str] = os.getenv(key="NEO4J_URI")
NEO4J_USERNAME: Optional[str] = os.getenv(key="NEO4J_USERNAME")
NEO4J_PASSWORD: Optional[str] = os.getenv(key="NEO4J_PASSWORD")

_CONSTRAINTS = (
    "CREATE CONSTRAINT movie_tconst IF NOT EXISTS "
    "FOR (m:Movie) REQUIRE m.tconst IS UNIQUE",
    "CREATE CONSTRAINT person_nconst IF NOT EXISTS "
    "FOR (p:Person) REQUIRE p.nconst IS UNIQUE",
    "CREATE CONSTRAINT genre_name IF NOT EXISTS "
    "FOR (g:Genre) REQUIRE g.name IS UNIQUE",
    "CREATE CONSTRAINT language_name IF NOT EXISTS "
    "FOR (l:Language) REQUIRE l.name IS UNIQUE",
    "CREATE CONSTRAINT country_code IF NOT EXISTS "
    "FOR (c:Country) REQUIRE c.code IS UNIQUE",
    "CREATE CONSTRAINT company_tmdb_id IF NOT EXISTS "
    "FOR (pc:ProductionCompany) REQUIRE pc.tmdb_id IS UNIQUE",
    "CREATE CONSTRAINT keyword_name IF NOT EXISTS "
    "FOR (k:Keyword) REQUIRE k.name IS UNIQUE",
    "CREATE CONSTRAINT collection_tmdb_id IF NOT EXISTS "
    "FOR (col:Collection) REQUIRE col.tmdb_id IS UNIQUE",
    "CREATE CONSTRAINT review_id IF NOT EXISTS "
    "FOR (r:Review) REQUIRE r.review_id IS UNIQUE",
)

# Full-text indexes back case-insensitive, fuzzy entity resolution (the
# `resolve_entity` agent tool), so a misspelled or differently-cased name
# still finds its node instead of silently missing on exact-match.
_FULLTEXT_INDEXES = (
    "CREATE FULLTEXT INDEX person_name_ft IF NOT EXISTS "
    "FOR (p:Person) ON EACH [p.primary_name]",
    "CREATE FULLTEXT INDEX movie_title_ft IF NOT EXISTS "
    "FOR (m:Movie) ON EACH [m.primary_title, m.original_title]",
)

# The vector index over `Movie.overview_embedding` powers semantic
# ("thematic") search; its dimension count must match the embedding model,
# so it is created via `ensure_vector_index` rather than a static statement.
_VECTOR_INDEX_NAME = "movie_overview"
_VECTOR_INDEX_TEMPLATE = (
    f"CREATE VECTOR INDEX {_VECTOR_INDEX_NAME} IF NOT EXISTS "
    "FOR (m:Movie) ON m.overview_embedding "
    "OPTIONS {indexConfig: {"
    "`vector.dimensions`: $dimensions, "
    "`vector.similarity_function`: 'cosine'}}"
)

_logger = get_logger(__name__)


class Neo4jClient:
    """
    Sync client for the Neo4j Bolt protocol.\n
    A single, local database instance is written to in batches, so this
    wraps the plain (non-async) driver rather than the concurrency/retry
    machinery built for the TMDb HTTP client.
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        """
        Opens the driver connection, falling back to the `NEO4J_URI`,
        `NEO4J_USERNAME` and `NEO4J_PASSWORD` env vars when omitted.

        :param uri: The Neo4j Bolt connection URI.
        :type uri: Optional[str]
        :param username: The Neo4j username.
        :type username: Optional[str]
        :param password: The Neo4j password.
        :type password: Optional[str]

        :raises ValueError: If any connection parameter can't be resolved.
        """

        uri = uri or NEO4J_URI
        username = username or NEO4J_USERNAME
        password = password or NEO4J_PASSWORD

        if not uri or not username or not password:
            raise ValueError(
                "Neo4j 'uri', 'username' and 'password' are required."
            )

        self._driver = GraphDatabase.driver(uri, auth=(username, password))

    def __enter__(self) -> "Neo4jClient":
        """Enters the context, returning this client instance."""
        return self

    def __exit__(self, *_) -> None:
        """Exits the context, closing the driver connection."""
        self.close()

    def close(self) -> None:
        """Closes the underlying driver connection."""
        self._driver.close()

    def ensure_constraints(self) -> None:
        """
        Creates the uniqueness constraints backing `Movie.tconst`,
        `Person.nconst` and `Genre.name`, if they don't already exist.
        """

        for statement in _CONSTRAINTS:
            self.execute_write(statement)

        _logger.info("Ensured %d Neo4j constraint(s).", len(_CONSTRAINTS))

    def ensure_fulltext_indexes(self) -> None:
        """
        Creates the full-text indexes backing fuzzy entity resolution over
        `Person.primary_name` and `Movie.primary_title`, if they don't
        already exist.
        """

        for statement in _FULLTEXT_INDEXES:
            self.execute_write(statement)

        _logger.info(
            "Ensured %d Neo4j full-text index(es).", len(_FULLTEXT_INDEXES)
        )

    def ensure_vector_index(self, dimensions: int) -> None:
        """
        Creates the vector index over `Movie.overview_embedding`, if it
        doesn't already exist.

        :param dimensions: The embedding vector length; must match the
            embedding model producing `Movie.overview_embedding`.
        :type dimensions: int
        """

        self.execute_write(_VECTOR_INDEX_TEMPLATE, dimensions=dimensions)
        _logger.info(
            "Ensured Neo4j vector index %r (%d dimensions).",
            _VECTOR_INDEX_NAME, dimensions
        )

    def execute_write(self, query: str, **parameters: Any) -> None:
        """
        Runs `query` inside a single managed write transaction.

        :param query: The Cypher query to execute.
        :type query: str
        :param parameters: Query parameters, passed through to the driver.
        :type parameters: Any
        """

        def _run(tx: ManagedTransaction) -> None:
            tx.run(query, **parameters).consume()

        with self._driver.session() as session:
            session.execute_write(_run)

    def execute_read(
        self, query: str, **parameters: Any
    ) -> List[Dict[str, Any]]:
        """
        Runs `query` inside a single managed read transaction.

        :param query: The Cypher query to execute.
        :type query: str
        :param parameters: Query parameters, passed through to the driver.
        :type parameters: Any

        :return: The matched records, each as a plain dictionary.
        :rtype: List[Dict[str, Any]]
        """

        def _run(tx: ManagedTransaction) -> List[Dict[str, Any]]:
            return [record.data() for record in tx.run(query, **parameters)]

        with self._driver.session() as session:
            return session.execute_read(_run)
