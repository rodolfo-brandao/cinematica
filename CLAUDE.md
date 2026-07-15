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
- `make api` — Run the FastAPI agent API (`uvicorn` with reload)

### Anthropic (reasoning)

The agent's reasoning stages call a frontier Claude model via the Anthropic API.

- Set `ANTHROPIC_API_KEY` in `.env`.
- `ANTHROPIC_MODEL` selects the model (defaults to `claude-sonnet-5`).

The grounding tools carry most of the reasoning load, so Sonnet is the
starting point and `claude-opus-4-8` is an escalation to justify with
evidence — swapping `ANTHROPIC_MODEL` makes a model ablation a one-line
change.

### Ollama (embeddings)

Ollama serves the local embedding model used to build and query the Neo4j
vector index for semantic (thematic) search — it no longer runs the agent.

- `brew install ollama` — Install Ollama
- `brew services start ollama` — Start the Ollama server as a background service
- `ollama pull nomic-embed-text` — Pull the embedding model (set
  `OLLAMA_EMBED_MODEL` in `.env` to match)

### Linting

Use [Pylint](https://www.pylint.org/).

- `pylint src/`

### Run the Project

Run as a module from the repository root (required for `src.*` imports):

- `python -m src.main` — full pipeline run
- `python -m src.main 200` — batched run: stop after 200 new shards (~100k movies)
- `make api` (or `python -m src.api.app`) — run the agent API, serving `POST /query`

## Architecture

Cinematica is a knowledge graph pipeline that ingests IMDb and TMDB film data into Neo4j, plus an agent layer that answers natural-language questions over that graph via a LangGraph pipeline: a frontier Claude model reasons over the graph through grounding tools (schema introspection, full-text entity resolution, read-only Cypher, and vector search), exposed through a FastAPI endpoint. Local Ollama embeddings back the vector index.

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
4. API responses are parsed into frozen dataclasses in `src/models/tmdb.py` (`TmdbMovie`, `Genre`, `SpokenLanguage`, `ProductionCompany`, `Collection`, `Keyword`). The `/movie/{id}` call uses `append_to_response=keywords`.
5. `src/pipeline/load.py` (`load_movies`) batches the consolidated JSONL
   records into Neo4j (Bolt on port 7687, Browser on port 7474) via
   `src/clients/neo4j/client.py` (`Neo4jClient`), `MERGE`-ing every
   relationship-worthy dimension as a first-class node so re-runs are
   idempotent: `Movie`, `Person`, `Genre`, `Language` (`SPOKEN_IN`),
   `Country` (`PRODUCED_IN`), `ProductionCompany` (`PRODUCED_BY`),
   `Keyword` (`HAS_KEYWORD`) and `Collection` (`PART_OF_COLLECTION`).
6. `src/pipeline/embed.py` (`embed_movie_overviews`) embeds each movie
   `overview` via local Ollama (`src/clients/ollama/client.py`) and stores
   the vector on `Movie.overview_embedding`; the run is resumable (only
   un-embedded movies are fetched). `ensure_constraints` /
   `ensure_fulltext_indexes` / `ensure_vector_index` back exact lookups,
   fuzzy entity resolution, and semantic search respectively.

### Agent Flow

1. `src/api/app.py` exposes a stateless `POST /query` endpoint
   (FastAPI), accepting `{"question": "..."}` and returning
   `{"question": "...", "answer": "..."}`. It opens one `Neo4jClient`,
   one `AnthropicClient` and one `OllamaClient` at startup (FastAPI
   `lifespan`) and reuses them across requests.
2. `src/agents/agent.py` (`answer_question`) is a thin wrapper that
   builds the initial pipeline state and invokes the compiled LangGraph
   pipeline from `src/agents/graph.py`, passing the three clients
   through per-invocation via `RunnableConfig` rather than the graph's
   state.
3. `src/agents/graph.py` defines the pipeline as five stages over
   `src/agents/state.py`'s `AgentState`, each driven by Claude
   (`src/clients/anthropic/client.py`, `AnthropicClient`) with the
   grounding tools in `src/agents/tools.py`:
   - `plan` classifies the question (multi-hop / analytical / thematic /
     hybrid) and names the entities to resolve.
   - `resolve` resolves each named person/movie to its canonical graph
     node via the full-text-backed `resolve_entity` tool, fixing the
     exact-match fragility of matching names literally.
   - `query` is a bounded Claude tool-use loop over `get_schema`,
     `run_cypher` and `vector_search`: the model writes/repairs Cypher
     against real `EXPLAIN`/execution errors (`run_cypher` rejects write
     clauses and relies on `execute_read`'s READ access mode as the
     authoritative guard) and uses vector search for thematic questions.
   - `verify` rejects an empty result outright (a deterministic guard),
     then has Claude judge whether the rows satisfy every constraint; a
     rejection loops back to `query` (bounded by `_MAX_QUERY_ATTEMPTS`).
   - `compose` writes the final answer strictly from the verified rows.
   - Exhausting the retry budget routes to a `fallback` node instead of
     composing an answer from unverified/failed data.

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
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── agent.py                  # Entry point (answer_question)
│   │   ├── graph.py                  # LangGraph pipeline nodes + wiring
│   │   ├── schema.py                 # Graph schema description prompt
│   │   ├── state.py                  # AgentState TypedDict
│   │   └── tools.py                  # Grounding tools (Claude tool-use)
│   ├── api/
│   │   ├── __init__.py
│   │   └── app.py                    # FastAPI app, POST /query
│   ├── clients/
│   │   ├── anthropic/
│   │   │   ├── __init__.py
│   │   │   └── client.py             # Async Anthropic (Claude) client
│   │   ├── neo4j/
│   │   │   ├── __init__.py
│   │   │   └── client.py             # Sync Neo4j Bolt client
│   │   ├── ollama/
│   │   │   ├── __init__.py
│   │   │   └── client.py             # Async Ollama embeddings client
│   │   └── tmdb/
│   │       ├── __init__.py
│   │       └── client.py             # Async TMDb API client
│   ├── imdb/
│   │   ├── __init__.py
│   │   ├── filters.py                # titleType filter predicates
│   │   └── loader.py                 # Row-by-row .tsv.gz streaming
│   ├── models/
│   │   ├── __init__.py
│   │   ├── agent.py                  # Frozen dataclasses for /query I/O
│   │   ├── imdb.py                   # Frozen dataclasses for IMDb records
│   │   └── tmdb.py                   # Frozen dataclasses for TMDb data
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── compile.py                # Compile .tsv.gz datasets into indexes
│   │   ├── consolidate.py            # Merge enriched JSONL shards
│   │   ├── embed.py                  # Embed overviews into the vector index
│   │   ├── enrich.py                 # TMDb enrichment into JSONL shards
│   │   ├── load.py                   # Batched loading into Neo4j
│   │   └── serialize.py              # Join IMDb/TMDb into JSON-safe records
│   ├── __init__.py
│   ├── logger.py                     # Logging configuration
│   └── main.py                       # Entry point
├── tests/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── test_agent.py
│   │   ├── test_graph.py
│   │   └── test_tools.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── test_app.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── test_compile.py
│   │   ├── test_consolidate.py
│   │   ├── test_enrich.py
│   │   ├── test_load.py
│   │   └── test_serialize.py
│   └── __init__.py
├── .env.example
├── .python-version                   # Python 3.14
├── CLAUDE.md
├── LICENSE
├── Makefile                          # make up / down / api
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

### Anthropic

- `ANTHROPIC_API_KEY` — API key for the reasoning model
- `ANTHROPIC_MODEL` — Claude model ID; defaults to `claude-sonnet-5`

### Ollama

- `OLLAMA_BASE_URL` — Ollama server URL; defaults to `http://localhost:11434` if unset
- `OLLAMA_EMBED_MODEL` — Embedding model name; defaults to `nomic-embed-text`

## Package Management

- Use [`uv`](https://docs.astral.sh/uv/) (not pip)
- Python 3.14 is required (see `.python-version`)
