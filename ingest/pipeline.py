import hashlib
from datetime import datetime, timezone

from .db import get_conn
from .embed import embed_texts
from .models import Job

UPSERT = """
INSERT INTO jobs (source, external_id, title, company, description, location,
                  is_remote, url, skills, experience_level, content_hash,
                  embedding, status, first_seen, last_seen)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'active',%s,%s)
ON CONFLICT (source, external_id) DO UPDATE SET
  title=EXCLUDED.title, company=EXCLUDED.company,
  description=EXCLUDED.description, location=EXCLUDED.location,
  is_remote=EXCLUDED.is_remote, url=EXCLUDED.url, skills=EXCLUDED.skills,
  experience_level=EXCLUDED.experience_level,
  content_hash=EXCLUDED.content_hash, embedding=EXCLUDED.embedding,
  status='active', last_seen=EXCLUDED.last_seen
"""


def content_hash(job: Job) -> str:
    raw = f"{job.title}\n{job.company}\n{job.description}"
    return hashlib.sha256(raw.encode()).hexdigest()


def embed_input(job: Job) -> str:
    return f"{job.title}. {job.company}. {job.description[:1500]}"


def ingest(source: str, jobs: list[Job]) -> dict:
    if not jobs:
        return {
            "new": 0,
            "updated": 0,
            "unchanged": 0,
            "expired": 0,
            "note": "empty fetch, skipped",
        }

    now = datetime.now(timezone.utc)
    unique = {job.external_id: job for job in jobs}
    stats = {"new": 0, "updated": 0, "unchanged": 0, "expired": 0}

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT external_id, content_hash FROM jobs WHERE source=%s",
            (source,),
        )
        existing = dict(cur.fetchall())

        to_write = []
        unchanged_ids = []
        for external_id, job in unique.items():
            job_hash = content_hash(job)
            if external_id not in existing:
                stats["new"] += 1
                to_write.append((job, job_hash))
            elif existing[external_id] != job_hash:
                stats["updated"] += 1
                to_write.append((job, job_hash))
            else:
                stats["unchanged"] += 1
                unchanged_ids.append(external_id)

        if to_write:
            vectors = embed_texts([embed_input(job) for job, _ in to_write])
            if len(vectors) != len(to_write):
                raise ValueError(
                    f"Expected {len(to_write)} embeddings, received {len(vectors)}"
                )
            rows = [
                (
                    job.source,
                    job.external_id,
                    job.title,
                    job.company,
                    job.description,
                    job.location,
                    job.is_remote,
                    job.url,
                    job.skills,
                    job.experience_level,
                    job_hash,
                    vector,
                    now,
                    now,
                )
                for (job, job_hash), vector in zip(to_write, vectors)
            ]
            cur.executemany(UPSERT, rows)

        if unchanged_ids:
            cur.execute(
                "UPDATE jobs SET last_seen=%s, status='active' "
                "WHERE source=%s AND external_id = ANY(%s)",
                (now, source, unchanged_ids),
            )

        cur.execute(
            "UPDATE jobs SET status='expired' "
            "WHERE source=%s AND status='active' AND last_seen < %s",
            (source, now),
        )
        stats["expired"] = cur.rowcount
    return stats
