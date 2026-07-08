# CLAUDE.md

This file provides guidance and context to [Claude Code](https://claude.com/product/claude-code) when working with it in this repository.

## Coding Best Practices

Coding conventions and mandatory rules live in [`.claude/rules/code-writing.md`](.claude/rules/code-writing.md). Follow them when writing or modifying any code in this repository.

## Commands

### Environment Setup

- `uv venv .venv` — Create virtual environment
- `source .venv/bin/activate` — Activate virtual environment
- `uv sync` — Install dependencies

### Docker

Use commands from [`Makefile`](/Makefile).

- `make up` — Start Neo4j container (docker/docker-compose.yml + .env)
- `make down` — Stop Neo4j container

### Linting

Use [Pylint](https://www.pylint.org/).

- `pylint src/`

### Run the Project

Run as a module from the repository root (required for `src.*` imports):

- `python -m src.main` — full pipeline run
- `python -m src.main 200` — batched run: stop after 200 new shards (~100k movies)

## Architecture

Cinematica is **currently** a knowledge graph pipeline that ingests IMDb and TMDB film data into Neo4j for semantic exploration and agentic AI querying.

### Datasets

This project uses IMDb non-commercial datasets and are not committed to the repo due to licensing issues. However, always keep in mind that they will be available **locally** in the `datasets/` directory. Therefore, read the data from there.

- `name.basics.tsv.gz` — People/persons
- `title.basics.tsv.gz` — Title/film metadata
- `title.principals.tsv.gz` — Person ↔ Title relationships
- `title.ratings.tsv.gz` — Ratings

For any further context needed, visit the official website: https://datasets.imdbws.com

### Data Flow
1. IMDb `.tsv.gz` datasets (in `datasets/`) are streamed row-by-row via `src/imdb/loader.py` to avoid loading large files into memory.
2. Filter predicates in `src/imdb/filters.py` classify records by `titleType` (e.g., `movie`, `short`).
3. `src/clients/tmdb/client.py` (`TmdbClient`) enriches filtered records via the TMDB API. It is fully async (`httpx.AsyncClient`), caps concurrency at 20 simultaneous connections via `asyncio.Semaphore`, and retries transient HTTP errors (429, 5xx) with exponential back-off using `tenacity`.
4. API responses are parsed into frozen dataclasses in `src/models/tmdb.py` (`TmdbMovie`, `Genre`, `SpokenLanguage`).
5. Processed data is written into Neo4j (Bolt on port 7687, Browser on port 7474).

## Project Structure

Version-controlled layout (unversioned files such as `.venv/`, `.env`, and the IMDb datasets are omitted):

```
.
├── .claude/
│   ├── agents/
│   │   └── code-reviewer.md          # Code review subagent
│   └── rules/
│       └── code-writing.md           # Mandatory coding conventions
├── .github/
│   └── workflows/
│       └── pylint.yml                # CI: Pylint
├── datasets/
│   └── README.md                     # IMDb datasets go here (not committed)
├── docker/
│   └── docker-compose.yml            # Neo4j service
├── src/
│   ├── clients/
│   │   └── tmdb/
│   │       ├── __init__.py
│   │       └── client.py             # Async TMDb API client
│   ├── imdb/
│   │   ├── __init__.py
│   │   ├── filters.py                # titleType filter predicates
│   │   └── loader.py                 # Row-by-row .tsv.gz streaming
│   ├── models/
│   │   ├── __init__.py
│   │   ├── imdb.py                   # Frozen dataclasses for IMDb records
│   │   └── tmdb.py                   # Frozen dataclasses for TMDb data
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── compile.py                # Compile .tsv.gz datasets into indexes
│   │   ├── consolidate.py            # Merge enriched JSONL shards
│   │   ├── enrich.py                 # TMDb enrichment into JSONL shards
│   │   └── serialize.py              # Join IMDb/TMDb into JSON-safe records
│   ├── __init__.py
│   ├── logger.py                     # Logging configuration
│   └── main.py                       # Entry point
├── tests/
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── test_compile.py
│   │   ├── test_consolidate.py
│   │   ├── test_enrich.py
│   │   └── test_serialize.py
│   └── __init__.py
├── .env.example
├── .python-version                   # Python 3.14
├── CLAUDE.md
├── LICENSE
├── Makefile                          # make up / make down
├── README.md
├── pyproject.toml                    # Project metadata & dependencies
└── uv.lock
```

## Key env vars

See [`.env.example`](/.env.example).

### TMDb

Base URL is hardcoded in `TmdbClient`.

- `TMDB_API_KEY`
- `TMDB_API_READ_ACCESS_TOKEN`

### Neo4j

- `NEO4J_URI` — Neo4j connection
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`

## Package Management

- Use [`uv`](https://docs.astral.sh/uv/) (not pip)
- Python 3.14 is required (see `.python-version`)
