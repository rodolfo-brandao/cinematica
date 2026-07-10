"""Synchronous client for the Neo4j Bolt protocol."""

import os
from typing import Any, Optional

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
