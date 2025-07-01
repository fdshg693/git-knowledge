#!/usr/bin/env zsh

#
# Text Processing and Log Analyzer
# Purpose: Demonstrate practical text processing with Zsh
# Usage: ./text_processor.zsh [log_file]
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to display usage
usage() {
    echo "Usage: $0 [log_file]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -i, --interactive  Run in interactive mode"
    echo ""
    echo "If no log file is provided, a sample log will be created."
}

# Function to create sample log file
create_sample_log() {
    local log_file="sample_access.log"
    
    print_colored $BLUE "Creating sample log file: $log_file"
    
    cat > "$log_file" << 'EOF'
192.168.1.100 - - [01/Jul/2025:10:00:01 +0000] "GET /index.html HTTP/1.1" 200 1234
192.168.1.101 - - [01/Jul/2025:10:00:15 +0000] "GET /about.html HTTP/1.1" 200 2456
192.168.1.102 - - [01/Jul/2025:10:01:30 +0000] "POST /login HTTP/1.1" 401 89
192.168.1.100 - - [01/Jul/2025:10:02:45 +0000] "GET /dashboard HTTP/1.1" 200 5678
192.168.1.103 - - [01/Jul/2025:10:03:12 +0000] "GET /api/users HTTP/1.1" 500 123
192.168.1.101 - - [01/Jul/2025:10:04:30 +0000] "GET /images/logo.png HTTP/1.1" 200 9876
192.168.1.104 - - [01/Jul/2025:10:05:45 +0000] "GET /nonexistent HTTP/1.1" 404 234
192.168.1.100 - - [01/Jul/2025:10:06:12 +0000] "DELETE /api/posts/123 HTTP/1.1" 200 0
192.168.1.105 - - [01/Jul/2025:10:07:30 +0000] "GET /admin HTTP/1.1" 403 156
192.168.1.102 - - [01/Jul/2025:10:08:45 +0000] "POST /contact HTTP/1.1" 200 567
EOF
    
    echo "$log_file"
}

# Function to analyze log file
analyze_log() {
    local log_file=$1
    
    if [[ ! -f "$log_file" ]]; then
        print_colored $RED "Error: Log file '$log_file' not found!"
        return 1
    fi
    
    print_colored $GREEN "=== Log Analysis for: $log_file ==="
    echo ""
    
    # Basic statistics
    local total_requests=$(wc -l < "$log_file")
    print_colored $BLUE "Total Requests: $total_requests"
    
    # Status code analysis
    print_colored $YELLOW "Status Code Distribution:"
    awk '{print $9}' "$log_file" | sort | uniq -c | sort -rn | while read count status; do
        case $status in
            2*) echo -e "  ${GREEN}$status${NC}: $count requests" ;;
            3*) echo -e "  ${YELLOW}$status${NC}: $count requests" ;;
            4*) echo -e "  ${RED}$status${NC}: $count requests" ;;
            5*) echo -e "  ${RED}$status${NC}: $count requests" ;;
            *) echo "  $status: $count requests" ;;
        esac
    done
    echo ""
    
    # Top IP addresses
    print_colored $YELLOW "Top 5 IP Addresses:"
    awk '{print $1}' "$log_file" | sort | uniq -c | sort -rn | head -5 | \
    while read count ip; do
        echo "  $ip: $count requests"
    done
    echo ""
    
    # HTTP methods
    print_colored $YELLOW "HTTP Methods:"
    awk '{print $6}' "$log_file" | sed 's/"//g' | sort | uniq -c | sort -rn | \
    while read count method; do
        echo "  $method: $count requests"
    done
    echo ""
    
    # Most requested pages
    print_colored $YELLOW "Top 5 Requested Pages:"
    awk '{print $7}' "$log_file" | sort | uniq -c | sort -rn | head -5 | \
    while read count page; do
        echo "  $page: $count requests"
    done
    echo ""
    
    # Error analysis (4xx and 5xx)
    local error_count=$(awk '$9 ~ /^[45]/ {count++} END {print count+0}' "$log_file")
    if [[ $error_count -gt 0 ]]; then
        print_colored $RED "Errors Found: $error_count"
        print_colored $YELLOW "Error Details:"
        awk '$9 ~ /^[45]/ {print "  " $1 " - " $9 " - " $7}' "$log_file"
    else
        print_colored $GREEN "No errors found!"
    fi
    echo ""
}

