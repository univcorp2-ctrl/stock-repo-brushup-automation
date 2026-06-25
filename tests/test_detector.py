from stock_repo_brushup.detector import parse_dependencies, score_repository
from stock_repo_brushup.models import RepositoryProfile


def test_score_repository_detects_japanese_stock_repo() -> None:
    repo = RepositoryProfile(
        name="kabushiki-portfolio",
        full_name="me/kabushiki-portfolio",
        description="株式投資のポートフォリオを分析する",
        language="Python",
        files={"README.md": "銘柄ごとのSharpeとdrawdownを確認する"},
    )

    scored = score_repository(repo)

    assert scored.relevance_score >= 4
    assert any("株式" in reason or "投資" in reason for reason in scored.relevance_reasons)


def test_parse_dependencies_from_requirements() -> None:
    deps = parse_dependencies({"requirements.txt": "pandas>=2\nyfinance==0.2.0\n# comment\n"})

    assert "pandas" in deps
    assert "yfinance" in deps
