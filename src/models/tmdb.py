from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Genre:
    id: int
    name: str


@dataclass(frozen=True)
class SpokenLanguage:
    english_name: str
    iso_639_1: str
    name: str


@dataclass(frozen=True)
class Movie:
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
    is_softcore: bool
    spoken_languages: List[SpokenLanguage]
    status: str
    tagline: str
    title: str
    has_video: bool
    vote_avarage: float
    vote_count: int
