from .sources import fetch_all
from .pipeline import ingest


if __name__ == "__main__":
    for source, jobs in fetch_all().items():
        stats = ingest(source, jobs)
        print(
            f"[{source}] +{stats['new']} new, {stats['updated']} updated, "
            f"{stats['expired']} expired, {stats['unchanged']} skipped"
        )
