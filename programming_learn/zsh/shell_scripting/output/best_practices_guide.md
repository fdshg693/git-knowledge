# Beginner-Friendly Shell Scripting Best Practices

## Overview

This guide provides essential best practices for writing maintainable, reliable, and professional Zsh scripts. Following these practices will help you avoid common pitfalls and create scripts that are easy to understand and debug.

## 1. Script Structure and Organization

### Always Start with a Proper Shebang

```zsh
#!/usr/bin/env zsh
```

**Why this matters:**
- Ensures your script runs with Zsh regardless of the user's default shell
- More portable than hardcoded paths like `#!/bin/zsh`

### Include Script Metadata

```zsh
#!/usr/bin/env zsh

#
# Script: backup_photos.zsh
# Purpose: Backup photos from phone to computer
# Author: Your Name
# Date: 2025-07-01
# Version: 1.0
# Usage: ./backup_photos.zsh [source] [destination]
#

# Script description and usage
SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(dirname "$0")"
```

### Use Consistent Formatting

```zsh
# Good formatting
if [[ -f "$file" ]]; then
    echo "File exists"
    process_file "$file"
else
    echo "File not found"
    exit 1
fi

# Avoid inconsistent indentation
if [[ -f "$file" ]]; then
echo "File exists"
  process_file "$file"
    else
echo "File not found"
exit 1
fi
```

## 2. Variable Handling Best Practices

### Use Meaningful Variable Names

```zsh
# Good
user_home_directory="/home/username"
backup_timestamp=$(date +%Y%m%d_%H%M%S)
max_file_size=1048576  # 1MB in bytes

# Avoid
dir="/home/username"
ts=$(date +%Y%m%d_%H%M%S)
max=1048576
```

### Quote Variables to Prevent Word Splitting

```zsh
# Always quote variables
file_name="my document.txt"
if [[ -f "$file_name" ]]; then  # Correct
    echo "Found: $file_name"
fi

# Avoid unquoted variables
if [[ -f $file_name ]]; then    # Wrong - will fail with spaces
    echo "Found: $file_name"
fi
```

### Use Local Variables in Functions

```zsh
process_files() {
    local input_dir="$1"    # Local variable
    local file_count=0      # Local variable
    
    for file in "$input_dir"/*; do
        if [[ -f "$file" ]]; then
            ((file_count++))
        fi
    done
    
    echo "Processed $file_count files"
}
```

### Check if Variables are Set

```zsh
# Method 1: Using parameter expansion
backup_dir="${BACKUP_DIR:-/tmp/backup}"

# Method 2: Explicit checking
if [[ -z "$REQUIRED_VAR" ]]; then
    echo "Error: REQUIRED_VAR must be set"
    exit 1
fi

# Method 3: Using set -u to catch unset variables
set -u  # Exit if unset variable is used
```

## 3. Error Handling and Validation

### Enable Strict Error Handling

```zsh
#!/usr/bin/env zsh

# Exit on any error
set -e

# Exit on undefined variables
set -u

# Make pipes fail if any command fails
set -o pipefail
```

### Check Command Success

```zsh
# Method 1: Check exit status
if ! cp "$source" "$destination"; then
    echo "Error: Failed to copy $source to $destination"
    exit 1
fi

# Method 2: Use && and ||
cp "$source" "$destination" && echo "Copy successful" || {
    echo "Copy failed"
    exit 1
}

# Method 3: Check specific commands exist
if ! command -v rsync &> /dev/null; then
    echo "Error: rsync is required but not installed"
    exit 1
fi
```

### Validate Input Parameters

```zsh
validate_input() {
    local file="$1"
    
    # Check if parameter provided
    if [[ -z "$file" ]]; then
        echo "Error: No file specified"
        return 1
    fi
    
    # Check if file exists
    if [[ ! -f "$file" ]]; then
        echo "Error: File '$file' does not exist"
        return 1
    fi
    
    # Check if file is readable
    if [[ ! -r "$file" ]]; then
        echo "Error: File '$file' is not readable"
        return 1
    fi
    
    return 0
}

# Usage
if validate_input "$1"; then
    process_file "$1"
fi
```

## 4. Function Best Practices

### Write Single-Purpose Functions

```zsh
# Good - single purpose
get_file_size() {
    local file="$1"
    [[ -f "$file" ]] && stat -c%s "$file" 2>/dev/null || echo 0
}

is_valid_email() {
    local email="$1"
    [[ "$email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]
}

# Avoid - multiple purposes in one function
process_and_validate_and_backup() {
    # Too many responsibilities
}
```

### Include Function Documentation

```zsh
#
# Function: backup_directory
# Purpose: Create a compressed backup of a directory
# Parameters:
#   $1 - Source directory path
#   $2 - Backup destination path
# Returns: 0 on success, 1 on failure
# Example: backup_directory "/home/user/docs" "/backups"
#
backup_directory() {
    local source_dir="$1"
    local backup_dir="$2"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_name="backup_${timestamp}.tar.gz"
    
    # Validation
    [[ -d "$source_dir" ]] || { echo "Source directory not found"; return 1; }
    [[ -d "$backup_dir" ]] || mkdir -p "$backup_dir"
    
    # Create backup
    tar -czf "${backup_dir}/${backup_name}" -C "$(dirname "$source_dir")" "$(basename "$source_dir")"
}
```

## 5. User Interaction Best Practices

### Provide Clear Usage Instructions

```zsh
usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS] source destination

Description:
    Backup files from source to destination with optional compression

Arguments:
    source         Source directory or file to backup
    destination    Destination directory for backup

Options:
    -c, --compress    Compress backup files
    -v, --verbose     Verbose output
    -h, --help        Show this help message

Examples:
    $SCRIPT_NAME /home/user/docs /backups
    $SCRIPT_NAME -c -v /home/user/docs /backups

EOF
}
```

