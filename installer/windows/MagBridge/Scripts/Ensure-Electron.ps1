# ====================================================================
# Ensure-Electron.ps1 — ensure Electron is installed and operational
# ====================================================================

param(
    [string]$PreferredVersion = "34.0.1",
    [string]$PackageKey = "Electron",
    [string]$MinimumRequiredVersion = ""
)

# Configure template
$taskConfig = [ScriptTemplate]::new(
    $PackageKey,                 # [string] $pkgKey
    "electron",                  # [string] $pkgName
    $PreferredVersion,           # [string] $prefVer
    $MinimumRequiredVersion,     # [string] $minVer
    "C:\ProgramData\chocolatey\lib\electron", # [string] $path
    "https://community.chocolatey.org/packages/electron", # [string] $src
    "choco"                      # [string] $cmd
)

# Bootstrap phase (none required for Chocolatey packages)
$taskConfig.BootstrapAction = {
    Write-Host "[VER] No manual bootstrap required for $($this.PackageKey) (handled by Chocolatey)."
}

# Verify phase — ensure executable or package presence
$taskConfig.VerifyAction = {
    Write-Host "[INFO] Verifying $($this.PackageKey) executable availability..."
    $exe = Get-Command electron -ErrorAction SilentlyContinue
    if ($exe) {
        Write-Host "[OK] Electron found at $($exe.Source)"
    }
    else {
        Write-Host "[ERR] Electron not found in PATH after installation."
        exit 3
    }
}

# Go Electron!
Invoke-Ensure -Config $taskConfig
