from stock_repo_brushup.models import RepositoryProfile
from stock_repo_brushup.recommendations import build_repository_recommendation
from stock_repo_brushup.report import render_markdown


def test_render_markdown_contains_repository_and_package() -> None:
    repo = RepositoryProfile(
        name="stock-dashboard",
        full_name="me/stock-dashboard",
        description="stock price portfolio dashboard with ticker data",
        language="Python",
        files={"requirements.txt": "pandas\n"},
    )
    item = build_repository_recommendation(repo)

    markdown = render_markdown([item])

    assert "me/stock-dashboard" in markdown
    assert "yfinance" in markdown
