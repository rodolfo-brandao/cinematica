"""Serialization of joined IMDb/TMDb data into JSON-safe records."""

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from src.models.imdb import (
    ImdbMovie,
    ImdbRating,
    ImdbPrincipal,
    ImdbPerson
)
from src.models.tmdb import TmdbMovie


def to_movie_record(
    movie: ImdbMovie,
    rating: Optional[ImdbRating],
    principals: List[ImdbPrincipal],
    names: Dict[str, ImdbPerson],
    tmdb: Optional[TmdbMovie]
) -> Dict[str, Any]:
    """
    Joins the IMDb indexes (and the enriched TMDb record) into a single,
    JSON-safe movie record. Each principal has its person resolved from the
    names index; absent ratings/people/TMDb data become `None`.

    :param movie: The IMDb movie (spine) record.
    :type movie: ImdbMovie
    :param rating: The IMDb rating for this movie, if any.
    :type rating: Optional[ImdbRating]
    :param principals: The cast/crew of this movie.
    :type principals: List[ImdbPrincipal]
    :param names: The global `nconst` to person index, for name resolution.
    :type names: Dict[str, ImdbPerson]
    :param tmdb: The enriched TMDb record for this movie, if any.
    :type tmdb: Optional[TmdbMovie]

    :return: A nested, JSON-serializable representation of the movie.
    :rtype: Dict[str, Any]
    """

    return {
        "tconst": movie.tconst,
        "primary_title": movie.primary_title,
        "original_title": movie.original_title,
        "is_adult": movie.is_adult,
        "start_year": movie.start_year,
        "runtime_min": movie.runtime_min,
        "genres": list(movie.genres),
        "rating": _rating_to_dict(rating),
        "principals": [_principal_to_dict(p, names) for p in principals],
        "tmdb": asdict(tmdb) if tmdb is not None else None
    }


# Private serialization helpers (module-level):
def _rating_to_dict(rating: Optional[ImdbRating]) -> Optional[Dict[str, Any]]:
    """Renders an :class:`ImdbRating` as a dict (the redundant `tconst` is dropped)."""

    if rating is None:
        return None

    return {
        "average_rating": rating.average_rating,
        "num_votes": rating.num_votes
    }


def _principal_to_dict(
        principal: ImdbPrincipal,
        names: Dict[str, ImdbPerson]
) -> Dict[str, Any]:
    """Renders an :class:`ImdbPrincipal` with its resolved person nested under `person`."""

    return {
        "nconst": principal.nconst,
        "ordering": principal.ordering,
        "category": principal.category,
        "job": principal.job,
        "characters": list(principal.characters),
        "person": _person_to_dict(names.get(principal.nconst))
    }


def _person_to_dict(person: Optional[ImdbPerson]) -> Optional[Dict[str, Any]]:
    """Renders an :class:`ImdbPerson` as a dict (the redundant `nconst` is dropped)."""

    if person is None:
        return None

    return {
        "primary_name": person.primary_name,
        "birth_year": person.birth_year,
        "death_year": person.death_year,
        "primary_profession": list(person.primary_profession)
    }
