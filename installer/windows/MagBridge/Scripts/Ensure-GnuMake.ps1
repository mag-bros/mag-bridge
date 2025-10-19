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
    Write-Host "[VER] Verifying $($this.PackageKey) installation..."
    Start-Sleep -Seconds 2

    # Get the installed version of GNU Make
    $finalVer = Get-ChocoVersion $this.PackageName -Silent

    if (-not $finalVer) {
        Write-Host "[ERR] Verification failed — $($this.PackageKey) not found via Chocolatey."
        exit 3
    }

    # Compare installed version with preferred version
    if ((Compare-Version $finalVer $this.PreferredVersion) -ge 0) {
        Write-Host "[OK] $($this.PackageKey) verified — version $finalVer (meets preferred $($this.PreferredVersion))."
        exit 0
    }

    # If the installed version meets the minimum required version
    if ($this.MinimumRequiredVersion -and (Compare-Version $finalVer $this.MinimumRequiredVersion) -ge 0) {
        Write-Host "[OK] $($this.PackageKey) meets minimum requirement ($finalVer ≥ $($this.MinimumRequiredVersion))."
        exit 0
    }

    Write-Host "[ERR] Installation completed but version $finalVer is below requirement ($($this.PreferredVersion))."
    exit 2
}

# Go Make!
Invoke-Ensure -Template $template
