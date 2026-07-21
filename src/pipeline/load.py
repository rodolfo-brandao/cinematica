"""Batched loading of the consolidated movie records into Neo4j."""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from src.clients.neo4j.client import Neo4jClient
from src.logger import get_logger


_logger = get_logger(__name__)

_DEFAULT_BATCH_SIZE = 1000

# IMDb `principals.category` -> Neo4j relationship type. Anything not
# listed here falls back to `_FALLBACK_RELATIONSHIP`.
_ROLE_RELATIONSHIPS = {
    "actor": "ACTED_IN",
    "actress": "ACTED_IN",
    "self": "ACTED_IN",
    "director": "DIRECTED",
    "writer": "WROTE",
    "producer": "PRODUCED",
    "composer": "COMPOSED",
    "cinematographer": "PHOTOGRAPHED",
    "editor": "EDITED",
    "production_designer": "DESIGNED",
    "casting_director": "CAST",
    "archive_footage": "ARCHIVED_IN",
    "archive_sound": "ARCHIVED_IN",
}
_FALLBACK_RELATIONSHIP = "WORKED_ON"

_MOVIE_UPSERT_QUERY = (
    "UNWIND $rows AS row "
    "MERGE (m:Movie {tconst: row.tconst}) "
    "SET m += row"
)
_GENRE_MERGE_QUERY = (
    "UNWIND $rows AS row "
    "MATCH (m:Movie {tconst: row.tconst}) "
    "MERGE (g:Genre {name: row.name}) "
    "MERGE (m)-[:HAS_GENRE]->(g)"
)
_LANGUAGE_MERGE_QUERY = (
    "UNWIND $rows AS row "
    "MATCH (m:Movie {tconst: row.tconst}) "
    "MERGE (l:Language {name: row.name}) "
    "MERGE (m)-[:SPOKEN_IN]->(l)"
)
_COUNTRY_MERGE_QUERY = (
    "UNWIND $rows AS row "
    "MATCH (m:Movie {tconst: row.tconst}) "
    "MERGE (c:Country {code: row.code}) "
    "MERGE (m)-[:PRODUCED_IN]->(c)"
)
_COMPANY_MERGE_QUERY = (
    "UNWIND $rows AS row "
    "MATCH (m:Movie {tconst: row.tconst}) "
    "MERGE (pc:ProductionCompany {tmdb_id: row.tmdb_id}) "
    "SET pc.name = row.name "
    "MERGE (m)-[:PRODUCED_BY]->(pc)"
)
_KEYWORD_MERGE_QUERY = (
    "UNWIND $rows AS row "
    "MATCH (m:Movie {tconst: row.tconst}) "
    "MERGE (k:Keyword {name: row.name}) "
    "MERGE (m)-[:HAS_KEYWORD]->(k)"
)
_COLLECTION_MERGE_QUERY = (
    "UNWIND $rows AS row "
    "MATCH (m:Movie {tconst: row.tconst}) "
    "MERGE (col:Collection {tmdb_id: row.tmdb_id}) "
    "SET col.name = row.name "
    "MERGE (m)-[:PART_OF_COLLECTION]->(col)"
)
# Relationship types can't be Cypher query parameters, so this
# placeholder (never valid Cypher syntax, unlike a real `$param`) is
# swapped in via `str.replace`, not `str.format` (the query text
# already contains literal `{...}` property maps).
_RELATIONSHIP_PLACEHOLDER = "__RELATIONSHIP__"
_PRINCIPAL_MERGE_QUERY_TEMPLATE = (
    "UNWIND $rows AS row "
    "MATCH (m:Movie {tconst: row.tconst}) "
    "MERGE (p:Person {nconst: row.nconst}) "
    "SET p += row.person "
    f"MERGE (p)-[r:{_RELATIONSHIP_PLACEHOLDER}]->(m) "
    "SET r += row.rel"
)


