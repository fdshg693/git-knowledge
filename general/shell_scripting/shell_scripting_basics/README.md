# Shell Scripting Basics for Beginners

## Overview

Shell scripting is the practice of writing sequences of commands that can be executed by a shell (command interpreter) to automate tasks, process data, and manage system operations. This guide covers the fundamental concepts every beginner needs to understand to start writing effective shell scripts.

## What is Shell Scripting?

A shell script is a text file containing a series of commands that would normally be typed at the command line. Instead of typing these commands one by one, you can save them in a file and execute them all at once. This automation capability makes shell scripting incredibly powerful for:

- **System Administration**: Automating backups, log management, user account creation
- **Data Processing**: File manipulation, text processing, batch operations
- **Development Workflows**: Build automation, testing, deployment
- **Personal Productivity**: Organizing files, batch renaming, repetitive tasks

## Core Concepts

### 1. The Shebang Line
Every shell script should begin with a "shebang" (`#!`) line that tells the system which interpreter to use:

```bash
#!/bin/bash
```

This line specifies that the script should be executed using the Bash shell.

### 2. Basic Script Structure
```bash
#!/bin/bash

# Comments start with # and are ignored by the shell
# They're essential for documenting your code

echo "Hello, World!"  # This prints text to the screen
```

### 3. Making Scripts Executable
Before you can run a script, you need to make it executable:
```bash
chmod +x script_name.sh
./script_name.sh
```

## Variables in Shell Scripting

Variables store data that can be used throughout your script. Understanding variables is crucial for writing dynamic and flexible scripts.

### Variable Declaration and Usage
```bash
#!/bin/bash

# Declaring variables (no spaces around =)
name="John"
age=25
current_date=$(date)

# Using variables (prefix with $)
echo "Hello, $name"
echo "You are $age years old"
echo "Today is $current_date"
```

### Types of Variables
1. **User-defined variables**: Created by the script author
2. **Environment variables**: System-wide variables (e.g., `$HOME`, `$PATH`)
3. **Special variables**: Built-in variables (e.g., `$1`, `$2` for script arguments)

### Variable Best Practices
- Use descriptive names: `user_count` instead of `uc`
- Use quotes to handle spaces: `file_name="my document.txt"`
- Use `${variable}` for clarity: `echo "${name}_backup"`

## Control Flow Structures

Control flow determines the order in which commands are executed in your script.

### Conditional Statements (if/else)
```bash
#!/bin/bash

age=18

if [ $age -ge 18 ]; then
    echo "You are an adult"
elif [ $age -ge 13 ]; then
    echo "You are a teenager"
else
    echo "You are a child"
fi
```

### Common Comparison Operators
- `-eq`: equal to
- `-ne`: not equal to
- `-gt`: greater than
- `-ge`: greater than or equal to
- `-lt`: less than
- `-le`: less than or equal to

### Loops
**For Loop**: Iterate over a list of items
```bash
#!/bin/bash

# Loop through a list
for fruit in apple banana orange; do
    echo "I like $fruit"
done

# Loop through files
for file in *.txt; do
    echo "Processing $file"
done
```

**While Loop**: Continue while a condition is true
```bash
#!/bin/bash

counter=1
while [ $counter -le 5 ]; do
    echo "Count: $counter"
    counter=$((counter + 1))
done
```

## Error Handling

Proper error handling makes your scripts robust and reliable.

### Exit Status
Every command returns an exit status:
- `0`: Success
- `1-255`: Various error conditions

### Basic Error Checking
```bash
#!/bin/bash

# Check if a command succeeded
if mkdir new_directory; then
    echo "Directory created successfully"
else
    echo "Failed to create directory"
    exit 1
fi
```

### Error Handling Best Practices
1. **Check critical operations**: Always verify important commands succeeded
2. **Provide meaningful error messages**: Help users understand what went wrong
3. **Exit gracefully**: Use appropriate exit codes
4. **Use `set -e`**: Stop script execution on any error

## Real-World Applications

### File Management
- Organizing downloads by file type
- Creating automated backups
- Batch renaming files

### System Monitoring
- Checking disk space
- Monitoring log files
- System health checks

### Development Support
- Building and deploying applications
- Running test suites
- Environment setup

## Getting Started Tips

1. **Start Simple**: Begin with basic scripts that echo text or list files
2. **Practice Regularly**: Write small scripts for daily tasks
3. **Read Others' Code**: Study well-written scripts to learn techniques
4. **Test Thoroughly**: Always test scripts in safe environments first
5. **Document Everything**: Use comments to explain complex logic

## Next Steps

Once you're comfortable with these basics, you can explore:
- Functions and modular programming
- Advanced text processing with `awk` and `sed`
- Network operations and API interactions
- Integration with other programming languages
- Advanced error handling and logging

Shell scripting is a powerful skill that grows more valuable with practice. Start with simple automation tasks and gradually build complexity as you become more comfortable with the concepts.
