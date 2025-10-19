# ====================================================================
# Remove-Choco.ps1 — uninstall Chocolatey and clean up environment
# Compatible with Windows 7 / PowerShell 5.1
# ====================================================================

param(
    [string]$PackageKey = "Chocolatey",
    [string]$PreferredVersion = "",
    [string]$MinimumRequiredVersion = ""
)

$ErrorActionPreference = 'Stop'

try {
    Write-Host "[INFO] Initiating ${PackageKey} removal process..."

    # ------------------------------------------------------------
    # Locate Chocolatey installation root
    # ------------------------------------------------------------
    $chocoRoot = $env:ChocolateyInstall
    if (-not $chocoRoot -or [string]::IsNullOrWhiteSpace($chocoRoot)) {
        $chocoRoot = "C:\ProgramData\chocolatey"
    }
    Write-Host "[VER] ChocolateyInstall resolved to: ${chocoRoot}"

    # ------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------
    $installed = Test-Path "${chocoRoot}"
    $chocoCmd = Get-Command choco -ErrorAction SilentlyContinue

    if (-not $installed -and -not $chocoCmd) {
        Write-Host "[OK] ${PackageKey} not detected. Nothing to remove."
        exit 0
    }

    # ------------------------------------------------------------
    # Stop background agent if running
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # Backup and sanitize PATH
    # ------------------------------------------------------------
    try {
        $userKey = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment', $true)
        $machineKey = [Microsoft.Win32.Registry]::LocalMachine.OpenSubKey(
            'SYSTEM\ControlSet001\Control\Session Manager\Environment\', $true)

        $userPath = $userKey.GetValue('PATH', [string]::Empty, 'DoNotExpandEnvironmentNames').ToString()
        $machinePath = $machineKey.GetValue('PATH', [string]::Empty, 'DoNotExpandEnvironmentNames').ToString()

        $timestamp = (Get-Date).ToString('yyyyMMdd_HHmmss')
        $backupDir = Join-Path -Path $env:ProgramData -ChildPath "MagBridge\Backups"
        if (-not (Test-Path $backupDir)) { New-Item -Path $backupDir -ItemType Directory -Force | Out-Null }
        $backupFile = Join-Path -Path $backupDir -ChildPath "PATH_backup_ChocolateyUninstall_${timestamp}.txt"
        
        @(
            "User PATH: ${userPath}"
            "Machine PATH: ${machinePath}"
        ) | Set-Content -Path "${backupFile}" -Encoding UTF8 -Force

        $sizeKB = [math]::Round((Get-Item "${backupFile}").Length / 1KB, 2)
        Write-Host "[OK] Backed up PATH values to: ${backupFile}"
        Write-Host "[VER] PATH backup size: ${sizeKB} KB"

        if ($userPath -like "*${chocoRoot}*") {
            Write-Host "${pathInfo}"
            $newUserPATH = @(
                $userPath -split [IO.Path]::PathSeparator |
                Where-Object { $_ -and $_ -ne "${chocoRoot}\bin" }
            ) -join [IO.Path]::PathSeparator
            $userKey.SetValue('PATH', $newUserPATH, 'ExpandString')
            Write-Host "[OK] Removed Chocolatey bin from User PATH."
        }

        if ($machinePath -like "*${chocoRoot}*") {
            Write-Host "${pathInfo}"
            $newMachinePATH = @(
                $machinePath -split [IO.Path]::PathSeparator |
                Where-Object { $_ -and $_ -ne "${chocoRoot}\bin" }
            ) -join [IO.Path]::PathSeparator
            $machineKey.SetValue('PATH', $newMachinePATH, 'ExpandString')
            Write-Host "[OK] Removed Chocolatey bin from Machine PATH."
        }

        $machineKey.Close()
        $userKey.Close()
    }
    catch {
        Write-Host "[WARN] Failed to adjust PATH — environment may require manual cleanup: $($_.Exception.Message)"
    }

    # ------------------------------------------------------------
    # Remove installation directory (safeguarded)
    # ------------------------------------------------------------
    try {
        if (Test-Path "${chocoRoot}") {
            $canonical = [IO.Path]::GetFullPath("${chocoRoot}")
            if ($canonical -notlike "*\ProgramData\chocolatey*") {
                Write-Host "[ERR] Refusing to remove non-standard Chocolatey path: ${canonical}"
                $global:RemovalFailed = $true
            }
            else {
                Write-Host "[INFO] Removing Chocolatey directory: ${canonical}"
                try {
                    Remove-Item -Path "${canonical}" -Recurse -Force -ErrorAction Stop
                    Write-Host "[OK] Removed ${canonical}"
                }
                catch {
                    if ($_.Exception.Message -match 'denied|in use|being used') {
                        Write-Host "[INFO] Files in use — scheduling safe deletion after reboot."
                        Schedule-DeleteOnReboot -Path "${canonical}"
                        Write-Host "[OK] Locked files will be removed automatically after reboot."
                    }
                }
            }
        }
        else {
            Write-Host "[VER] Install directory not found: ${chocoRoot}"
        }
    }
    catch {
        Write-Host "[ERR] Fatal removal error: $($_.Exception.Message)"
        $global:RemovalFailed = $true
    }

    # ------------------------------------------------------------
    # Remove optional Chocolatey tools directory
    # ------------------------------------------------------------
    try {
        if ($env:ChocolateyToolsLocation -and (Test-Path "${env:ChocolateyToolsLocation}")) {
            Write-Host "[VER] Removing optional Chocolatey tools directory: ${env:ChocolateyToolsLocation}"
            Remove-Item -Path "${env:ChocolateyToolsLocation}" -Recurse -Force -ErrorAction Stop
            Write-Host "[OK] Removed tools directory."
        }
    }
    catch {
        Write-Host "[WARN] Could not remove tools directory — files may be in use: $($_.Exception.Message)"
    }

    # ------------------------------------------------------------
    # Clear Chocolatey environment variables (with verbose per-var logging)
    # ------------------------------------------------------------
    try {
        Write-Host "[INFO] Clearing Chocolatey environment variables..."

        $varsToClear = @(
            'ChocolateyInstall',
            'ChocolateyToolsLocation',
            'ChocolateyProfile',
            'ChocolateyLastPathUpdate',
            'ChocolateyPackageName',
            'ChocolateyEnvironmentPath',
            'ChocolateyInstallOverride',
            'ChocolateyExecutionPath'
        )

        foreach ($scope in 'User', 'Machine') {
            foreach ($v in $varsToClear) {
                $prev = [Environment]::GetEnvironmentVariable("${v}", $scope)
                if ($null -ne $prev -and -not [string]::IsNullOrWhiteSpace("${prev}")) {
                    Write-Host "[VER] Clearing ${v} (scope=${scope}) — previous value length=${($prev).Length}"
                }
                else {
                    Write-Host "[VER] ${v} not set (scope=${scope})"
                }

                try { [Environment]::SetEnvironmentVariable("${v}", $null, $scope) }
                catch { Write-Host "[WARN] Failed to clear ${v} (scope=${scope}): $($_.Exception.Message)" }
            }
        }

        foreach ($v in $varsToClear) {
            if (Test-Path "Env:\${v}") {
                Write-Host "[VER] Removing Env:${v} from current session"
                Remove-Item "Env:\${v}" -ErrorAction SilentlyContinue
            }
            else {
                Write-Host "[VER] Env:${v} not present in current session"
            }
        }

        Write-Host "[OK] Cleared Chocolatey environment variables (no profile edits required)."
    }
    catch {
        Write-Host "[WARN] Skipped clearing some environment variables — details: $($_.Exception.Message)"
    }

    # ------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------
    if ($global:RemovalFailed) {
        Write-Host "[ERR] ${PackageKey} removal failed due to unexpected error(s)."
        exit 3
    }

    if (Test-Path "${chocoRoot}") {
        Write-Host "[INFO] ${PackageKey} directory still present — likely in use, safe to remove later: ${chocoRoot}"
        Write-Host "[INFO] This usually happens when files are in use. Reboot and remove manually if desired."
        exit 0
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
