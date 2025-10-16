# 🧰 --- Ensure-GnuMake -------------------------------------------------------
# Ensures GNU Make is installed; installs via Chocolatey if needed; sets $script:GnuMakeAvailable.
function Ensure-GnuMake {
    param(
        [Parameter()][switch]$AdvanceStep   # optional flag: true if called within step sequence
    )

    if ($AdvanceStep) { Advance-Step "Checking GNU Make..." }
    else { Write-LogInfo "Checking GNU Make..." }

    try {
        Ensure-Path
        $makeCmd = Get-Command make.exe -ErrorAction SilentlyContinue
        if ($makeCmd) {
            $ver = (& $makeCmd.Source --version 2>$null)
            if ($LASTEXITCODE -eq 0 -and $ver) {
                $script:GnuMakeAvailable = $true
                Write-LogOk ("GNU Make detected: " + ($ver -split "`r?`n")[0])
                return
            }
        }

        # --- Attempt install -------------------------------------------------
        $script:GnuMakeAvailable = $false
        Write-LogWarn "GNU Make not found — attempting installation..."

        if ($script:ChocoAvailable) {
            if ($AdvanceStep) { Advance-Step "Installing GNU Make..." }
            choco install make -y --no-progress | Out-Null
        } else {
            Write-LogFail "Chocolatey not available — cannot install Make."
            return
        }

        # --- Verify after install -------------------------------------------
        Ensure-Path
        $makeCmd2 = Get-Command make.exe -ErrorAction SilentlyContinue
        if ($makeCmd2) {
            $ver2 = (& $makeCmd2.Source --version 2>$null)
            if ($LASTEXITCODE -eq 0 -and $ver2) {
                $script:GnuMakeAvailable = $true
                Write-LogOk ("GNU Make installed successfully: " + ($ver2 -split "`r?`n")[0])
                return
            }
        }

        $script:GnuMakeAvailable = $false
        Write-LogFail "GNU Make installation failed or not detected on PATH."
    } catch {
        $script:GnuMakeAvailable = $false
        Write-LogFail "Ensure-GnuMake error: $($_.Exception.Message)"
    }
}
