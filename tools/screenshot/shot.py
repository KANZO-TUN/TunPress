"""
HTML ページのスクリーンショット撮影スクリプト

Docker コンテナ（Playwright 公式イメージ）の中で実行する前提。
直接ではなく run.sh 経由で呼び出し。

主な用途
- ワイヤーフレームなど HTML ページの見た目確認
- 将来の CI での表示チェック（コンソールエラーがあれば終了コード 1）
"""

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# 画面サイズの定義（名前で指定できるように）
# mobile: Pixel 相当の縦長画面、desktop: PC の横長画面
VIEWPORTS = {
    "mobile": {"width": 412, "height": 915, "scale": 2},
    "desktop": {"width": 1440, "height": 900, "scale": 1},
    "wide": {"width": 2000, "height": 1100, "scale": 1},
}


def parse_args() -> argparse.Namespace:
    # コマンドライン引数の定義
    parser = argparse.ArgumentParser(description="HTML ページのスクリーンショット撮影")
    parser.add_argument("pages", nargs="+", help="撮影する HTML ファイルのパス（リポジトリ直下からの相対パス）")
    parser.add_argument("--viewport", choices=VIEWPORTS.keys(), default="desktop", help="画面サイズ")
    parser.add_argument("--full-page", action="store_true", help="ページ全体を縦に長く撮影")
    parser.add_argument("--wait", type=float, default=1.5, help="読み込み後に待つ秒数（アニメーション終了待ち）")
    parser.add_argument("--out", default="tools/screenshot/out", help="画像の保存先ディレクトリ")
    parser.add_argument("--allow-errors", action="store_true", help="コンソールエラーがあっても失敗扱いにしない")
    return parser.parse_args()


def shoot(page_path: Path, args: argparse.Namespace, browser) -> list[str]:
    # 1ページ分の撮影処理。発生したエラーの一覧を返却
    vp = VIEWPORTS[args.viewport]
    context = browser.new_context(
        viewport={"width": vp["width"], "height": vp["height"]},
        device_scale_factor=vp["scale"],
        color_scheme="dark",
    )
    page = context.new_page()

    # ブラウザ内で起きたエラーの収集（CI で失敗判定に使用）
    errors: list[str] = []
    page.on("console", lambda msg: errors.append(f"console.{msg.type}: {msg.text}") if msg.type == "error" else None)
    page.on("pageerror", lambda exc: errors.append(f"pageerror: {exc}"))

    # ローカルファイルを file:// の URL として表示
    page.goto(page_path.resolve().as_uri(), wait_until="networkidle")

    # Web フォント（Google Fonts）の読み込み完了待ち
    page.evaluate("document.fonts.ready")

    # 起動画面などのアニメーション終了待ち
    page.wait_for_timeout(args.wait * 1000)

    # 保存先のファイル名: 元ファイル名 + 画面サイズ名
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{page_path.stem}.{args.viewport}.png"
    page.screenshot(path=str(out_file), full_page=args.full_page)
    print(f"撮影: {page_path} -> {out_file}")

    context.close()
    return errors


def main() -> int:
    args = parse_args()
    all_errors: dict[str, list[str]] = {}

    with sync_playwright() as p:
        # ヘッドレス（画面なし）の Chromium を起動
        browser = p.chromium.launch()
        for raw in args.pages:
            path = Path(raw)
            # 存在しないファイルは撮影せずエラーとして記録
            if not path.is_file():
                all_errors[raw] = [f"ファイルが見つからない: {raw}"]
                continue
            errors = shoot(path, args, browser)
            if errors:
                all_errors[raw] = errors
        browser.close()

    # エラーの報告と終了コードの決定
    if all_errors:
        for name, errors in all_errors.items():
            print(f"\n[エラー] {name}", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
        if not args.allow_errors:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
