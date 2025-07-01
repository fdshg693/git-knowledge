# System Monitoring and Health Check Script
# Demonstrates PowerShell system monitoring capabilities

<#
.SYNOPSIS
    Comprehensive system monitoring script for performance and health checks
.DESCRIPTION
    This script demonstrates advanced PowerShell monitoring techniques including:
    - Performance counter monitoring
    - Service health checks
    - Resource utilization analysis
    - Event log monitoring
    - Network connectivity testing
    - Custom alert generation
.PARAMETER MonitorDuration
    Duration in minutes to run continuous monitoring
.PARAMETER AlertThresholds
    Hashtable of alert thresholds for various metrics
.EXAMPLE
    .\SystemMonitoring.ps1 -MonitorDuration 10
    .\SystemMonitoring.ps1 -AlertThresholds @{CPU=80; Memory=85; Disk=90}
#>

param(
    [Parameter(Mandatory=$false)]
    [int]$MonitorDuration = 5,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$AlertThresholds = @{
        CPU = 80
        Memory = 85
        Disk = 90
        ResponseTime = 5000
    },
    
    [Parameter(Mandatory=$false)]
    [string]$LogPath = "$env:TEMP\SystemMonitoring"
)

# Initialize monitoring environment
if (-not (Test-Path $LogPath)) {
    New-Item -Path $LogPath -ItemType Directory -Force | Out-Null
}

$monitoringLog = Join-Path $LogPath "SystemMonitoring_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$alertLog = Join-Path $LogPath "Alerts_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-MonitorLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $monitoringLog -Value $logEntry
    
    switch ($Level) {
        "ALERT" { 
            Write-Host $logEntry -ForegroundColor Red
            Add-Content -Path $alertLog -Value $logEntry
        }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        default { Write-Host $logEntry -ForegroundColor Cyan }
    }
}

# System Information Collection
function Get-SystemOverview {
    Write-MonitorLog "Collecting system overview information"
    
    try {
        $computerInfo = Get-ComputerInfo
        $osInfo = Get-CimInstance -ClassName Win32_OperatingSystem
        
        $systemInfo = [PSCustomObject]@{
            ComputerName = $env:COMPUTERNAME
            Domain = $env:USERDOMAIN
            OperatingSystem = $osInfo.Caption
            Version = $osInfo.Version
            Architecture = $osInfo.OSArchitecture
            TotalMemoryGB = [math]::Round($osInfo.TotalVisibleMemorySize / 1MB, 2)
            LastBootTime = $osInfo.LastBootUpTime
            Uptime = (Get-Date) - $osInfo.LastBootUpTime
            CurrentUser = $env:USERNAME
            PowerShellVersion = $PSVersionTable.PSVersion.ToString()
            Timestamp = Get-Date
        }
        
        Write-MonitorLog "System: $($systemInfo.ComputerName) | OS: $($systemInfo.OperatingSystem) | Uptime: $($systemInfo.Uptime.Days) days"
        return $systemInfo
    }
    catch {
        Write-MonitorLog "Error collecting system overview: $($_.Exception.Message)" "WARNING"
    }
}

# Performance Monitoring Functions
function Get-PerformanceMetrics {
    Write-MonitorLog "Collecting performance metrics"
    
    try {
        # CPU Usage
        $cpuCounter = Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 3
        $avgCpuUsage = ($cpuCounter.CounterSamples | Measure-Object -Property CookedValue -Average).Average
        
        # Memory Usage
        $osInfo = Get-CimInstance -ClassName Win32_OperatingSystem
        $totalMemory = $osInfo.TotalVisibleMemorySize * 1KB
        $availableMemory = $osInfo.FreePhysicalMemory * 1KB
        $usedMemory = $totalMemory - $availableMemory
        $memoryUsagePercent = [math]::Round(($usedMemory / $totalMemory) * 100, 2)
        
        # Disk Usage
        $diskInfo = Get-CimInstance -ClassName Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
        $diskUsage = foreach ($disk in $diskInfo) {
            $usedSpace = $disk.Size - $disk.FreeSpace
            $usagePercent = [math]::Round(($usedSpace / $disk.Size) * 100, 2)
            
            [PSCustomObject]@{
                Drive = $disk.DeviceID
                SizeGB = [math]::Round($disk.Size / 1GB, 2)
                FreeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
                UsedGB = [math]::Round($usedSpace / 1GB, 2)
                UsagePercent = $usagePercent
            }
        }
        
        # Network Adapters
        $networkAdapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }
        $networkStats = foreach ($adapter in $networkAdapters) {
            $stats = Get-Counter "\Network Interface($($adapter.InterfaceDescription))\Bytes Total/sec" -MaxSamples 1 -ErrorAction SilentlyContinue
            if ($stats) {
                [PSCustomObject]@{
                    Name = $adapter.Name
                    Description = $adapter.InterfaceDescription
                    LinkSpeed = $adapter.LinkSpeed
                    BytesPerSec = $stats.CounterSamples[0].CookedValue
                }
            }
        }
        
        $performanceData = [PSCustomObject]@{
            Timestamp = Get-Date
            CPUUsage = [math]::Round($avgCpuUsage, 2)
            MemoryUsagePercent = $memoryUsagePercent
            MemoryUsedGB = [math]::Round($usedMemory / 1GB, 2)
            MemoryAvailableGB = [math]::Round($availableMemory / 1GB, 2)
            DiskUsage = $diskUsage
            NetworkAdapters = $networkStats
        }
        
        # Check thresholds and generate alerts
        if ($performanceData.CPUUsage -gt $AlertThresholds.CPU) {
            Write-MonitorLog "ALERT: High CPU usage detected: $($performanceData.CPUUsage)%" "ALERT"
        }
        
        if ($performanceData.MemoryUsagePercent -gt $AlertThresholds.Memory) {
            Write-MonitorLog "ALERT: High memory usage detected: $($performanceData.MemoryUsagePercent)%" "ALERT"
        }
        
        foreach ($disk in $performanceData.DiskUsage) {
            if ($disk.UsagePercent -gt $AlertThresholds.Disk) {
                Write-MonitorLog "ALERT: High disk usage on $($disk.Drive): $($disk.UsagePercent)%" "ALERT"
            }
        }
        
        Write-MonitorLog "Performance metrics: CPU: $($performanceData.CPUUsage)% | Memory: $($performanceData.MemoryUsagePercent)%"
        return $performanceData
    }
    catch {
        Write-MonitorLog "Error collecting performance metrics: $($_.Exception.Message)" "WARNING"
    }
}

