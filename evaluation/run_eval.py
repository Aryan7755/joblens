import json
from pathlib import Path

from app.search import search
from ingest.db import get_conn

K = 10
DIRECTORY = Path(__file__).parent
LABELS_PATH = DIRECTORY / "labels.json"
RESULTS_PATH = DIRECTORY / "results.md"


def load_positive_labels():
    if not LABELS_PATH.exists():
        raise SystemExit(
            "No relevance labels found. Run `python -m evaluation.label` first."
        )
    with LABELS_PATH.open(encoding="utf-8") as file:
        labels = {
            query: set(relevant)
            for query, relevant in json.load(file).items()
            if relevant
        }
    if not labels:
        raise SystemExit(
            "No queries have relevant jobs labeled yet. "
            "Run `python -m evaluation.label` and label relevant candidates."
        )
    return labels


def keys(ids):
    if not ids:
        return {}
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, source || '|' || external_id FROM jobs "
            "WHERE id = ANY(%s)",
            (ids,),
        )
        return dict(cur.fetchall())


def evaluate(mode, labels):
    recalls, reciprocal_ranks = [], []
    for query, relevant in labels.items():
        results = search(query, limit=K, mode=mode)
        job_keys = keys([result["id"] for result in results])
        retrieved = [job_keys[result["id"]] for result in results if result["id"] in job_keys]
        recalls.append(len(relevant & set(retrieved)) / min(len(relevant), K))
        reciprocal_ranks.append(
            next(
                (1 / rank for rank, key in enumerate(retrieved, 1) if key in relevant),
                0,
            )
        )
    return sum(recalls) / len(recalls), sum(reciprocal_ranks) / len(reciprocal_ranks)


def main():
    labels = load_positive_labels()
    rows = ["| Method | Recall@10 | MRR |", "|---|---|---|"]
    for mode in ("fts", "vector", "hybrid"):
        recall, reciprocal_rank = evaluate(mode, labels)
        rows.append(f"| {mode} | {recall:.2f} | {reciprocal_rank:.2f} |")
    table = "\n".join(rows)
    print(f"Queries evaluated: {len(labels)}\n")
    print(table)
    RESULTS_PATH.write_text(table + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
