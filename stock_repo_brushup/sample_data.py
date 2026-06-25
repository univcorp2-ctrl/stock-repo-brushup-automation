from __future__ import annotations

from stock_repo_brushup.models import RepositoryProfile


def sample_repositories() -> list[RepositoryProfile]:
    return [
        RepositoryProfile(
            name="my-stock-dashboard",
            full_name="demo/my-stock-dashboard",
            description="株価とポートフォリオを可視化するPython dashboard",
            topics=["stock", "portfolio", "finance"],
            language="Python",
            files={
                "README.md": "Track tickers, portfolio returns, Sharpe ratio and drawdown.",
                "requirements.txt": "pandas\nplotly\n",
            },
        ),
        RepositoryProfile(
            name="moving-average-strategy",
            full_name="demo/moving-average-strategy",
            description="Trading strategy and backtest experiments",
            topics=["trading", "backtest"],
            language="Python",
            files={
                "README.md": "Moving average cross over signal with OHLCV data, RSI and MACD.",
                "pyproject.toml": "[project]\ndependencies = ['pandas', 'numpy']\n",
            },
        ),
        RepositoryProfile(
            name="todo-app",
            full_name="demo/todo-app",
            description="A tiny todo application",
            topics=["productivity"],
            language="TypeScript",
            files={"README.md": "Manage tasks."},
        ),
    ]
