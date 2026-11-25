from ingest.models import Job
from ingest.pipeline import content_hash


def make(**kwargs):
    values = dict(
        source="s",
        external_id="1",
        title="Dev",
        company="A",
        description="d",
        location="",
        is_remote=False,
        url="u",
    )
    values.update(kwargs)
    return Job(**values)


def test_same_job_same_hash():
    assert content_hash(make()) == content_hash(make())


def test_description_change_changes_hash():
    assert content_hash(make()) != content_hash(make(description="new"))


def test_url_change_ignored():
    assert content_hash(make()) == content_hash(make(url="other"))
