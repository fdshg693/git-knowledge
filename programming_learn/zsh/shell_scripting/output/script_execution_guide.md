# Zsh Script Execution Guide for Beginners

## Overview

Understanding how to properly execute Zsh scripts is fundamental to shell scripting. This guide covers different execution methods, permissions, and common execution scenarios that beginners often encounter.

## Making Scripts Executable

### Method 1: Using chmod (Recommended)

Before running a script directly, you need to make it executable:

```zsh
chmod +x script_name.zsh
```

**Permission Levels:**
- `chmod +x` - Makes executable for user, group, and others
- `chmod u+x` - Makes executable only for the user (owner)
- `chmod 755` - Read, write, execute for owner; read, execute for others

### Method 2: Checking Current Permissions

```zsh
ls -l script_name.zsh
```

Output explanation:
```
-rwxr-xr-x  1 user group  1234 Jul 1 10:30 script_name.zsh
```
- First character: file type (`-` = regular file)
- Next 3: owner permissions (`rwx` = read, write, execute)
- Next 3: group permissions (`r-x` = read, execute)
- Last 3: other permissions (`r-x` = read, execute)

## Script Execution Methods

### 1. Direct Execution (Shebang Required)

**Requirements:**
- Script must have execute permissions
- Script must start with shebang line: `#!/bin/zsh`

```zsh
# Make executable
chmod +x my_script.zsh

# Run the script
./my_script.zsh
```

### 2. Explicit Interpreter Call

**No execute permissions needed:**

```zsh
zsh my_script.zsh
```

**Advantages:**
- Works without setting execute permissions
- Useful for testing scripts
- Can specify interpreter options

### 3. Source/Dot Execution

**Runs script in current shell session:**

```zsh
source my_script.zsh
# or
. my_script.zsh
```

**Use cases:**
- Setting environment variables that persist
- Loading functions into current session
- Configuration scripts

## Shebang Lines Explained

### Standard Zsh Shebang

```zsh
#!/bin/zsh
```

### Portable Shebang (Recommended)

```zsh
#!/usr/bin/env zsh
```

**Benefits:**
- Works across different systems where zsh might be in different locations
- More portable and flexible

### With Options

```zsh
#!/usr/bin/env zsh -e
```

Common options:
- `-e` - Exit immediately if any command fails
- `-u` - Treat unset variables as errors
- `-x` - Print commands before executing (debugging)

## Running Scripts from Different Locations

### 1. Current Directory

```zsh
./script_name.zsh
```

### 2. Absolute Path

```zsh
/full/path/to/script_name.zsh
```

### 3. Adding to PATH

**For frequently used scripts:**

```zsh
# Add directory to PATH in ~/.zshrc
export PATH="$HOME/scripts:$PATH"

# Then run from anywhere
script_name.zsh
```

### 4. Creating Symbolic Links

```zsh
# Create a link in a PATH directory
ln -s /full/path/to/script_name.zsh /usr/local/bin/script_name

# Run from anywhere
script_name
```

## Common Execution Issues and Solutions

### Issue 1: Permission Denied

**Error:** `zsh: permission denied: ./script.zsh`

**Solution:**
```zsh
chmod +x script.zsh
```

### Issue 2: Command Not Found

**Error:** `zsh: command not found: script.zsh`

**Solutions:**
```zsh
# Use relative path
./script.zsh

# Or add to PATH
export PATH="$PWD:$PATH"
```

### Issue 3: Bad Interpreter

**Error:** `zsh: bad interpreter: No such file or directory`

**Causes & Solutions:**
```zsh
# Wrong shebang path
#!/bin/zsh  # Might not exist on all systems

# Use portable version
#!/usr/bin/env zsh

# Or check zsh location
which zsh
```

### Issue 4: Script Runs But Variables Don't Persist

**Problem:** Environment changes don't affect parent shell

**Solution:** Use `source` instead of direct execution
```zsh
source script.zsh
```

## Best Practices for Script Execution

### 1. Always Use Proper Shebang

```zsh
#!/usr/bin/env zsh
```

### 2. Set Appropriate Permissions

```zsh
# For personal scripts
chmod u+x script.zsh

# For shared scripts
chmod 755 script.zsh
```

### 3. Test Before Deployment

```zsh
# Test with explicit interpreter
zsh script.zsh

# Test with different options
zsh -n script.zsh  # Check syntax without executing
zsh -x script.zsh  # Debug mode
```

### 4. Use Meaningful Names

```zsh
# Good
backup_system.zsh
process_logs.zsh

# Avoid
script1.zsh
temp.zsh
```

### 5. Document Execution Requirements

**Include comments in your scripts:**

```zsh
#!/usr/bin/env zsh
#
# Script: backup_system.zsh
# Purpose: Backup home directory to external drive
# Usage: ./backup_system.zsh [destination]
# Requirements: rsync, external drive mounted
#
```

## Debugging Script Execution

### Enable Debugging Mode

```zsh
#!/usr/bin/env zsh -x
```

Or temporarily:
```zsh
zsh -x script.zsh
```

### Check Script Syntax

```zsh
zsh -n script.zsh
```

### Verbose Output

```zsh
zsh -v script.zsh
```

## Script Organization Tips

### 1. Use Consistent Directory Structure

```
~/scripts/
├── personal/
│   ├── backup.zsh
│   └── organize.zsh
├── work/
│   ├── deploy.zsh
│   └── monitor.zsh
└── utils/
    ├── common_functions.zsh
    └── config.zsh
```

### 2. Load Common Functions

```zsh
#!/usr/bin/env zsh

# Load common functions
source "$HOME/scripts/utils/common_functions.zsh"

# Your script code here
```

### 3. Make Scripts Self-Contained

**Include error checking:**

```zsh
#!/usr/bin/env zsh

# Check if required commands exist
if ! command -v rsync &> /dev/null; then
    echo "Error: rsync is required but not installed"
    exit 1
fi
```

## Summary

- Always use proper shebang lines (`#!/usr/bin/env zsh`)
- Set appropriate execute permissions with `chmod`
- Understand the difference between direct execution and sourcing
- Use absolute paths or add scripts to PATH for convenience
- Test scripts thoroughly before deployment
- Include proper documentation and error handling

Mastering script execution is essential for effective shell scripting and will save you time and frustration as you develop more complex automation tools.
