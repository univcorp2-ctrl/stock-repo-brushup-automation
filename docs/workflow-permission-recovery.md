# GitHub Actions workflow反映の復旧ガイド

## 状況

初回commit時、通常ファイルは作成できましたが、`.github/workflows/ci.yml` と `.github/workflows/scan-and-brushup.yml` の作成だけGitHub APIが `404 Not Found` を返しました。

この挙動は、GitHub APIでworkflowファイルを作成・更新するTokenに `workflow` 権限がない場合に起きることがあります。リポジトリ本体や通常ファイルは作れるが、`.github/workflows/*` だけ拒否される状態です。

## repo内の代替配置

workflowの内容は以下にテンプレートとして保存済みです。

- `docs/workflows/ci.yml`
- `docs/workflows/scan-and-brushup.yml`

## 正式配置先

GitHub Actionsとして動かすには、最終的に以下のパスへ配置します。

- `.github/workflows/ci.yml`
- `.github/workflows/scan-and-brushup.yml`

## 復旧方法

GitHub連携Workerで使うGitHub Tokenにworkflow更新権限を付けたあと、同じ内容を `.github/workflows/` に再commitしてください。

Fine-grained tokenを使う場合は、少なくとも対象repoに対して以下を付与してください。

- Contents: Read and write
- Actions: Read and write
- Workflows: Read and write が表示される場合は有効化
- Metadata: Read

Classic PATを使う場合は `repo` に加えて `workflow` scope が必要です。

## 影響

- Pythonパッケージ、CLI、テスト、README、docs、devcontainerは作成済みです
- GitHub Actions画面にはworkflowが出ません
- CI実行は未実行です
- workflow権限が復旧すれば、`docs/workflows/*` の内容をそのまま `.github/workflows/*` に置けます
