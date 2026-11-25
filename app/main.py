from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse

from ingest.embed import embed_texts
from .search import search


@asynccontextmanager
async def lifespan(app):
    embed_texts(["warm up"])
    yield


app = FastAPI(title="JobLens", lifespan=lifespan)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/search")
def search_jobs(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    remote: bool | None = None,
    level: str | None = None,
    skills: str | None = None,
    mode: str = Query("hybrid", pattern="^(hybrid|fts|vector)$"),
):
    skill_list = (
        [skill.strip().lower() for skill in skills.split(",") if skill.strip()]
        if skills
        else None
    )
    results = search(q, limit, remote, level, skill_list, mode)
    return {"query": q, "mode": mode, "count": len(results), "results": results}