### Implement Proper Argument Parsing

```zsh
# Initialize variables
COMPRESS=false
VERBOSE=false
SOURCE=""
DESTINATION=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--compress)
            COMPRESS=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
        *)
            if [[ -z "$SOURCE" ]]; then
                SOURCE="$1"
            elif [[ -z "$DESTINATION" ]]; then
                DESTINATION="$1"
            else
                echo "Too many arguments"
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate required arguments
if [[ -z "$SOURCE" || -z "$DESTINATION" ]]; then
    echo "Error: Both source and destination are required"
    usage
    exit 1
fi
```

### Provide User Feedback

```zsh
# Use consistent messaging
log_info() {
    echo "[INFO] $1"
}

log_warning() {
    echo "[WARNING] $1" >&2
}

log_error() {
    echo "[ERROR] $1" >&2
}

# Progress indicators for long operations
show_progress() {
    local current=$1
    local total=$2
    local percent=$((current * 100 / total))
    printf "\rProgress: %d%% (%d/%d)" $percent $current $total
}

# Example usage
log_info "Starting backup process..."
for i in {1..100}; do
    # Simulate work
    sleep 0.1
    show_progress $i 100
done
echo  # New line after progress
log_info "Backup completed successfully"
```

## 6. Code Readability and Maintenance

### Use Comments Effectively

```zsh
# Good comments explain WHY, not just WHAT
# Convert timestamp to human-readable format for log files
formatted_date=$(date -d "@$timestamp" "+%Y-%m-%d %H:%M:%S")

# Group related functionality with section comments
#==========================================
# File Processing Functions
#==========================================

# Avoid obvious comments
file_count=0  # Set file count to zero (obvious)
```

### Organize Code Logically

```zsh
#!/usr/bin/env zsh

#==========================================
# Constants and Configuration
#==========================================
readonly SCRIPT_NAME="$(basename "$0")"
readonly DEFAULT_BACKUP_DIR="/tmp/backup"
readonly MAX_RETRIES=3

#==========================================
# Global Variables
#==========================================
VERBOSE=false
DRY_RUN=false

#==========================================
# Utility Functions
#==========================================
log_info() { /* ... */ }
log_error() { /* ... */ }

#==========================================
# Core Functions
#==========================================
backup_files() { /* ... */ }
restore_files() { /* ... */ }

#==========================================
# Main Script Logic
#==========================================
main() {
    parse_arguments "$@"
    validate_environment
    execute_backup
}

# Entry point
main "$@"
```

## 7. Security Considerations

### Avoid Command Injection

```zsh
# Dangerous - user input directly in command
user_input="$1"
eval "ls $user_input"  # Never do this!

# Safe - validate and quote input
user_input="$1"
if [[ "$user_input" =~ ^[a-zA-Z0-9_/-]+$ ]]; then
    ls "$user_input"
else
    echo "Invalid input"
    exit 1
fi
```

### Handle Temporary Files Securely

```zsh
# Create secure temporary files
temp_file=$(mktemp) || {
    echo "Failed to create temporary file"
    exit 1
}

# Always clean up temporary files
cleanup() {
    [[ -f "$temp_file" ]] && rm -f "$temp_file"
}

trap cleanup EXIT  # Cleanup on script exit
```

### Set Appropriate File Permissions

```zsh
# Create files with restricted permissions
backup_file="${backup_dir}/backup_$(date +%Y%m%d).tar.gz"
touch "$backup_file"
chmod 600 "$backup_file"  # Only owner can read/write
```

## 8. Testing and Debugging

### Include Debug Mode

```zsh
# Add debug option
DEBUG=false

debug_log() {
    if [[ "$DEBUG" == true ]]; then
        echo "[DEBUG] $1" >&2
    fi
}

# Usage
debug_log "Processing file: $filename"
```

### Test Edge Cases

```zsh
# Test your scripts with various inputs
test_backup_function() {
    echo "Testing backup function..."
    
    # Test with non-existent source
    backup_directory "/nonexistent" "/tmp" && echo "FAIL: Should have failed" || echo "PASS: Correctly failed"
    
    # Test with valid inputs
    mkdir -p "/tmp/test_source"
    backup_directory "/tmp/test_source" "/tmp" && echo "PASS: Backup succeeded" || echo "FAIL: Backup failed"
    
    # Cleanup
    rm -rf "/tmp/test_source"
}
```

## 9. Performance Considerations

### Avoid Unnecessary Subshells

```zsh
# Slow - creates subshell for each iteration
for file in $(ls); do
    echo "Processing $file"
done

# Fast - uses globbing
for file in *; do
    echo "Processing $file"
done
```

### Use Built-in Commands When Possible

```zsh
# Slow - external command
filename=$(basename "$filepath")

# Fast - parameter expansion
filename="${filepath##*/}"

# Slow - external command
extension=$(echo "$filename" | cut -d. -f2)

# Fast - parameter expansion
extension="${filename##*.}"
```

## 10. Summary Checklist

Before considering your script complete, check:

- ✅ Proper shebang line (`#!/usr/bin/env zsh`)
- ✅ Script metadata and usage function
- ✅ Consistent indentation and formatting
- ✅ All variables quoted appropriately
- ✅ Input validation for all parameters
- ✅ Error handling for critical operations
- ✅ Functions have single responsibilities
- ✅ Clear, helpful comments
- ✅ Temporary files cleaned up
- ✅ Security considerations addressed
- ✅ Script tested with various inputs

Following these best practices will help you write professional, maintainable shell scripts that are reliable and easy to understand.
