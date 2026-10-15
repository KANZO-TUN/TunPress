# 作業のまとめ: 開発環境の構築（feat/dev-environment）

PR: #3 / 関連 Issue: #1

## やったこと
1. **スクリーンショット撮影ツール**（`tools/screenshot/`）
   - Playwright 公式イメージに Python の `playwright` を追加した使い捨てコンテナで、HTML ページを撮影
   - 1回あたり約7秒（イメージのビルド済みの場合）
2. **CI**（`.github/workflows/ci.yml`）
   - Docker Compose 構文チェック、Ruff（Lint・整形）、pytest（backend 作成後）、Biome・型チェック・ビルド（frontend 作成後）
   - 未作成部分はスキップし、実行結果に通知を表示
3. **整理**: Cloud のペルソナ定義の具体化、設計ドキュメント分割に伴う参照先の更新、README・CLAUDE.md への追記

## 検証結果
| 項目 | 結果 |
| :--- | :--- |
| `docker compose config --quiet` | 成功 |
| Ruff 0.16.9（Lint / 整形） | All checks passed / 18 files already formatted |
| actionlint 1.7.7 | エラーなし |
| 撮影ツール | ワイヤーフレームの撮影に成功。撮影した画像から表示崩れを2件発見・修正 |
| security エージェントの監査 | 公開リスクなし。軽微な指摘（改行コード・例示パス）を修正 |
| GitHub Actions（PR #3） | 3ジョブともグリーン（4〜7秒）。pytest とフロントエンドにスキップの通知が出ることを確認 |

## つまずいた点と解決
| 症状 | 原因 | 解決 |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'playwright'` | 公式イメージにはブラウザはあるが Python のパッケージが無い | 公式イメージに `pip install playwright==1.62.0` を足す Dockerfile を作成 |
| ホストで Python の仮想環境が作れない | `python3-venv` が未導入 | ホストに入れず、Ruff も公式 Docker イメージで実行 |
| `.gitignore` の差分が全行の書き換えに見える | 編集時に改行コードが CRLF から LF に変わった | CRLF に戻して差分を最小化 |

## 本番への影響
- 開発用ツールは `docker-compose.yaml` に入れていないため、main へのマージ後も本番で起動しない
- 本番コンテナの作成・起動時刻の調査から、compose を変えないコミットではコンテナが作り直されないことを確認

## 今後
- フロントエンド・バックエンドの作成時に、CI の検査が自動で有効になる（`frontend/.nvmrc`・`package-lock.json`・Biome 設定、`backend/pyproject.toml` を用意）
- 撮影ツールを CI に組み込み、実アプリの画面を開いてエラーが無いかを自動確認
- `ubuntu-latest` が 2026-10-19 から Ubuntu 26 に切り替わる告知あり。必要に応じてバージョンを固定
