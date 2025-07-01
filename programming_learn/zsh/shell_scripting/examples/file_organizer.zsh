#!/usr/bin/env zsh

# File Organizer Script
# Demonstrates: arrays, loops, file operations, and functions

set -euo pipefail

# Configuration
readonly SCRIPT_NAME=$(basename "$0")
readonly LOG_FILE="/tmp/${SCRIPT_NAME%.zsh}.log"

# Color codes
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

# File type mappings (associative array)
typeset -A file_types
file_types=(
    [images]="jpg jpeg png gif bmp svg webp"
    [documents]="pdf doc docx txt rtf odt"
    [spreadsheets]="xls xlsx csv ods"
    [presentations]="ppt pptx odp"
    [archives]="zip rar tar gz 7z bz2"
    [audio]="mp3 wav flac aac ogg"
    [video]="mp4 avi mkv mov wmv flv"
    [code]="py js html css php java cpp c sh zsh"
)

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Colored output function
print_colored() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $SCRIPT_NAME [OPTIONS] <source_directory>"
    echo
    echo "Options:"
    echo "  -d, --dry-run    Show what would be moved without actually moving"
    echo "  -h, --help       Show this help message"
    echo "  -v, --verbose    Enable verbose output"
    echo
    echo "This script organizes files in the specified directory by type."
    echo "Files are moved into subdirectories based on their extensions."
}

# Function to get file extension
get_extension() {
    local filename="$1"
    local extension="${filename##*.}"
    echo "${extension:l}"  # Convert to lowercase
}

# Function to determine file category
get_file_category() {
    local extension="$1"
    
    for category in "${(@k)file_types}"; do
        local extensions="${file_types[$category]}"
        if [[ " $extensions " == *" $extension "* ]]; then
            echo "$category"
            return 0
        fi
    done
    
    echo "misc"
}

# Function to create directory if it doesn't exist
ensure_directory() {
    local dir="$1"
    
    if [[ ! -d "$dir" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            print_colored "$YELLOW" "Would create directory: $dir"
        else
            mkdir -p "$dir"
            log "Created directory: $dir"
        fi
    fi
}

# Function to move file
move_file() {
    local source="$1"
    local destination="$2"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_colored "$YELLOW" "Would move: $source -> $destination"
    else
        if mv "$source" "$destination"; then
            log "Moved: $source -> $destination"
            if [[ "$VERBOSE" == "true" ]]; then
                print_colored "$GREEN" "Moved: $(basename "$source") -> $(dirname "$destination")"
            fi
        else
            print_colored "$RED" "Failed to move: $source"
            return 1
        fi
    fi
}

# Function to organize files
organize_files() {
    local source_dir="$1"
    local files_moved=0
    local files_skipped=0
    
    print_colored "$GREEN" "Organizing files in: $source_dir"
    
    # Get all files (not directories) in the source directory
    local files=()
    for file in "$source_dir"/*; do
        if [[ -f "$file" ]]; then
            files+=("$file")
        fi
    done
    
    if [[ ${#files[@]} -eq 0 ]]; then
        print_colored "$YELLOW" "No files found to organize"
        return 0
    fi
    
    print_colored "$GREEN" "Found ${#files[@]} files to process"
    
    # Process each file
    for file in "${files[@]}"; do
        local filename=$(basename "$file")
        local extension=$(get_extension "$filename")
        
        # Skip files without extensions or hidden files
        if [[ "$extension" == "$filename" || "$filename" == .* ]]; then
            if [[ "$VERBOSE" == "true" ]]; then
                print_colored "$YELLOW" "Skipping: $filename (no extension or hidden file)"
            fi
            ((files_skipped++))
            continue
        fi
        
        local category=$(get_file_category "$extension")
        local target_dir="$source_dir/$category"
        local target_file="$target_dir/$filename"
        
        # Create category directory
        ensure_directory "$target_dir"
        
        # Check if target file already exists
        if [[ -f "$target_file" ]]; then
            local counter=1
            local name_without_ext="${filename%.*}"
            local file_ext="${filename##*.}"
            
            while [[ -f "$target_dir/${name_without_ext}_${counter}.${file_ext}" ]]; do
                ((counter++))
            done
            
            target_file="$target_dir/${name_without_ext}_${counter}.${file_ext}"
        fi
        
        # Move the file
        if move_file "$file" "$target_file"; then
            ((files_moved++))
        else
            ((files_skipped++))
        fi
    done
    
    # Summary
    echo
    print_colored "$GREEN" "Organization complete!"
    echo "Files processed: $((files_moved + files_skipped))"
    echo "Files moved: $files_moved"
    echo "Files skipped: $files_skipped"
    
    if [[ "$files_moved" -gt 0 ]]; then
        echo
        print_colored "$GREEN" "Created directories:"
        for category in "${(@k)file_types}"; do
            local dir="$source_dir/$category"
            if [[ -d "$dir" ]]; then
                local count=$(find "$dir" -type f | wc -l)
                echo "  $category: $count files"
            fi
        done
        
        # Check misc directory
        local misc_dir="$source_dir/misc"
        if [[ -d "$misc_dir" ]]; then
            local misc_count=$(find "$misc_dir" -type f | wc -l)
            echo "  misc: $misc_count files"
        fi
    fi
}

# Function to validate directory
validate_directory() {
    local dir="$1"
    
    if [[ ! -d "$dir" ]]; then
        print_colored "$RED" "Error: Directory does not exist: $dir"
        exit 1
    fi
    
    if [[ ! -r "$dir" ]]; then
        print_colored "$RED" "Error: Directory is not readable: $dir"
        exit 1
    fi
    
    if [[ ! -w "$dir" ]] && [[ "$DRY_RUN" != "true" ]]; then
        print_colored "$RED" "Error: Directory is not writable: $dir"
        exit 1
    fi
}

# Main function
main() {
    local source_directory=""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--dry-run)
                DRY_RUN="true"
                shift
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            -*)
                print_colored "$RED" "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                if [[ -z "$source_directory" ]]; then
                    source_directory="$1"
                else
                    print_colored "$RED" "Too many arguments"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Check if directory is provided
    if [[ -z "$source_directory" ]]; then
        print_colored "$RED" "Error: Please specify a source directory"
        show_usage
        exit 1
    fi
    
    # Validate directory
    validate_directory "$source_directory"
    
    # Start organizing
    log "Starting file organization in: $source_directory"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_colored "$YELLOW" "DRY RUN MODE - No files will be moved"
    fi
    
    organize_files "$source_directory"
    
    log "File organization completed"
}

# Initialize variables
DRY_RUN="false"
VERBOSE="false"

# Run main function with all arguments
main "$@"
