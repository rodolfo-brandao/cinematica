"""Textual description of the Neo4j graph schema, for LLM prompting."""


GRAPH_SCHEMA_DESCRIPTION: str = """\
Node labels and properties:

- Movie: tconst (unique id), primary_title, original_title, is_adult,
  start_year, runtime_min, average_rating, num_votes, tmdb_id, overview,
  tagline, status, budget, revenue, popularity, release_date,
  original_language, vote_average, vote_count, has_video,
  audience_sentiment_label, audience_sentiment_score,
  audience_sentiment_summary, audience_sentiment_reviewed_at.
  A movie's title is `primary_title` — there is no `title` property.

  IMPORTANT: there are two independent rating systems on Movie:
  `average_rating`/`num_votes` come from IMDb, `vote_average`/
  `vote_count` come from TMDb. A high `average_rating` or `vote_average`
  on its own does NOT mean a movie is critically acclaimed or widely
  seen: an obscure title can have a 9+ rating from only a handful of
  votes. When a question asks for "critically acclaimed", "well
  received", "high reception" or similar, filter on a meaningful
  minimum `num_votes` (e.g. >= 1000) or `vote_count` in addition to the
  rating itself, not the rating alone.

  The `audience_sentiment_*` properties are null until the
  `save_movie_sentiment` tool has been run for that movie. When present,
  they are a frontier-model judgment synthesized from a sample of public
  TMDb reviews — not a statistically rigorous metric — so phrase answers
  citing it accordingly (e.g. "reviews suggest..." rather than stating it
  as a hard fact). `audience_sentiment_label` is one of "positive",
  "mixed" or "negative"; `audience_sentiment_score` ranges from -1.0
  (very negative) to 1.0 (very positive).

  A movie ingested on demand from TMDb (via `ingest_movie`, rather than
  the offline IMDb pipeline) has no Person relationships (no cast/crew
  data) and no `average_rating`/`num_votes` (IMDb-only fields) — don't
  expect those to exist for it.

- Person: nconst (unique id), primary_name, birth_year, death_year,
  primary_profession (list of strings).

- Genre: name (unique).
- Language: name (unique) — a spoken language, e.g. "English".
- Country: code (unique) — an ISO country code, e.g. "US".
- ProductionCompany: tmdb_id (unique), name.
- Keyword: name (unique) — a TMDb thematic tag, e.g. "dystopia".
- Collection: tmdb_id (unique), name — a franchise, e.g. "The Godfather
  Collection".
- Review: review_id (unique) — a TMDb review id, author, content,
  tmdb_rating (the reviewer's own 1-10 score, nullable), created_at, url.

Relationships:

- Person -> Movie, one of: ACTED_IN, DIRECTED, WROTE, PRODUCED, COMPOSED,
  PHOTOGRAPHED, EDITED, DESIGNED, CAST, ARCHIVED_IN. Each may carry
  `ordering` (int), `job` (string or null) and `characters` (list of
  strings) properties. `WORKED_ON` is a generic fallback relationship for
  roles not covered above; it also carries a `category` property.
- Movie -> Genre: HAS_GENRE.
- Movie -> Language: SPOKEN_IN.
- Movie -> Country: PRODUCED_IN.
- Movie -> ProductionCompany: PRODUCED_BY.
- Movie -> Keyword: HAS_KEYWORD.
- Movie -> Collection: PART_OF_COLLECTION.
- Movie -> Review: HAS_REVIEW.

Resolving names:

Prefer the `resolve_entity` tool to turn a person or movie name into its
canonical node id before referencing it in a query — it is fuzzy and
case-insensitive, whereas an exact `{primary_name: '...'}` match fails
silently (empty result, not an error) on any case or spelling difference.
Once resolved, match on the id (`{nconst: '...'}` / `{tconst: '...'}`).

To find people who worked with a given person on the same movie(s), join
through the shared Movie node, e.g.:
MATCH (a:Person)-[]->(m:Movie)<-[]-(b:Person)
WHERE a.nconst = 'nm...' AND a <> b

Ordering caveat:

When ordering by a property that can be null for some rows (e.g. a rating
on an unrated movie), Neo4j's `ORDER BY x DESC` puts null values FIRST,
not last — the opposite of what "top N by x" usually means, and it will
surface unrated junk ahead of the real answer. Always exclude nulls on
the sort key before ordering by it, e.g. `WHERE m.average_rating IS NOT
NULL` before `ORDER BY m.average_rating DESC`.

Read-only:

`run_cypher` is strictly read-only: only MATCH/WHERE/WITH/RETURN/ORDER
BY/LIMIT clauses are allowed. Never use CREATE, MERGE, DELETE, SET,
REMOVE, DROP, LOAD CSV or any write-capable procedure in it. Always
include a LIMIT clause. The only ways to write to the graph are the
dedicated `ingest_movie` and `save_movie_sentiment` tools — never try to
write via `run_cypher`.
"""
