# スクリーンショット撮影ツール用のイメージ
# 公式イメージにはブラウザ（Chromium 等）と依存ライブラリが入っているが、
# Python 側の playwright パッケージは入っていないため追加
FROM mcr.microsoft.com/playwright/python:v1.62.0-noble

# ブラウザと同じバージョンの playwright を導入（バージョンがずれるとブラウザが見つからない）
# --break-system-packages: Ubuntu 24.04 のシステム Python へ直接入れるための許可（使い捨てコンテナのため許容）
RUN pip install --no-cache-dir --break-system-packages playwright==1.62.0
