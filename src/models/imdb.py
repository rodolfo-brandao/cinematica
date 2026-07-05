"""Frozen dataclasses modeling IMDb dataset records."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ImdbMovie:
    """A movie title record from the IMDb `title.basics` dataset."""
    tconst: str                 # IMDb ID (tt --prefixed string)
    primary_title: str
    original_title: str
    is_adult: bool
    start_year: Optional[int]
    runtime_min: Optional[int]
    genres: List[str]


@dataclass(frozen=True)
class ImdbRating:
    """A rating record from the IMDb `title.ratings` dataset."""
    tconst: str                 # IMDb ID (tt --prefixed string)
    average_rating: float
    num_votes: int


@dataclass(frozen=True)
class ImdbPrincipal:
    """A cast/crew membership from the IMDb `title.principals` dataset."""
    tconst: str                 # IMDb ID (tt --prefixed string)
    nconst: str                 # Name/person ID (nm --prefixed string)
    ordering: Optional[int]
    category: Optional[str]
    job: Optional[str]
    characters: List[str]


@dataclass(frozen=True)
class ImdbPerson:
    """A person record from the IMDb `name.basics` dataset."""
    nconst: str                 # Name/person ID (nm --prefixed string)
    primary_name: str
    birth_year: Optional[int]
    death_year: Optional[int]
    primary_profession: List[str]
