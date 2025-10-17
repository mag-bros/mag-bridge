# Ensure-Choco.ps1
# Detects or installs Chocolatey (https://chocolatey.org)
# Emits standardized output for MagBridge logger.

Write-Host "=== Checking for Chocolatey ==="

try {
    # --- Detection phase ---------------------------------------------------
    $cmd = Get-Command choco.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        $ver = (& choco --version 2>$null).Trim()
        if ($ver) {
            Write-Host ("Chocolatey v{0} detected at {1}" -f $ver, $cmd.Source)
            exit 0
        }
    }

    # --- Installation phase ------------------------------------------------
    Write-Warning "Chocolatey not found — attempting installation..."
    $chocoRoot = Join-Path $env:ProgramData "chocolatey"

    if (Test-Path $chocoRoot) {
        Write-Warning "Removing incomplete Chocolatey directory..."
        try {
            Remove-Item -Recurse -Force $chocoRoot -ErrorAction SilentlyContinue | Out-Null
            Start-Sleep -Seconds 1
        }
        catch {
            Write-Warning ("Failed to clean {0}: {1}" -f $chocoRoot, $_.Exception.Message)
        }
    }

    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $env:ChocolateyInstall = $chocoRoot
    $env:ChocolateyUseWindowsCompression = 'false'

    $installUrl = 'https://community.chocolatey.org/install.ps1'
    Write-Host ("Downloading and executing Chocolatey installer from {0}" -f $installUrl)

    try {
        $installScript = (New-Object System.Net.WebClient).DownloadString($installUrl)
        Invoke-Expression $installScript
    }
    catch {
        Write-Error ("Chocolatey installation script failed: {0}" -f $_.Exception.Message)
    }

    # --- Verification phase ------------------------------------------------
    $cmd2 = Get-Command choco.exe -ErrorAction SilentlyContinue
    if ($cmd2) {
        $ver2 = (& choco --version 2>$null).Trim()
        if ($ver2) {
            Write-Host ("Chocolatey installed successfully (v{0})" -f $ver2)
            exit 0
        }
    }

    Write-Error "Chocolatey installation failed or executable not found on PATH."
    exit 1
}
catch {
    Write-Error ("Ensure-Choco encountered an error: {0}" -f $_.Exception.Message)
    exit 2
}
