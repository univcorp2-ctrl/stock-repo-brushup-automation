# 初期設定ガイド

## 1. レポートだけ作る場合

追加設定は不要です。

1. GitHubでこのrepoを開く
2. `Actions` タブを開く
3. `Scan and brush up stock investment repositories` を選ぶ
4. `Run workflow` を押す
5. `owner` にGitHubユーザー名またはOrganization名を入れる
6. `apply` は `false` のまま実行する
7. 完了後、artifact `stock-brushup-report` を確認する

## 2. 対象repoへPRを作る場合

他repoへPRを作るには `TARGET_GITHUB_TOKEN` が必要です。

### 必要権限

Fine-grained personal access tokenを使う場合、対象リポジトリに対して以下を付与してください。

- Contents: Read and write
- Pull requests: Read and write
- Metadata: Read

### Secret登録

1. このrepoの `Settings` を開く
2. `Secrets and variables` → `Actions` を開く
3. `New repository secret` を押す
4. Name に `TARGET_GITHUB_TOKEN` を入力
5. Secret にGitHub tokenを貼り付けて保存

### PR作成実行

1. `Actions` タブを開く
2. `Scan and brush up stock investment repositories` を選ぶ
3. `Run workflow` を押す
4. `owner` を入力
5. `apply` を `true` にする
6. 実行後、artifact内の `pull-requests.json` を確認する

## 3. 初心者向けの確認ポイント

- まずは必ず `apply=false` で実行し、レポートだけ確認してください
- 推薦されたライブラリをすべて導入する必要はありません
- `requirements.stock-investment-brushup.txt` は候補一覧です。自動で本番依存に追加するものではありません
- APIキーや証券口座情報をrepoに入れないでください
- バックテスト結果は将来成績を保証しません

## 4. ローカル実行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
stock-brushup sample --output reports
```

GitHubをスキャンする場合:

```bash
export TARGET_GITHUB_TOKEN=github_pat_xxx
stock-brushup github-scan --owner YOUR_GITHUB_OWNER --output reports
```

## 5. トラブルシューティング

### public repoなのに取得できない

GitHub API rate limitに到達している可能性があります。`TARGET_GITHUB_TOKEN` を設定してください。

### PR作成に失敗する

Tokenの対象repo権限に `Contents: Read and write` と `Pull requests: Read and write` があるか確認してください。

### 株式投資repoが検出されない

READMEやtopicsに以下のような説明を追加すると検出されやすくなります。

- `stock`
- `investment`
- `portfolio`
- `trading`
- `backtest`
- `株式`
- `投資`
- `銘柄`
- `ポートフォリオ`
