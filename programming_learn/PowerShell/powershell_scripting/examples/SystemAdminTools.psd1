# Module Manifest for SystemAdminTools
# SystemAdminTools.psd1

@{
    # Module Metadata
    RootModule = 'SystemAdminTools.psm1'
    ModuleVersion = '1.0.0'
    GUID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    
    # Author and Company Information
    Author = 'System Administrator'
    CompanyName = 'Your Organization'
    Copyright = '(c) 2024 Your Organization. All rights reserved.'
    Description = 'PowerShell module for system administration and automation tasks'
    
    # PowerShell Version Requirements
    PowerShellVersion = '5.1'
    
    # Required Modules
    RequiredModules = @()
    
    # Required Assemblies
    RequiredAssemblies = @()
    
    # Functions to Export
    FunctionsToExport = @(
        'Get-SystemHealth',
        'Invoke-SystemMaintenance', 
        'Export-SystemReport'
    )
    
    # Cmdlets to Export
    CmdletsToExport = @()
    
    # Variables to Export
    VariablesToExport = @()
    
    # Aliases to Export
    AliasesToExport = @()
    
    # Private Data
    PrivateData = @{
        PSData = @{
            # Tags for PowerShell Gallery
            Tags = @('SystemAdmin', 'Automation', 'Monitoring', 'Windows')
            
            # License URI
            LicenseUri = ''
            
            # Project URI
            ProjectUri = ''
            
            # Icon URI
            IconUri = ''
            
            # Release Notes
            ReleaseNotes = @'
Version 1.0.0
- Initial release
- System health monitoring
- Automated maintenance tasks
- Report generation functionality
'@
        }
    }
    
    # Help Info URI
    HelpInfoURI = ''
    
    # Default Prefix
    DefaultCommandPrefix = ''
}
