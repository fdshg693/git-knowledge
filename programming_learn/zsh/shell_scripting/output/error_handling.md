# Error Handling and Best Practices

## Error Handling in Zsh Scripts

Robust error handling is crucial for reliable shell scripts. This guide covers techniques to make your scripts more resilient and user-friendly.

## Basic Error Handling Concepts

### Exit Status Codes

Every command returns an exit status:
- `0`: Success
- `1-255`: Various error conditions

```zsh
# Check if a command succeeded
if ls /nonexistent/directory; then
    echo "Directory listing successful"
else
    echo "Failed to list directory"
fi

# Using exit status directly
ls /some/directory
if [[ $? -eq 0 ]]; then
    echo "Command succeeded"
else
    echo "Command failed with exit code $?"
fi
```

### The `set` Command for Error Control

```zsh
#!/usr/bin/env zsh

# Exit immediately if any command fails
set -e

# Exit if any undefined variable is used
set -u

# Pipe failures are detected
set -o pipefail

# Combine all three (recommended)
set -euo pipefail
```

### Error Handling Functions

```zsh
#!/usr/bin/env zsh

# Function to handle errors
error_exit() {
    echo "Error: $1" >&2
    exit "${2:-1}"
}

# Function to log messages
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Usage examples
if ! command -v git >/dev/null 2>&1; then
    error_exit "Git is not installed" 1
fi

log_message "Starting backup process"
```

### Trap for Cleanup

```zsh
#!/usr/bin/env zsh

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    rm -f "$temp_file"
    echo "Cleanup complete"
}

# Set trap to run cleanup on exit
trap cleanup EXIT

# Set trap for specific signals
trap 'error_exit "Script interrupted"' INT TERM

temp_file=$(mktemp)
echo "Created temporary file: $temp_file"

# Your script logic here
sleep 5
echo "Script completed"
```

## Input Validation

### Validating Arguments

```zsh
#!/usr/bin/env zsh

validate_args() {
    if [[ $# -lt 2 ]]; then
        error_exit "Usage: $0 <source> <destination>" 1
    fi
    
    local source="$1"
    local dest="$2"
    
    if [[ ! -f "$source" ]]; then
        error_exit "Source file '$source' does not exist" 2
    fi
    
    if [[ -e "$dest" ]]; then
        read -q "REPLY?Destination '$dest' exists. Overwrite? (y/n): "
        echo
        if [[ "$REPLY" != "y" ]]; then
            exit 0
        fi
    fi
}

# Main script
validate_args "$@"
echo "Validation passed"
```

### Validating User Input

```zsh
#!/usr/bin/env zsh

get_user_choice() {
    local prompt="$1"
    local valid_choices="$2"
    local choice
    
    while true; do
        echo -n "$prompt"
        read choice
        
        if [[ "$valid_choices" == *"$choice"* ]]; then
            echo "$choice"
            return 0
        else
            echo "Invalid choice. Please enter one of: $valid_choices"
        fi
    done
}

# Usage
choice=$(get_user_choice "Enter choice (y/n): " "yn")
echo "You chose: $choice"
```

## Debugging Techniques

### Debug Mode

```zsh
#!/usr/bin/env zsh

# Enable debug mode
set -x  # Print commands before executing

# Or conditionally enable debugging
DEBUG=${DEBUG:-0}
if [[ $DEBUG -eq 1 ]]; then
    set -x
fi

# Disable debug mode
set +x
```

### Custom Debug Function

```zsh
#!/usr/bin/env zsh

DEBUG=${DEBUG:-0}

debug() {
    if [[ $DEBUG -eq 1 ]]; then
        echo "DEBUG: $*" >&2
    fi
}

# Usage
debug "Processing file: $filename"
debug "Current directory: $(pwd)"
```

### Error Logging

```zsh
#!/usr/bin/env zsh

LOG_FILE="/tmp/script.log"

log_error() {
    echo "[ERROR $(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE" >&2
}

log_info() {
    echo "[INFO $(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Usage
log_info "Script started"
if ! some_command; then
    log_error "some_command failed"
fi
```

## Best Practices

### 1. Use Strict Mode

```zsh
#!/usr/bin/env zsh
set -euo pipefail
```

### 2. Quote Variables

```zsh
# Good
echo "Hello, $name"
cp "$source" "$destination"

# Bad (can break with spaces or special characters)
echo Hello, $name
cp $source $destination
```

### 3. Check Dependencies

```zsh
check_dependencies() {
    local deps=("git" "curl" "jq")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            missing+=("$dep")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        error_exit "Missing dependencies: ${missing[*]}"
    fi
}
```

### 4. Use Functions for Repeated Code

