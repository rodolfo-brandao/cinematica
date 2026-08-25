# Project Structure

## Datasets

This project uses IMDb non-commercial datasets and are not committed to the repo due to licensing issues. However, always keep in mind that they will be available **locally** in the `datasets/` directory. Therefore, read the data from there.

- `name.basics.tsv.gz` — People/persons
- `title.basics.tsv.gz` — Title/film metadata
- `title.principals.tsv.gz` — Person ↔ Title relationships
- `title.ratings.tsv.gz` — Ratings

For any further context needed, visit the official website: https://datasets.imdbws.com

## Data Flow
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

## Agent Flow

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

## File Structure

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