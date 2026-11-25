CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS jobs (
    id               BIGSERIAL PRIMARY KEY,
    source           TEXT NOT NULL,
    external_id      TEXT NOT NULL,
    title            TEXT NOT NULL,
    company          TEXT NOT NULL,
    description      TEXT NOT NULL DEFAULT '',
    location         TEXT NOT NULL DEFAULT '',
    is_remote        BOOLEAN NOT NULL DEFAULT FALSE,
    url              TEXT NOT NULL,
    skills           TEXT[] NOT NULL DEFAULT '{}',
    experience_level TEXT NOT NULL DEFAULT 'mid',

    content_hash     TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'active'
                     CHECK (status IN ('active', 'expired')),
    first_seen       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen        TIMESTAMPTZ NOT NULL DEFAULT now(),

    embedding        vector(384),
    tsv              tsvector GENERATED ALWAYS AS (
                         setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
                         setweight(to_tsvector('english', coalesce(description, '')), 'B')
                     ) STORED,

    UNIQUE (source, external_id)
);

CREATE INDEX IF NOT EXISTS jobs_tsv_idx
    ON jobs USING GIN (tsv);
CREATE INDEX IF NOT EXISTS jobs_embed_idx
    ON jobs USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS jobs_skills_idx
    ON jobs USING GIN (skills);
CREATE INDEX IF NOT EXISTS jobs_filter_idx
    ON jobs (status, is_remote, experience_level);
