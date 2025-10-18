# ====================================================================
# Ensure-GnuMake.ps1 — ensure GNU Make is installed and operational
# ====================================================================
param(
    [string]$PreferredVersion = "4.4.1",
    [string]$PackageKey = "GNU Make",
    [string]$MinimumRequiredVersion = "4.3.0"
)

# Configure template
$taskConfig = [ScriptTemplate]::new(
    $PackageKey,
    "make",
    $PreferredVersion,
    $MinimumRequiredVersion,
    "C:\ProgramData\chocolatey\lib\make",
    "https://community.chocolatey.org/packages/make",
    "choco"
)

# Bootstrap — can be empty since it's a choco package
$taskConfig.BootstrapAction = {
    Write-Host "[VER] No manual bootstrap required for {PackageKey} (handled by Chocolatey)."
}

# Verify Action
$taskConfig.VerifyAction = {
    Write-Host "[INFO] Verifying {PackageKey} executable availability..."
    $makeCmd = Get-Command make -ErrorAction SilentlyContinue
    if ($makeCmd) {
        Write-Host "[OK] GNU Make found at {$makeCmd.Source}"
    }
    else {
        Write-Host "[ERR] GNU Make not found in PATH after installation."
        exit 3
    }
}

# Run the shared ensure routine
Invoke-Ensure -Config $taskConfig
