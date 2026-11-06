# Transferring the Neo4j Database Between Computers

This guide moves a fully populated Cinematica database from one computer
to another. Both computers run Neo4j with Docker Desktop through
[`docker/docker-compose.yml`](/docker/docker-compose.yml).

The transfer uses a Neo4j `.dump` file. The dump contains every node and
relationship, the `overview_embedding` vectors, and the constraints,
full-text indexes and vector index. You don't need to run the data
pipeline or re-embed the overviews on the target computer.

## Before You Start

- Docker Desktop is installed and running on both computers.
- The source database is fully populated: `python -m src.main` has
  finished loading and embedding.
- Run every command from the repository root.

## Part 1: Export on the Source Computer

### 1. Check the Neo4j version

While the container is running, run:

```bash
docker exec cinematica-neo4j neo4j --version
```

Write the version down (for example, `2026.06.0`). The commands below
call it `<version>`. Use this version on both computers, because the
Compose file uses `neo4j:latest`, which can point to different versions
on different computers.

### 2. Stop Neo4j

The Community edition can only dump a database while Neo4j is stopped.

```bash
make down
```

### 3. Create the dump

```bash
mkdir -p backups
docker run --rm \
  -v docker_neo4j_data:/data \
  -v "$PWD/backups":/backups \
  neo4j:<version> \
  neo4j-admin database dump neo4j --to-path=/backups
```

`docker_neo4j_data` is the Docker volume that holds the database. Don't
use `docker_neo4j_logs`, which only holds server logs. If Docker prints
`Unable to find image ... Pulling from library/neo4j`, that's expected:
it downloads the image for that version tag and then runs the dump.

When the command finishes, the dump is at `backups/neo4j.dump`. Confirm
it exists:

```bash
ls -lh backups/
```

### 4. Start Neo4j again

```bash
make up
```

### 5. Copy the dump to the target computer

Copy `backups/neo4j.dump` to the other computer with AirDrop, an external
drive or `scp`. Don't commit it to Git.

## Part 2: Import on the Target Computer

### 1. Set up the repository

Clone the repository and create `.env` from `.env.example`. The
`NEO4J_PASSWORD` you set in `.env` becomes this instance's password.
Users and passwords aren't included in the dump.

Put the dump inside the repository at `backups/neo4j.dump`.

### 2. Pin the Neo4j version

In [`docker/docker-compose.yml`](/docker/docker-compose.yml), replace
`neo4j:latest` with the version from Part 1:

```yaml
    image: neo4j:<version>
```

### 3. Initialize the database, then stop it

`make up` creates the `docker_neo4j_data` volume and sets the password
from `.env`.

```bash
make up
```

Wait until http://localhost:7474 loads, then stop Neo4j:

```bash
make down
```

### 4. Load the dump

```bash
docker run --rm \
  -v docker_neo4j_data:/data \
  -v "$PWD/backups":/backups \
  neo4j:<version> \
  neo4j-admin database load neo4j --from-path=/backups \
  --overwrite-destination=true
```

This replaces anything already in the target's `neo4j` database.

### 5. Start Neo4j

```bash
make up
```

### 6. Verify the import

Open http://localhost:7474, log in with the password from `.env`, and
run:

```cypher
MATCH (n) RETURN count(n);
```

The count should match the same query on the source computer. Then run:

```cypher
SHOW INDEXES;
```

The full-text and vector indexes should be listed as `ONLINE`. They may
show as `POPULATING` for a few minutes after startup.

## Part 3: Run the Agent on the Target Computer

`NEO4J_URI` stays `bolt://localhost:7687`, so `.env` needs no other Neo4j
changes.

The agent embeds each question at query time, so the target computer
also needs Ollama with the same embedding model used on the source
computer. The model must match because the question embeddings must have
the same dimensions as the vectors stored in the dump.

```bash
brew install ollama
make ollama-up
ollama pull nomic-embed-text
```

Then start the API:

```bash
make api
```

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| The dump or load fails because the database is in use or locked | `cinematica-neo4j` is still running. Run `make down` and try again. |
| The load fails because of the store version | The target uses an older Neo4j version than the source. Use the same `<version>` on both computers. |
| Login fails after the import | Use the `NEO4J_PASSWORD` from the target's `.env`, not the source's. |
| The node count is 0 | The dump was loaded into a different volume. Run `docker volume ls` and confirm the volume is `docker_neo4j_data`. |
