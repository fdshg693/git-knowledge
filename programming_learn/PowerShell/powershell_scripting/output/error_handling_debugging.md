# Advanced Error Handling and Debugging in PowerShell

## Overview
Robust error handling and effective debugging are crucial skills for intermediate PowerShell developers. This guide covers advanced error handling patterns, debugging techniques, and troubleshooting strategies for system administration and automation scripts.

## Table of Contents
- [Error Types and Categories](#error-types-and-categories)
- [Advanced Error Handling Patterns](#advanced-error-handling-patterns)
- [Debugging Techniques](#debugging-techniques)
- [Logging and Monitoring](#logging-and-monitoring)
- [Performance Troubleshooting](#performance-troubleshooting)
- [Best Practices](#best-practices)

## Error Types and Categories

### Understanding PowerShell Error Types

PowerShell distinguishes between two main error categories:

#### Terminating Errors
These errors stop script execution immediately:
```powershell
# Examples of terminating errors
throw "Critical failure occurred"
$null.DoSomething()  # NullReferenceException
Get-Content -Path "C:\NonExistent.txt" -ErrorAction Stop
```

#### Non-Terminating Errors
These errors are recorded but allow script continuation:
```powershell
# Examples of non-terminating errors
Get-Service -Name "InvalidService"  # Service not found
Get-ChildItem -Path "C:\Restricted" # Access denied
```

### Error Categories
PowerShell categorizes errors for better handling:
```powershell
# Common error categories
$Error[0].CategoryInfo.Category
# Categories include:
# - ObjectNotFound
# - PermissionDenied
# - InvalidOperation
# - ResourceUnavailable
# - NotSpecified
```

## Advanced Error Handling Patterns

### Hierarchical Try-Catch with Specific Exception Types
```powershell
function Invoke-SafeFileOperation {
    param(
        [string]$FilePath,
        [string]$Operation
    )
    
    try {
        switch ($Operation) {
            "Read" { 
                $content = Get-Content -Path $FilePath -ErrorAction Stop
                return $content
            }
            "Delete" { 
                Remove-Item -Path $FilePath -ErrorAction Stop
                Write-Verbose "File deleted successfully: $FilePath"
            }
            "Move" {
                $destination = "$FilePath.backup"
                Move-Item -Path $FilePath -Destination $destination -ErrorAction Stop
                Write-Verbose "File moved to: $destination"
            }
        }
    }
    catch [System.IO.FileNotFoundException] {
        Write-Warning "File not found: $FilePath"
        return $null
    }
    catch [System.IO.DirectoryNotFoundException] {
        Write-Warning "Directory not found for file: $FilePath"
        return $null
    }
    catch [System.UnauthorizedAccessException] {
        Write-Error "Access denied to file: $FilePath"
        throw
    }
    catch [System.IO.IOException] {
        Write-Error "IO error occurred with file: $FilePath - $($_.Exception.Message)"
        # Implement retry logic
        Start-Sleep -Seconds 1
        try {
            # Retry the operation once
            Invoke-SafeFileOperation -FilePath $FilePath -Operation $Operation
        }
        catch {
            Write-Error "Retry failed: $($_.Exception.Message)"
            throw
        }
    }
    catch {
        Write-Error "Unexpected error in file operation: $($_.Exception.Message)"
        Write-Debug "Stack trace: $($_.ScriptStackTrace)"
        throw
    }
}
```

### Custom Error Handling with Error Records
```powershell
function New-CustomError {
    param(
        [string]$Message,
        [string]$ErrorId,
        [System.Management.Automation.ErrorCategory]$Category,
        [object]$TargetObject
    )
    
    $errorRecord = New-Object System.Management.Automation.ErrorRecord(
        [System.Exception]::new($Message),
        $ErrorId,
        $Category,
        $TargetObject
    )
    
    return $errorRecord
}

function Test-ServiceHealth {
    param([string[]]$ServiceNames)
    
    $results = @()
    
    foreach ($serviceName in $ServiceNames) {
        try {
            $service = Get-Service -Name $serviceName -ErrorAction Stop
            
            if ($service.Status -ne 'Running') {
                $errorRecord = New-CustomError -Message "Service '$serviceName' is not running" `
                                               -ErrorId "ServiceNotRunning" `
                                               -Category "ResourceUnavailable" `
                                               -TargetObject $service
                $PSCmdlet.WriteError($errorRecord)
            }
            
            $results += [PSCustomObject]@{
                ServiceName = $serviceName
                Status = $service.Status
                StartType = $service.StartType
                IsHealthy = $service.Status -eq 'Running'
            }
        }
        catch {
            $errorRecord = New-CustomError -Message "Failed to check service '$serviceName': $($_.Exception.Message)" `
                                           -ErrorId "ServiceCheckFailed" `
                                           -Category "ObjectNotFound" `
                                           -TargetObject $serviceName
            $PSCmdlet.WriteError($errorRecord)
        }
    }
    
    return $results
}
```

### Error Aggregation and Reporting
```powershell
class ErrorCollector {
    [System.Collections.ArrayList]$Errors
    [System.Collections.ArrayList]$Warnings
    [int]$ErrorCount
    [int]$WarningCount
    
    ErrorCollector() {
        $this.Errors = @()
        $this.Warnings = @()
        $this.ErrorCount = 0
        $this.WarningCount = 0
    }
    
    [void]AddError([string]$Message, [string]$Source) {
        $errorInfo = [PSCustomObject]@{
            Timestamp = Get-Date
            Message = $Message
            Source = $Source
            Type = "Error"
        }
        $this.Errors.Add($errorInfo) | Out-Null
        $this.ErrorCount++
    }
    
    [void]AddWarning([string]$Message, [string]$Source) {
        $warningInfo = [PSCustomObject]@{
            Timestamp = Get-Date
            Message = $Message
            Source = $Source
            Type = "Warning"
        }
        $this.Warnings.Add($warningInfo) | Out-Null
        $this.WarningCount++
    }
    
    [PSCustomObject]GetSummary() {
        return [PSCustomObject]@{
            TotalErrors = $this.ErrorCount
            TotalWarnings = $this.WarningCount
            HasErrors = $this.ErrorCount -gt 0
            HasWarnings = $this.WarningCount -gt 0
            AllIssues = $this.Errors + $this.Warnings | Sort-Object Timestamp
        }
    }
}

function Invoke-BulkOperation {
    param(
        [string[]]$FilePaths,
        [string]$Operation
    )
    
    $errorCollector = [ErrorCollector]::new()
    $successCount = 0
    
    foreach ($filePath in $FilePaths) {
        try {
            switch ($Operation) {
                "Backup" {
                    $backupPath = "$filePath.bak"
                    Copy-Item -Path $filePath -Destination $backupPath -ErrorAction Stop
                    $successCount++
                }
                "Validate" {
                    if (-not (Test-Path $filePath)) {
                        throw "File does not exist"
                    }
                    $successCount++
                }
            }
        }
        catch {
            $errorCollector.AddError($_.Exception.Message, $filePath)
        }
    }
    
    $summary = $errorCollector.GetSummary()
    $summary | Add-Member -NotePropertyName "SuccessCount" -NotePropertyValue $successCount
    $summary | Add-Member -NotePropertyName "TotalFiles" -NotePropertyValue $FilePaths.Count
    
    return $summary
}
```

## Debugging Techniques

### Using PowerShell Debugger
```powershell
# Set breakpoints in scripts
Set-PSBreakpoint -Script "C:\Scripts\MyScript.ps1" -Line 25
Set-PSBreakpoint -Script "C:\Scripts\MyScript.ps1" -Variable "criticalVar"
Set-PSBreakpoint -Script "C:\Scripts\MyScript.ps1" -Command "Get-Service"

# Debug with conditional breakpoints
Set-PSBreakpoint -Script "C:\Scripts\MyScript.ps1" -Line 30 -Action { 
    if ($errorCount -gt 5) { 
        break 
    } 
}

# Remove breakpoints
Get-PSBreakpoint | Remove-PSBreakpoint
```

### Verbose and Debug Output
```powershell
function Invoke-DetailedProcess {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProcessName
    )
    
    Write-Verbose "Starting process analysis for: $ProcessName"
    Write-Debug "Debug mode enabled, detailed information will be shown"
    
    try {
        $processes = Get-Process -Name $ProcessName -ErrorAction Stop
        Write-Verbose "Found $($processes.Count) processes matching '$ProcessName'"
        
        foreach ($process in $processes) {
            Write-Debug "Processing PID: $($process.Id)"
            Write-Verbose "Process: $($process.Name), CPU: $($process.CPU), Memory: $($process.WorkingSet64)"
            
            # Detailed analysis
            $processInfo = [PSCustomObject]@{
                Name = $process.Name
                Id = $process.Id
                CPU = $process.CPU
                Memory = [math]::Round($process.WorkingSet64 / 1MB, 2)
                StartTime = $process.StartTime
                Handles = $process.Handles
            }
            
            Write-Output $processInfo
        }
    }
    catch {
        Write-Error "Failed to analyze process '$ProcessName': $($_.Exception.Message)"
        Write-Debug "Full exception: $($_.Exception | Format-List * | Out-String)"
    }
}

# Usage with verbose and debug output
# Invoke-DetailedProcess -ProcessName "notepad" -Verbose -Debug
```

### Trace and Audit Functions
```powershell
function Trace-FunctionExecution {
    param(
        [scriptblock]$ScriptBlock,
        [string]$FunctionName
    )
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $startTime = Get-Date
    
    Write-Host "[$startTime] Entering function: $FunctionName" -ForegroundColor Cyan
    
    try {
        $result = & $ScriptBlock
        $stopwatch.Stop()
        $endTime = Get-Date
        
        Write-Host "[$endTime] Exiting function: $FunctionName (Duration: $($stopwatch.ElapsedMilliseconds)ms)" -ForegroundColor Green
        return $result
    }
    catch {
        $stopwatch.Stop()
        $endTime = Get-Date
        
        Write-Host "[$endTime] Function failed: $FunctionName (Duration: $($stopwatch.ElapsedMilliseconds)ms)" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        throw
    }
}

# Usage example
$result = Trace-FunctionExecution -FunctionName "Get-SystemInfo" -ScriptBlock {
    Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory, CsProcessors
}
```

## Logging and Monitoring

### Structured Logging Implementation
```powershell
enum LogLevel {
    Debug = 0
    Info = 1
    Warning = 2
    Error = 3
    Critical = 4
}

class Logger {
    [string]$LogPath
    [LogLevel]$MinimumLevel
    [bool]$WriteToConsole
    
    Logger([string]$logPath, [LogLevel]$minimumLevel = [LogLevel]::Info, [bool]$writeToConsole = $true) {
        $this.LogPath = $logPath
        $this.MinimumLevel = $minimumLevel
        $this.WriteToConsole = $writeToConsole
        
        # Ensure log directory exists
        $logDir = Split-Path $logPath -Parent
        if (-not (Test-Path $logDir)) {
            New-Item -Path $logDir -ItemType Directory -Force | Out-Null
        }
    }
    
    [void]WriteLog([LogLevel]$level, [string]$message, [string]$source = "", [hashtable]$properties = @{}) {
        if ($level -lt $this.MinimumLevel) {
            return
        }
        
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
        $levelName = $level.ToString().ToUpper()
        
        # Create structured log entry
        $logEntry = [PSCustomObject]@{
            Timestamp = $timestamp
            Level = $levelName
            Source = $source
            Message = $message
            Properties = $properties
            ProcessId = $PID
            ThreadId = [System.Threading.Thread]::CurrentThread.ManagedThreadId
        }
        
        # Convert to JSON for structured logging
        $jsonEntry = $logEntry | ConvertTo-Json -Compress
        Add-Content -Path $this.LogPath -Value $jsonEntry
        
        # Console output with color coding
        if ($this.WriteToConsole) {
            $consoleMessage = "[$timestamp] [$levelName] $message"
            
            switch ($level) {
                ([LogLevel]::Error) { Write-Host $consoleMessage -ForegroundColor Red }
                ([LogLevel]::Warning) { Write-Host $consoleMessage -ForegroundColor Yellow }
                ([LogLevel]::Info) { Write-Host $consoleMessage -ForegroundColor White }
                ([LogLevel]::Debug) { Write-Host $consoleMessage -ForegroundColor Gray }
                ([LogLevel]::Critical) { Write-Host $consoleMessage -ForegroundColor Magenta }
            }
        }
    }
    
    [void]Debug([string]$message, [string]$source = "", [hashtable]$properties = @{}) {
        $this.WriteLog([LogLevel]::Debug, $message, $source, $properties)
    }
    
    [void]Info([string]$message, [string]$source = "", [hashtable]$properties = @{}) {
        $this.WriteLog([LogLevel]::Info, $message, $source, $properties)
    }
    
    [void]Warning([string]$message, [string]$source = "", [hashtable]$properties = @{}) {
        $this.WriteLog([LogLevel]::Warning, $message, $source, $properties)
    }
    
    [void]Error([string]$message, [string]$source = "", [hashtable]$properties = @{}) {
        $this.WriteLog([LogLevel]::Error, $message, $source, $properties)
    }
    
    [void]Critical([string]$message, [string]$source = "", [hashtable]$properties = @{}) {
        $this.WriteLog([LogLevel]::Critical, $message, $source, $properties)
    }
}

# Usage example
$logger = [Logger]::new("C:\Logs\PowerShell\application.log", [LogLevel]::Debug)

$logger.Info("Application started", "Main", @{Version="1.0"; Environment="Production"})
$logger.Warning("Configuration file not found, using defaults", "Config")
$logger.Error("Database connection failed", "Database", @{ConnectionString="Server=localhost"; Timeout=30})
```

## Performance Troubleshooting

### Measuring Script Performance
```powershell
function Measure-ScriptPerformance {
    param(
        [scriptblock]$ScriptBlock,
        [int]$Iterations = 1,
        [string]$Description = "Script execution"
    )
    
    $results = @()
    
    for ($i = 1; $i -le $Iterations; $i++) {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $memoryBefore = [System.GC]::GetTotalMemory($false)
        
        try {
            $result = & $ScriptBlock
            $stopwatch.Stop()
            $memoryAfter = [System.GC]::GetTotalMemory($false)
            
            $results += [PSCustomObject]@{
                Iteration = $i
                ExecutionTime = $stopwatch.ElapsedMilliseconds
                MemoryUsed = $memoryAfter - $memoryBefore
                Success = $true
                Result = $result
            }
        }
        catch {
            $stopwatch.Stop()
            $results += [PSCustomObject]@{
                Iteration = $i
                ExecutionTime = $stopwatch.ElapsedMilliseconds
                MemoryUsed = 0
                Success = $false
                Error = $_.Exception.Message
            }
        }
    }
    
    # Calculate statistics
    $successfulRuns = $results | Where-Object Success
    $statistics = [PSCustomObject]@{
        Description = $Description
        TotalIterations = $Iterations
        SuccessfulRuns = $successfulRuns.Count
        FailedRuns = $Iterations - $successfulRuns.Count
        AverageTime = if ($successfulRuns) { ($successfulRuns.ExecutionTime | Measure-Object -Average).Average } else { 0 }
        MinTime = if ($successfulRuns) { ($successfulRuns.ExecutionTime | Measure-Object -Minimum).Minimum } else { 0 }
        MaxTime = if ($successfulRuns) { ($successfulRuns.ExecutionTime | Measure-Object -Maximum).Maximum } else { 0 }
        TotalMemoryUsed = ($successfulRuns.MemoryUsed | Measure-Object -Sum).Sum
        Results = $results
    }
    
    return $statistics
}

# Example usage
$performance = Measure-ScriptPerformance -Iterations 5 -Description "File system scan" -ScriptBlock {
    Get-ChildItem -Path C:\Windows -Recurse -File | Where-Object Extension -eq ".exe" | Measure-Object
}

Write-Host "Performance Results:"
Write-Host "Average execution time: $($performance.AverageTime) ms"
Write-Host "Memory usage: $($performance.TotalMemoryUsed) bytes"
```

## Best Practices

### Error Handling Best Practices
1. **Always specify ErrorAction**: Be explicit about how errors should be handled
2. **Use specific exception types**: Catch specific exceptions rather than generic ones
3. **Implement retry logic**: For transient errors, implement intelligent retry mechanisms
4. **Log errors appropriately**: Include context and correlation information
5. **Clean up resources**: Use try-finally or using statements for resource management

### Debugging Best Practices
1. **Use meaningful variable names**: Makes debugging easier
2. **Implement comprehensive logging**: Log entry/exit points and key decisions
3. **Use Write-Verbose and Write-Debug**: Provide different levels of diagnostic information
4. **Test error paths**: Ensure error handling code is tested
5. **Document error scenarios**: Document known error conditions and their resolutions

### Code Quality for Error Handling
```powershell
# Good: Specific error handling with context
try {
    $config = Get-Content -Path $configPath -ErrorAction Stop | ConvertFrom-Json
}
catch [System.IO.FileNotFoundException] {
    Write-Warning "Configuration file not found at '$configPath', creating default configuration"
    $config = New-DefaultConfiguration
    $config | ConvertTo-Json | Set-Content -Path $configPath
}
catch [System.ArgumentException] {
    Write-Error "Invalid JSON in configuration file '$configPath'. Please check the file format."
    throw
}

# Bad: Generic error handling without context
try {
    $config = Get-Content $configPath | ConvertFrom-Json
}
catch {
    Write-Error "Something went wrong"
}
```

This comprehensive guide provides intermediate PowerShell developers with advanced error handling and debugging techniques essential for robust system administration and automation scripts.