# Function for interactive mode
interactive_mode() {
    local log_file=""
    
    print_colored $BLUE "=== Interactive Text Processing Mode ==="
    echo ""
    
    while true; do
        echo "Please choose an option:"
        echo "1. Analyze existing log file"
        echo "2. Create and analyze sample log"
        echo "3. Process custom text file"
        echo "4. Word frequency analysis"
        echo "5. Exit"
        echo -n "Enter choice (1-5): "
        
        read choice
        
        case $choice in
            1)
                echo -n "Enter log file path: "
                read log_file
                if [[ -f "$log_file" ]]; then
                    analyze_log "$log_file"
                else
                    print_colored $RED "File not found: $log_file"
                fi
                ;;
            2)
                log_file=$(create_sample_log)
                analyze_log "$log_file"
                ;;
            3)
                echo -n "Enter text file path: "
                read text_file
                if [[ -f "$text_file" ]]; then
                    process_text_file "$text_file"
                else
                    print_colored $RED "File not found: $text_file"
                fi
                ;;
            4)
                echo -n "Enter text file for word analysis: "
                read text_file
                if [[ -f "$text_file" ]]; then
                    word_frequency_analysis "$text_file"
                else
                    print_colored $RED "File not found: $text_file"
                fi
                ;;
            5)
                print_colored $GREEN "Goodbye!"
                exit 0
                ;;
            *)
                print_colored $RED "Invalid choice. Please try again."
                ;;
        esac
        echo ""
        echo "Press Enter to continue..."
        read
        echo ""
    done
}

# Function to process general text files
process_text_file() {
    local text_file=$1
    
    print_colored $GREEN "=== Text File Analysis for: $text_file ==="
    echo ""
    
    # Basic file statistics
    local line_count=$(wc -l < "$text_file")
    local word_count=$(wc -w < "$text_file")
    local char_count=$(wc -c < "$text_file")
    
    print_colored $BLUE "File Statistics:"
    echo "  Lines: $line_count"
    echo "  Words: $word_count"
    echo "  Characters: $char_count"
    echo ""
    
    # Line length analysis
    print_colored $YELLOW "Line Length Analysis:"
    awk '{print length}' "$text_file" | sort -n | {
        read shortest
        total=0
        count=0
        longest=0
        
        while read length; do
            total=$((total + length))
            count=$((count + 1))
            longest=$length
        done
        
        if [[ $count -gt 0 ]]; then
            average=$((total / count))
            echo "  Shortest line: $shortest characters"
            echo "  Longest line: $longest characters"
            echo "  Average line: $average characters"
        fi
    }
    echo ""
    
    # Find empty lines
    local empty_lines=$(grep -c '^$' "$text_file")
    echo "Empty lines: $empty_lines"
    echo ""
}

# Function for word frequency analysis
word_frequency_analysis() {
    local text_file=$1
    
    print_colored $GREEN "=== Word Frequency Analysis for: $text_file ==="
    echo ""
    
    # Convert to lowercase, remove punctuation, and count words
    print_colored $YELLOW "Top 10 Most Frequent Words:"
    tr '[:upper:]' '[:lower:]' < "$text_file" | \
    tr -d '[:punct:]' | \
    tr ' ' '\n' | \
    grep -v '^$' | \
    sort | \
    uniq -c | \
    sort -rn | \
    head -10 | \
    while read count word; do
        echo "  $word: $count occurrences"
    done
    echo ""
    
    # Unique word count
    local unique_words=$(tr '[:upper:]' '[:lower:]' < "$text_file" | \
                        tr -d '[:punct:]' | \
                        tr ' ' '\n' | \
                        grep -v '^$' | \
                        sort -u | \
                        wc -l)
    
    print_colored $BLUE "Unique words: $unique_words"
}

# Main script logic
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -i|--interactive)
                interactive_mode
                exit 0
                ;;
            -*)
                print_colored $RED "Unknown option: $1"
                usage
                exit 1
                ;;
            *)
                # Assume it's a log file
                if [[ -f "$1" ]]; then
                    analyze_log "$1"
                    exit 0
                else
                    print_colored $RED "File not found: $1"
                    exit 1
                fi
                ;;
        esac
        shift
    done
    
    # If no arguments provided, create sample and analyze
    print_colored $BLUE "No arguments provided. Creating sample log file..."
    local sample_log=$(create_sample_log)
    analyze_log "$sample_log"
    
    echo ""
    print_colored $YELLOW "Tip: Run with -i flag for interactive mode"
    print_colored $YELLOW "Example: $0 -i"
}

# Run main function with all arguments
main "$@"
