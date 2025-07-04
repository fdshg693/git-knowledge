import os
from pathlib import Path
import argparse
import json


def load_config_file(config_path):
    """
    設定ファイルから保持対象を読み込む

    Args:
        config_path: 設定ファイルのパス

    Returns:
        tuple: (keep_files, keep_dirs) のタプル
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        keep_files = config.get("keep_files", [])
        keep_dirs = config.get("keep_dirs", [])

        print(f"設定ファイルから読み込み完了: {config_path}")
        return keep_files, keep_dirs

    except FileNotFoundError:
        print(f"エラー: 設定ファイル {config_path} が見つかりません")
        return [], []
    except json.JSONDecodeError as e:
        print(f"エラー: 設定ファイルのJSON形式が正しくありません - {e}")
        return [], []
    except Exception as e:
        print(f"エラー: 設定ファイルの読み込みに失敗しました - {e}")
        return [], []


def should_keep_file(file_path, keep_files, keep_dirs, target_dir=None):
    """
    ファイルを保持すべきかどうかを判断する

    Args:
        file_path: チェックするファイルのパス
        keep_files: 保持するファイル名のリスト
        keep_dirs: 保持するディレクトリパスのリスト
        target_dir: 対象ディレクトリ（相対パス解決用）

    Returns:
        bool: 保持する場合True
    """
    file_path = Path(file_path)

    # ファイル名が保持リストに含まれているかチェック
    if file_path.name in keep_files:
        return True

    # ファイルが保持ディレクトリ配下にあるかチェック
    for keep_dir in keep_dirs:
        keep_dir_path = Path(keep_dir)

        # 相対パスの場合は target_dir を基準に絶対パスに変換
        if not keep_dir_path.is_absolute() and target_dir:
            keep_dir_path = Path(target_dir) / keep_dir_path

        try:
            # 絶対パスに正規化して比較
            keep_dir_path = keep_dir_path.resolve()
            file_path_resolved = file_path.resolve()

            if (
                keep_dir_path in file_path_resolved.parents
                or file_path_resolved == keep_dir_path
            ):
                return True
        except Exception:
            continue

    return False


def delete_files_except(target_dir, keep_files=None, keep_dirs=None, dry_run=False):
    """
    指定したファイル名・ディレクトリ配下以外のファイルを削除

    Args:
        target_dir: 対象ディレクトリ
        keep_files: 保持するファイル名のリスト
        keep_dirs: 保持するディレクトリパスのリスト
        dry_run: True の場合、実際には削除せずに削除対象を表示
    """
    if keep_files is None:
        keep_files = []
    if keep_dirs is None:
        keep_dirs = []

    target_path = Path(target_dir)
    if not target_path.exists():
        print(f"エラー: ディレクトリ {target_dir} が存在しません")
        return

    deleted_files = []

    # ファイルの削除
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for file in files:
            file_path = Path(root) / file

            if not should_keep_file(file_path, keep_files, keep_dirs, target_dir):
                if dry_run:
                    print(f"[DRY RUN] 削除対象ファイル: {file_path}")
                else:
                    try:
                        file_path.unlink()
                        deleted_files.append(str(file_path))
                        print(f"削除しました: {file_path}")
                    except Exception as e:
                        print(f"エラー: {file_path} の削除に失敗しました - {e}")

    # 空ディレクトリの削除
    deleted_dirs = []
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name

            # ディレクトリが空で、保持対象でない場合削除
            if not should_keep_file(dir_path, [], keep_dirs, target_dir):
                try:
                    if not any(dir_path.iterdir()):  # 空ディレクトリかチェック
                        if dry_run:
                            print(f"[DRY RUN] 削除対象ディレクトリ: {dir_path}")
                        else:
                            dir_path.rmdir()
                            deleted_dirs.append(str(dir_path))
                            print(f"空ディレクトリを削除しました: {dir_path}")
                except Exception as e:
                    print(f"エラー: {dir_path} の削除に失敗しました - {e}")

    print("\n削除完了:")
    print(f"  ファイル: {len(deleted_files)}個")
    print(f"  ディレクトリ: {len(deleted_dirs)}個")


def main():
    parser = argparse.ArgumentParser(
        description="特定のファイル・ディレクトリ配下以外を削除",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # README.md と LICENSE ファイルを残して他を削除
  python file_cleanup.py /path/to/dir --keep-files README.md LICENSE
  
  # docs/ ディレクトリ配下のファイルを残して他を削除
  python file_cleanup.py /path/to/dir --keep-dirs docs/
  
  # 複数の条件を指定
  python file_cleanup.py /path/to/dir --keep-files .gitignore --keep-dirs src/ tests/
  
  # 削除対象を確認（実際には削除しない）
  python file_cleanup.py /path/to/dir --keep-files README.md --dry-run
  
  # 設定ファイルから保持対象を読み込み
  python file_cleanup.py /path/to/dir --config config.json
  
設定ファイル例（config.json）:
{
  "keep_files": ["README.md", ".gitignore"],
  "keep_dirs": ["src", "docs", "tests/unit"]
}
注意: keep_dirs では相対パスと絶対パス両方が使用可能です
        """,
    )

    parser.add_argument("target_dir", help="対象ディレクトリ")
    parser.add_argument(
        "--keep-files", nargs="*", default=[], help="保持するファイル名（複数指定可能）"
    )
    parser.add_argument(
        "--keep-dirs",
        nargs="*",
        default=[],
        help="保持するディレクトリパス（複数指定可能）",
    )
    parser.add_argument(
        "--config",
        help="保持対象を記載した設定ファイル（JSON形式）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="削除対象を表示するのみ（実際には削除しない）",
    )

    args = parser.parse_args()

    keep_files = args.keep_files[:]
    keep_dirs = args.keep_dirs[:]

    # 設定ファイルが指定されている場合は読み込み
    if args.config:
        config_files, config_dirs = load_config_file(args.config)
        keep_files.extend(config_files)
        keep_dirs.extend(config_dirs)

    print(f"対象ディレクトリ: {args.target_dir}")
    print(f"保持ファイル: {keep_files}")
    print(f"保持ディレクトリ: {keep_dirs}")
    print(f"ドライラン: {args.dry_run}")
    print("-" * 50)

    if not args.dry_run:
        confirm = input("本当に削除しますか？ (y/N): ")
        if confirm.lower() != "y":
            print("キャンセルされました")
            return

    delete_files_except(
        args.target_dir,
        keep_files=keep_files,
        keep_dirs=keep_dirs,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
