# PowerShell Scripting for Intermediate Developers

## Overview
PowerShell is a powerful command-line shell and scripting language designed for system administration and automation. It combines the flexibility of traditional shells with the power of .NET Framework, making it an essential tool for Windows, Linux, and macOS environments.

## Table of Contents
- [Core Concepts](#core-concepts)
- [Cmdlets and Pipeline](#cmdlets-and-pipeline)
- [Variables and Data Types](#variables-and-data-types)
- [Error Handling](#error-handling)
- [Real-World Applications](#real-world-applications)
- [Best Practices](#best-practices)

## Core Concepts

### What Makes PowerShell Unique
PowerShell operates on .NET objects rather than plain text, which sets it apart from traditional shells. This object-oriented approach provides:
- Rich data manipulation capabilities
- Type safety and validation
- Seamless integration with .NET libraries
- Consistent command structure across different operations

### PowerShell Philosophy
- **Verb-Noun Syntax**: Commands follow a consistent `Verb-Noun` pattern (e.g., `Get-Process`, `Set-Location`)
- **Object Pipeline**: Commands pass full objects, not just text
- **Discoverability**: Built-in help system and command discovery features

## Cmdlets and Pipeline

### Understanding Cmdlets
Cmdlets (pronounced "command-lets") are the building blocks of PowerShell. They follow the `Verb-Noun` naming convention:

```powershell
# Common verbs and their purposes
Get-*     # Retrieve information
Set-*     # Modify configuration
New-*     # Create new objects
Remove-*  # Delete objects
Start-*   # Begin processes
Stop-*    # End processes
```

### The PowerShell Pipeline
The pipeline (`|`) is PowerShell's most powerful feature, allowing you to chain commands together:

```powershell
# Basic pipeline example
Get-Process | Where-Object {$_.CPU -gt 10} | Sort-Object CPU -Descending

# More complex pipeline with multiple stages
Get-ChildItem -Path C:\Logs -Filter "*.log" | 
    Where-Object {$_.LastWriteTime -gt (Get-Date).AddDays(-7)} |
    Sort-Object LastWriteTime -Descending |
    Select-Object Name, Length, LastWriteTime
```

### Pipeline Object Flow
```powershell
# Understanding what flows through the pipeline
Get-Service | Get-Member  # Shows the object type and available properties
Get-Process | Select-Object Name, CPU, WorkingSet | Format-Table
```

## Variables and Data Types

### Variable Declaration and Assignment
```powershell
# Basic variable assignment
$name = "PowerShell"
$version = 7.4
$isActive = $true

# Arrays and collections
$colors = @("Red", "Green", "Blue")
$numbers = 1..10
$hashtable = @{
    Name = "Server01"
    OS = "Windows"
    Memory = 16
}
```

### Strongly Typed Variables
```powershell
# Type constraints
[string]$username = "admin"
[int]$port = 8080
[datetime]$startTime = Get-Date

# Array type constraints
[string[]]$serverNames = @("Web01", "Web02", "DB01")
```

### Automatic Variables
PowerShell provides several automatic variables:
```powershell
$_           # Current object in pipeline
$args        # Command-line arguments
$error       # Array of recent errors
$host        # Current host program info
$pid         # Process ID of current session
$pwd         # Current directory
```

## Error Handling

### Try-Catch-Finally Blocks
```powershell
try {
    # Risky operation
    $content = Get-Content -Path "C:\NonExistent.txt" -ErrorAction Stop
    Write-Host "File read successfully"
}
catch [System.IO.FileNotFoundException] {
    Write-Warning "File not found: $($_.Exception.Message)"
}
catch {
    Write-Error "Unexpected error: $($_.Exception.Message)"
}
finally {
    Write-Host "Cleanup operations completed"
}
```

### Error Action Preferences
```powershell
# Global error handling preference
$ErrorActionPreference = "Stop"  # Stop, Continue, SilentlyContinue, Inquire

# Per-command error handling
Get-Service -Name "NonExistentService" -ErrorAction SilentlyContinue
```

### Error Variables and Validation
```powershell
# Capture errors for later analysis
Get-Process -Name "InvalidProcess" -ErrorVariable ProcessError -ErrorAction SilentlyContinue

if ($ProcessError) {
    Write-Host "Error occurred: $($ProcessError.Exception.Message)"
}
```

## Real-World Applications

### System Administration Tasks
PowerShell excels at:
- **Service Management**: Starting, stopping, and monitoring Windows services
- **Registry Operations**: Reading and modifying system registry
- **User Account Management**: Creating and managing user accounts
- **Network Configuration**: Managing network adapters and connections
- **Scheduled Tasks**: Creating and managing automated tasks

### Automation Scenarios
Common automation use cases:
- **Log Analysis**: Parsing and analyzing system logs
- **File System Operations**: Bulk file operations and cleanup
- **System Monitoring**: Health checks and performance monitoring
- **Deployment Scripts**: Application and configuration deployment
- **Backup Operations**: Automated backup and restore procedures

## Best Practices

### Script Organization
```powershell
# Use comment-based help
<#
.SYNOPSIS
    Brief description of the script
.DESCRIPTION
    Detailed description of what the script does
.PARAMETER ParameterName
    Description of the parameter
.EXAMPLE
    Example of how to use the script
#>

# Use proper parameter validation
param(
    [Parameter(Mandatory=$true)]
    [string]$ComputerName,
    
    [ValidateRange(1, 65535)]
    [int]$Port = 80
)
```

### Performance Considerations
```powershell
# Use efficient filtering early in the pipeline
Get-ChildItem -Path C:\ -Recurse | Where-Object {$_.Extension -eq ".log"}
# Better:
Get-ChildItem -Path C:\ -Recurse -Filter "*.log"

# Use ForEach-Object for memory efficiency with large datasets
Get-Content -Path "largefile.txt" | ForEach-Object { 
    # Process one line at a time
}
```

### Security Best Practices
- **Execution Policy**: Understand and configure appropriate execution policies
- **Credential Management**: Use secure credential storage mechanisms
- **Input Validation**: Always validate user input and parameters
- **Least Privilege**: Run scripts with minimum required permissions
- **Logging**: Implement comprehensive logging for audit trails

### Code Quality
```powershell
# Use approved verbs
Get-Verb | Where-Object {$_.Verb -like "*file*"}

# Follow naming conventions
$camelCaseVariables = "Good"
$PascalCaseFunctions = "Good"

# Use explicit parameter names for clarity
Get-ChildItem -Path $targetPath -Recurse -Force
# Instead of:
Get-ChildItem $targetPath -r -fo
```

## Advanced Features Preview

### Modules and Functions
PowerShell supports modular programming through custom functions and modules, enabling code reuse and organization.

### Remote Management
PowerShell Remoting allows execution of commands on remote systems, crucial for enterprise environment management.

### Desired State Configuration (DSC)
DSC provides declarative configuration management capabilities for ensuring system compliance.

## Next Steps
To continue your PowerShell journey, explore the practical examples in the `examples/` directory, which demonstrate real-world file manipulation and system monitoring scenarios.
