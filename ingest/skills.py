import re

SKILLS = [
    "python", "java", "javascript", "typescript", "spring boot", "react",
    "node.js", "sql", "postgresql", "mysql", "mongodb", "docker", "kubernetes",
    "aws", "gcp", "azure", "fastapi", "django", "flask", "c++", "c#", "golang",
    "rust", "kafka", "redis", "graphql", "machine learning", "llm", "pytorch",
    "tensorflow", "git", "linux",
]

_PATTERNS = {
    skill: re.compile(r"(?<![\w+#.])" + re.escape(skill) + r"(?![\w+#])", re.I)
    for skill in SKILLS
}


def extract_skills(text: str) -> list[str]:
    return sorted(skill for skill, pattern in _PATTERNS.items() if pattern.search(text))


def guess_level(title: str) -> str:
    title = title.lower()
    if re.search(r"\b(intern|trainee)\b", title):
        return "intern"
    if re.search(r"\b(junior|jr|graduate|entry)\b", title):
        return "junior"
    if re.search(r"\b(senior|sr|lead|staff|principal)\b", title):
        return "senior"
    return "mid"
