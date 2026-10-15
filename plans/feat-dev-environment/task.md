# タスク: 開発環境の構築（feat/dev-environment）

## 事前の整理
- [x] Cloud のペルソナ定義の具体化をコミット
- [x] 設計ドキュメント分割に伴う参照先の更新をコミット

## スクリーンショット撮影ツール
- [x] 開発環境のメモリ・ディスクの空きを確認
- [x] Playwright 公式イメージの取得
- [x] Python の playwright が入っていない問題を Dockerfile で解消
- [x] `shot.py`（撮影・エラー検知）と `run.sh`（コンテナ起動）の作成
- [x] ワイヤーフレームの撮影で動作確認
- [x] 出力先を `.gitignore` に追加
- [x] README に使い方を追記
- [x] 本番の自動デプロイへの影響を調査（影響なし）

## CI
- [x] Issue #1 と依頼内容の統合
- [x] `ruff.toml` の作成と、既存コードの Lint・整形チェック
- [x] `.github/workflows/ci.yml` の作成
- [x] actionlint による構文チェック
- [x] `docker compose config --quiet` の確認
- [x] README・CLAUDE.md への追記
- [x] PR 作成後、GitHub Actions 上で全ジョブのグリーンを確認（3ジョブとも10秒以内に完了）

## 仕上げ
- [x] security エージェントによる差分監査（公開リスクなし。軽微な指摘のうち改行コードと例示パスを修正）
- [x] カンゾーさんへ PR 内容の事前確認
- [x] PR 作成・レビュアー指定・ラベル付与（#3）
