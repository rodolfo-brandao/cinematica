# Instructions

This is the entry point file that provides guidance and context in this repository when working with Claude Code.

Regarding the project, Cinematica is a knowledge graph pipeline that ingests IMDb and TMDB film data into Neo4j, plus an agent layer that answers natural-language questions over that graph via a LangGraph pipeline: a frontier Claude model reasons over the graph through grounding tools (schema introspection, full-text entity resolution, read-only Cypher, and vector search), exposed through a FastAPI endpoint. Local Ollama embeddings back the vector index.

## Invariants

Consult these files for important details regarding this repo:
- `docs/commands.md` — useful CLI commands for different contexts
- `docs/project-structure.md` — module layout, datasets and architecture
- `docs/rules.md` — mandatory code-writing conventions
- `docs/subagents.md` — agents available under .claude/agents/

## Package Management

- Use [`uv`](https://docs.astral.sh/uv/) (not pip)
- Python 3.14 is required (see [`.python-version`](/.python-version))

## Anthropic API (reasoning)

The agent's reasoning stages call a frontier Claude model via the Anthropic API.

- Set `ANTHROPIC_API_KEY` in `.env`.
- `ANTHROPIC_MODEL` selects the model (defaults to `claude-sonnet-5`).

The grounding tools carry most of the reasoning load, so Sonnet is the
starting point and `claude-opus-4-8` is an escalation to justify with
evidence — swapping `ANTHROPIC_MODEL` makes a model ablation a one-line
change.

## Key env vars

See [`.env.example`](/.env.example).

### TMDb API

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