```zsh
#!/usr/bin/env zsh

# Instead of repeating this pattern:
# if [[ ! -d "$dir1" ]]; then mkdir -p "$dir1"; fi
# if [[ ! -d "$dir2" ]]; then mkdir -p "$dir2"; fi

# Create a function:
ensure_directory() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir" || error_exit "Failed to create directory: $dir"
    fi
}

# Usage
ensure_directory "/tmp/myapp"
ensure_directory "/var/log/myapp"
```

### 5. Validate File Operations

```zsh
safe_copy() {
    local source="$1"
    local dest="$2"
    
    [[ -f "$source" ]] || error_exit "Source file does not exist: $source"
    
    if ! cp "$source" "$dest"; then
        error_exit "Failed to copy $source to $dest"
    fi
    
    echo "Successfully copied $source to $dest"
}
```

### 6. Use Meaningful Exit Codes

```zsh
#!/usr/bin/env zsh

# Define exit codes
readonly EXIT_SUCCESS=0
readonly EXIT_GENERAL_ERROR=1
readonly EXIT_MISSING_DEPENDENCY=2
readonly EXIT_INVALID_ARGUMENT=3
readonly EXIT_FILE_NOT_FOUND=4

# Usage
if [[ ! -f "$config_file" ]]; then
    error_exit "Configuration file not found: $config_file" $EXIT_FILE_NOT_FOUND
fi
```

### 7. Use Readonly Variables for Constants

```zsh
#!/usr/bin/env zsh

# Constants
readonly SCRIPT_NAME=$(basename "$0")
readonly SCRIPT_DIR=$(dirname "$0")
readonly CONFIG_FILE="$HOME/.myapp/config"
readonly LOG_FILE="/tmp/myapp.log"
```

### 8. Handle Signals Gracefully

```zsh
#!/usr/bin/env zsh

# Global variables for state
running=true
job_pid=""

# Signal handlers
handle_sigint() {
    echo "Received SIGINT, stopping gracefully..."
    running=false
    if [[ -n "$job_pid" ]]; then
        kill "$job_pid" 2>/dev/null
    fi
    exit 0
}

handle_sigterm() {
    echo "Received SIGTERM, stopping immediately..."
    if [[ -n "$job_pid" ]]; then
        kill -9 "$job_pid" 2>/dev/null
    fi
    exit 0
}

# Set up signal handlers
trap handle_sigint INT
trap handle_sigterm TERM

# Main loop
while $running; do
    # Start background job
    long_running_command &
    job_pid=$!
    
    # Wait for job to complete
    wait "$job_pid"
    job_pid=""
    
    sleep 5
done
```

## Complete Example: Robust Backup Script

```zsh
#!/usr/bin/env zsh

set -euo pipefail

# Constants
readonly SCRIPT_NAME=$(basename "$0")
readonly LOG_FILE="/tmp/${SCRIPT_NAME%.sh}.log"
readonly DATE_FORMAT="+%Y-%m-%d_%H-%M-%S"

# Error handling
error_exit() {
    echo "ERROR: $1" | tee -a "$LOG_FILE" >&2
    exit "${2:-1}"
}

log() {
    echo "[$(date)] $1" | tee -a "$LOG_FILE"
}

cleanup() {
    if [[ -n "${temp_dir:-}" && -d "$temp_dir" ]]; then
        rm -rf "$temp_dir"
        log "Cleaned up temporary directory: $temp_dir"
    fi
}

# Set up cleanup on exit
trap cleanup EXIT

# Validate arguments
if [[ $# -ne 2 ]]; then
    error_exit "Usage: $SCRIPT_NAME <source_dir> <backup_dir>" 1
fi

source_dir="$1"
backup_dir="$2"

# Validate directories
[[ -d "$source_dir" ]] || error_exit "Source directory does not exist: $source_dir" 2
[[ -d "$backup_dir" ]] || mkdir -p "$backup_dir" || error_exit "Cannot create backup directory: $backup_dir" 3

# Create timestamped backup
timestamp=$(date "$DATE_FORMAT")
backup_name="backup_${timestamp}.tar.gz"
backup_path="$backup_dir/$backup_name"

log "Starting backup of $source_dir to $backup_path"

# Create backup
if tar -czf "$backup_path" -C "$(dirname "$source_dir")" "$(basename "$source_dir")"; then
    log "Backup completed successfully: $backup_path"
    log "Backup size: $(du -h "$backup_path" | cut -f1)"
else
    error_exit "Backup failed" 4
fi

log "Backup process completed"
```

This comprehensive error handling approach ensures your scripts are robust, maintainable, and user-friendly.
