from collections import Counter

from .sources import fetch_all


if __name__ == "__main__":
    jobs = fetch_all()
    print(f"\nTotal: {len(jobs)}")
    print(Counter(job.source for job in jobs))
    for job in jobs[:3]:
        print(f"- {job.title} @ {job.company} | {job.experience_level} | {job.skills}")
