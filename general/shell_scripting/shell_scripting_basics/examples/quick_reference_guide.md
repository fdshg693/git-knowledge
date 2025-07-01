# Shell Scripting Quick Reference

## Essential Commands & Syntax

### Script Structure
```bash
#!/bin/bash                    # Shebang line
# Comments start with #
echo "Hello World"             # Print to screen
```

### Variables
```bash
name="John"                    # String variable
age=25                         # Number variable
today=$(date)                  # Command substitution
echo "$name is $age years old" # Variable usage
echo "${name}_backup"          # Variable with suffix
```

### Special Variables
| Variable | Description |
|----------|-------------|
| `$0` | Script name |
| `$1`, `$2`, `$3` | First, second, third argument |
| `$#` | Number of arguments |
| `$@` | All arguments |
| `$?` | Exit status of last command |
| `$$` | Process ID of current script |

### Input/Output
```bash
read variable                  # Get user input
read -p "Enter name: " name   # Prompt with message
echo "text"                   # Print text
printf "Name: %s\n" "$name"   # Formatted output
```

## Conditional Statements

### Basic If Statement
```bash
if [ condition ]; then
    commands
elif [ condition ]; then
    commands
else
    commands
fi
```

### File Tests
| Test | Description |
|------|-------------|
| `[ -f file ]` | File exists and is regular file |
| `[ -d dir ]` | Directory exists |
| `[ -e path ]` | Path exists |
| `[ -r file ]` | File is readable |
| `[ -w file ]` | File is writable |
| `[ -x file ]` | File is executable |

### String Comparisons
| Test | Description |
|------|-------------|
| `[ "$a" = "$b" ]` | Strings are equal |
| `[ "$a" != "$b" ]` | Strings are not equal |
| `[ -z "$string" ]` | String is empty |
| `[ -n "$string" ]` | String is not empty |

### Numeric Comparisons
| Test | Description |
|------|-------------|
| `[ $a -eq $b ]` | Equal |
| `[ $a -ne $b ]` | Not equal |
| `[ $a -gt $b ]` | Greater than |
| `[ $a -ge $b ]` | Greater than or equal |
| `[ $a -lt $b ]` | Less than |
| `[ $a -le $b ]` | Less than or equal |

## Loops

### For Loop
```bash
# Loop through list
for item in apple banana cherry; do
    echo "$item"
done

# Loop through files
for file in *.txt; do
    echo "Processing $file"
done

# C-style for loop
for ((i=1; i<=10; i++)); do
    echo "Number: $i"
done
```

### While Loop
```bash
counter=1
while [ $counter -le 5 ]; do
    echo "Count: $counter"
    counter=$((counter + 1))
done
```

### Until Loop
```bash
counter=1
until [ $counter -gt 5 ]; do
    echo "Count: $counter"
    counter=$((counter + 1))
done
```

## Functions

### Basic Function
```bash
function greet() {
    echo "Hello, $1!"
}

# Or without 'function' keyword
greet() {
    echo "Hello, $1!"
}

# Call function
greet "John"
```

### Function with Return Value
```bash
add_numbers() {
    local result=$(($1 + $2))
    echo $result
}

sum=$(add_numbers 5 3)
echo "Sum: $sum"
```

## Arrays

### Basic Arrays
```bash
# Declare array
fruits=("apple" "banana" "cherry")

# Access elements
echo ${fruits[0]}              # First element
echo ${fruits[@]}              # All elements
echo ${#fruits[@]}             # Array length

# Add element
fruits+=("date")

# Loop through array
for fruit in "${fruits[@]}"; do
    echo "$fruit"
done
```

## Text Processing

### Common Commands
```bash
grep "pattern" file            # Search for pattern
sed 's/old/new/g' file        # Replace text
awk '{print $1}' file         # Print first column
sort file                     # Sort lines
uniq file                     # Remove duplicates
wc -l file                    # Count lines
cut -d',' -f1 file            # Cut first field (CSV)
```

### String Manipulation
```bash
string="Hello World"
echo ${string#Hello }          # Remove "Hello " from start
echo ${string%World}           # Remove "World" from end
echo ${string/World/Universe}  # Replace World with Universe
echo ${#string}                # String length
echo ${string:6:5}             # Substring (position 6, length 5)
```

## Error Handling

### Exit Codes
```bash
exit 0                         # Success
exit 1                         # General error
exit 2                         # Misuse of shell command
```

### Error Checking
```bash
# Check if command succeeded
if command; then
    echo "Success"
else
    echo "Failed"
    exit 1
fi

# Short form
command || { echo "Failed"; exit 1; }

# Set strict mode
set -e                         # Exit on any error
set -u                         # Exit on undefined variable
set -o pipefail               # Exit on pipe failure
```

## File Operations

### Basic Operations
```bash
touch file.txt                # Create empty file
mkdir directory               # Create directory
mkdir -p path/to/dir          # Create nested directories
cp source dest                # Copy file
mv source dest                # Move/rename file
rm file.txt                   # Delete file
rm -rf directory              # Delete directory recursively
```

### File Information
```bash
ls -la                        # List files with details
stat file.txt                 # File statistics
du -h file.txt                # File size
find . -name "*.txt"          # Find files
```

## Process Management

### Background Processes
```bash
command &                     # Run in background
jobs                          # List background jobs
fg %1                         # Bring job 1 to foreground
kill %1                       # Kill job 1
nohup command &               # Run command immune to hangups
```

## Useful Tips

### Script Debugging
```bash
bash -x script.sh             # Debug mode
set -x                        # Enable debugging in script
set +x                        # Disable debugging
```

### Script Execution
```bash
chmod +x script.sh            # Make executable
./script.sh                   # Run script
bash script.sh                # Run with bash
```

### Command Substitution
```bash
result=$(command)             # Modern syntax
result=`command`              # Legacy syntax (avoid)
```

### Redirection
```bash
command > file                # Redirect stdout to file
command >> file               # Append stdout to file
command 2> file               # Redirect stderr to file
command &> file               # Redirect both stdout and stderr
command < file                # Use file as stdin
```

## Common Patterns

### Check if file exists before processing
```bash
if [ -f "$filename" ]; then
    echo "Processing $filename"
    # process file
else
    echo "File $filename not found"
    exit 1
fi
```

### Process command line arguments
```bash
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done
```

### Create log files with timestamps
```bash
LOG_FILE="script.log"
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

log "Script started"
```

This reference covers the most commonly used shell scripting constructs. Keep it handy while writing your scripts!
