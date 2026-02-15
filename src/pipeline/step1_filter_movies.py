from pathlib import Path
from src.imdb.filters import is_movie, is_short
from src.imdb.loader import stream_title_basics


def run(file_path: Path):
    print("[STEP 1] Running pipeline..." + "\n")
    movie_count: int=0
    short_count: int=0
    total_count: int=0

    for record in stream_title_basics(file_path):
        total_count += 1

        if (is_movie(record)):
            movie_count += 1

        if (is_short(record)):
            short_count += 1

    print("Movies:", movie_count)
    print("Shorts:", short_count)
    print("TV Episodes:", total_count - (movie_count + short_count))
    print("Total records:", total_count)
