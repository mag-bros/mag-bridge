# ====================================================================
# Ensure-Choco.ps1 — ensure Chocolatey is installed and operational
# _Helpers.ps1 must be sourced upstream (Invoke-Choco, Compare-Version, Get-ChocoVersion)
# ====================================================================

param(
    [string]$PackageKey = "chocolatey",
    [string]$PreferredVersion = "2.5.1",
    [string]$MinimumRequiredVersion = ""
)

$template = [ScriptTemplate]::new(
    "Chocolatey",                # [string] $pkgKey
    "chocolatey",                # [string] $pkgName
    "2.5.1",                     # [string] $prefVer
    "0.0.0",                     # [string] $minVer
    "C:\ProgramData\chocolatey", # [string] $path
    "https://community.chocolatey.org/install.ps1", # [string] $src
    "bootstrap"                  # [string] $cmd
)

$template.BootstrapAction = {
    $this.Info("Chocolatey not found — starting official bootstrap...")

    # prevents previous chocolety files
    # $this.Ver("Checking for stale Chocolatey directory...")
    # if (Test-Path $this.InstallPath) {
    #     $exePath = Join-Path $this.InstallPath "bin\choco.exe"
    #     if (-not (Test-Path $exePath)) {
    #         $timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
    #         $backupPath = "${this.InstallPath}_backup_${timestamp}"

    #         $this.Warn("Stale Chocolatey folder detected at $($this.InstallPath).")
    #         $this.Info("Renaming existing folder to: $backupPath (no deletion).")

    #         try {
    #             Rename-Item -Path $this.InstallPath -NewName ("chocolatey_backup_${timestamp}") -ErrorAction Stop
    #             $this.Ok("Renamed safely — previous files preserved.")
    #         }
    #         catch {
    #             $this.Err("Could not rename folder: $($_.Exception.Message)")
    #             $this.Info("Installation will continue using existing folder.")
    #         }
    #     }
    #     else {
    #         $this.Ok("Existing Chocolatey installation found — skipping bootstrap.")
    #         exit 0
    #     }
    # }

    $installScript = Join-Path $env:TEMP "install_choco.ps1"
    try {
        Invoke-WebRequest -Uri $this.InstallSource -OutFile $installScript -UseBasicParsing
        $this.Ver("Downloaded installer to ${installScript}")
        Set-ExecutionPolicy Bypass -Scope Process -Force
        & powershell -NoProfile -ExecutionPolicy Bypass -File $installScript | ForEach-Object { $this.Ver($_) }
        $this.Ok("Chocolatey bootstrap completed successfully.")
    }
    catch {
        $this.Err("Bootstrap failed: $($_.Exception.Message)")
        exit 3
    }
    finally {
        Remove-Item $installScript -Force -ErrorAction SilentlyContinue
    }
}

$template.VerifyAction = {
    $this.Ver("Verifying $($this.PackageKey) installation...")
    Start-Sleep -Seconds 1

    $cmd = Get-Command choco -ErrorAction SilentlyContinue
    $finalVersion = Get-ChocoVersion $this.PackageName

    if ($finalVersion) {
        $this.Ok("Verified $($this.PackageKey) installation — version $finalVersion")
        if ($cmd) {
            $this.Ok("Chocolatey ready. Version $finalVersion")
        }
        else {
            $this.Info("PATH not yet refreshed — restart PowerShell to enable choco.exe command.")
            $this.Info("Executable location: C:\ProgramData\chocolatey\bin\choco.exe")
        }
        exit 0
    }
    else {
        $this.Err("Verification failed — executable missing. Try rerunning or rebooting.")
        exit 3
    }
}

# Go Choco!
$template.RunBootstrap()
$template.RunVerify()
