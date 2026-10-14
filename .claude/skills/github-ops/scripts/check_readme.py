"""README.md のリンク・ディレクトリ記載の整合性チェック

検証内容
- README.md 内の相対リンク（[テキスト](パス)）の参照先が実在するか
- 参照先が gitignore 対象でないか（GitHub 上ではリンク切れ・非公開資料の露出になるため）
- リポジトリ直下のディレクトリが README.md に記載されているか（記載漏れは警告のみ）

終了コード
- 0: 不整合なし（警告のみの場合も 0）
- 1: リンク切れあり、または README.md が存在しない
"""

import re
import subprocess
import sys
from pathlib import Path

# README に記載不要なディレクトリ名の一覧（依存物・仮想環境・ビルド成果物）
IGNORED_DIRS = {"node_modules", "venv", ".venv", "__pycache__", "dist", "build"}

# Markdown リンク [テキスト](参照先) の抽出用正規表現
#   - 先頭の "!" 付き（画像）も同じ形式のため対象に含む
#   - 参照先の後ろに続くタイトル指定 ("...") は除外
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")

# 外部 URL など、ファイル存在チェックの対象外とする参照先の接頭辞
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#")


def find_repo_root() -> Path:
    """リポジトリのルートディレクトリを取得"""
    try:
        # git 管理下であれば git にルートを問い合わせ
        output = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return Path(output)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # git が使えない場合はスクリプト位置から逆算
        # （scripts → github-ops → skills → .claude → リポジトリルート）
        return Path(__file__).resolve().parents[4]


def is_git_ignored(root: Path, target: Path) -> bool:
    """対象パスが gitignore で除外されているかを判定"""
    try:
        # git check-ignore は除外対象なら終了コード 0、対象外なら 1 を返却
        result = subprocess.run(
            ["git", "-C", str(root), "check-ignore", "-q", str(target)],
            capture_output=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        # git 未インストール時は判定不能のため「除外なし」として扱い
        return False


def check_links(readme: Path, content: str) -> int:
    """README 内の相対リンク切れを検出し、エラー件数を返却"""
    errors = 0
    checked = set()

    for target in LINK_PATTERN.findall(content):
        # 外部 URL・ページ内アンカーは対象外
        if target.startswith(EXTERNAL_PREFIXES):
            continue

        # "path#anchor" のアンカー部分を除去
        path_part = target.split("#", 1)[0]
        if not path_part or path_part in checked:
            continue
        checked.add(path_part)

        # README の位置を基準に相対パスを解決
        resolved = (readme.parent / path_part).resolve()
        if not resolved.exists():
            print(f"❌ リンク切れ: {path_part}")
            errors += 1
        elif is_git_ignored(readme.parent, resolved):
            # ローカルには存在するが GitHub には公開されないパス
            print(f"❌ gitignore 対象へのリンク（GitHub 上でリンク切れ）: {path_part}")
            errors += 1
        else:
            print(f"✅ リンク先の存在確認OK: {path_part}")

    return errors


def check_top_level_dirs(root: Path, content: str) -> None:
    """リポジトリ直下のディレクトリの README 記載漏れを警告"""
    for item in sorted(root.iterdir()):
        # 隠しディレクトリ・ファイル・除外対象はスキップ
        if not item.is_dir() or item.name.startswith(".") or item.name in IGNORED_DIRS:
            continue
        # gitignore 対象（非公開の docs/ 等）は README 記載不要のためスキップ
        if is_git_ignored(root, item):
            continue
        if item.name not in content:
            print(f"⚠️ 注意: ディレクトリ '{item.name}/' が README.md に未記載")


def main() -> int:
    """README 整合性チェックのエントリーポイント"""
    root = find_repo_root()
    readme = root / "README.md"

    # README 自体の存在確認
    if not readme.exists():
        print(f"❌ README.md が見つからない: {readme}")
        return 1

    content = readme.read_text(encoding="utf-8")

    errors = check_links(readme, content)
    check_top_level_dirs(root, content)

    # 結果の集計と終了コードの決定
    if errors:
        print(f"🚨 検証完了: {errors} 件のリンク切れを検出")
        return 1
    print("🎉 検証完了: README.md のリンクはすべて正常")
    return 0


if __name__ == "__main__":
    sys.exit(main())
