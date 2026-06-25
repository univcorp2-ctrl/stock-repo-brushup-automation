# 実装ステータス

## 完了

- 株式投資系repo検出ロジック
- 日本語・英語キーワード対応
- 依存関係ファイル解析
- OSSライブラリ推薦ロジック
- Markdown / JSON レポート生成
- GitHub APIによるrepo棚卸し
- `apply=true` 時の安全なPR作成処理
- テストコード
- devcontainer
- README
- アーキテクチャdocs
- セットアップdocs
- workflowテンプレート

## 制限

- `.github/workflows/*` の直接commitは、現在のGitHub連携Token権限ではGitHub APIが `404 Not Found` を返しました
- そのためworkflowは `docs/workflows/*` にテンプレートとして保存しています
- Actions CIは未実行です

## 次に行うべきこと

GitHub連携Tokenへworkflow更新権限が付いたら、`docs/workflows/*` を `.github/workflows/*` に配置してください。配置後、CIと手動スキャンworkflowが利用できます。
