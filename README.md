# JobLens
Hybrid job search engine: Postgres full-text + pgvector semantic search, merged with Reciprocal Rank Fusion.

## Run locally
docker compose up -d

## Status
🚧 Phase 1 complete: `jobs` schema with full-text (GIN) and vector (HNSW) indexes.