# Service Monitoring
function Get-ServiceHealth {
    param(
        [string[]]$CriticalServices = @("Spooler", "BITS", "Winmgmt", "EventLog", "PlugPlay")
    )
    
    Write-MonitorLog "Checking service health for critical services"
    
    try {
        $serviceStatus = foreach ($serviceName in $CriticalServices) {
            $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
            if ($service) {
                [PSCustomObject]@{
                    Name = $service.Name
                    DisplayName = $service.DisplayName
                    Status = $service.Status
                    StartType = $service.StartType
                    Timestamp = Get-Date
                }
                
                if ($service.Status -ne "Running" -and $service.StartType -eq "Automatic") {
                    Write-MonitorLog "ALERT: Critical service '$($service.DisplayName)' is not running" "ALERT"
                }
            }
            else {
                Write-MonitorLog "WARNING: Service '$serviceName' not found" "WARNING"
            }
        }
        
        $runningCount = ($serviceStatus | Where-Object { $_.Status -eq "Running" }).Count
        Write-MonitorLog "Service health check: $runningCount/$($CriticalServices.Count) critical services running"
        
        return $serviceStatus
    }
    catch {
        Write-MonitorLog "Error checking service health: $($_.Exception.Message)" "WARNING"
    }
}

# Event Log Monitoring
function Get-RecentEvents {
    param(
        [int]$Hours = 1,
        [string[]]$LogNames = @("System", "Application"),
        [int[]]$EventLevels = @(1, 2, 3)  # Critical, Error, Warning
    )
    
    Write-MonitorLog "Checking recent events from last $Hours hours"
    
    try {
        $startTime = (Get-Date).AddHours(-$Hours)
        $events = @()
        
        foreach ($logName in $LogNames) {
            $logEvents = Get-WinEvent -FilterHashtable @{
                LogName = $logName
                StartTime = $startTime
                Level = $EventLevels
            } -MaxEvents 50 -ErrorAction SilentlyContinue
            
            if ($logEvents) {
                $events += $logEvents | Select-Object TimeCreated, Id, LevelDisplayName, LogName, ProviderName, Message
            }
        }
        
        # Group events by level for summary
        $eventSummary = $events | Group-Object LevelDisplayName | ForEach-Object {
            [PSCustomObject]@{
                Level = $_.Name
                Count = $_.Count
                LatestEvent = ($_.Group | Sort-Object TimeCreated -Descending | Select-Object -First 1).TimeCreated
            }
        }
        
        if ($eventSummary) {
            Write-MonitorLog "Recent events summary:"
            foreach ($summary in $eventSummary) {
                Write-MonitorLog "  $($summary.Level): $($summary.Count) events (latest: $($summary.LatestEvent))"
                
                if ($summary.Level -in @("Critical", "Error") -and $summary.Count -gt 5) {
                    Write-MonitorLog "ALERT: High number of $($summary.Level) events detected: $($summary.Count)" "ALERT"
                }
            }
        }
        
        return $events
    }
    catch {
        Write-MonitorLog "Error checking recent events: $($_.Exception.Message)" "WARNING"
    }
}

