# ====================================================================
# Ensure-GnuMake.ps1 — ensure GNU Make is installed and operational
# ====================================================================
param(
    [string]$PreferredVersion = "4.4.1",
    [string]$PackageKey = "GNU Make",
    [string]$MinimumRequiredVersion = "4.3.0"
)

$template = [ScriptTemplate]::new(
    $PackageKey,                 # [string] $pkgKey
    "make",                      # [string] $pkgName
    $PreferredVersion,           # [string] $prefVer
    $MinimumRequiredVersion,     # [string] $minVer
    "C:\ProgramData\chocolatey\lib\make", # [string] $path
    "https://community.chocolatey.org/packages/make", # [string] $src
    "choco"                      # [string] $cmd
)

$template.BootstrapAction = {
    Write-Host "[VER] No manual bootstrap required for {PackageKey} (handled by Chocolatey)."
}

$template.VerifyAction = {
    Write-Host "[INFO] Verifying $($this.PackageKey) executable availability..."
    $makeCmd = Get-Command make -ErrorAction SilentlyContinue

    # Check if make command is found
    if ($makeCmd) {
        Write-Host "[OK] GNU Make found at $($makeCmd.Source)"
    }
    else {
        Write-Host "[INFO] GNU Make not found in PATH after installation."
        Write-Host "[INFO] It may be necessary to restart the terminal or system for changes to take effect."
        Write-Host "[ERR] GNU Make installation verification failed."
        exit 3
    }
}

# Go Make!
Invoke-Ensure -Template $template
