# File Management Automation Script
# Demonstrates PowerShell file manipulation capabilities for system administration

<#
.SYNOPSIS
    Comprehensive file management operations including cleanup, organization, and monitoring
.DESCRIPTION
    This script showcases various file manipulation techniques including:
    - Bulk file operations (copy, move, rename)
    - Directory organization and cleanup
    - File filtering and search operations
    - Log file analysis and archival
.PARAMETER TargetPath
    The root directory to perform operations on
.PARAMETER LogPath
    Path where operation logs will be stored
.EXAMPLE
    .\FileManagement.ps1 -TargetPath "C:\Data" -LogPath "C:\Logs"
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateScript({Test-Path $_ -PathType Container})]
    [string]$TargetPath,
    
    [Parameter(Mandatory=$false)]
    [string]$LogPath = "$env:TEMP\PowerShell_Logs"
)

# Ensure log directory exists
if (-not (Test-Path $LogPath)) {
    New-Item -Path $LogPath -ItemType Directory -Force | Out-Null
    Write-Host "Created log directory: $LogPath" -ForegroundColor Green
}

# Initialize log file with timestamp
$logFile = Join-Path $LogPath "FileOperations_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$startTime = Get-Date

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $logFile -Value $logEntry
    
    # Also display to console with color coding
    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        default { Write-Host $logEntry -ForegroundColor White }
    }
}

Write-Log "Starting file management operations on: $TargetPath"

# Example 1: Find and organize files by extension
function Invoke-FileOrganization {
    param([string]$BasePath)
    
    Write-Log "Starting file organization in: $BasePath"
    
    try {
        # Get all files recursively, excluding system directories
        $files = Get-ChildItem -Path $BasePath -File -Recurse | 
                 Where-Object { $_.DirectoryName -notmatch '(System|Windows|Program Files)' }
        
        # Group files by extension
        $fileGroups = $files | Group-Object Extension
        
        foreach ($group in $fileGroups) {
            $extension = if ($group.Name) { $group.Name.TrimStart('.') } else { "NoExtension" }
            $targetDir = Join-Path $BasePath "Organized\$extension"
            
            # Create target directory if it doesn't exist
            if (-not (Test-Path $targetDir)) {
                New-Item -Path $targetDir -ItemType Directory -Force | Out-Null
                Write-Log "Created directory: $targetDir" "SUCCESS"
            }
            
            # Move files to organized directories (simulation - copy instead of move for safety)
            foreach ($file in $group.Group) {
                $destinationPath = Join-Path $targetDir $file.Name
                
                # Handle duplicate names
                $counter = 1
                while (Test-Path $destinationPath) {
                    $nameWithoutExt = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
                    $ext = [System.IO.Path]::GetExtension($file.Name)
                    $destinationPath = Join-Path $targetDir "$nameWithoutExt`_$counter$ext"
                    $counter++
                }
                
                Copy-Item -Path $file.FullName -Destination $destinationPath -Force
                Write-Log "Organized: $($file.Name) -> $extension folder"
            }
        }
        
        Write-Log "File organization completed successfully" "SUCCESS"
    }
    catch {
        Write-Log "Error during file organization: $($_.Exception.Message)" "ERROR"
    }
}

# Example 2: Clean up old and temporary files
function Invoke-FileCleanup {
    param(
        [string]$BasePath,
        [int]$DaysOld = 30,
        [string[]]$TempExtensions = @(".tmp", ".temp", ".bak", ".old")
    )
    
    Write-Log "Starting cleanup of files older than $DaysOld days"
    
    try {
        $cutoffDate = (Get-Date).AddDays(-$DaysOld)
        $totalSize = 0
        $fileCount = 0
        
        # Find old temporary files
        $oldTempFiles = Get-ChildItem -Path $BasePath -Recurse -File | 
                       Where-Object { 
                           $_.LastWriteTime -lt $cutoffDate -and 
                           $TempExtensions -contains $_.Extension 
                       }
        
        foreach ($file in $oldTempFiles) {
            try {
                $size = $file.Length
                Remove-Item -Path $file.FullName -Force
                $totalSize += $size
                $fileCount++
                Write-Log "Removed old temp file: $($file.Name) ($(Format-FileSize $size))"
            }
            catch {
                Write-Log "Failed to remove: $($file.FullName) - $($_.Exception.Message)" "WARNING"
            }
        }
        
        # Find empty directories and remove them
        $emptyDirs = Get-ChildItem -Path $BasePath -Recurse -Directory | 
                    Where-Object { (Get-ChildItem $_.FullName -Force).Count -eq 0 }
        
        foreach ($dir in $emptyDirs) {
            try {
                Remove-Item -Path $dir.FullName -Force
                Write-Log "Removed empty directory: $($dir.Name)"
            }
            catch {
                Write-Log "Failed to remove directory: $($dir.FullName) - $($_.Exception.Message)" "WARNING"
            }
        }
        
        Write-Log "Cleanup completed: $fileCount files removed, $(Format-FileSize $totalSize) freed" "SUCCESS"
    }
    catch {
        Write-Log "Error during cleanup: $($_.Exception.Message)" "ERROR"
    }
}