# Network Connectivity Testing
function Test-NetworkConnectivity {
    param(
        [string[]]$TestHosts = @("8.8.8.8", "google.com", "microsoft.com"),
        [int]$TimeoutMs = 5000
    )
    
    Write-MonitorLog "Testing network connectivity"
    
    try {
        $connectivityResults = foreach ($host in $TestHosts) {
            $ping = Test-Connection -ComputerName $host -Count 1 -Quiet -TimeoutSeconds ($TimeoutMs / 1000)
            $responseTime = if ($ping) {
                (Test-Connection -ComputerName $host -Count 1).ResponseTime
            } else { $null }
            
            [PSCustomObject]@{
                Host = $host
                Reachable = $ping
                ResponseTimeMs = $responseTime
                Timestamp = Get-Date
            }
            
            if (-not $ping) {
                Write-MonitorLog "ALERT: Unable to reach $host" "ALERT"
            }
            elseif ($responseTime -gt $AlertThresholds.ResponseTime) {
                Write-MonitorLog "WARNING: High response time to $host`: $responseTime ms" "WARNING"
            }
        }
        
        $successfulTests = ($connectivityResults | Where-Object { $_.Reachable }).Count
        Write-MonitorLog "Network connectivity: $successfulTests/$($TestHosts.Count) hosts reachable"
        
        return $connectivityResults
    }
    catch {
        Write-MonitorLog "Error testing network connectivity: $($_.Exception.Message)" "WARNING"
    }
}

# Process Monitoring
function Get-ProcessAnalysis {
    param([int]$TopProcessCount = 10)
    
    Write-MonitorLog "Analyzing top processes by resource usage"
    
    try {
        $processes = Get-Process | Where-Object { $_.ProcessName -ne "Idle" } | 
                    Sort-Object CPU -Descending | Select-Object -First $TopProcessCount
        
        $processAnalysis = foreach ($process in $processes) {
            [PSCustomObject]@{
                Name = $process.ProcessName
                ID = $process.Id
                CPUTime = $process.TotalProcessorTime.TotalSeconds
                WorkingSetMB = [math]::Round($process.WorkingSet / 1MB, 2)
                HandleCount = $process.HandleCount
                ThreadCount = $process.Threads.Count
                StartTime = if ($process.StartTime) { $process.StartTime } else { "N/A" }
            }
        }
        
        Write-MonitorLog "Top CPU consumers:"
        foreach ($proc in $processAnalysis | Select-Object -First 5) {
            Write-MonitorLog "  $($proc.Name) (PID: $($proc.ID)): CPU: $($proc.CPUTime)s, Memory: $($proc.WorkingSetMB)MB"
        }
        
        return $processAnalysis
    }
    catch {
        Write-MonitorLog "Error analyzing processes: $($_.Exception.Message)" "WARNING"
    }
}

# Main Monitoring Loop
function Start-SystemMonitoring {
    param([int]$DurationMinutes)
    
    Write-MonitorLog "=== STARTING SYSTEM MONITORING ===" "SUCCESS"
    Write-MonitorLog "Duration: $DurationMinutes minutes | Alert Thresholds: CPU:$($AlertThresholds.CPU)% Memory:$($AlertThresholds.Memory)% Disk:$($AlertThresholds.Disk)%"
    
    $startTime = Get-Date
    $endTime = $startTime.AddMinutes($DurationMinutes)
    $monitoringData = @()
    
    # Initial system overview
    $systemOverview = Get-SystemOverview
    
    while ((Get-Date) -lt $endTime) {
        try {
            Write-MonitorLog "--- Monitoring Cycle: $(Get-Date -Format 'HH:mm:ss') ---"
            
            # Collect all monitoring data
            $currentData = [PSCustomObject]@{
                Timestamp = Get-Date
                Performance = Get-PerformanceMetrics
                Services = Get-ServiceHealth
                Events = Get-RecentEvents -Hours 1
                Network = Test-NetworkConnectivity
                Processes = Get-ProcessAnalysis
            }
            
            $monitoringData += $currentData
            
            # Wait before next cycle (30 seconds)
            Start-Sleep -Seconds 30
        }
        catch {
            Write-MonitorLog "Error in monitoring cycle: $($_.Exception.Message)" "WARNING"
            Start-Sleep -Seconds 10
        }
    }
    
    # Generate final report
    Write-MonitorLog "=== MONITORING COMPLETED ===" "SUCCESS"
    $totalDuration = (Get-Date) - $startTime
    Write-MonitorLog "Total monitoring time: $($totalDuration.TotalMinutes) minutes"
    
    # Export monitoring data
    $reportPath = Join-Path $LogPath "MonitoringReport_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $finalReport = @{
        SystemOverview = $systemOverview
        MonitoringData = $monitoringData
        Summary = @{
            StartTime = $startTime
            EndTime = Get-Date
            Duration = $totalDuration
            AlertThresholds = $AlertThresholds
            DataPoints = $monitoringData.Count
        }
    }
    
    $finalReport | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportPath -Encoding UTF8
    Write-MonitorLog "Detailed report exported to: $reportPath" "SUCCESS"
    Write-MonitorLog "Alert log location: $alertLog" "SUCCESS"
    
    return $finalReport
}

# Execute monitoring
try {
    $monitoringResults = Start-SystemMonitoring -DurationMinutes $MonitorDuration
    Write-MonitorLog "System monitoring completed successfully" "SUCCESS"
}
catch {
    Write-MonitorLog "Critical error in system monitoring: $($_.Exception.Message)" "ALERT"
    exit 1
}
finally {
    Write-MonitorLog "Monitoring session ended"
}
