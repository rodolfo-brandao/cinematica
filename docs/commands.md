# Commands

This file provides useful CLI commands for different contexts in this repository.

## Python

### Environment Setup

- `uv venv .venv` — Create virtual environment
- `source .venv/bin/activate` — Activate virtual environment
- `uv sync` — Install dependencies

### Linting

Use [Pylint](https://www.pylint.org/).

- `pylint src/`

## Docker

See [`Makefile`](/Makefile).

- `make up` — Start Neo4j container (docker/docker-compose.yml + .env)
- `make down` — Stop Neo4j container
- `make api` — Run the FastAPI agent API (`uvicorn` with reload)

## Ollama (embeddings)

Ollama serves the local embedding model used to build and query the Neo4j
vector index for semantic (thematic) search — it no longer runs the agent.

- `brew install ollama` — Install Ollama
- `make ollama-up` — Start the Ollama server as a background service
- `make ollama-down` — Stop the Ollama server
- `ollama pull nomic-embed-text` — Pull the embedding model (set
  `OLLAMA_EMBED_MODEL` in `.env` to match)

## Run the Project

Run as a module from the repository root (required for `src.*` imports):

- `python -m src.main` — full pipeline run
- `python -m src.main 200` — batched run: stop after 200 new shards (~100k movies)
- `make api` (or `python -m src.api.app`) — run the agent API, serving `POST /query`