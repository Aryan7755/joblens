import html

import requests
from bs4 import BeautifulSoup

from .models import Job
from .skills import extract_skills, guess_level

TIMEOUT = 30
HEADERS = {"User-Agent": "joblens-learning-project"}
GREENHOUSE_BOARDS = ["stripe", "airbnb", "cloudflare"]


def clean_html(raw: str) -> str:
    text = BeautifulSoup(html.unescape(raw or ""), "html.parser").get_text(" ")
    return " ".join(text.split())


def make_job(
    source,
    external_id,
    title,
    company,
    description_html,
    location,
    is_remote,
    url,
) -> Job:
    desc = clean_html(description_html)
    return Job(
        source=source,
        external_id=str(external_id),
        title=title.strip(),
        company=company.strip(),
        description=desc,
        location=location or "",
        is_remote=is_remote,
        url=url,
        skills=extract_skills(f"{title} {desc}"),
        experience_level=guess_level(title),
    )


def fetch_remotive() -> list[Job]:
    response = requests.get(
        "https://remotive.com/api/remote-jobs",
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return [
        make_job(
            "remotive",
            job["id"],
            job["title"],
            job["company_name"],
            job["description"],
            job.get("candidate_required_location") or "Anywhere",
            True,
            job["url"],
        )
        for job in response.json()["jobs"]
    ]


def fetch_arbeitnow() -> list[Job]:
    response = requests.get(
        "https://www.arbeitnow.com/api/job-board-api",
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return [
        make_job(
            "arbeitnow",
            job["slug"],
            job["title"],
            job["company_name"],
            job["description"],
            job.get("location"),
            bool(job.get("remote")),
            job["url"],
        )
        for job in response.json()["data"]
    ]


def fetch_greenhouse(board: str) -> list[Job]:
    response = requests.get(
        f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true",
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    jobs = []
    for job in response.json()["jobs"]:
        location = (job.get("location") or {}).get("name", "")
        jobs.append(
            make_job(
                f"greenhouse:{board}",
                job["id"],
                job["title"],
                board.title(),
                job.get("content", ""),
                location,
                "remote" in location.lower(),
                job["absolute_url"],
            )
        )
    return jobs


def fetch_all() -> list[Job]:
    fetchers = [("remotive", fetch_remotive), ("arbeitnow", fetch_arbeitnow)]
    fetchers += [
        (f"greenhouse:{board}", lambda board=board: fetch_greenhouse(board))
        for board in GREENHOUSE_BOARDS
    ]
    jobs = []
    for name, fetcher in fetchers:
        try:
            fetched_jobs = fetcher()
            print(f"{name}: {len(fetched_jobs)} jobs")
            jobs += fetched_jobs
        except (requests.RequestException, ValueError, KeyError, TypeError) as error:
            print(f"{name}: FAILED ({error})")
    return jobs
