from ingest.skills import extract_skills, guess_level


def test_java_not_matched_inside_javascript():
    assert extract_skills("We use JavaScript daily") == ["javascript"]


def test_multiple_and_special_chars():
    skills = extract_skills("Python, C++ and Spring Boot with Docker")
    assert {"python", "c++", "spring boot", "docker"} <= set(skills)


def test_levels():
    assert guess_level("Senior Backend Engineer") == "senior"
    assert guess_level("Software Engineer Intern") == "intern"
    assert guess_level("Backend Engineer") == "mid"
