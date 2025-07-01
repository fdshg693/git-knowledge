#!/bin/zsh

# 現在のディレクトリの直下で.github、backup、logs以外のディレクトリを削除するスクリプト
# 子フォルダ・ファイルもまとめて削除します

set -e  # エラーが発生した場合にスクリプトを終了

# 実行ディレクトリのチェック
EXPECTED_DIR="$HOME/CodeStudy/git-knowledge"
CURRENT_DIR=$(pwd)

if [[ "$CURRENT_DIR" != "$EXPECTED_DIR" ]]; then
    echo "エラー: このスクリプトは $EXPECTED_DIR で実行してください"
    echo "現在のディレクトリ: $CURRENT_DIR"
    exit 1
fi

# ログファイルの設定
LOG_FILE="logs/cleanup_directories.log"

# ログ出力関数
log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" | tee -a "$LOG_FILE"
}

# 保護するディレクトリのリスト
PROTECTED_DIRS=(".github" "backup" "logs", ".git")

log_message "=== ディレクトリ削除スクリプト開始 ==="
log_message "保護されるディレクトリ: ${PROTECTED_DIRS[*]}"
log_message ""

# 現在のディレクトリ内のディレクトリのみを取得
for dir in */; do
    # 末尾の/を削除
    dir_name="${dir%/}"
    
    # 保護されたディレクトリかチェック
    is_protected=false
    for protected in "${PROTECTED_DIRS[@]}"; do
        if [[ "$dir_name" == "$protected" ]]; then
            is_protected=true
            break
        fi
    done
    
    if [[ "$is_protected" == true ]]; then
        log_message "保護: $dir_name (削除されません)"
    else
        log_message "削除中: $dir_name"
        if [[ -d "$dir_name" ]]; then
            rm -rf "$dir_name"
            log_message "削除完了: $dir_name"
        else
            log_message "警告: $dir_name はディレクトリではありません"
        fi
    fi
done

log_message ""
log_message "=== ディレクトリ削除スクリプト完了 ==="
log_message "残存ディレクトリ:"
remaining_dirs=$(ls -la | grep "^d" | awk '{print $9}' | grep -v "^\.$" | grep -v "^\.\.$")
if [[ -n "$remaining_dirs" ]]; then
    while IFS= read -r dir; do
        log_message "  $dir"
    done <<< "$remaining_dirs"
else
    log_message "  (ディレクトリなし)"
fi
