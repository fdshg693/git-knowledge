#!/bin/bash

# Git Knowledge Repository Sync Script
# This script adds new files and modifications to the repository
# while preserving deletions locally (not pushing deletions to remote)

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

# Add all new files (untracked)
new_files=$(git ls-files --others --exclude-standard)
if [ ! -z "$new_files" ]; then
    print_status "Adding new files:"
    echo "$new_files" | while read file; do
        log_text "  + $file"
        git add "$file"
    done
fi

# Add all modified files (but not deleted ones)
modified_files=$(git diff --name-only --diff-filter=M)
if [ ! -z "$modified_files" ]; then
    print_status "Adding modified files:"
    echo "$modified_files" | while read file; do
        log_text "  ~ $file"
        git add "$file"
    done
fi

# Check for deleted files and warn about them
deleted_files=$(git diff --name-only --diff-filter=D)
if [ ! -z "$deleted_files" ]; then
    print_warning "Deleted files detected (will NOT be removed from remote):"
    echo "$deleted_files" | while read file; do
        log_text "  - $file"
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
