# 🍫 Ensure-Choco.ps1
# Detects or installs Chocolatey (https://chocolatey.org)
# Emits status messages via Write-Output for MagBridge logger.

[CmdletBinding()]
param()

Write-Output "🔍 Checking for Chocolatey..."

try {
    # --- Detection phase ---------------------------------------------------
    $cmd = Get-Command choco.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        $ver = (& choco --version 2>$null).Trim()
        if ($ver) {
            Write-Output "✅ Chocolatey v$ver detected at $($cmd.Source)"
            return
        }
    }

    # --- Installation phase ------------------------------------------------
    Write-Output "⚙️ Chocolatey not found — attempting installation..."
    $chocoRoot = Join-Path $env:ProgramData "chocolatey"

    if (Test-Path $chocoRoot) {
        Write-Output "🧹 Removing incomplete Chocolatey directory..."
        try {
            Remove-Item -Recurse -Force $chocoRoot -ErrorAction SilentlyContinue | Out-Null
            Start-Sleep -Seconds 1
        }
        catch {
            Write-Output ("⚠️ Failed to clean {0}: {1}" -f $chocoRoot, $_.Exception.Message)
        }
    }

    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $env:ChocolateyInstall = $chocoRoot
    $env:ChocolateyUseWindowsCompression = 'false'

    $installUrl = 'https://community.chocolatey.org/install.ps1'
    Write-Output "⬇️ Downloading and executing Chocolatey installer from $installUrl"

    try {
        $installScript = (New-Object System.Net.WebClient).DownloadString($installUrl)
        Invoke-Expression $installScript
    }
    catch {
        Write-Output "❌ Chocolatey installation script failed: $($_.Exception.Message)"
    }

    # --- Verification phase ------------------------------------------------
    $cmd2 = Get-Command choco.exe -ErrorAction SilentlyContinue
    if ($cmd2) {
        $ver2 = (& choco --version 2>$null).Trim()
        if ($ver2) {
            Write-Output "✅ Chocolatey installed successfully (v$ver2)"
            exit 0
        }
    }

    Write-Output "❌ Chocolatey installation failed or executable not found on PATH."
    exit 1

}
catch {
    Write-Output "❌ Ensure-Choco encountered an error: $($_.Exception.Message)"
    exit 2
}
