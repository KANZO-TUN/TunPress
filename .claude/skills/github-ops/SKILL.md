---
name: github-ops
description: AI 名義での git commit、gh による PR 作成・レビュアー指定・進捗ラベル貼り替え・レビューコメントへのスレッド返信、README 整合性チェックの具体的なコマンド手順。コミット・push・PR 操作を行うときに使う。
---

# GitHub 操作手順（TunPress）

ルールそのもの（いつ・何をするか）は `.claude/rules/git.md` と `.claude/rules/pull-request.md` が正本。本スキルは「どう実行するか」のコマンド集。

- リポジトリ: `KANZO-TUN/TunPress`
- 認証情報: リポジトリ直下の `.secrets/github/`（`github_username`, `github_email`, `github_token`）
- コマンドはすべてリポジトリのルートで実行する。

## 1. AI 名義でのコミット
`git config` は変更せず、そのコマンドだけに有効な環境変数で名義を渡す。

```bash
AI_NAME=$(cat .secrets/github/github_username)
AI_EMAIL=$(cat .secrets/github/github_email)
GIT_AUTHOR_NAME="$AI_NAME" GIT_AUTHOR_EMAIL="$AI_EMAIL" \
GIT_COMMITTER_NAME="$AI_NAME" GIT_COMMITTER_EMAIL="$AI_EMAIL" \
  git commit -m "feat: 〇〇を追加" -m "本文（日本語・体言止め）"
```

## 2. push 前のチェック
1. `python3 .claude/skills/github-ops/scripts/check_readme.py` を実行し、README の整合性を確認する。
2. `security` サブエージェントで差分を監査し、「公開リスクなし」を確認する。

## 3. PR の作成とレビュアー指定
`gh` は `GH_TOKEN` を一時的に渡して実行する（カンゾーさんのログイン状態には触れない）。

```bash
GH_TOKEN=$(cat .secrets/github/github_token) \
  gh pr create --base main --title "feat: 〇〇を追加" \
  --body-file /path/to/pr_body.md --reviewer KANZO-TUN
```

`gh pr edit` で GraphQL 関連のエラーが出る場合は、REST API を使う。

```bash
GH_TOKEN=$(cat .secrets/github/github_token) \
  gh api /repos/KANZO-TUN/TunPress/pulls/<PR番号>/requested_reviewers \
  -f "reviewers[]=KANZO-TUN"
```

## 4. 進捗ラベルの貼り替え
次のラベルを貼ってから、前のラベルを外す（REST API で統一）。

```bash
# 次フェーズのラベルを追加
GH_TOKEN=$(cat .secrets/github/github_token) \
  gh api /repos/KANZO-TUN/TunPress/issues/<PR番号>/labels -f "labels[]=2.needs-review"

# 前フェーズのラベルを削除
GH_TOKEN=$(cat .secrets/github/github_token) \
  gh api -X DELETE /repos/KANZO-TUN/TunPress/issues/<PR番号>/labels/1.unit-test-passed
```

## 5. レビューコメントへのスレッド返信
1. 返信先のコメント ID を取得する。
   ```bash
   GH_TOKEN=$(cat .secrets/github/github_token) \
     gh api /repos/KANZO-TUN/TunPress/pulls/<PR番号>/comments \
     --jq '.[] | {id, path, line, body}'
   ```
2. 指摘ごとに個別コミットで修正し、push する。
3. `in_reply_to` を指定して、そのスレッドに返信する（修正コミットはリンク形式で記載）。
   ```bash
   GH_TOKEN=$(cat .secrets/github/github_token) \
     gh api /repos/KANZO-TUN/TunPress/pulls/<PR番号>/comments \
     -f body="ご指摘ありがとうございます。[abcdef1](https://github.com/KANZO-TUN/TunPress/commit/<フルSHA>) で修正しました。" \
     -F in_reply_to=<コメントID>
   ```
