"""Unit tests for src.pipeline.compile."""

import gzip
from pathlib import Path
from typing import List

from src.pipeline.compile import (
    build_movie_index,
    build_ratings_index,
    build_principals_index,
    collect_nconsts,
    build_names_index
)


def _write_tsv_gz(path: Path, header: List[str], rows: List[List[str]]) -> None:
    """Writes a `.tsv.gz` fixture file with the given header and rows."""

    with gzip.open(filename=path, mode="wt", encoding="utf-8") as file:
        file.write("\t".join(header) + "\n")

        for row in rows:
            file.write("\t".join(row) + "\n")


def test_build_movie_index_filters_non_movies_and_normalizes_fields(tmp_path):
    """Only "movie" rows are kept; `\\N`, flags and lists are normalized."""

    file_path = tmp_path / "title.basics.tsv.gz"
    _write_tsv_gz(
        file_path,
        header=[
            "tconst", "titleType", "primaryTitle", "originalTitle",
            "isAdult", "startYear", "endYear", "runtimeMinutes", "genres"
        ],
        rows=[
            ["tt0000001", "movie", "Movie One", "Movie One",
             "0", "1999", "\\N", "139", "Drama,Thriller"],
            ["tt0000002", "short", "Short One", "Short One",
             "0", "2000", "\\N", "5", "Comedy"],
            ["tt0000003", "movie", "Movie Two", "Movie Two",
             "1", "\\N", "\\N", "\\N", "\\N"]
        ]
    )

    index = build_movie_index(file_path)

    assert set(index) == {"tt0000001", "tt0000003"}

    movie_one = index["tt0000001"]
    assert movie_one.primary_title == "Movie One"
    assert movie_one.is_adult is False
    assert movie_one.start_year == 1999
    assert movie_one.runtime_min == 139
    assert movie_one.genres == ["Drama", "Thriller"]

    movie_two = index["tt0000003"]
    assert movie_two.is_adult is True
    assert movie_two.start_year is None
    assert movie_two.runtime_min is None
    assert movie_two.genres == []


def test_build_ratings_index_filters_to_movie_ids(tmp_path):
    """Ratings for `tconst`s outside the movie set are dropped."""

    file_path = tmp_path / "title.ratings.tsv.gz"
    _write_tsv_gz(
        file_path,
        header=["tconst", "averageRating", "numVotes"],
        rows=[
            ["tt0000001", "8.8", "2000000"],
            ["tt0000002", "5.0", "100"]
        ]
    )

    ratings = build_ratings_index(file_path, movie_ids={"tt0000001"})

    assert set(ratings) == {"tt0000001"}
    assert ratings["tt0000001"].average_rating == 8.8
    assert ratings["tt0000001"].num_votes == 2000000


def test_build_principals_index_groups_by_tconst_and_parses_characters(tmp_path):
    """Principals group under their movie; `characters` JSON is parsed."""

    file_path = tmp_path / "title.principals.tsv.gz"
    _write_tsv_gz(
        file_path,
        header=["tconst", "ordering", "nconst", "category", "job", "characters"],
        rows=[
            ["tt0000001", "1", "nm0000001", "actor", "\\N", '["Tyler Durden"]'],
            ["tt0000001", "2", "nm0000002", "director", "\\N", "\\N"],
            ["tt0000002", "1", "nm0000003", "actor", "\\N", "\\N"]
        ]
    )

    principals = build_principals_index(file_path, movie_ids={"tt0000001"})

    assert set(principals) == {"tt0000001"}
    assert len(principals["tt0000001"]) == 2
    assert principals["tt0000001"][0].characters == ["Tyler Durden"]
    assert principals["tt0000001"][1].characters == []

    assert collect_nconsts(principals) == {"nm0000001", "nm0000002"}


def test_build_names_index_filters_to_referenced_ids(tmp_path):
    """Only people referenced by a movie principal are indexed."""

    file_path = tmp_path / "name.basics.tsv.gz"
    _write_tsv_gz(
        file_path,
        header=[
            "nconst", "primaryName", "birthYear", "deathYear",
            "primaryProfession", "knownForTitles"
        ],
        rows=[
            ["nm0000001", "Brad Pitt", "1963", "\\N", "actor,producer", "\\N"],
            ["nm0000099", "Unreferenced Person", "1970", "\\N", "actor", "\\N"]
        ]
    )

    names = build_names_index(file_path, nconst_ids={"nm0000001"})

    assert set(names) == {"nm0000001"}
    person = names["nm0000001"]
    assert person.primary_name == "Brad Pitt"
    assert person.birth_year == 1963
    assert person.death_year is None
    assert person.primary_profession == ["actor", "producer"]
