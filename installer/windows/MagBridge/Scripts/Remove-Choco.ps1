# ====================================================================
# Remove-Choco.ps1 — uninstall Chocolatey and clean up environment
# NOTE: _Helpers.ps1 is sourced upstream by the runner (do NOT dot-source here).
# This script intentionally ignores Preferred/Minimum version parameters.
# ====================================================================

param(
    [string]$PackageKey = "Chocolatey",
    [string]$PreferredVersion = "",
    [string]$MinimumRequiredVersion = ""
)

$ErrorActionPreference = 'Stop'

try {
    Write-Host [INFO] Initiating ${PackageKey} removal process...

    # Resolve install root
    $chocoRoot = $env:ChocolateyInstall
    if (-not $chocoRoot -or [string]::IsNullOrWhiteSpace($chocoRoot)) {
        $chocoRoot = "C:\ProgramData\chocolatey"
    }
    Write-Host "[VER] ChocolateyInstall resolved to: $chocoRoot"

    # Quick detection (exists or not)
    $installed = Test-Path $chocoRoot
    $chocoCmd = Get-Command choco -ErrorAction SilentlyContinue

    if (-not $installed -and -not $chocoCmd) {
        Write-Host "[OK] ${PackageKey} not detected. Nothing to remove."
        exit 0
    }

    # Stop related services (best effort)
    try {
        $svc = Get-Service -Name chocolatey-agent -ErrorAction SilentlyContinue
        if ($svc -and $svc.Status -eq 'Running') {
            Write-Host "[VER] Attempting to stop background service: chocolatey-agent..."
            $svc.Stop()
            $svc.WaitForStatus('Stopped', '00:00:10') | Out-Null
            Write-Host "[OK] chocolatey-agent stopped."
        }
    }
    catch {
        Write-Host "[INFO] Skipped stopping chocolatey-agent (not running or inaccessible)."
    }

    # Backup PATH (User & Machine) preserving env refs
    try {
        $userKey = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment', $true)
        $machineKey = [Microsoft.Win32.Registry]::LocalMachine.OpenSubKey('SYSTEM\ControlSet001\Control\Session Manager\Environment\', $true)

        $userPath = $userKey.GetValue('PATH', [string]::Empty, 'DoNotExpandEnvironmentNames').ToString()
        $machinePath = $machineKey.GetValue('PATH', [string]::Empty, 'DoNotExpandEnvironmentNames').ToString()

        $backupFile = "C:\PATH_backups_ChocolateyUninstall.txt"
        @(
            "User PATH: $userPath"
            "Machine PATH: $machinePath"
        ) | Set-Content -Path $backupFile -Encoding UTF8 -Force

        Write-Host "[OK] Backed up PATH values to: $backupFile"

        $pathInfo = "[INFO] Adjusting PATH variables — backup saved to $backupFile."

        if ($userPath -like "*$chocoRoot*") {
            Write-Host "${pathInfo}"
            $newUserPATH = @(
                $userPath -split [System.IO.Path]::PathSeparator |
                Where-Object { $_ -and $_ -ne "$chocoRoot\bin" }
            ) -join [System.IO.Path]::PathSeparator
            $userKey.SetValue('PATH', $newUserPATH, 'ExpandString')
            Write-Host "[OK] Removed Chocolatey bin from User PATH."
        }

        if ($machinePath -like "*$chocoRoot*") {
            Write-Host "${pathInfo}"
            $newMachinePATH = @(
                $machinePath -split [System.IO.Path]::PathSeparator |
                Where-Object { $_ -and $_ -ne "$chocoRoot\bin" }
            ) -join [System.IO.Path]::PathSeparator
            $machineKey.SetValue('PATH', $newMachinePATH, 'ExpandString')
            Write-Host "[OK] Removed Chocolatey bin from Machine PATH."
        }

        $machineKey.Close()
        $userKey.Close()
    }
    catch {
        Write-Host "[WARN] Failed to adjust PATH — environment may require manual cleanup: $($_.Exception.Message)"
    }

    # Remove installation directory (packages, shims, logs)
    try {
        if (Test-Path $chocoRoot) {
            Write-Host "[INFO] Removing Chocolatey directory: $chocoRoot"

            try {
                Remove-Item -Path $chocoRoot -Recurse -Force -ErrorAction Stop
                Write-Host "[OK] Removed $chocoRoot"
            }
            catch {
                if ($_.Exception.Message -match 'denied|in use|being used') {
                    Write-Host "[INFO] Files in use — scheduling safe deletion after reboot."
                    Schedule-DeleteOnReboot -Path $chocoRoot
                    Write-Host "[OK] Locked files will be removed automatically after reboot."
                }
            }
        }
        else {
            Write-Host "[VER] Install directory not found: $chocoRoot"
        }
    }
    catch {
        Write-Host "[ERR] Fatal removal error: $($_.Exception.Message)"
        $global:RemovalFailed = $true
    }

    # Remove Chocolatey Tools Location directory if present
    try {
        if ($env:ChocolateyToolsLocation -and (Test-Path $env:ChocolateyToolsLocation)) {
            Write-Host "[VER] Removing optional Chocolatey tools directory: $env:ChocolateyToolsLocation"
            Remove-Item -Path $env:ChocolateyToolsLocation -Recurse -Force -ErrorAction Stop
            Write-Host "[OK] Removed tools directory."
        }
    }
    catch {
        Write-Host "[WARN] Could not remove tools directory — files may be in use: $($_.Exception.Message)"
    }

    # Clear Chocolatey environment variables (User & Machine)
    try {
        foreach ($scope in 'User', 'Machine') {
            [Environment]::SetEnvironmentVariable('ChocolateyInstall', [string]::Empty, $scope)
            [Environment]::SetEnvironmentVariable('ChocolateyLastPathUpdate', [string]::Empty, $scope)
            [Environment]::SetEnvironmentVariable('ChocolateyToolsLocation', [string]::Empty, $scope)
        }
        Write-Host "[OK] Cleared Chocolatey environment variables."
    }
    catch {
        Write-Host "[WARN] Skipped clearing some environment variables — details: $($_.Exception.Message)"
    }

    # Final verification
    if ($global:RemovalFailed) {
        Write-Host "[ERR] ${PackageKey} removal failed due to unexpected error(s)."
        exit 3
    }

    if (Test-Path $chocoRoot) {
        Write-Host "[INFO] ${PackageKey} directory still present — likely in use, safe to remove later: $chocoRoot"
        Write-Host "[INFO] This usually happens when files are in use. Reboot and remove manually if desired."
        exit 0  # ✅ Treat as soft success
    }

    Write-Host "[OK] ${PackageKey} fully removed."
    exit 0
}
catch {
    Write-Host "[ERR] Unexpected error during ${PackageKey} removal: $($_.Exception.Message)"
    exit 9
}
finally {
    $ErrorActionPreference = 'Continue'
}
