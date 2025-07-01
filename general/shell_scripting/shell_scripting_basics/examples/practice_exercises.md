# Shell Scripting Practice Exercises

## Exercise 1: Personal Greeting Script

**Objective**: Create a script that greets the user with their name and current time.

**Requirements**:
- Ask for the user's name
- Display a personalized greeting
- Show the current date and time

**Solution**:
```bash
#!/bin/bash

# Get user input
echo "What's your name?"
read name

# Get current time
current_time=$(date "+%H:%M")
current_date=$(date "+%Y-%m-%d")

# Display greeting
echo "Hello, $name! Welcome!"
echo "Today is $current_date and the time is $current_time"
```

**Key Learning Points**:
- Using `read` to get user input
- Command substitution with `$()`
- String formatting with `date`

---

## Exercise 2: File Counter

**Objective**: Count different types of files in a directory.

**Requirements**:
- Count .txt files
- Count .md files  
- Display totals

**Solution**:
```bash
#!/bin/bash

# Count different file types
txt_count=$(ls *.txt 2>/dev/null | wc -l)
md_count=$(ls *.md 2>/dev/null | wc -l)
total_files=$(ls -1 | wc -l)

echo "File Summary:"
echo "============="
echo "Text files (.txt): $txt_count"
echo "Markdown files (.md): $md_count"
echo "Total files: $total_files"
```

**Key Learning Points**:
- Error redirection with `2>/dev/null`
- Command chaining with pipes
- Arithmetic operations

---

## Exercise 3: Simple Backup Script

**Objective**: Create backups of important files with timestamp.

**Requirements**:
- Backup a specified directory
- Add timestamp to backup name
- Check if backup was successful

**Solution**:
```bash
#!/bin/bash

# Configuration
SOURCE_DIR="$1"
BACKUP_DIR="backups"
TIMESTAMP=$(date "+%Y%m%d_%H%M%S")

# Check if source directory was provided
if [ -z "$SOURCE_DIR" ]; then
    echo "Usage: $0 <source_directory>"
    exit 1
fi

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Directory '$SOURCE_DIR' does not exist"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup
BACKUP_NAME="${BACKUP_DIR}/backup_${TIMESTAMP}.tar.gz"
if tar -czf "$BACKUP_NAME" "$SOURCE_DIR"; then
    echo "Backup successful: $BACKUP_NAME"
    echo "Backup size: $(du -h "$BACKUP_NAME" | cut -f1)"
else
    echo "Backup failed!"
    exit 1
fi
```

**Key Learning Points**:
- Command line arguments (`$1`, `$2`, etc.)
- Directory existence checking
- Conditional execution with `&&` and `||`
- Exit codes for error handling

---

## Exercise 4: System Information Reporter

**Objective**: Create a script that displays useful system information.

**Requirements**:
- Show current user
- Display disk usage
- Show memory usage
- List running processes count

**Solution**:
```bash
#!/bin/bash

echo "==========================="
echo "  SYSTEM INFORMATION REPORT"
echo "==========================="
echo ""

# Current user and hostname
echo "User: $(whoami)"
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo ""

# Disk usage
echo "Disk Usage:"
echo "-----------"
df -h | head -2
echo ""

# Memory usage
echo "Memory Usage:"
echo "-------------"
free -h | head -2
echo ""

# Process count
process_count=$(ps aux | wc -l)
echo "Running Processes: $((process_count - 1))"
echo ""

# Current directory files
echo "Files in current directory: $(ls -1 | wc -l)"
```

**Key Learning Points**:
- System information commands
- Command substitution
- Arithmetic with `$(())`
- Text processing with `head` and `wc`

---

## Exercise 5: Interactive Menu System

**Objective**: Create a menu-driven script with multiple options.

**Requirements**:
- Display a menu with options
- Handle user selection
- Implement different actions
- Loop until user chooses to exit

**Solution**:
```bash
#!/bin/bash

while true; do
    echo ""
    echo "==== MAIN MENU ===="
    echo "1. Show current directory"
    echo "2. List files"
    echo "3. Show disk usage"
    echo "4. Show current date/time"
    echo "5. Exit"
    echo "==================="
    echo -n "Choose an option (1-5): "
    
    read choice
    
    case $choice in
        1)
            echo "Current directory: $(pwd)"
            ;;
        2)
            echo "Files in current directory:"
            ls -la
            ;;
        3)
            echo "Disk usage:"
            df -h
            ;;
        4)
            echo "Current date and time: $(date)"
            ;;
        5)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid option. Please choose 1-5."
            ;;
    esac
    
    echo -n "Press Enter to continue..."
    read
done
```

**Key Learning Points**:
- `while` loops for continuous execution
- `case` statements for multiple conditions
- User input validation
- Menu-driven interfaces

---

## Challenge Exercises

### Challenge 1: Log File Analyzer
Create a script that analyzes log files and reports:
- Total number of lines
- Number of error messages
- Most recent 10 entries
- File size

### Challenge 2: Directory Organizer
Write a script that organizes files in a directory by:
- Moving images to an "images" folder
- Moving documents to a "documents" folder
- Moving scripts to a "scripts" folder
- Creating folders if they don't exist

### Challenge 3: Simple Password Generator
Create a script that generates random passwords with:
- Configurable length
- Option to include/exclude special characters
- Multiple password generation
- Strength indicator

## Tips for Success

1. **Start Small**: Begin with the first exercise and gradually work up
2. **Experiment**: Modify the examples to see how they behave
3. **Error Testing**: Intentionally break scripts to understand error messages
4. **Documentation**: Add comments explaining your thought process
5. **Version Control**: Save different versions as you improve your scripts

Remember: The best way to learn shell scripting is by doing. Try these exercises, make mistakes, and learn from them!
