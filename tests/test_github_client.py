from stock_repo_brushup.github_client import build_pr_files
from stock_repo_brushup.models import RepositoryProfile
from stock_repo_brushup.recommendations import build_repository_recommendation


def test_build_pr_files_are_safe_documentation_only() -> None:
    repo = RepositoryProfile(
        name="stock-dashboard",
        full_name="me/stock-dashboard",
        description="stock portfolio ticker dashboard",
        language="Python",
        files={"requirements.txt": "pandas\n"},
    )
    item = build_repository_recommendation(repo)

    files = build_pr_files(item)

    assert set(files) == {"docs/stock-investment-brushup.md", "requirements.stock-investment-brushup.txt"}
    assert "stock-dashboard" in files["docs/stock-investment-brushup.md"]
