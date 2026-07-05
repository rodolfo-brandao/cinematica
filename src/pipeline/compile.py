"""Compilation of IMDb `.tsv.gz` datasets into in-memory indexes."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set

from src.imdb.filters import is_movie
from src.imdb.loader import stream_tsv_gz
from src.logger import get_logger
from src.models.imdb import (
    ImdbMovie,
    ImdbRating,
    ImdbPrincipal,
    ImdbPerson
)


_logger = get_logger(__name__)

# IMDb encodes missing values as a literal "\N":
_IMDB_NULL_TOKEN = "\\N"


def build_movie_index(file_path: Path) -> Dict[str, ImdbMovie]:
    """
    Streams the IMDb `title.basics` dataset and builds the pipeline spine:
    An index of every movie record, keyed by its `tconst` (`tt` --prefixed string).\n
    Shorts, TV titles and anything else are skipped.

    :param file_path: Path to the `title.basics.tsv.gz` file.
    :type file_path: Path

    :return: A mapping of `tconst` to its :class:`~src.models.imdb.ImdbMovie`.
    :rtype: Dict[str, ImdbMovie]
    """

    _logger.info("Building movie index from %s", file_path)
    index: Dict[str, ImdbMovie] = {}

    for row in stream_tsv_gz(file_path):
        if not is_movie(row):
            continue

        tconst = row["tconst"]
        index[tconst] = ImdbMovie(
            tconst=tconst,
            primary_title=row["primaryTitle"],
            original_title=row["originalTitle"],
            is_adult=_parse_bool(row["isAdult"]),
            start_year=_parse_int(row["startYear"]),
            runtime_min=_parse_int(row["runtimeMinutes"]),
            genres=_parse_list(row["genres"])
        )

    _logger.info("Indexed %d movie record(s).", len(index))
    return index


def build_ratings_index(file_path: Path, movie_ids: Set[str]) -> Dict[str, ImdbRating]:
    """
    Streams the IMDb `title.ratings` dataset and indexes the ratings that belong
    to the given movies, keyed by `tconst`. Ratings for non-movie titles (and
    malformed rows) are skipped.

    :param file_path: Path to the `title.ratings.tsv.gz` file.
    :type file_path: Path
    :param movie_ids: The set of movie `tconst`s to keep (from the movie index).
    :type movie_ids: Set[str]

    :return: A mapping of `tconst` to its :class:`~src.models.imdb.ImdbRating`.
    :rtype: Dict[str, ImdbRating]
    """

    _logger.info("Building ratings index from %s", file_path)
    index: Dict[str, ImdbRating] = {}

    for row in stream_tsv_gz(file_path):
        tconst = row["tconst"]

        if tconst not in movie_ids:
            continue

        average_rating = _parse_float(row["averageRating"])
        num_votes = _parse_int(row["numVotes"])

        if average_rating is None or num_votes is None:
            continue

        index[tconst] = ImdbRating(
            tconst=tconst,
            average_rating=average_rating,
            num_votes=num_votes
        )

    _logger.info("Indexed %d rating(s) for %d movie(s).", len(index), len(movie_ids))
    return index


def build_principals_index(
    file_path: Path,
    movie_ids: Set[str]
) -> Dict[str, List[ImdbPrincipal]]:
    """
    Streams the IMDb `title.principals` dataset (the largest file) once and
    groups the cast/crew of each movie, keyed by `tconst`. Principals of
    non-movie titles are skipped. Person names are not resolved here; that is
    done in :func:`build_names_index` via the referenced `nconst`s.

    :param file_path: Path to the `title.principals.tsv.gz` file.
    :type file_path: Path
    :param movie_ids: The set of movie `tconst`s to keep (from the movie index).
    :type movie_ids: Set[str]

    :return: A mapping of `tconst` to its list of :class:`~src.models.imdb.ImdbPrincipal`.
    :rtype: Dict[str, List[ImdbPrincipal]]
    """

    _logger.info("Building principals index from %s", file_path)
    index: Dict[str, List[ImdbPrincipal]] = {}

    for row in stream_tsv_gz(file_path):
        tconst = row["tconst"]

        if tconst not in movie_ids:
            continue

        principal = ImdbPrincipal(
            tconst=tconst,
            nconst=row["nconst"],
            ordering=_parse_int(row["ordering"]),
            category=_clean(row["category"]),
            job=_clean(row["job"]),
            characters=_parse_characters(row["characters"])
        )
        index.setdefault(tconst, []).append(principal)

    _logger.info("Indexed principals for %d movie(s).", len(index))
    return index


def collect_nconsts(principals: Dict[str, List[ImdbPrincipal]]) -> Set[str]:
    """
    Collects the **distinct** person IDs (`nconst`s) referenced across all
    principals, to drive name resolution in :func:`build_names_index`.

    :param principals: The principals index (from :func:`build_principals_index`).
    :type principals: Dict[str, List[ImdbPrincipal]]

    :return: The set of distinct `nconst`s.
    :rtype: Set[str]
    """

    return { p.nconst for people in principals.values() for p in people }


def build_names_index(file_path: Path, nconst_ids: Set[str]) -> Dict[str, ImdbPerson]:
    """
    Streams the IMDb `name.basics` dataset and resolves the people referenced by
    the principals, keyed by `nconst`. People not referenced by any movie
    principal are skipped.

    :param file_path: Path to the `name.basics.tsv.gz` file.
    :type file_path: Path
    :param nconst_ids: The set of person `nconst`s to keep (from :func:`collect_nconsts`).
    :type nconst_ids: Set[str]

    :return: A mapping of `nconst` to its :class:`~src.models.imdb.ImdbPerson`.
    :rtype: Dict[str, ImdbPerson]
    """

    _logger.info("Building names index from %s", file_path)
    index: Dict[str, ImdbPerson] = {}

    for row in stream_tsv_gz(file_path):
        nconst = row["nconst"]

        if nconst not in nconst_ids:
            continue

        index[nconst] = ImdbPerson(
            nconst=nconst,
            primary_name=row["primaryName"],
            birth_year=_parse_int(row["birthYear"]),
            death_year=_parse_int(row["deathYear"]),
            primary_profession=_parse_list(row["primaryProfession"])
        )

    _logger.info("Indexed %d person(s) for %d referenced ID(s).", len(index), len(nconst_ids))
    return index


# Private normalization helpers (module-level):
def _clean(value: Optional[str]) -> Optional[str]:
    """Normalizes IMDb's "\\N" null token (and empty strings) to `None`."""

    if value is None or value == _IMDB_NULL_TOKEN or value == "":
        return None

    return value