def load_movies(
    input_path: Path,
    client: Optional[Neo4jClient] = None,
    batch_size: int = _DEFAULT_BATCH_SIZE
) -> int:
    """
    Streams the consolidated JSONL movie records from `input_path` and
    upserts them into Neo4j in batches: one `Movie` node per record, its
    `Genre` relationships, and typed relationships to each `Person` in
    its cast/crew. Every write uses `MERGE`, so re-running this over the
    same (or a grown) input is idempotent.

    :param input_path: Path to the consolidated `movies.jsonl` file.
    :type input_path: Path
    :param client: An existing Neo4j client; one is created (and closed)
        if omitted.
    :type client: Optional[Neo4jClient]
    :param batch_size: Number of movie records per write batch.
    :type batch_size: int

    :return: The total number of movie records loaded.
    :rtype: int
    """

    owns_client = client is None
    client = client or Neo4jClient()
    loaded_count = 0

    try:
        with open(file=input_path, mode="r", encoding="utf-8") as input_file:
            batch: List[Dict[str, Any]] = []

            for line in input_file:
                line = line.strip()

                if not line:
                    continue

                batch.append(json.loads(line))

                if len(batch) >= batch_size:
                    _load_batch(batch, client)
                    loaded_count += len(batch)
                    batch = []

            if batch:
                _load_batch(batch, client)
                loaded_count += len(batch)
    finally:
        if owns_client:
            client.close()

    _logger.info(
        "Loaded %d movie record(s) into Neo4j from %s",
        loaded_count, input_path
    )
    return loaded_count


def load_movie_record(record: Dict[str, Any], client: Neo4jClient) -> None:
    """
    Upserts a single movie record into Neo4j: its `Movie` node, `Genre`
    relationships and TMDb dimensions, and any cast/crew principals. A
    thin, one-record wrapper around the same batch path `load_movies`
    uses, for ingesting a movie found on demand (e.g. via TMDb search)
    outside the offline pipeline.

    :param record: A movie record shaped like `to_movie_record`'s output.
    :type record: Dict[str, Any]
    :param client: The Neo4j client to write through.
    :type client: Neo4jClient
    """

    _load_batch([record], client)


# Private helpers (module-level):
def _load_batch(batch: List[Dict[str, Any]], client: Neo4jClient) -> None:
    """Upserts one batch of movie records: nodes, genres, principals."""

    client.execute_write(
        _MOVIE_UPSERT_QUERY,
        rows=[_movie_properties(record) for record in batch]
    )

    genre_rows = [
        {"tconst": record["tconst"], "name": name}
        for record in batch
        for name in _genre_names(record)
    ]
    if genre_rows:
        client.execute_write(_GENRE_MERGE_QUERY, rows=genre_rows)

    _load_tmdb_dimensions(batch, client)

    rows_by_relationship = _principal_rows_by_relationship(batch)
    for relationship, rows in rows_by_relationship.items():
        query = _PRINCIPAL_MERGE_QUERY_TEMPLATE.replace(
            _RELATIONSHIP_PLACEHOLDER, relationship
        )
        client.execute_write(query, rows=rows)


def _load_tmdb_dimensions(
    batch: List[Dict[str, Any]], client: Neo4jClient
) -> None:
    """
    Merges the TMDb-sourced dimensions of one batch into first-class nodes:
    languages, countries, production companies, keywords and collections,
    each linked back to its `Movie`. Rows are only written when present, so
    records without TMDb enrichment simply contribute nothing here.
    """

    language_rows = [
        {"tconst": record["tconst"], "name": name}
        for record in batch
        for name in _language_names(record)
    ]
    if language_rows:
        client.execute_write(_LANGUAGE_MERGE_QUERY, rows=language_rows)

    country_rows = [
        {"tconst": record["tconst"], "code": code}
        for record in batch
        for code in _country_codes(record)
    ]
    if country_rows:
        client.execute_write(_COUNTRY_MERGE_QUERY, rows=country_rows)

    company_rows = [
        {"tconst": record["tconst"], "tmdb_id": company["id"],
         "name": company["name"]}
        for record in batch
        for company in _tmdb(record).get("production_companies") or []
    ]
    if company_rows:
        client.execute_write(_COMPANY_MERGE_QUERY, rows=company_rows)

    keyword_rows = [
        {"tconst": record["tconst"], "name": keyword["name"]}
        for record in batch
        for keyword in _tmdb(record).get("keywords") or []
    ]
    if keyword_rows:
        client.execute_write(_KEYWORD_MERGE_QUERY, rows=keyword_rows)

    collection_rows = [
        {"tconst": record["tconst"],
         "tmdb_id": _tmdb(record)["belongs_to_collection"]["id"],
         "name": _tmdb(record)["belongs_to_collection"]["name"]}
        for record in batch
        if _tmdb(record).get("belongs_to_collection")
    ]
    if collection_rows:
        client.execute_write(_COLLECTION_MERGE_QUERY, rows=collection_rows)


