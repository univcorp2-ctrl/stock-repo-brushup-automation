from __future__ import annotations

import re

from stock_repo_brushup.models import RepositoryProfile

KEYWORD_WEIGHTS: dict[str, int] = {
    "stock": 3,
    "stocks": 3,
    "equity": 3,
    "portfolio": 3,
    "investment": 3,
    "investing": 3,
    "finance": 2,
    "financial": 2,
    "trading": 3,
    "backtest": 4,
    "backtesting": 4,
    "ticker": 2,
    "ohlcv": 4,
    "price data": 3,
    "technical analysis": 4,
    "rsi": 2,
    "macd": 2,
    "moving average": 2,
    "sharpe": 3,
    "drawdown": 3,
    "risk parity": 3,
    "black-litterman": 4,
    "株": 4,
    "株式": 4,
    "投資": 4,
    "銘柄": 3,
    "ポートフォリオ": 4,
    "バックテスト": 4,
    "テクニカル": 3,
}

DEPENDENCY_PATTERN = re.compile(r"^[\w.-]+", re.MULTILINE)
PYPROJECT_DEP_PATTERN = re.compile(r"[\"']([A-Za-z0-9_.-]+)[<>=!~;,\"'\s]?")

COMMON_DEP_FILES = (
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "Pipfile",
    "poetry.lock",
    "environment.yml",
    "package.json",
)


def _search_text(repo: RepositoryProfile) -> str:
    parts = [repo.name, repo.full_name, repo.description, repo.language, " ".join(repo.topics)]
    for path, content in repo.files.items():
        parts.append(path)
        if path.lower().endswith((".md", ".txt", ".toml", ".yml", ".yaml", ".json")):
            parts.append(content[:5000])
    return "\n".join(parts).lower()


def parse_dependencies(files: dict[str, str]) -> set[str]:
    deps: set[str] = set()
    for path, content in files.items():
        name = path.rsplit("/", 1)[-1]
        if name not in COMMON_DEP_FILES:
            continue
        if name in {"requirements.txt", "requirements-dev.txt"}:
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                match = DEPENDENCY_PATTERN.match(line)
                if match:
                    deps.add(match.group(0).lower().replace("_", "-"))
        elif name == "pyproject.toml":
            for match in PYPROJECT_DEP_PATTERN.finditer(content):
                value = match.group(1).lower().replace("_", "-")
                if value not in {"project", "dependencies", "optional-dependencies"}:
                    deps.add(value)
        elif name == "package.json":
            for match in re.finditer(r'"([@A-Za-z0-9_.-]+)"\s*:', content):
                deps.add(match.group(1).lower())
        else:
            for match in DEPENDENCY_PATTERN.finditer(content):
                deps.add(match.group(0).lower().replace("_", "-"))
    return deps


def score_repository(repo: RepositoryProfile) -> RepositoryProfile:
    """Compute an explainable relevance score for stock investment repositories."""

    text = _search_text(repo)
    score = 0
    reasons: list[str] = []
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword.lower() in text:
            score += weight
            reasons.append(f"keyword:{keyword}+{weight}")

    repo.dependencies = parse_dependencies(repo.files)
    finance_deps = {
        "yfinance",
        "pandas-datareader",
        "ta",
        "ta-lib",
        "backtesting",
        "backtrader",
        "quantstats",
        "pyportfolioopt",
        "skfolio",
        "openbb",
        "riskfolio-lib",
        "vectorbt",
    }
    found = sorted(repo.dependencies & finance_deps)
    if found:
        score += 2 * len(found)
        reasons.append("finance-dependencies:" + ",".join(found))

    if repo.language.lower() in {"python", "jupyter notebook"} and score > 0:
        score += 1
        reasons.append("python-friendly+1")

    repo.relevance_score = score
    repo.relevance_reasons = reasons
    return repo


def is_investment_related(repo: RepositoryProfile, min_score: int = 4) -> bool:
    return score_repository(repo).relevance_score >= min_score
