# Cinematica

![License: MIT](https://img.shields.io/badge/License-MIT-3DA639?logo=opensourceinitiative&logoColor=white)
![Python version](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![Neo4j version](https://img.shields.io/badge/Neo4j-2026.04.0-4581C3?logo=neo4j&logoColor=white)
![uv version](https://img.shields.io/badge/uv-0.11.16-DE5FE9?logo=uv&logoColor=white)
![Claude Code](https://img.shields.io/badge/Claude-Code-D97757?logo=claude&logoColor=white)
[![Pylint](https://github.com/rodolfo-brandao/cinematica/actions/workflows/pylint.yml/badge.svg)](https://github.com/rodolfo-brandao/cinematica/actions/workflows/pylint.yml)

## Overview

An agentic AI-powered Knowledge Graph for semantic exploration and intelligent insights over film data.

> [!NOTE]
> Regarding the use of Artificial Intelligence: when necessary, LLMs are used for code generation. However, all generated code is **always** reviewed by me, [@rodolfo-brandao](https://github.com/rodolfo-brandao), author and sole contributor of this repository.
>
> What made me adopt this approach? [This post](https://x.com/karpathy/status/2015883857489522876) by [Andrej Karpathy](https://github.com/karpathy) and [this note](https://www-cs-faculty.stanford.edu/~knuth/papers/claude-cycles.pdf) from none other than [Donald Knuth](https://en.wikipedia.org/wiki/Donald_Knuth).
>
> In Karpathy's own words: _It hurts the ego a bit_ :hurtrealbad:
>
> For everything else, [Claude Code](https://claude.ai/code) is used as an analysis and insights tool — for better understanding codebases, documentation, and trade-offs, as well as supporting decision-making.

## Initial Setup

### Requirements

- [Docker](https://www.docker.com/get-started/)
- [Python 3.14](https://www.python.org/downloads/release/python-3140/)
- [uv](https://docs.astral.sh/uv/)

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

3. Install all dependencies in the current `.venv`:
```bash
uv sync
```

4. Copy `.env.example` to `.env` and fill in the required values:
```bash
cp .env.example .env
```

> [!IMPORTANT]
> _The `NEO4J_PASSWORD` variable is used by the Docker Compose file to set the Neo4j database password._
>
> _Make sure it is set before starting the container._

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