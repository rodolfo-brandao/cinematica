"""
This is the application entrypoint.

To run, on root folder:
1. Create virtual environment:              $ python3 -m venv .venv
2. Activate it:                             $ source .venv/bin/activate
3. Install dependencies:                    $ pip install -r requirements.txt
4. If new dependencies were installed:      $ pip freeze > requirements.txt
5. Run the application:                     $ python3 -m src.main
"""


from pathlib import Path
from src.pipeline.step1_filter_movies import run


if __name__ == "__main__":
    imdb_title_basics_file_path = Path("datasets/title.basics.tsv.gz")
    run(imdb_title_basics_file_path)
