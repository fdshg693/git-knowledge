# PowerShell Modules and Advanced Functions

## Overview
PowerShell modules and advanced functions are the foundation of scalable, reusable code in PowerShell. This guide covers creating custom modules, advanced function techniques, and best practices for building professional PowerShell solutions for system administration and automation.

## Table of Contents
- [Module Fundamentals](#module-fundamentals)
- [Creating Custom Modules](#creating-custom-modules)
- [Advanced Function Techniques](#advanced-function-techniques)
- [Parameter Validation and Transformation](#parameter-validation-and-transformation)
- [Module Distribution and Publishing](#module-distribution-and-publishing)
- [Best Practices and Patterns](#best-practices-and-patterns)

## Module Fundamentals

### What are PowerShell Modules?
PowerShell modules are packages of related functions, cmdlets, variables, and other components that can be loaded and used together. They provide:
- **Code Organization**: Group related functionality
- **Namespace Management**: Avoid naming conflicts
- **Reusability**: Share code across multiple scripts
- **Version Control**: Manage different versions of functionality

### Module Types
```powershell
# Script Modules (.psm1) - Most common type
# Binary Modules (.dll) - Compiled .NET assemblies
# Manifest Modules (.psd1) - Metadata and dependency management
# Dynamic Modules - Created in memory at runtime
```

### Module Auto-Discovery
PowerShell automatically discovers modules in these locations:
```powershell
$env:PSModulePath -split ';'
# Common paths:
# - C:\Users\[User]\Documents\PowerShell\Modules
# - C:\Program Files\PowerShell\Modules
# - C:\Windows\System32\WindowsPowerShell\v1.0\Modules
```

## Creating Custom Modules

### Basic Script Module Structure
```powershell
# SystemAdminTools.psm1 - Main module file

#Region Helper Functions (Private)
function Write-ModuleLog {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [ValidateSet('Info', 'Warning', 'Error')]
        [string]$Level = 'Info'
    )
    
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logMessage = "[$timestamp] [$Level] $Message"
    
    switch ($Level) {
        'Info' { Write-Verbose $logMessage }
        'Warning' { Write-Warning $logMessage }
        'Error' { Write-Error $logMessage }
    }
}

function Test-AdminPrivileges {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}
#EndRegion

#Region Public Functions
function Get-SystemHealth {
    <#
    .SYNOPSIS
        Performs comprehensive system health checks
    .DESCRIPTION
        Analyzes various system metrics including CPU, memory, disk space,
        and critical services to provide an overall health assessment
    .PARAMETER ComputerName
        Name of the computer to check. Defaults to local computer
    .PARAMETER IncludePerformanceCounters
        Include detailed performance counter information
    .EXAMPLE
        Get-SystemHealth
        
        Performs health check on local computer
    .EXAMPLE
        Get-SystemHealth -ComputerName "Server01" -IncludePerformanceCounters
        
        Performs detailed health check on remote server
    .OUTPUTS
        PSCustomObject with health metrics and recommendations
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(ValueFromPipeline=$true, ValueFromPipelineByPropertyName=$true)]
        [Alias('CN', 'Server')]
        [string]$ComputerName = $env:COMPUTERNAME,
        
        [switch]$IncludePerformanceCounters
    )
    
    begin {
        Write-ModuleLog "Starting system health check" -Level Info
        $healthResults = @()
    }
    
    process {
        try {
            Write-ModuleLog "Checking health for computer: $ComputerName" -Level Info
            
            # CPU Information
            $cpu = Get-CimInstance -ClassName Win32_Processor -ComputerName $ComputerName
            $cpuUsage = (Get-Counter -Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 3).CounterSamples | 
                        Measure-Object -Property CookedValue -Average | Select-Object -ExpandProperty Average
            
            # Memory Information
            $memory = Get-CimInstance -ClassName Win32_OperatingSystem -ComputerName $ComputerName
            $memoryUsagePercent = [math]::Round(((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100), 2)
            
            # Disk Information
            $disks = Get-CimInstance -ClassName Win32_LogicalDisk -ComputerName $ComputerName | 
                     Where-Object { $_.DriveType -eq 3 -and $_.Size -gt 0 }
            
            $diskHealth = foreach ($disk in $disks) {
                $freeSpacePercent = [math]::Round((($disk.FreeSpace / $disk.Size) * 100), 2)
                [PSCustomObject]@{
                    Drive = $disk.DeviceID
                    SizeGB = [math]::Round($disk.Size / 1GB, 2)
                    FreeSpaceGB = [math]::Round($disk.FreeSpace / 1GB, 2)
                    FreeSpacePercent = $freeSpacePercent
                    Status = if ($freeSpacePercent -lt 10) { "Critical" } elseif ($freeSpacePercent -lt 20) { "Warning" } else { "Good" }
                }
            }
            
            # Service Health (Critical Windows Services)
            $criticalServices = @('Winmgmt', 'EventLog', 'PlugPlay', 'RpcSs', 'LanmanWorkstation')
            $serviceHealth = foreach ($serviceName in $criticalServices) {
                try {
                    $service = Get-Service -Name $serviceName -ComputerName $ComputerName -ErrorAction Stop
                    [PSCustomObject]@{
                        ServiceName = $service.Name
                        Status = $service.Status
                        StartType = $service.StartType
                        IsHealthy = $service.Status -eq 'Running'
                    }
                }
                catch {
                    [PSCustomObject]@{
                        ServiceName = $serviceName
                        Status = "Not Found"
                        StartType = "Unknown"
                        IsHealthy = $false
                    }
                }
            }
            
            # Overall Health Assessment
            $healthScore = 100
            if ($cpuUsage -gt 90) { $healthScore -= 20 }
            elseif ($cpuUsage -gt 70) { $healthScore -= 10 }
            
            if ($memoryUsagePercent -gt 90) { $healthScore -= 20 }
            elseif ($memoryUsagePercent -gt 80) { $healthScore -= 10 }
            
            $criticalDiskIssues = $diskHealth | Where-Object { $_.Status -eq "Critical" }
            $warningDiskIssues = $diskHealth | Where-Object { $_.Status -eq "Warning" }
            $healthScore -= ($criticalDiskIssues.Count * 15) + ($warningDiskIssues.Count * 5)
            
            $unhealthyServices = $serviceHealth | Where-Object { -not $_.IsHealthy }
            $healthScore -= ($unhealthyServices.Count * 10)
            
            $healthScore = [math]::Max(0, $healthScore)
            
            # Performance Counters (if requested)
            $performanceCounters = $null
            if ($IncludePerformanceCounters) {
                $performanceCounters = @{
                    DiskReadBytes = (Get-Counter -Counter "\PhysicalDisk(_Total)\Disk Read Bytes/sec").CounterSamples.CookedValue
                    DiskWriteBytes = (Get-Counter -Counter "\PhysicalDisk(_Total)\Disk Write Bytes/sec").CounterSamples.CookedValue
                    NetworkBytesTotal = (Get-Counter -Counter "\Network Interface(*)\Bytes Total/sec").CounterSamples.CookedValue | Measure-Object -Sum | Select-Object -ExpandProperty Sum
                }
            }
            
            $healthResult = [PSCustomObject]@{
                ComputerName = $ComputerName
                Timestamp = Get-Date
                HealthScore = $healthScore
                OverallStatus = if ($healthScore -ge 80) { "Good" } elseif ($healthScore -ge 60) { "Warning" } else { "Critical" }
                CPU = [PSCustomObject]@{
                    Name = $cpu.Name
                    Cores = $cpu.NumberOfCores
                    LogicalProcessors = $cpu.NumberOfLogicalProcessors
                    CurrentUsage = [math]::Round($cpuUsage, 2)
                }
                Memory = [PSCustomObject]@{
                    TotalGB = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
                    FreeGB = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
                    UsagePercent = $memoryUsagePercent
                }
                Disks = $diskHealth
                Services = $serviceHealth
                PerformanceCounters = $performanceCounters
                Recommendations = @()
            }
            
            # Generate recommendations
            if ($cpuUsage -gt 80) {
                $healthResult.Recommendations += "High CPU usage detected. Consider investigating running processes."
            }
            if ($memoryUsagePercent -gt 85) {
                $healthResult.Recommendations += "High memory usage detected. Consider adding more RAM or investigating memory leaks."
            }
            if ($criticalDiskIssues) {
                $healthResult.Recommendations += "Critical disk space issues found on drives: $($criticalDiskIssues.Drive -join ', ')"
            }
            if ($unhealthyServices) {
                $healthResult.Recommendations += "Critical services not running: $($unhealthyServices.ServiceName -join ', ')"
            }
            
            $healthResults += $healthResult
            Write-ModuleLog "Health check completed for $ComputerName with score: $healthScore" -Level Info
        }
        catch {
            Write-ModuleLog "Failed to check health for $ComputerName`: $($_.Exception.Message)" -Level Error
            throw
        }
    }
    
    end {
        return $healthResults
    }
}

function Invoke-SystemMaintenance {
    <#
    .SYNOPSIS
        Performs automated system maintenance tasks
    .DESCRIPTION
        Executes a series of maintenance tasks including temp file cleanup,
        log rotation, and system optimization
    .PARAMETER Tasks
        Specific maintenance tasks to perform
    .PARAMETER Force
        Skip confirmation prompts
    .EXAMPLE
        Invoke-SystemMaintenance -Tasks TempCleanup, LogRotation
        
        Performs temporary file cleanup and log rotation
    .NOTES
        Requires administrator privileges for most tasks
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [ValidateSet('TempCleanup', 'LogRotation', 'RegistryCleanup', 'ServiceOptimization', 'All')]
        [string[]]$Tasks = @('TempCleanup', 'LogRotation'),
        
        [switch]$Force
    )
    
    if (-not (Test-AdminPrivileges)) {
        throw "Administrator privileges required for system maintenance"
    }
    
    $results = @()
    
    if ($Tasks -contains 'All') {
        $Tasks = @('TempCleanup', 'LogRotation', 'RegistryCleanup', 'ServiceOptimization')
    }
    
    foreach ($task in $Tasks) {
        if ($Force -or $PSCmdlet.ShouldProcess($env:COMPUTERNAME, "Execute $task")) {
            $taskResult = switch ($task) {
                'TempCleanup' {
                    Write-ModuleLog "Starting temporary file cleanup" -Level Info
                    $tempPaths = @($env:TEMP, "$env:WINDIR\Temp", "$env:LOCALAPPDATA\Temp")
                    $totalCleaned = 0
                    
                    foreach ($path in $tempPaths) {
                        if (Test-Path $path) {
                            $files = Get-ChildItem -Path $path -Recurse -Force -ErrorAction SilentlyContinue
                            $sizeBeforeKB = ($files | Measure-Object -Property Length -Sum).Sum / 1KB
                            
                            $files | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
                            $totalCleaned += $sizeBeforeKB
                        }
                    }
                    
                    [PSCustomObject]@{
                        Task = 'TempCleanup'
                        Status = 'Completed'
                        Details = "Cleaned $([math]::Round($totalCleaned / 1MB, 2)) MB of temporary files"
                    }
                }
                
                'LogRotation' {
                    Write-ModuleLog "Starting log rotation" -Level Info
                    $logPaths = @("$env:WINDIR\Logs", "$env:ProgramData\Microsoft\Windows\PowerShell\PowerShellGet")
                    $rotatedCount = 0
                    
                    foreach ($logPath in $logPaths) {
                        if (Test-Path $logPath) {
                            $logFiles = Get-ChildItem -Path $logPath -Filter "*.log" -Recurse | 
                                       Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }
                            
                            foreach ($logFile in $logFiles) {
                                $archivePath = "$($logFile.FullName).archived"
                                Compress-Archive -Path $logFile.FullName -DestinationPath $archivePath -Force
                                Remove-Item -Path $logFile.FullName -Force
                                $rotatedCount++
                            }
                        }
                    }
                    
                    [PSCustomObject]@{
                        Task = 'LogRotation'
                        Status = 'Completed'
                        Details = "Rotated $rotatedCount log files"
                    }
                }
                
                default {
                    [PSCustomObject]@{
                        Task = $task
                        Status = 'Not Implemented'
                        Details = "Task implementation pending"
                    }
                }
            }
            
            $results += $taskResult
            Write-ModuleLog "Completed task: $task" -Level Info
        }
    }
    
    return $results
}

function Export-SystemReport {
    <#
    .SYNOPSIS
        Generates comprehensive system reports
    .DESCRIPTION
        Creates detailed reports combining system health, configuration,
        and performance data in various formats
    .PARAMETER OutputPath
        Directory where reports will be saved
    .PARAMETER Format
        Output format for the report
    .PARAMETER IncludeHistory
        Include historical performance data
    .EXAMPLE
        Export-SystemReport -OutputPath "C:\Reports" -Format HTML, JSON
        
        Generates HTML and JSON reports in the specified directory
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateScript({Test-Path $_ -PathType Container})]
        [string]$OutputPath,
        
        [ValidateSet('HTML', 'JSON', 'CSV', 'XML')]
        [string[]]$Format = @('HTML', 'JSON'),
        
        [switch]$IncludeHistory
    )
    
    $reportData = @{
        GeneratedAt = Get-Date
        ComputerName = $env:COMPUTERNAME
        SystemHealth = Get-SystemHealth -IncludePerformanceCounters
        SystemInfo = Get-ComputerInfo
        InstalledSoftware = Get-CimInstance -ClassName Win32_Product | Select-Object Name, Version, Vendor
        NetworkAdapters = Get-NetAdapter | Select-Object Name, InterfaceDescription, LinkSpeed, Status
    }
    
    if ($IncludeHistory) {
        # Add historical data collection logic here
        $reportData.HistoricalData = @{
            Note = "Historical data collection not yet implemented"
        }
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $baseFileName = "SystemReport_$($env:COMPUTERNAME)_$timestamp"
    
    $generatedFiles = @()
    
    foreach ($fmt in $Format) {
        $fileName = "$baseFileName.$($fmt.ToLower())"
        $filePath = Join-Path $OutputPath $fileName
        
        switch ($fmt) {
            'HTML' {
                $htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>System Report - $($env:COMPUTERNAME)</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .health-good { color: green; }
        .health-warning { color: orange; }
        .health-critical { color: red; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>System Report</h1>
        <p><strong>Computer:</strong> $($reportData.ComputerName)</p>
        <p><strong>Generated:</strong> $($reportData.GeneratedAt)</p>
        <p><strong>Health Score:</strong> <span class="health-$($reportData.SystemHealth.OverallStatus.ToLower())">$($reportData.SystemHealth.HealthScore)% ($($reportData.SystemHealth.OverallStatus))</span></p>
    </div>
    
    <div class="section">
        <h2>System Health Summary</h2>
        <table>
            <tr><th>Component</th><th>Status</th><th>Details</th></tr>
            <tr><td>CPU</td><td>$($reportData.SystemHealth.CPU.CurrentUsage)%</td><td>$($reportData.SystemHealth.CPU.Name)</td></tr>
            <tr><td>Memory</td><td>$($reportData.SystemHealth.Memory.UsagePercent)%</td><td>$($reportData.SystemHealth.Memory.TotalGB) GB Total</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
"@
                foreach ($recommendation in $reportData.SystemHealth.Recommendations) {
                    $htmlContent += "<li>$recommendation</li>"
                }
                
                $htmlContent += @"
        </ul>
    </div>
</body>
</html>
"@
                $htmlContent | Set-Content -Path $filePath -Encoding UTF8
            }
            
            'JSON' {
                $reportData | ConvertTo-Json -Depth 10 | Set-Content -Path $filePath -Encoding UTF8
            }
            
            'CSV' {
                # Create a flattened version for CSV
                $csvData = [PSCustomObject]@{
                    ComputerName = $reportData.ComputerName
                    GeneratedAt = $reportData.GeneratedAt
                    HealthScore = $reportData.SystemHealth.HealthScore
                    OverallStatus = $reportData.SystemHealth.OverallStatus
                    CPUUsage = $reportData.SystemHealth.CPU.CurrentUsage
                    MemoryUsage = $reportData.SystemHealth.Memory.UsagePercent
                    TotalMemoryGB = $reportData.SystemHealth.Memory.TotalGB
                }
                $csvData | Export-Csv -Path $filePath -NoTypeInformation
            }
            
            'XML' {
                $reportData | ConvertTo-Xml -NoTypeInformation | Select-Object -ExpandProperty OuterXml | Set-Content -Path $filePath -Encoding UTF8
            }
        }
        
        $generatedFiles += $filePath
        Write-ModuleLog "Generated $fmt report: $filePath" -Level Info
    }
    
    return $generatedFiles
}
#EndRegion

# Export only public functions
Export-ModuleMember -Function Get-SystemHealth, Invoke-SystemMaintenance, Export-SystemReport
