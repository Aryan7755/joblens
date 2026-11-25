# JobLens
Hybrid job search engine: Postgres full-text + pgvector semantic search, merged with Reciprocal Rank Fusion.

## Run locally
docker compose up -d

## Status
🚧 Phase 1 complete: `jobs` schema with full-text (GIN) and vector (HNSW) indexes.

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