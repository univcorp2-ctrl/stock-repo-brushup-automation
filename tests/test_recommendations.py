from stock_repo_brushup.models import RepositoryProfile
from stock_repo_brushup.recommendations import recommend_libraries


def test_recommendations_include_core_libraries_for_strategy_repo() -> None:
    repo = RepositoryProfile(
        name="stock-strategy",
        full_name="me/stock-strategy",
        description="stock trading strategy backtest with OHLCV, RSI, MACD and returns",
        language="Python",
        files={"requirements.txt": "pandas\nnumpy\n"},
    )

    packages = {item.package for item in recommend_libraries(repo)}

    assert "yfinance" in packages
    assert "ta" in packages
    assert "backtesting" in packages
    assert "quantstats" in packages


def test_existing_dependency_is_not_recommended_again() -> None:
    repo = RepositoryProfile(
        name="portfolio-optimizer",
        full_name="me/portfolio-optimizer",
        description="portfolio allocation optimizer",
        language="Python",
        files={"requirements.txt": "PyPortfolioOpt\nyfinance\n"},
    )

    packages = {item.package for item in recommend_libraries(repo)}

    assert "PyPortfolioOpt" not in packages
    assert "yfinance" not in packages
