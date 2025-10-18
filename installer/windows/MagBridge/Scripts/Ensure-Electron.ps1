# ====================================================================
# Ensure-Electron.ps1 — ensure Electron is installed and operational
# ====================================================================

param(
    [string]$PreferredVersion = "34.0.1",
    [string]$PackageKey = "Electron",
    [string]$MinimumRequiredVersion = ""
)

$template = [ScriptTemplate]::new(
    $PackageKey,                 # [string] $pkgKey
    "electron",                  # [string] $pkgName
    $PreferredVersion,           # [string] $prefVer
    $MinimumRequiredVersion,     # [string] $minVer
    "C:\ProgramData\chocolatey\lib\electron", # [string] $path
    "https://community.chocolatey.org/packages/electron", # [string] $src
    "choco"                      # [string] $cmd
)

$template.BootstrapAction = {
    Write-Host "[VER] No manual bootstrap required for $($this.PackageKey) (handled by Chocolatey)."
}

$template.VerifyAction = {
    Write-Host "[VER] Verifying $($this.PackageKey) installation..."
    Start-Sleep -Seconds 2
    $finalVer = Get-ChocoVersion $this.PackageName -Silent

    if (-not $finalVer) {
        Write-Host "[ERR] Verification failed — $($this.PackageKey) not found via Chocolatey."
        exit 3
    }

    if ((Compare-Version $finalVer $this.PreferredVersion) -ge 0) {
        Write-Host "[OK] $($this.PackageKey) verified — version $finalVer (meets preferred $($this.PreferredVersion))."
        exit 0
    }

    if ($this.MinimumRequiredVersion -and (Compare-Version $finalVer $this.MinimumRequiredVersion) -ge 0) {
        Write-Host "[OK] $($this.PackageKey) meets minimum requirement ($finalVer ≥ $($this.MinimumRequiredVersion))."
        exit 0
    }

    Write-Host "[ERR] Installation completed but version $finalVer is below requirement ($($this.PreferredVersion))."
    exit 2
}

# Go Electron!
Invoke-Ensure -Template $template
