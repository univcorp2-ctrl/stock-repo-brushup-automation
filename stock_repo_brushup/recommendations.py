from __future__ import annotations

from stock_repo_brushup.detector import _search_text, score_repository
from stock_repo_brushup.library_catalog import make_recommendation
from stock_repo_brushup.models import LibraryRecommendation, RepositoryProfile, RepositoryRecommendation


def _has_any(deps: set[str], names: set[str]) -> bool:
    normalized = {name.lower().replace("_", "-") for name in deps}
    return bool(normalized & names)


def recommend_libraries(repo: RepositoryProfile) -> list[LibraryRecommendation]:
    repo = score_repository(repo)
    text = _search_text(repo)
    deps = repo.dependencies
    recs: list[LibraryRecommendation] = []

    if not _has_any(deps, {"yfinance", "openbb", "pandas-datareader"}):
        if any(word in text for word in ["price", "ticker", "ohlcv", "銘柄", "価格", "株価", "finance"]):
            recs.append(make_recommendation("yfinance", 90))

    if not _has_any(deps, {"ta", "ta-lib", "pandas-ta", "pandas-ta-classic"}):
        if any(word in text for word in ["ohlcv", "rsi", "macd", "moving average", "indicator", "テクニカル"]):
            recs.append(make_recommendation("ta", 85))

    if not _has_any(deps, {"backtesting", "backtrader", "vectorbt"}):
        if any(word in text for word in ["strategy", "signal", "backtest", "trade", "trading", "売買", "バックテスト"]):
            recs.append(make_recommendation("backtesting", 82))

    if not _has_any(deps, {"quantstats"}):
        if any(word in text for word in ["returns", "sharpe", "drawdown", "performance", "backtest", "成績"]):
            recs.append(make_recommendation("quantstats", 78))

    portfolio_words = [
        "portfolio",
        "allocation",
        "efficient frontier",
        "black-litterman",
        "risk parity",
        "weight",
        "ポートフォリオ",
        "配分",
    ]
    if any(word in text for word in portfolio_words):
        if _has_any(deps, {"scikit-learn", "sklearn"}) and not _has_any(deps, {"skfolio"}):
            recs.append(make_recommendation("skfolio", 80))
        if not _has_any(deps, {"pyportfolioopt", "skfolio", "riskfolio-lib"}):
            recs.append(make_recommendation("pyportfolioopt", 76))

    if not _has_any(deps, {"openbb"}):
        if any(word in text for word in ["fundamental", "financial statement", "news", "sec", "edgar", "決算", "財務"]):
            recs.append(make_recommendation("openbb", 65))

    if repo.language and repo.language.lower() not in {"python", "jupyter notebook"}:
        for rec in recs:
            rec.priority -= 15
            rec.integration_hint = "Pythonサブパッケージまたは別CLIとして切り出すと、既存実装を壊さず段階導入できます。 " + rec.integration_hint

    recs.sort(key=lambda item: item.priority, reverse=True)
    return recs[:6]


def build_repository_recommendation(repo: RepositoryProfile) -> RepositoryRecommendation:
    return RepositoryRecommendation(repository=score_repository(repo), recommendations=recommend_libraries(repo))
