# JobLens
Hybrid job search engine: Postgres full-text + pgvector semantic search, merged with Reciprocal Rank Fusion.

## Run locally
docker compose up -d

## Status
🚧 Phase 4 complete: hybrid search with full-text and vector retrieval, reciprocal-rank fusion, and filters.

## How incremental ingestion works

The first ingestion added jobs from all five sources. Running it again found no
content changes, so it skipped re-embedding and only refreshed `last_seen`:

```text
[remotive] +0 new, 0 updated, 0 expired, 15 skipped
[arbeitnow] +0 new, 0 updated, 0 expired, 300 skipped
[greenhouse:stripe] +0 new, 0 updated, 0 expired, 771 skipped
[greenhouse:airbnb] +0 new, 0 updated, 0 expired, 200 skipped
[greenhouse:cloudflare] +0 new, 0 updated, 0 expired, 513 skipped
```

## Search API

Start the API from the repository root after the database is running and jobs
have been ingested:

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) to try the
interactive API. `GET /health` returns `{"status":"ok"}`. Search supports
`hybrid`, `fts`, and `vector` modes, plus `remote`, `level`, and comma-separated
`skills` filters. For example:

```text
/search?q=python%20backend%20developer&mode=hybrid
/search?q=backend&skills=python,docker
```

The synonym query shows the difference between keyword and semantic retrieval.
On the current dataset, `server-side engineer` returns 3 FTS results and 10
vector results:

```text
/search?q=server-side%20engineer&mode=fts
/search?q=server-side%20engineer&mode=vector
```

Filters are applied before ranking. This dataset currently has no jobs that
are both remote and intern-level, so
`/search?q=developer&remote=true&level=intern` returns no results; the
`/search?q=backend&skills=python,docker` filter returns matching jobs.