def _parse_bool(value: Optional[str]) -> bool:
    """Parses IMDb's "0"/"1" flag into a `bool` ("\\N" -> `False`)."""

    return _clean(value) == "1"


def _parse_int(value: Optional[str]) -> Optional[int]:
    """Parses a numeric IMDb field into an `int`, or `None` when absent/invalid."""

    cleaned = _clean(value)

    if cleaned is None:
        return None

    try:
        return int(cleaned)
    except ValueError:
        return None


def _parse_float(value: Optional[str]) -> Optional[float]:
    """Parses a numeric IMDb field into a `float`, or `None` when absent/invalid."""

    cleaned = _clean(value)

    if cleaned is None:
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_list(value: Optional[str]) -> List[str]:
    """Splits a comma-joined IMDb field (e.g. genres) into a list ("\\N" -> `[]`)."""

    cleaned = _clean(value)

    if cleaned is None:
        return []

    return [item for item in cleaned.split(",") if item]


def _parse_characters(value: Optional[str]) -> List[str]:
    """
    Parses the IMDb `characters` field, a JSON-array string (e.g.
    `["Tyler Durden"]`), into a list of strings ("\\N"/malformed -> `[]`).
    """

    cleaned = _clean(value)

    if cleaned is None:
        return []

    try:
        parsed = json.loads(cleaned)
    except (ValueError, TypeError):
        return []

    if not isinstance(parsed, list):
        return []

    return [str(item) for item in parsed if item]
