#!/usr/bin/env python3
"""
Git Auto Push Script
新規追加されたファイルを自動的にGitでコミット・プッシュするスクリプト
"""

import subprocess
import sys
import os
from datetime import datetime
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "/Users/seiwan/CodeStudy/git-knowledge/logs/git_auto_push.log"
        ),
        logging.StreamHandler(sys.stdout),
    ],
)


class GitAutoPush:
    def __init__(self, repo_path=None):
        """
        GitAutoPushクラスの初期化

        Args:
            repo_path (str): Gitリポジトリのパス（デフォルトは現在のディレクトリ）
        """
        self.repo_path = repo_path or os.getcwd()
        self.logger = logging.getLogger(__name__)

    def run_git_command(self, command):
        """
        Gitコマンドを実行する

        Args:
            command (list): 実行するGitコマンド

        Returns:
            tuple: (成功フラグ, 出力結果, エラーメッセージ)
        """
        try:
            result = subprocess.run(
                command, cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            return True, result.stdout.strip(), None
        except subprocess.CalledProcessError as e:
            return False, e.stdout.strip(), e.stderr.strip()
        except Exception as e:
            return False, "", str(e)

    def check_git_repo(self):
        """
        Gitリポジトリかどうかを確認する

        Returns:
            bool: Gitリポジトリの場合True
        """
        success, _, _ = self.run_git_command(["git", "status"])
        return success

    def get_untracked_files(self):
        """
        新規追加（未追跡）ファイルのリストを取得する

        Returns:
            list: 未追跡ファイルのリスト
        """
        success, output, error = self.run_git_command(["git", "status", "--porcelain"])
        if not success:
            self.logger.error(f"Failed to get git status: {error}")
            return []

        untracked_files = []
        for line in output.split("\n"):
            if line.startswith("??"):
                # ?? はuntracked filesを示す
                filename = line[3:].strip()
                untracked_files.append(filename)

        return untracked_files

    def get_modified_files(self):
        """
        変更されたファイルのリストを取得する
        ステージングエリアにある新規ファイルと変更されたファイルを含む

        Returns:
            list: 変更されたファイルのリスト
        """
        success, output, error = self.run_git_command(["git", "status", "--porcelain"])
        if not success:
            self.logger.error(f"Failed to get git status: {error}")
            return []

        modified_files = []
        for line in output.split("\n"):
            if line.strip():
                line = line.strip()
                status = line.split(" ", 1)[0].strip()
                filename = line.split(" ", 1)[1].strip()
                # M: 修正されたファイル、A: 新規追加されたファイル（ステージング済み）
                # AM: 新規追加後に修正されたファイル、MM: 修正後にさらに修正されたファイル
                if any(char in status for char in ["M", "A"]):
                    modified_files.append(filename)

        return modified_files

    def add_files(self, files):
        """
        ファイルをGitインデックスに追加する

        Args:
            files (list): 追加するファイルのリスト

        Returns:
            bool: 成功フラグ
        """
        if not files:
            self.logger.info("No files to add")
            return True

        # ファイルを一つずつ追加
        for file in files:
            success, output, error = self.run_git_command(["git", "add", file])
            if not success:
                self.logger.error(f"Failed to add file {file}: {error}")
                return False
            else:
                self.logger.info(f"Added file: {file}")

        return True

    def commit_changes(self, message=None):
        """
        変更をコミットする

        Args:
            message (str): コミットメッセージ（デフォルトは自動生成）

        Returns:
            bool: 成功フラグ
        """
        if not message:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"Auto commit: Add new files - {timestamp}"

        success, output, error = self.run_git_command(["git", "commit", "-m", message])
        if not success:
            if error and "nothing to commit" in error:
                self.logger.info("Nothing to commit")
                return True
            else:
                self.logger.error(f"Failed to commit: {error}")
                return False

        self.logger.info(f"Committed successfully: {message}")
        return True

    def push_to_remote(self, remote="origin", branch=None):
        """
        リモートリポジトリにプッシュする

        Args:
            remote (str): リモート名（デフォルトはorigin）
            branch (str): ブランチ名（デフォルトは現在のブランチ）

        Returns:
            bool: 成功フラグ
        """
        # 現在のブランチを取得
        if not branch:
            success, current_branch, error = self.run_git_command(
                ["git", "branch", "--show-current"]
            )
            if not success:
                self.logger.error(f"Failed to get current branch: {error}")
                return False
            branch = current_branch

        success, output, error = self.run_git_command(["git", "push", remote, branch])
        if not success:
            self.logger.error(f"Failed to push to {remote}/{branch}: {error}")
            return False

        self.logger.info(f"Pushed successfully to {remote}/{branch}")
        return True

    def auto_push_new_files(self, commit_message=None, include_modified=False):
        """
        新規ファイルを自動的にコミット・プッシュする

        Args:
            commit_message (str): コミットメッセージ
            include_modified (bool): 変更されたファイルも含めるかどうか

        Returns:
            bool: 成功フラグ
        """
        self.logger.info("Starting auto push process...")

        # Gitリポジトリか確認
        if not self.check_git_repo():
            self.logger.error("This is not a git repository")
            return False

        # 新規ファイルを取得
        untracked_files = self.get_untracked_files()
        files_to_add = untracked_files.copy()

        # 変更されたファイルも含める場合
        if include_modified:
            modified_files = self.get_modified_files()
            # 重複を避けるため、既にリストにないファイルのみを追加
            for file in modified_files:
                if file not in files_to_add:
                    files_to_add.append(file)

        if not files_to_add:
            self.logger.info("No new or modified files to process")
            return True

        self.logger.info(f"Files to process: {files_to_add}")

        # ファイルを追加
        if not self.add_files(files_to_add):
            return False

        # コミット
        if not self.commit_changes(commit_message):
            return False

        # プッシュ
        if not self.push_to_remote():
            return False

        self.logger.info("Auto push completed successfully!")
        return True


def main():
    """
    メイン関数
    """
    import argparse

    parser = argparse.ArgumentParser(description="Git Auto Push Script")
    parser.add_argument("--message", "-m", help="Commit message")
    parser.add_argument(
        "--include-modified",
        "-i",
        action="store_true",
        help="Include modified files in addition to new files",
    )
    parser.add_argument(
        "--repo-path", "-p", help="Repository path (default: current directory)"
    )

    args = parser.parse_args()

    git_auto_push = GitAutoPush(args.repo_path)

    success = git_auto_push.auto_push_new_files(
        commit_message=args.message, include_modified=args.include_modified
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
