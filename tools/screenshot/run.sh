#!/usr/bin/env bash
# スクリーンショット撮影ツールの起動スクリプト
# Playwright 公式イメージのコンテナを使い捨てで起動し、shot.py を実行
#
# 使い方（リポジトリ直下で実行）:
#   tools/screenshot/run.sh path/to/page.html --viewport mobile
#   tools/screenshot/run.sh path/to/board.html --viewport wide --full-page
#
# 画像の保存先: tools/screenshot/out/（gitignore 対象）

# エラー時に即停止、未定義変数の参照を禁止、パイプ途中の失敗も検知
set -euo pipefail

# 使用するイメージ（Dockerfile から作る自前イメージ。タグは Playwright のバージョンと揃える）
IMAGE="tun-press-screenshot:1.62.0"

# リポジトリ直下の絶対パス（このスクリプトの2階層上）
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# イメージが未作成なら初回だけビルド（2回目以降はキャッシュを利用）
if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
  echo "イメージ ${IMAGE} をビルド中（初回のみ）..."
  docker build -q -t "${IMAGE}" "${REPO_ROOT}/tools/screenshot" >/dev/null
fi

# 保存先を先にホスト側で作成（コンテナ内で root 所有のディレクトリが作られるのを防止）
mkdir -p "${REPO_ROOT}/tools/screenshot/out"

# コンテナの起動
# --rm            : 終了後にコンテナを自動削除
# --init          : ブラウザの子プロセスを正しく片付けるための小さな init を同梱
# --memory        : メモリ上限（他のアプリを巻き込まないため）
# --shm-size      : Chromium が使う共有メモリ（既定の 64MB では不足しやすい）
# --user          : ホストと同じユーザーで実行し、画像の所有者を自分にする
# -e HOME         : 上記ユーザーにはホームが無いため一時領域を指定
# -v ...:ro       : リポジトリを読み取り専用でマウント
# -v .../out      : 保存先だけ書き込み可能でマウント
docker run --rm --init \
  --memory=1536m \
  --shm-size=1g \
  --user "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "${REPO_ROOT}:/work:ro" \
  -v "${REPO_ROOT}/tools/screenshot/out:/work/tools/screenshot/out" \
  -w /work \
  "${IMAGE}" \
  python tools/screenshot/shot.py "$@"
