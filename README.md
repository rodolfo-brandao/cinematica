# Cinematica

![License: MIT](https://img.shields.io/badge/License-MIT-3DA639?logo=opensourceinitiative&logoColor=white)
[![CI](https://github.com/rodolfo-brandao/cinematica/actions/workflows/ci.yml/badge.svg)](https://github.com/rodolfo-brandao/cinematica/actions/workflows/ci.yml)

## Overview

Cinematica is an agentic AI-powered Knowledge Graph for semantic exploration and intelligent insights over film data.

It ingests [IMDb non-commercial datasets](https://datasets.imdbws.com) and enriches each title via the [TMDB](https://www.themoviedb.org) API, then loads the consolidated data into a [Neo4j](https://neo4j.com) graph — modeling movies, people, genres, languages, countries, production companies, keywords, and collections as nodes and their relationships as edges.

On top of that graph sits an agent layer: a [LangGraph](https://langchain-ai.github.io/langgraph/) pipeline — plan, entity resolution, querying, verification, and answer composition — in which a frontier [Claude](https://www.anthropic.com/claude) model reasons over the graph through grounding tools (schema introspection, fuzzy full-text entity resolution, validated read-only Cypher, and [Ollama](https://ollama.com)-embedded vector search), exposed through a [FastAPI](https://fastapi.tiangolo.com) endpoint that answers natural-language questions about the film graph.

> [!NOTE]
> Regarding the use of Artificial Intelligence: when necessary, LLMs are used for code generation. However, all generated code is **always** reviewed by me, [@rodolfo-brandao](https://github.com/rodolfo-brandao), author and sole contributor of this repository.
>
> For everything else, [Claude Code](https://claude.ai/code) is used as an analysis and insights tool — for better understanding codebases and documentation, as well as supporting decision-making.

## Tech Stack

| Technology | Role |
| --- | --- |
| [![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3140/) | Language runtime for the whole project, version 3.14 |
| [![Neo4j](https://img.shields.io/badge/Neo4j-4581C3?logo=neo4j&logoColor=white)](https://neo4j.com) | Graph database storing movies, people, genres, languages, countries, production companies, keywords, and collections as nodes and their relationships as edges; also hosts the vector index used for semantic search |
| [![Ollama](https://img.shields.io/badge/Ollama-000000?logo=ollama&logoColor=white)](https://ollama.com) | Serves the local embedding model (`nomic-embed-text` by default) used to embed movie overviews and query themes for vector search |
| [![LangGraph](https://img.shields.io/badge/LangGraph-7FC8FF?logo=langgraph&logoColor=white)](https://langchain-ai.github.io/langgraph/) | Orchestrates the agent's reasoning pipeline as a graph of stages: plan, entity resolution, querying, verification, and answer composition |
| [![Claude](https://img.shields.io/badge/Claude-D97757?logo=claude&logoColor=white)](https://www.anthropic.com/claude) | Frontier LLM reasoning (Anthropic API) over the graph at each pipeline stage, driving tool use for schema introspection, entity resolution, Cypher generation/repair, and final answer composition |
| [![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com) | Exposes the film-graph agent over HTTP |

## Initial Setup

### Requirements

- [x] [Anthropic API key](https://console.anthropic.com)
- [x] [Docker](https://www.docker.com/get-started/)
- [x] [Ollama](https://ollama.com/download)
- [x] [Python 3.14](https://www.python.org/downloads/release/python-3140/)
- [x] [uv](https://docs.astral.sh/uv/)

### Repository Setup

1. Clone this repository & navigate to its root folder:
```bash
git clone https://github.com/rodolfo-brandao/cinematica.git && \
cd cinematica
```

2. Create `.venv` & activate it:
```bash
uv venv .venv && \
source .venv/bin/activate
```

3. Install all dependencies in the current environment:
```bash
uv sync
```

4. Copy `.env.example` to `.env` and fill in the required values:
```bash
cp .env.example .env
```

### Neo4j Database

The Neo4j database runs as a Docker container. After configuring `.env`, start it with:
```bash
make up
```

This spins up the `cinematica-neo4j` container with:
- Neo4j Browser: `http://localhost:7474`
- Bolt Protocol: `bolt://localhost:7687`

To stop the container:
```bash
make down
```

### Anthropic

The agent's reasoning stages call a frontier [Claude](https://www.anthropic.com/claude) model via the Anthropic API. Set `ANTHROPIC_API_KEY` in `.env`; `ANTHROPIC_MODEL` selects the model and defaults to [`claude-sonnet-5`](https://docs.claude.com/en/docs/about-claude/models/overview).

Because the grounding tools (schema introspection, entity resolution, error-repair loops) carry most of the reasoning load, Sonnet is the starting point rather than an assumed ceiling — raising `ANTHROPIC_MODEL` to `claude-opus-4-8` is a one-line change, which makes a model ablation cheap to run.

### Ollama

[Ollama](https://ollama.com) serves the **local** embedding model that powers semantic (thematic) search: overviews are embedded into a Neo4j vector index at load time, and query themes are embedded at request time. Install it, start it as a background service, and pull the embedding model:
```bash
brew install ollama && \
brew services start ollama && \
ollama pull nomic-embed-text
```

The chosen embedding model for this experiment was [`nomic-embed-text`](https://ollama.com/library/nomic-embed-text).

To stop Ollama background service:
```bash
brew services stop ollama
```

> [!IMPORTANT]
> _The `NEO4J_PASSWORD` variable is used by the Docker Compose file to set the Neo4j database password._
>
> _Make sure it is set before starting the container._
>
> _Also, set `OLLAMA_EMBED_MODEL` in `.env` to the name of the pulled model (e.g. `nomic-embed-text`)._
>
> _`OLLAMA_BASE_URL` defaults to `http://localhost:11434` if left unset._

## Running the Project

### Pipeline

With the IMDb datasets in `datasets/` (see [`datasets/README.md`](datasets/README.md)) and `.env` configured, run the full ingestion pipeline — streams the IMDb datasets, enriches each movie via TMDb, and loads the result into Neo4j:
```bash
python -m src.main
```

To stop after a fixed number of new shards instead (e.g. a first, partial run of ~100k movies):
```bash
python -m src.main 200
```

### Agent API

With Neo4j loaded (see above), Ollama running, and `ANTHROPIC_API_KEY` set, start the agent API:
```bash
make api
```

Then ask a natural-language question about any film:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me thrillers directed by someone who worked with Denis Villeneuve, released after 2015, with high critical reception."}'
```