# Example 3: Analyze disk usage and generate report
function Get-DiskUsageReport {
    param([string]$BasePath)
    
    Write-Log "Generating disk usage report for: $BasePath"
    
    try {
        # Analyze directory sizes
        $directories = Get-ChildItem -Path $BasePath -Directory
        $report = @()
        
        foreach ($dir in $directories) {
            $size = (Get-ChildItem -Path $dir.FullName -Recurse -File | 
                    Measure-Object -Property Length -Sum).Sum
            
            $fileCount = (Get-ChildItem -Path $dir.FullName -Recurse -File).Count
            
            $report += [PSCustomObject]@{
                Directory = $dir.Name
                SizeBytes = $size
                SizeFormatted = Format-FileSize $size
                FileCount = $fileCount
                LastModified = $dir.LastWriteTime
            }
        }
        
        # Sort by size and display top consumers
        $sortedReport = $report | Sort-Object SizeBytes -Descending
        
        Write-Log "=== DISK USAGE REPORT ===" "SUCCESS"
        $sortedReport | Select-Object Directory, SizeFormatted, FileCount, LastModified | 
                       Format-Table -AutoSize | Out-String | Write-Log
        
        # Export detailed report
        $reportPath = Join-Path $LogPath "DiskUsageReport_$(Get-Date -Format 'yyyyMMdd').csv"
        $sortedReport | Export-Csv -Path $reportPath -NoTypeInformation
        Write-Log "Detailed report exported to: $reportPath" "SUCCESS"
        
        return $sortedReport
    }
    catch {
        Write-Log "Error generating disk usage report: $($_.Exception.Message)" "ERROR"
    }
}

# Helper function to format file sizes
function Format-FileSize {
    param([long]$Size)
    
    if ($Size -eq 0) { return "0 B" }
    
    $units = @("B", "KB", "MB", "GB", "TB")
    $unitIndex = 0
    $sizeInUnits = $Size
    
    while ($sizeInUnits -ge 1024 -and $unitIndex -lt $units.Length - 1) {
        $sizeInUnits = $sizeInUnits / 1024
        $unitIndex++
    }
    
    return "{0:N2} {1}" -f $sizeInUnits, $units[$unitIndex]
}

# Example 4: Search and filter files with advanced criteria
function Find-FilesAdvanced {
    param(
        [string]$BasePath,
        [string]$Pattern = "*",
        [datetime]$ModifiedAfter,
        [long]$MinSize = 0,
        [long]$MaxSize = [long]::MaxValue,
        [string[]]$ExcludeExtensions = @()
    )
    
    Write-Log "Performing advanced file search with criteria:"
    Write-Log "  Pattern: $Pattern"
    Write-Log "  Modified after: $ModifiedAfter"
    Write-Log "  Size range: $(Format-FileSize $MinSize) - $(Format-FileSize $MaxSize)"
    
    try {
        $results = Get-ChildItem -Path $BasePath -Recurse -File -Filter $Pattern |
                   Where-Object {
                       $_.LastWriteTime -gt $ModifiedAfter -and
                       $_.Length -ge $MinSize -and
                       $_.Length -le $MaxSize -and
                       $ExcludeExtensions -notcontains $_.Extension
                   }
        
        Write-Log "Found $($results.Count) files matching criteria"
        
        # Display summary
        if ($results.Count -gt 0) {
            $totalSize = ($results | Measure-Object -Property Length -Sum).Sum
            Write-Log "Total size of matching files: $(Format-FileSize $totalSize)"
            
            # Show top 10 largest files
            $topFiles = $results | Sort-Object Length -Descending | Select-Object -First 10
            Write-Log "=== TOP 10 LARGEST MATCHING FILES ==="
            $topFiles | Select-Object Name, @{Name="Size";Expression={Format-FileSize $_.Length}}, LastWriteTime |
                       Format-Table -AutoSize | Out-String | Write-Log
        }
        
        return $results
    }
    catch {
        Write-Log "Error in advanced file search: $($_.Exception.Message)" "ERROR"
    }
}

# Main execution block
try {
    Write-Log "=== STARTING FILE MANAGEMENT OPERATIONS ==="
    
    # Execute file organization (commented out for safety)
    # Write-Log "Skipping file organization - uncomment to enable"
    # Invoke-FileOrganization -BasePath $TargetPath
    
    # Perform cleanup of old temporary files
    Invoke-FileCleanup -BasePath $TargetPath -DaysOld 30
    
    # Generate disk usage report
    $usageReport = Get-DiskUsageReport -BasePath $TargetPath
    
    # Perform advanced file search for large files modified in last 7 days
    $recentLargeFiles = Find-FilesAdvanced -BasePath $TargetPath -ModifiedAfter (Get-Date).AddDays(-7) -MinSize 10MB
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Log "=== OPERATIONS COMPLETED ===" "SUCCESS"
    Write-Log "Total execution time: $($duration.TotalSeconds) seconds" "SUCCESS"
    Write-Log "Log file location: $logFile" "SUCCESS"
}
catch {
    Write-Log "Critical error in main execution: $($_.Exception.Message)" "ERROR"
    exit 1
}
finally {
    Write-Log "File management script execution finished"
}
