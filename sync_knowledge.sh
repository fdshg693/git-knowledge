#!/bin/bash

# Git Knowledge Repository Sync Script
# This script adds new files and modifications to the repository
# while preserving deletions locally (not pushing deletions to remote)
#
# Usage:
#   ./sync_knowledge.sh [commit_message]
#   ./sync_knowledge.sh --restore-deleted  # Restore deleted files from last commit
#   ./sync_knowledge.sh --allow-deletions  # Allow deletions to be committed to remote
#   ./sync_knowledge.sh --help             # Show help message

set -e  # Exit on any error

# Log file setup
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/sync_knowledge.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log to file and optionally print colored output
log_and_print() {
    local level="$1"
    local color="$2"
    local message="$3"
    local print_to_console="$4"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Log to file (without colors)
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    # Print to console only if specified (with colors)
    if [ "$print_to_console" = "true" ]; then
        echo -e "${color}[$level]${NC} $message"
    fi
}

print_status() {
    log_and_print "INFO" "$BLUE" "$1" "false"
}

print_success() {
    log_and_print "SUCCESS" "$GREEN" "$1" "false"
}

print_warning() {
    log_and_print "WARNING" "$YELLOW" "$1" "false"
}

print_error() {
    log_and_print "ERROR" "$RED" "$1" "true"
}

# Function to show help
show_help() {
    echo "Git Knowledge Repository Sync Script"
    echo ""
    echo "Usage:"
    echo "  $0 [commit_message]           # Sync repository with optional custom commit message"
    echo "  $0 --restore-deleted          # Restore deleted files from last commit"
    echo "  $0 --allow-deletions          # Allow deletions to be committed to remote"
    echo "  $0 --help                     # Show this help message"
    echo ""
    echo "This script adds new files and modifications to the repository"
    echo "while preserving deletions locally (not pushing deletions to remote)."
}

# Function to restore deleted files
restore_deleted_files() {
    print_status "Checking for deleted files to restore..."
    
    deleted_files=$(git diff --name-only --diff-filter=D)
    if [ -z "$deleted_files" ]; then
        print_status "No deleted files found."
        return 0
    fi
    
    print_status "Restoring deleted files from last commit:"
    echo "$deleted_files" | while read file; do
        log_text "  Restoring: $file"
        git checkout HEAD -- "$file"
        echo "  ✓ $file"
    done
    
    print_success "Deleted files have been restored!"
}

# Check command line arguments
ALLOW_DELETIONS=false
if [ "$1" = "--help" ]; then
    show_help
    exit 0
elif [ "$1" = "--restore-deleted" ]; then
    restore_deleted_files
    exit 0
elif [ "$1" = "--allow-deletions" ]; then
    ALLOW_DELETIONS=true
    shift  # Remove the --allow-deletions argument so $1 becomes the commit message
fi

# Function to log plain text (for file lists and detailed output)
log_text() {
    local text="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Log to file only
    echo "[$timestamp] $text" >> "$LOG_FILE"
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "Not in a git repository. Please run this script from the repository root."
    exit 1
fi

print_status "Starting git knowledge sync..."
log_text "=== Git Knowledge Sync Session Started ==="

# Get the current branch
# Check if repository has any commits
if git rev-parse --verify HEAD >/dev/null 2>&1; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
else
    # No commits yet, use default branch name
    CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "main")
fi
print_status "Current branch: $CURRENT_BRANCH"

# Check for uncommitted changes
git_status=$(git status --porcelain)

if [ -z "$git_status" ]; then
    print_status "No changes detected. Repository is up to date."
    exit 0
fi

print_status "Changes detected:"
log_text "$git_status"

# Add new files and modifications (but not deletions)
print_status "Adding new files and modifications..."

# Check for deleted files but don't restore them automatically
deleted_files=$(git diff --name-only --diff-filter=D)
if [ ! -z "$deleted_files" ]; then
    if [ "$ALLOW_DELETIONS" = "true" ]; then
        print_warning "Deleted files detected (will be committed to remote):"
        echo "$deleted_files" | while read file; do
            log_text "  - $file (will be deleted from remote)"
        done
        # Stage the deletions
        echo "$deleted_files" | while read file; do
            git add "$file"
        done
    else
        print_warning "Deleted files detected (will be ignored, not committed to remote):"
        echo "$deleted_files" | while read file; do
            log_text "  - $file (deleted locally, will not be committed)"
        done
    fi
fi

# Add all new files (untracked)
new_files=$(git ls-files --others --exclude-standard)
if [ ! -z "$new_files" ]; then
    print_status "Adding new files:"
    echo "$new_files" | while read file; do
        log_text "  + $file"
        git add "$file"
    done
fi

# Add all modified files (but explicitly exclude any deletions)
modified_files=$(git diff --name-only --diff-filter=M)
if [ ! -z "$modified_files" ]; then
    print_status "Adding modified files:"
    echo "$modified_files" | while read file; do
        log_text "  ~ $file"
        git add "$file"
    done
fi

# Double-check: unstage any deletions that might have been accidentally staged
staged_deletions=$(git diff --staged --name-only --diff-filter=D)
if [ ! -z "$staged_deletions" ]; then
    print_warning "Unstaging deleted files to prevent remote deletion:"
    echo "$staged_deletions" | while read file; do
        log_text "  Unstaging deletion: $file"
        git reset HEAD -- "$file" 2>/dev/null || true
        # Restore the file again if it was deleted
        git checkout HEAD -- "$file" 2>/dev/null || true
    done
fi

# Check if there are staged changes
staged_changes=$(git diff --staged --name-only)
if [ -z "$staged_changes" ]; then
    print_status "No changes to commit."
    exit 0
fi

print_status "Staged files for commit:"
echo "$staged_changes" | while read file; do
    log_text "  $file"
done

# Create commit message
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
commit_message="Update knowledge repository - $timestamp"

# Allow custom commit message
if [ ! -z "$1" ]; then
    commit_message="$1"
fi

print_status "Committing changes with message: '$commit_message'"
git commit -m "$commit_message"

# Push to remote
print_status "Pushing to remote repository..."
if git push origin "$CURRENT_BRANCH"; then
    print_success "Successfully pushed changes to remote repository!"
else
    print_error "Failed to push to remote repository."
    print_status "You may need to set up the remote repository first:"
    print_status "git remote add origin <your-repository-url>"
    exit 1
fi

print_success "Git knowledge sync completed successfully!"
log_text "=== Git Knowledge Sync Session Completed Successfully ==="
