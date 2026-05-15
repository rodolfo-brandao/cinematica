# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Note on AI Usage

Per the project's explicit policy (see README), Claude Code is used **strictly as an analysis and insights tool** — for understanding codebases, documentation, and trade-offs. It must **never generate code** that enters this repository. All code is written by hand by the author.

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
Pylint is configured via `.vscode/settings.json` to disable C0114 (missing module docstring) and C0115 (missing class docstring).

## Architecture

Cinematica is a knowledge graph pipeline that ingests IMDb and TMDB film data into Neo4j for semantic exploration and agentic AI querying.

**Data flow:**
1. IMDb `.tsv.gz` datasets (in `datasets/`) are streamed row-by-row via `src/imdb/loader.py` to avoid loading large files into memory.
2. Filter predicates in `src/imdb/filters.py` classify records by `titleType` (e.g., `movie`, `short`).
3. `src/pipelines/tmdb/client.py` connects to the TMDB API to enrich film records with additional metadata.
4. Processed data is written into Neo4j (Bolt on port 7687, Browser on port 7474).

**IMDb datasets used** (downloaded 2026-02-15, not committed to the repo — must be sourced from `https://datasets.imdbws.com`):
- `name.basics.tsv.gz` — people/persons
- `title.basics.tsv.gz` — title/film metadata
- `title.principals.tsv.gz` — person↔title relationships
- `title.ratings.tsv.gz` — ratings

**Key env vars** (see `.env.example`):
- `TMDB_API_BASE_URL`, `TMDB_API_KEY`, `TMDB_API_READ_ACCESS_TOKEN` — TMDB API access
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` — Neo4j connection

**Package management:** `uv` (not pip). Python 3.14 is required (see `.python-version`).
