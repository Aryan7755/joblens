from app.search import build_filters


def test_default_only_active():
    where, params = build_filters(None, None, None)
    assert where == "status = 'active'" and params == []


def test_all_filters():
    where, params = build_filters(True, "junior", ["python"])
    assert "is_remote = %s" in where
    assert "experience_level = %s" in where
    assert "skills @> %s::text[]" in where
    assert params == [True, "junior", ["python"]]
