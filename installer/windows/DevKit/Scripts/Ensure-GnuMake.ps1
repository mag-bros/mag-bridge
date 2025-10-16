# 🧰 Ensure-GnuMake.ps1
# Ensures GNU Make is installed; installs via Chocolatey if missing.
# Emits clean Write-Output messages for DevKit logger.

[CmdletBinding()]
param()

Write-Output "🔍 Checking for GNU Make..."

try {
    # --- Detection phase ---------------------------------------------------
    $makeCmd = Get-Command make.exe -ErrorAction SilentlyContinue
    if ($makeCmd) {
        $ver = (& $makeCmd.Source --version 2>$null)
        if ($LASTEXITCODE -eq 0 -and $ver) {
            $line = ($ver -split "`r?`n")[0]
            Write-Output "✅ GNU Make detected: $line"
            exit 0
        }
    }

    Write-Output "⚙️ GNU Make not found — attempting installation..."

    # --- Install phase -----------------------------------------------------
    $chocoCmd = Get-Command choco.exe -ErrorAction SilentlyContinue
    if (-not $chocoCmd) {
        Write-Output "❌ Chocolatey not available — cannot install GNU Make."
        exit 1
    }

    try {
        Write-Output "⬇️ Installing GNU Make via Chocolatey..."
        choco install make -y --no-progress | Out-Null
    } catch {
        Write-Output ("❌ Chocolatey install command failed: {0}" -f $_.Exception.Message)
    }

    # --- Verify phase ------------------------------------------------------
    $makeCmd2 = Get-Command make.exe -ErrorAction SilentlyContinue
    if ($makeCmd2) {
        $ver2 = (& $makeCmd2.Source --version 2>$null)
        if ($LASTEXITCODE -eq 0 -and $ver2) {
            $line2 = ($ver2 -split "`r?`n")[0]
            Write-Output "✅ GNU Make installed successfully: $line2"
            # Refresh path
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
            exit 0
        }
    }

    Write-Output "❌ GNU Make installation failed or not detected on PATH."
    exit 2

} catch {
    Write-Output ("❌ Ensure-GnuMake encountered an error: {0}" -f $_.Exception.Message)
    exit 3
}
