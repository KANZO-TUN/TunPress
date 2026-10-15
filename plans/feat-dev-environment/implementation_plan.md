# 実装計画: 開発環境の構築（feat/dev-environment）

関連 Issue: #1（GitHub Actions による CI 自動テスト基盤の導入）

## 目的
- アプリ本体の実装に入る前に、品質を自動で確認できる開発環境を整える
- AI（Claude Code）が画面の見た目を自分で確認できるようにする
- バイブコーディングで混入しがちなミス（構文・型・ビルドの破綻）を PR の段階で検知する

## 調査結果
- リポジトリにはまだアプリ本体（Next.js / FastAPI）のコードが無い。CI は「中身ができた部分から検査が始まる」作りにする必要がある
- 本番デプロイは Portainer が main を自動巡回し、`docker-compose.yaml` に書かれたサービスだけを起動する。CI でデプロイ処理・Secrets を扱う必要はない
- 開発用ツールを `docker-compose.yaml` に入れると本番でも起動してしまうため、compose の外に置く
- 開発環境のホストには Python の仮想環境を作る部品が無い。ツールは Docker の使い捨てコンテナで動かす方針とする

## 設計

### ディレクトリ構成（仮決め。正式には基本設計で確定）
```text
frontend/            # Next.js（未作成）
backend/             # FastAPI（未作成）
tools/screenshot/    # スクリーンショット撮影ツール
.github/workflows/   # CI
ruff.toml            # Python の Lint・整形設定
```

### 1. スクリーンショット撮影ツール（`tools/screenshot/`）
- Playwright 公式イメージ（v1.62.0）に Python の `playwright` を追加した自前イメージ
- `run.sh` がコンテナを使い捨てで起動（メモリ上限 1.5GB、リポジトリは読み取り専用でマウント）
- `shot.py` はコンソールエラーがあれば終了コード 1 を返す（将来 CI での表示チェックに流用）

### 2. CI（`.github/workflows/ci.yml`）
| ジョブ | 内容 | 現時点の動作 |
| :--- | :--- | :--- |
| Docker Compose 構文チェック | `docker compose config --quiet` | 実行 |
| Python | Ruff（Lint・整形チェック）、pytest | Ruff は実行、pytest は `backend/pyproject.toml` ができるまでスキップ |
| フロントエンド | Biome、`tsc --noEmit`、`npm run build` | `frontend/package.json` ができるまでスキップ |

- 発火: main への push と、すべての PR
- 権限は `contents: read` のみ。同じブランチの古い実行は自動キャンセル
- キャッシュ: npm（setup-node）、Next.js のビルドキャッシュ（actions/cache）
- ツールの選定: フロントは Biome（Lint と整形を1つで高速に実行）、Python は Ruff（同じ思想の高速ツール）

## リスクと対策
| リスク | 対策 |
| :--- | :--- |
| main へのマージで本番が再デプロイされる | compose を変更しないため本番コンテナは作り直されない（本番での調査で確認済み） |
| CI が常にスキップでグリーンになり、検査されている錯覚を生む | スキップ時は `::notice::` で理由を明示 |
| Action のバージョン更新で CI が壊れる | メジャーバージョンを固定（checkout / setup-python / setup-node は v7、cache は v6） |

## 検証計画
- `docker compose config --quiet` がローカルで成功すること
- Ruff（0.16.9）の Lint・整形チェックがローカルで通ること（公式 Docker イメージで実行）
- actionlint（1.7.7）でワークフローの構文エラーが無いこと（Docker で実行）
- 撮影ツールでワイヤーフレームを撮影し、画像が生成されること
- PR 作成後、GitHub Actions 上で全ジョブがグリーンになること（フロントエンドと pytest はスキップの通知が出ること）

## 今後
- フロントエンド作成時: `frontend/.nvmrc`・`package-lock.json`・Biome 設定を用意すれば CI が自動で検査を開始
- バックエンド作成時: `backend/pyproject.toml` に `dev` の追加依存として pytest を定義
- 撮影ツールを CI に組み込み、実アプリの画面を開いてエラーが無いかを自動確認
