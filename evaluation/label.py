import json
import random
from pathlib import Path

from app.search import search
from ingest.db import get_conn

DIRECTORY = Path(__file__).parent
QUERIES_PATH = DIRECTORY / "queries.txt"
OUT = DIRECTORY / "labels.json"


def load_labels():
    if not OUT.exists():
        return {}
    with OUT.open(encoding="utf-8") as file:
        return json.load(file)


def save_labels(labels):
    with OUT.open("w", encoding="utf-8") as file:
        json.dump(labels, file, indent=2)
        file.write("\n")


def info(ids):
    if not ids:
        return {}
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, source || '|' || external_id, title, company "
            "FROM jobs WHERE id = ANY(%s)",
            (ids,),
        )
        return {row[0]: row[1:] for row in cur.fetchall()}


def main():
    with QUERIES_PATH.open(encoding="utf-8") as file:
        queries = [query.strip() for query in file if query.strip()]
    labels = load_labels()

    for query in queries:
        if query in labels:
            continue
        pool = []
        for mode in ("fts", "vector", "hybrid"):
            for result in search(query, limit=10, mode=mode):
                if result["id"] not in pool:
                    pool.append(result["id"])
        if not pool:
            labels[query] = []
            save_labels(labels)
            print(f"\n=== {query} (no candidates)")
            continue

        random.shuffle(pool)
        metadata = info(pool)
        pool = [job_id for job_id in pool if job_id in metadata]
        print(f"\n=== {query} ({len(pool)} candidates)")
        for number, job_id in enumerate(pool, 1):
            _, title, company = metadata[job_id]
            print(f"{number:>2}. {title} @ {company}")

        answer = input(
            "Relevant numbers (space-separated), Enter = none, q = save & quit: "
        ).strip()
        if answer.lower() == "q":
            break
        selected = {
            int(value)
            for value in answer.split()
            if value.isdigit() and 1 <= int(value) <= len(pool)
        }
        labels[query] = [
            metadata[pool[number - 1]][0]
            for number in sorted(selected)
        ]
        save_labels(labels)

    save_labels(labels)
    print(f"\nLabeled {len(labels)} queries")


if __name__ == "__main__":
    main()
