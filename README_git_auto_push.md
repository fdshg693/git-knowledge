# Git Auto Push Script

新規追加されたファイルを自動的にGitでコミット・プッシュするPythonスクリプトです。

## 機能

- 新規追加（未追跡）ファイルの自動検出
- 変更されたファイルの検出（オプション）
- 自動的なGit add、commit、push
- ログ出力機能
- コマンドライン引数での柔軟な設定

## 使用方法

### 基本的な使用方法

```bash
# 新規ファイルのみを自動コミット・プッシュ
python3 git_auto_push.py

# カスタムコミットメッセージを指定
python3 git_auto_push.py -m "Add new documentation files"

# 変更されたファイルも含めて処理
python3 git_auto_push.py --include-modified

# 全てのオプションを組み合わせ
python3 git_auto_push.py -m "Update project files" --include-modified
```

### コマンドライン引数

- `-m, --message`: コミットメッセージを指定
- `-i, --include-modified`: 変更されたファイルも含めて処理
- `-p, --repo-path`: リポジトリパスを指定（デフォルトは現在のディレクトリ）

### 実行例

```bash
# 新規ファイルのみを処理
python3 git_auto_push.py

# 変更ファイルも含めて処理
python3 git_auto_push.py --include-modified -m "Update and add new files"
```

## ログ

スクリプトの実行ログは以下の場所に保存されます：
- `/Users/seiwan/CodeStudy/git-knowledge/logs/git_auto_push.log`

## 注意事項

- このスクリプトはGitリポジトリ内で実行する必要があります
- リモートリポジトリが設定されている必要があります
- 実行前に必要なファイルのバックアップを取ることを推奨します

## 処理フロー

1. Gitリポジトリかどうかを確認
2. 新規ファイル（未追跡ファイル）を検出
3. オプションで変更されたファイルも検出
4. 検出されたファイルをGitインデックスに追加
5. 自動生成またはカスタムメッセージでコミット
6. リモートリポジトリにプッシュ

## エラーハンドリング

- Git操作に失敗した場合、詳細なエラーメッセージをログに出力
- コミットするものがない場合は正常終了
- ネットワークエラーなどでプッシュに失敗した場合はエラー終了
