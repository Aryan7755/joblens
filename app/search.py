from ingest.db import get_conn
from ingest.embed import embed_texts

K = 50
RRF_K = 60


def build_filters(remote, level, skills):
    clauses, params = ["status = 'active'"], []
    if remote is not None:
        clauses.append("is_remote = %s")
        params.append(remote)
    if level:
        clauses.append("experience_level = %s")
        params.append(level)
    if skills:
        clauses.append("skills @> %s::text[]")
        params.append(skills)
    return " AND ".join(clauses), params


def fts_ids(cur, query, where, params):
    cur.execute(
        f"""
        SELECT id FROM jobs, websearch_to_tsquery('english', %s) query
        WHERE {where} AND tsv @@ query
        ORDER BY ts_rank(tsv, query) DESC LIMIT {K}""",
        [query, *params],
    )
    return [row[0] for row in cur.fetchall()]


def vector_ids(cur, query_vector, where, params):
    cur.execute(
        f"""
        SELECT id FROM jobs
        WHERE {where} AND embedding IS NOT NULL
        ORDER BY embedding <=> %s LIMIT {K}""",
        [*params, query_vector],
    )
    return [row[0] for row in cur.fetchall()]


def rrf(rankings, k=RRF_K):
    """Return document IDs scored by reciprocal rank fusion, best first."""
    scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def search(q, limit=10, remote=None, level=None, skills=None, mode="hybrid"):
    if mode not in ("hybrid", "fts", "vector"):
        raise ValueError(f"Unsupported search mode: {mode}")

    where, params = build_filters(remote, level, skills)
    with get_conn() as conn, conn.cursor() as cur:
        rankings = []
        if mode in ("hybrid", "fts"):
            rankings.append(fts_ids(cur, q, where, params))
        if mode in ("hybrid", "vector"):
            query_vector = embed_texts([q])[0]
            rankings.append(vector_ids(cur, query_vector, where, params))

        fused = rrf(rankings)[:limit]
        if not fused:
            return []

        cur.execute(
            "SELECT id, title, company, location, is_remote, skills, "
            "experience_level, url FROM jobs WHERE id = ANY(%s)",
            ([doc_id for doc_id, _ in fused],),
        )
        rows = {row[0]: row for row in cur.fetchall()}

    return [
        {
            "id": doc_id,
            "title": rows[doc_id][1],
            "company": rows[doc_id][2],
            "location": rows[doc_id][3],
            "is_remote": rows[doc_id][4],
            "skills": rows[doc_id][5],
            "level": rows[doc_id][6],
            "url": rows[doc_id][7],
            "score": round(score, 4),
        }
        for doc_id, score in fused
        if doc_id in rows
    ]