def _movie_properties(record: Dict[str, Any]) -> Dict[str, Any]:
    """Flattens one movie record's rating/TMDb data into `Movie` properties."""

    rating = record.get("rating") or {}
    tmdb = record.get("tmdb") or {}

    return {
        "tconst": record["tconst"],
        "primary_title": record["primary_title"],
        "original_title": record["original_title"],
        "is_adult": record["is_adult"],
        "start_year": record["start_year"],
        "runtime_min": record["runtime_min"],
        "average_rating": rating.get("average_rating"),
        "num_votes": rating.get("num_votes"),
        "tmdb_id": tmdb.get("tmdb_id"),
        "overview": tmdb.get("overview"),
        "tagline": tmdb.get("tagline"),
        "status": tmdb.get("status"),
        "budget": tmdb.get("budget"),
        "revenue": tmdb.get("revenue"),
        "popularity": tmdb.get("popularity"),
        "release_date": tmdb.get("release_date"),
        "original_language": tmdb.get("original_language"),
        "vote_average": tmdb.get("vote_average"),
        "vote_count": tmdb.get("vote_count"),
        "has_video": tmdb.get("has_video")
    }


def _tmdb(record: Dict[str, Any]) -> Dict[str, Any]:
    """Returns the record's TMDb sub-object, or an empty dict when absent."""

    return record.get("tmdb") or {}


def _genre_names(record: Dict[str, Any]) -> Set[str]:
    """Merges IMDb and TMDb genre names for one movie record, deduplicated."""

    names = set(record.get("genres") or [])
    names.update(genre["name"] for genre in _tmdb(record).get("genres") or [])
    return names


def _language_names(record: Dict[str, Any]) -> Set[str]:
    """Collects the distinct spoken-language names for one movie record."""

    return {
        language["english_name"]
        for language in _tmdb(record).get("spoken_languages") or []
        if language.get("english_name")
    }


def _country_codes(record: Dict[str, Any]) -> Set[str]:
    """
    Collects the distinct country codes for one movie record, drawing from
    both the TMDb `origin_country` list and each production company's own
    `origin_country`.
    """

    tmdb = _tmdb(record)
    codes = set(tmdb.get("origin_country") or [])
    codes.update(
        company["origin_country"]
        for company in tmdb.get("production_companies") or []
        if company.get("origin_country")
    )
    return codes


def _principal_rows_by_relationship(
    batch: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """Groups every principal in `batch` by its mapped relationship type."""

    rows_by_relationship: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for record in batch:
        for principal in record.get("principals") or []:
            relationship = _ROLE_RELATIONSHIPS.get(
                principal["category"], _FALLBACK_RELATIONSHIP
            )
            rows_by_relationship[relationship].append(
                _principal_row(record["tconst"], principal, relationship)
            )

    return rows_by_relationship


def _principal_row(
    tconst: str,
    principal: Dict[str, Any],
    relationship: str
) -> Dict[str, Any]:
    """Builds one `(tconst, nconst, person, rel)` UNWIND row."""

    person = principal.get("person") or {}
    rel_properties = {
        "ordering": principal.get("ordering"),
        "job": principal.get("job"),
        "characters": principal.get("characters") or []
    }

    if relationship == _FALLBACK_RELATIONSHIP:
        rel_properties["category"] = principal.get("category")

    return {
        "tconst": tconst,
        "nconst": principal["nconst"],
        "person": {
            "primary_name": person.get("primary_name"),
            "birth_year": person.get("birth_year"),
            "death_year": person.get("death_year"),
            "primary_profession": person.get("primary_profession") or []
        },
        "rel": rel_properties
    }
