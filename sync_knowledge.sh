#!/bin/bash

# Git Knowledge Repository Sync Script
# This script adds only new files to the repository
# Modifications and deletions are ignored and not pushed to remote
#
# Usage:
#   ./sync_knowledge.sh [commit_message]
#   ./sync_knowledge.sh --restore-deleted  # Restore deleted files from last commit
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
    echo "  $0 --help                     # Show this help message"
    echo ""
    echo "This script adds only new files to the repository."
    echo "Modifications and deletions are ignored and not pushed to remote."
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
if [ "$1" = "--help" ]; then
    show_help
    exit 0
elif [ "$1" = "--restore-deleted" ]; then
    restore_deleted_files
    exit 0
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

# Add only new files (ignore modifications and deletions)
print_status "Adding only new files..."

# Check for deleted files and inform user (but do nothing)
deleted_files=$(git diff --name-only --diff-filter=D)
if [ ! -z "$deleted_files" ]; then
    print_warning "Deleted files detected (will be ignored):"
    echo "$deleted_files" | while read file; do
        log_text "  - $file (deleted locally, ignoring)"
        echo "  - $file"
    done
fi

# Check for modified files and inform user (but do nothing)
modified_files=$(git diff --name-only --diff-filter=M)
if [ ! -z "$modified_files" ]; then
    print_warning "Modified files detected (will be ignored):"
    echo "$modified_files" | while read file; do
        log_text "  ~ $file (modified locally, ignoring)"
        echo "  ~ $file"
    done
fi

# Add only new files (untracked)
new_files=$(git ls-files --others --exclude-standard)
if [ ! -z "$new_files" ]; then
    print_status "Adding new files:"
    echo "$new_files" | while read file; do
        log_text "  + $file"
        echo "  + $file"
        git add "$file"
    done
else
    print_status "No new files to add."
fi

# Check if there are staged changes (should only be new files)
staged_changes=$(git diff --staged --name-only)
if [ -z "$staged_changes" ]; then
    print_status "No new files to commit."
    exit 0
fi

print_status "New files staged for commit:"
echo "$staged_changes" | while read file; do
    log_text "  + $file"
    echo "  + $file"
done

# Create commit message
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
commit_message="Add new files to knowledge repository - $timestamp"

# Allow custom commit message
if [ ! -z "$1" ]; then
    commit_message="$1"
fi

print_status "Committing changes with message: '$commit_message'"
git commit -m "$commit_message"

# Push to remote
print_status "Pushing to remote repository..."
if git push origin "$CURRENT_BRANCH"; then
    print_success "Successfully pushed new files to remote repository!"
else
    print_error "Failed to push to remote repository."
    print_status "You may need to set up the remote repository first:"
    print_status "git remote add origin <your-repository-url>"
    exit 1
fi

print_success "Git knowledge sync completed successfully!"
log_text "=== Git Knowledge Sync Session Completed Successfully ==="
