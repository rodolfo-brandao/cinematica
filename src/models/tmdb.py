"""Frozen dataclasses modeling TMDb API movie data."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Genre:
    """A genre from a movie."""
    id: int
    name: str


@dataclass(frozen=True)
class SpokenLanguage:
    "The language spoken in a movie."
    english_name: str
    iso_639_1: str
    name: str


@dataclass(frozen=True)
class ProductionCompany:
    """A production company credited on a movie."""
    id: int
    name: str
    origin_country: str


@dataclass(frozen=True)
class Collection:
    """A collection (franchise) a movie belongs to."""
    id: int
    name: str


@dataclass(frozen=True)
class Keyword:
    """A thematic keyword tagged on a movie."""
    id: int
    name: str


# Mirrors the flat shape of the TMDb `/movie/{id}` payload, hence the field count:
@dataclass(frozen=True)
# pylint: disable-next=too-many-instance-attributes
class TmdbMovie:
    """Movie details from the TMDb API."""
    tmdb_id: int
    imdb_id: str
    is_adult: bool
    budget: int
    genres: List[Genre]
    origin_country: List[str]
    original_language: str
    original_title: str
    overview: str
    popularity: float
    release_date: str
    revenue: int
    runtime_min: int
    spoken_languages: List[SpokenLanguage]
    status: str
    tagline: str
    title: str
    has_video: bool
    vote_average: float
    vote_count: int
    production_companies: List[ProductionCompany]
    belongs_to_collection: Optional[Collection]
    keywords: List[Keyword]
