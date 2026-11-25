from app.search import rrf


def test_job_in_both_lists_wins():
    assert rrf([[1, 2, 3], [3, 4, 5]])[0][0] == 3


def test_score_formula():
    assert dict(rrf([[7]]))[7] == 1 / 61


def test_empty():
    assert rrf([[], []]) == []
