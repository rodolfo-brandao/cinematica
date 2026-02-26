from pathlib import Path
from src.pipeline.step1_filter_movies import run


if __name__ == "__main__":
    imdb_title_basics_file_path = Path("datasets/title.basics.tsv.gz")
    run(imdb_title_basics_file_path)
