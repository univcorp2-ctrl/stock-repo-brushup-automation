# CODEX.md

## 開発エージェント向け指示

このrepoは、株式投資関連の既存GitHubリポジトリを棚卸しし、OSSライブラリ導入候補を提案・PR化する自動化ツールです。

## 重要な制約

- 投資助言を書かない
- 売買推奨を書かない
- APIキー、口座情報、個人データを出力しない
- デフォルトでは対象repoを変更しない
- PR作成時も既存コードを直接変更せず、docsと候補requirementsのみ追加する

## テスト

```bash
pip install -e .[dev]
ruff check .
pytest -q
```

## 主なエントリポイント

- `stock_repo_brushup/cli.py`
- `stock_repo_brushup/detector.py`
- `stock_repo_brushup/recommendations.py`
- `stock_repo_brushup/github_client.py`
