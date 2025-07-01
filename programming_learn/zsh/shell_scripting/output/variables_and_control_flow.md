# Variables and Control Flow in Zsh

## Variables

Variables are fundamental building blocks in shell scripting. Zsh provides flexible ways to work with different types of data.

### Basic Variable Declaration and Usage

```zsh
# Variable assignment (no spaces around =)
name="John Doe"
age=25
pi=3.14159

# Using variables
echo "Hello, $name"
echo "You are $age years old"
echo "Pi is approximately ${pi}"
```

### Variable Types

#### Strings
```zsh
# Simple string
greeting="Hello World"

# String with spaces (quotes required)
message="This is a longer message"

# String concatenation
first_name="John"
last_name="Doe"
full_name="$first_name $last_name"
```

#### Numbers
```zsh
# Integers
count=10
total=100

# Arithmetic operations
result=$((count + total))
product=$((count * 5))
```

#### Arrays
```zsh
# Index arrays
fruits=("apple" "banana" "orange")
numbers=(1 2 3 4 5)

# Accessing array elements
echo ${fruits[1]}     # First element (1-indexed in Zsh)
echo ${fruits[@]}     # All elements
echo ${#fruits[@]}    # Array length
```

#### Associative Arrays
```zsh
# Declare associative array
typeset -A person
person[name]="Alice"
person[age]="30"
person[city]="New York"

# Access values
echo "Name: ${person[name]}"
echo "Age: ${person[age]}"

# Get all keys
echo "Keys: ${(k)person[@]}"
```

### Parameter Expansion

Zsh offers powerful parameter expansion features:

```zsh
filename="document.txt"

# String length
echo ${#filename}           # 12

# Substring extraction
echo ${filename:0:8}        # "document"

# Remove extension
echo ${filename%.*}         # "document"

# Get extension
echo ${filename##*.}        # "txt"

# Default values
echo ${username:-"guest"}   # Use "guest" if username is unset
```

## Control Flow Structures

### Conditional Statements

#### Basic if-then-else

```zsh
#!/usr/bin/env zsh

age=18

if [[ $age -ge 18 ]]; then
    echo "You are an adult"
elif [[ $age -ge 13 ]]; then
    echo "You are a teenager"
else
    echo "You are a child"
fi
```

#### Comparison Operators

```zsh
# Numeric comparisons
[[ $a -eq $b ]]    # Equal
[[ $a -ne $b ]]    # Not equal
[[ $a -lt $b ]]    # Less than
[[ $a -le $b ]]    # Less than or equal
[[ $a -gt $b ]]    # Greater than
[[ $a -ge $b ]]    # Greater than or equal

# String comparisons
[[ "$str1" = "$str2" ]]     # Equal
[[ "$str1" != "$str2" ]]    # Not equal
[[ "$str1" < "$str2" ]]     # Lexicographically less
[[ "$str1" > "$str2" ]]     # Lexicographically greater

# Pattern matching
[[ "$string" = pattern* ]]   # Starts with pattern
[[ "$string" = *pattern ]]   # Ends with pattern
[[ "$string" = *pattern* ]]  # Contains pattern
```

#### File Tests

```zsh
if [[ -f "file.txt" ]]; then
    echo "file.txt exists and is a regular file"
fi

if [[ -d "mydir" ]]; then
    echo "mydir exists and is a directory"
fi

if [[ -r "file.txt" ]]; then
    echo "file.txt is readable"
fi

if [[ -w "file.txt" ]]; then
    echo "file.txt is writable"
fi

if [[ -x "script.sh" ]]; then
    echo "script.sh is executable"
fi
```

### Loops

#### For Loops

```zsh
# Loop over a list
for fruit in apple banana orange; do
    echo "I like $fruit"
done

# Loop over array elements
fruits=("apple" "banana" "orange")
for fruit in "${fruits[@]}"; do
    echo "Processing: $fruit"
done

# C-style for loop
for ((i=1; i<=5; i++)); do
    echo "Number: $i"
done

# Loop over files
for file in *.txt; do
    echo "Processing file: $file"
done
```

#### While Loops

```zsh
# Basic while loop
counter=1
while [[ $counter -le 5 ]]; do
    echo "Count: $counter"
    ((counter++))
done

# Reading file line by line
while IFS= read -r line; do
    echo "Line: $line"
done < "input.txt"
```

#### Until Loops

```zsh
# Until loop (opposite of while)
counter=1
until [[ $counter -gt 5 ]]; do
    echo "Count: $counter"
    ((counter++))
done
```

### Case Statements

```zsh
#!/usr/bin/env zsh

echo "Enter a choice (1-3):"
read choice

case $choice in
    1)
        echo "You chose option 1"
        ;;
    2)
        echo "You chose option 2"
        ;;
    3)
        echo "You chose option 3"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
```

### Pattern Matching in Case

```zsh
filename="document.pdf"

case $filename in
    *.txt)
        echo "Text file"
        ;;
    *.pdf)
        echo "PDF document"
        ;;
    *.jpg|*.png|*.gif)
        echo "Image file"
        ;;
    *)
        echo "Unknown file type"
        ;;
esac
```

## Functions

Functions help organize code and avoid repetition:

```zsh
# Basic function
greet() {
    echo "Hello, $1!"
}

# Function with multiple parameters
calculate_area() {
    local width=$1
    local height=$2
    local area=$((width * height))
    echo "Area: $area"
}

# Using functions
greet "Alice"
calculate_area 5 10
```

## Best Practices

1. **Use meaningful variable names**: `user_count` instead of `uc`
2. **Quote variables**: Use `"$variable"` to prevent word splitting
3. **Use local variables in functions**: Prevent global scope pollution
4. **Check command success**: Use `if command; then` or `command || exit 1`
5. **Use arrays for lists**: Instead of space-separated strings
6. **Validate input**: Check if required parameters are provided
7. **Use consistent indentation**: Makes code more readable

## Common Patterns

### Menu System
```zsh
show_menu() {
    echo "1. List files"
    echo "2. Show date"
    echo "3. Exit"
    echo -n "Choose an option: "
}

while true; do
    show_menu
    read choice
    case $choice in
        1) ls -la ;;
        2) date ;;
        3) exit 0 ;;
        *) echo "Invalid option" ;;
    esac
done
```

### Processing Command Line Arguments
```zsh
#!/usr/bin/env zsh

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

filename="$1"
if [[ -f "$filename" ]]; then
    echo "Processing $filename..."
    # Process the file
else
    echo "Error: File '$filename' not found"
    exit 1
fi
```
