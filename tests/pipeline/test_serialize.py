"""Unit tests for src.pipeline.serialize."""

from src.models.imdb import ImdbMovie, ImdbRating, ImdbPrincipal, ImdbPerson
from src.models.tmdb import (
    Collection,
    Genre,
    Keyword,
    ProductionCompany,
    SpokenLanguage,
    TmdbMovie,
)
from src.pipeline.serialize import to_movie_record


def _make_movie() -> ImdbMovie:
    """Builds a minimal, well-known IMDb movie fixture."""

    return ImdbMovie(
        tconst="tt0137523",
        primary_title="Fight Club",
        original_title="Fight Club",
        is_adult=False,
        start_year=1999,
        runtime_min=139,
        genres=["Drama"]
    )


def test_to_movie_record_full_join():
    """All four indexes join into one nested record."""

    movie = _make_movie()
    rating = ImdbRating(tconst="tt0137523", average_rating=8.8, num_votes=2_000_000)
    principals = [
        ImdbPrincipal(
            tconst="tt0137523",
            nconst="nm0000093",
            ordering=1,
            category="actor",
            job=None,
            characters=["Tyler Durden"]
        )
    ]
    names = {
        "nm0000093": ImdbPerson(
            nconst="nm0000093",
            primary_name="Brad Pitt",
            birth_year=1963,
            death_year=None,
            primary_profession=["actor", "producer"]
        )
    }

    record = to_movie_record(movie, rating, principals, names, tmdb=None)

    assert record["tconst"] == "tt0137523"
    assert record["genres"] == ["Drama"]
    assert record["rating"] == {"average_rating": 8.8, "num_votes": 2_000_000}
    assert len(record["principals"]) == 1
    assert record["principals"][0]["person"]["primary_name"] == "Brad Pitt"
    assert record["tmdb"] is None


def test_to_movie_record_handles_missing_rating_and_unresolved_person():
    """Missing rating and unresolved `nconst` serialize as `None`."""

    movie = _make_movie()
    principals = [
        ImdbPrincipal(
            tconst="tt0137523",
            nconst="nm9999999",
            ordering=1,
            category="actor",
            job=None,
            characters=[]
        )
    ]

    record = to_movie_record(movie, rating=None, principals=principals, names={}, tmdb=None)

    assert record["rating"] is None
    assert record["principals"][0]["person"] is None


def test_to_movie_record_nests_tmdb_data():
    """The TMDb dataclass nests as plain dicts under `tmdb`."""

    movie = _make_movie()
    tmdb = TmdbMovie(
        tmdb_id=550,
        imdb_id="tt0137523",
        is_adult=False,
        budget=63_000_000,
        genres=[Genre(id=18, name="Drama")],
        origin_country=["US"],
        original_language="en",
        original_title="Fight Club",
        overview="An insomniac office worker...",
        popularity=50.0,
        release_date="1999-10-15",
        revenue=100_853_753,
        runtime_min=139,
        spoken_languages=[SpokenLanguage(english_name="English", iso_639_1="en", name="English")],
        status="Released",
        tagline="Mischief. Mayhem. Soap.",
        title="Fight Club",
        has_video=False,
        vote_average=8.4,
        vote_count=25_000,
        production_companies=[
            ProductionCompany(id=508, name="Regency", origin_country="US")
        ],
        belongs_to_collection=Collection(id=1, name="Fight Club Collection"),
        keywords=[Keyword(id=851, name="dual identity")]
    )

    record = to_movie_record(movie, rating=None, principals=[], names={}, tmdb=tmdb)

    assert record["tmdb"]["tmdb_id"] == 550
    assert record["tmdb"]["genres"] == [{"id": 18, "name": "Drama"}]
    assert record["tmdb"]["spoken_languages"] == [
        {"english_name": "English", "iso_639_1": "en", "name": "English"}
    ]
    assert record["tmdb"]["keywords"] == [{"id": 851, "name": "dual identity"}]
    assert record["tmdb"]["belongs_to_collection"] == {
        "id": 1, "name": "Fight Club Collection"
    }
