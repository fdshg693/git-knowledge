#!/usr/bin/env zsh

# Basic Calculator Script
# Demonstrates: variables, user input, arithmetic, conditionals, and functions

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Function to display colored output
print_colored() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

# Function to display the menu
show_menu() {
    echo
    print_colored "$BLUE" "=== Basic Calculator ==="
    echo "1. Addition"
    echo "2. Subtraction"
    echo "3. Multiplication"
    echo "4. Division"
    echo "5. Exit"
    echo -n "Choose an operation (1-5): "
}

# Function to get a number from user
get_number() {
    local prompt="$1"
    local number
    
    while true; do
        echo -n "$prompt"
        read number
        
        # Check if input is a valid number
        if [[ "$number" =~ ^-?[0-9]+\.?[0-9]*$ ]]; then
            echo "$number"
            return 0
        else
            print_colored "$RED" "Error: Please enter a valid number"
        fi
    done
}

# Function to perform addition
add_numbers() {
    local num1="$1"
    local num2="$2"
    local result
    
    result=$(echo "$num1 + $num2" | bc -l)
    print_colored "$GREEN" "Result: $num1 + $num2 = $result"
}

# Function to perform subtraction
subtract_numbers() {
    local num1="$1"
    local num2="$2"
    local result
    
    result=$(echo "$num1 - $num2" | bc -l)
    print_colored "$GREEN" "Result: $num1 - $num2 = $result"
}

# Function to perform multiplication
multiply_numbers() {
    local num1="$1"
    local num2="$2"
    local result
    
    result=$(echo "$num1 * $num2" | bc -l)
    print_colored "$GREEN" "Result: $num1 × $num2 = $result"
}

# Function to perform division
divide_numbers() {
    local num1="$1"
    local num2="$2"
    local result
    
    # Check for division by zero
    if [[ "$num2" == "0" ]]; then
        print_colored "$RED" "Error: Division by zero is not allowed"
        return 1
    fi
    
    result=$(echo "scale=4; $num1 / $num2" | bc -l)
    print_colored "$GREEN" "Result: $num1 ÷ $num2 = $result"
}

# Function to perform calculation based on choice
calculate() {
    local choice="$1"
    local num1 num2
    
    # Get numbers from user
    num1=$(get_number "Enter first number: ")
    num2=$(get_number "Enter second number: ")
    
    case "$choice" in
        1)
            add_numbers "$num1" "$num2"
            ;;
        2)
            subtract_numbers "$num1" "$num2"
            ;;
        3)
            multiply_numbers "$num1" "$num2"
            ;;
        4)
            divide_numbers "$num1" "$num2"
            ;;
    esac
}

# Main function
main() {
    print_colored "$BLUE" "Welcome to the Basic Calculator!"
    
    # Check if bc is available (for floating point arithmetic)
    if ! command -v bc >/dev/null 2>&1; then
        print_colored "$RED" "Error: 'bc' calculator is required but not installed"
        exit 1
    fi
    
    # Main loop
    while true; do
        show_menu
        read choice
        
        case "$choice" in
            1|2|3|4)
                calculate "$choice"
                ;;
            5)
                print_colored "$GREEN" "Thank you for using the calculator!"
                exit 0
                ;;
            *)
                print_colored "$RED" "Invalid choice. Please select 1-5."
                ;;
        esac
        
        # Ask if user wants to continue
        echo
        echo -n "Do you want to perform another calculation? (y/n): "
        read continue_choice
        if [[ "$continue_choice" != "y" && "$continue_choice" != "Y" ]]; then
            print_colored "$GREEN" "Goodbye!"
            exit 0
        fi
    done
}

# Run the main function
main
