from dataclasses import dataclass, field


@dataclass
class Job:
    source: str
    external_id: str
    title: str
    company: str
    description: str
    location: str
    is_remote: bool
    url: str
    skills: list[str] = field(default_factory=list)
    experience_level: str = "mid"
