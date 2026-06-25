from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from stock_repo_brushup.models import RepositoryRecommendation


def recommendation_to_dict(item: RepositoryRecommendation) -> dict[str, Any]:
    repo = item.repository
    return {
        "repository": {
            "name": repo.name,
            "full_name": repo.full_name,
            "html_url": repo.html_url,
            "language": repo.language,
            "topics": repo.topics,
            "description": repo.description,
            "default_branch": repo.default_branch,
            "relevance_score": repo.relevance_score,
            "relevance_reasons": repo.relevance_reasons,
            "dependencies": sorted(repo.dependencies),
        },
        "recommendations": [
            {
                "key": rec.key,
                "package": rec.package,
                "category": rec.category,
                "priority": rec.priority,
                "reason": rec.reason,
                "integration_hint": rec.integration_hint,
                "caution": rec.caution,
            }
            for rec in item.recommendations
        ],
        "should_apply": item.should_apply,
    }


def render_markdown(items: list[RepositoryRecommendation], *, apply_mode: bool = False) -> str:
    lines = [
        "# 株式投資系リポジトリ改善レポート",
        "",
        "このレポートは、リポジトリ名、説明、topics、README、依存関係ファイルをもとに自動生成されています。",
        "投資助言ではなく、開発・分析基盤の改善提案です。",
        "",
        f"- 対象repo数: {len(items)}",
        f"- PR作成モード: {'ON' if apply_mode else 'OFF'}",
        "",
    ]
    if not items:
        lines.extend(
            [
                "## 結果",
                "",
                "株式投資に関連すると判定できるリポジトリは見つかりませんでした。",
                "min-scoreを下げるか、README/topicsに `stock`, `portfolio`, `investment`, `株式`, `投資` などの説明を追加してください。",
            ]
        )
        return "\n".join(lines) + "\n"

    for index, item in enumerate(items, start=1):
        repo = item.repository
        lines.extend(
            [
                f"## {index}. {repo.full_name}",
                "",
                f"- URL: {repo.html_url or '(not provided)'}",
                f"- language: {repo.language or '(unknown)'}",
                f"- relevance score: {repo.relevance_score}",
                f"- reasons: {', '.join(repo.relevance_reasons) or '(none)'}",
                f"- dependencies: {', '.join(sorted(repo.dependencies)) or '(none detected)'}",
                "",
            ]
        )
        if not item.recommendations:
            lines.extend(["推薦ライブラリはありません。既に主要な構成が入っている可能性があります。", ""])
            continue
        lines.append("| 優先度 | 候補 | 分類 | 理由 | 反映方法 | 注意点 |")
        lines.append("|---:|---|---|---|---|---|")
        for rec in item.recommendations:
            lines.append(
                "| {priority} | `{package}` | {category} | {reason} | {hint} | {caution} |".format(
                    priority=rec.priority,
                    package=rec.package,
                    category=rec.category,
                    reason=rec.reason.replace("|", "\\|"),
                    hint=rec.integration_hint.replace("|", "\\|"),
                    caution=rec.caution.replace("|", "\\|"),
                )
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def write_outputs(items: list[RepositoryRecommendation], output_dir: Path, *, apply_mode: bool = False) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "stock-investment-repo-report.md").write_text(
        render_markdown(items, apply_mode=apply_mode), encoding="utf-8"
    )
    payload = [recommendation_to_dict(item) for item in items]
    (output_dir / "recommendations.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
