# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Environment setup:**
```bash
uv venv .venv && source .venv/bin/activate  # Create and activate `.venv`
uv sync                                     # Install all dependencies
```

**Run the project:**
```bash
python src/main.py
```

**Docker (Neo4j):**
```bash
make up    # start Neo4j container (docker/docker-compose.yml + .env)
make down  # stop Neo4j container
```

**Linting:**
```bash
pylint src/
```

## Architecture

Cinematica is **currently** a knowledge graph pipeline that ingests IMDb and TMDB film data into Neo4j for semantic exploration and agentic AI querying.

**Data flow:**
1. IMDb `.tsv.gz` datasets (in `datasets/`) are streamed row-by-row via `src/imdb/loader.py` to avoid loading large files into memory.
2. Filter predicates in `src/imdb/filters.py` classify records by `titleType` (e.g., `movie`, `short`).
3. `src/clients/tmdb/client.py` (`TmdbClient`) enriches filtered records via the TMDB API. It is fully async (`httpx.AsyncClient`), caps concurrency at 20 simultaneous connections via `asyncio.Semaphore`, and retries transient HTTP errors (429, 5xx) with exponential back-off using `tenacity`.
4. API responses are parsed into frozen dataclasses in `src/models/tmdb.py` (`TmdbMovie`, `Genre`, `SpokenLanguage`).
5. Processed data is written into Neo4j (Bolt on port 7687, Browser on port 7474).

**IMDb datasets used** (downloaded 2026-02-15, not committed to the repo — must be sourced from `https://datasets.imdbws.com`):
- `name.basics.tsv.gz` — people/persons
- `title.basics.tsv.gz` — title/film metadata
- `title.principals.tsv.gz` — person↔title relationships
- `title.ratings.tsv.gz` — ratings

**Key env vars** (see `.env.example`):
- `TMDB_API_KEY`, `TMDB_API_READ_ACCESS_TOKEN` — TMDB API access (base URL is hardcoded in `TmdbClient`)
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` — Neo4j connection

**Package management:** `uv` (not pip). Python 3.14 is required (see `.python-version`).

## Coding Best Practices

Coding conventions and mandatory rules live in [`.claude/rules/coding.md`](.claude/rules/coding.md). Follow them when writing or modifying any code in this repository.
