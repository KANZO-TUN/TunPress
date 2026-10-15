# TunPress

ニュース記事配信・管理アプリケーション

## 構成
- Docker / Docker Compose
- 自動デプロイ: Portainer

## ディレクトリ
| パス | 内容 |
| :--- | :--- |
| [docker-compose.yaml](docker-compose.yaml) | コンテナ構成 |
| [CLAUDE.md](CLAUDE.md) | Claude Code 用の開発ガイドライン（入口） |
| [.claude/](.claude/) | Claude Code の規約・サブエージェント・スキル |
| [plans/](plans/) | ブランチ単位の実装計画・タスク |
| [tools/screenshot/](tools/screenshot/) | HTML ページのスクリーンショット撮影ツール（Docker / Playwright） |
| [.github/workflows/](.github/workflows/) | CI（品質チェック） |
| [ruff.toml](ruff.toml) | Python の Lint・整形設定 |

## CI
GitHub Actions で、main への push とすべてのプルリクエストに対して品質チェックを実行する（デプロイは行わない）。

| ジョブ | 内容 |
| :--- | :--- |
| Docker Compose 構文チェック | `docker compose config --quiet` |
| Python | Ruff による Lint・整形チェック、`backend/` 作成後は pytest |
| フロントエンド | `frontend/` 作成後に Biome・型チェック（`tsc --noEmit`）・本番ビルド |

未作成の部分の検査はスキップし、その旨を実行結果に表示する。

## 開発補助ツール

### スクリーンショット撮影
HTML ページを Docker 上のヘッドレスブラウザで開いて撮影する。コンソールエラーがあれば終了コード 1 を返すため、CI での表示チェックにも使える。

```bash
# スマホ幅で撮影（画像は tools/screenshot/out/ に保存）
tools/screenshot/run.sh path/to/page.html --viewport mobile

# PC の横長画面でページ全体を撮影
tools/screenshot/run.sh path/to/page.html --viewport wide --full-page
```
