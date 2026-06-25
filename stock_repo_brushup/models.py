from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RepositoryProfile:
    """Normalized repository metadata used by the scanner and recommender."""

    name: str
    full_name: str
    html_url: str = ""
    description: str = ""
    topics: list[str] = field(default_factory=list)
    language: str = ""
    default_branch: str = "main"
    files: dict[str, str] = field(default_factory=dict)
    dependencies: set[str] = field(default_factory=set)
    relevance_score: int = 0
    relevance_reasons: list[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "RepositoryProfile":
        owner = ""
        if isinstance(raw.get("owner"), dict):
            owner = raw["owner"].get("login", "")
        full_name = raw.get("full_name") or f"{owner}/{raw.get('name', '')}".strip("/")
        return cls(
            name=str(raw.get("name", "")),
            full_name=str(full_name),
            html_url=str(raw.get("html_url", "")),
            description=str(raw.get("description") or ""),
            topics=list(raw.get("topics") or []),
            language=str(raw.get("language") or ""),
            default_branch=str(raw.get("default_branch") or "main"),
        )

    @property
    def owner_repo(self) -> tuple[str, str]:
        owner, _, repo = self.full_name.partition("/")
        return owner, repo


@dataclass(slots=True)
class LibraryRecommendation:
    key: str
    package: str
    category: str
    priority: int
    reason: str
    integration_hint: str
    caution: str = ""


@dataclass(slots=True)
class RepositoryRecommendation:
    repository: RepositoryProfile
    recommendations: list[LibraryRecommendation]

    @property
    def should_apply(self) -> bool:
        return bool(self.recommendations) and self.repository.relevance_score >= 4
