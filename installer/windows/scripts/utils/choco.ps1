# 🍫 --- Ensure-Choco ---------------------------------------------------------
# Checks for Chocolatey; if missing, installs it; sets $script:ChocoAvailable.
function Ensure-Choco {
    Write-LogInfo "Checking for Chocolatey..."

    try {
        $cmd = Get-Command choco.exe -ErrorAction SilentlyContinue
        if ($cmd) {
            $ver = (& choco --version 2>$null).Trim()
            if ($ver) {
                $script:ChocoAvailable = $true
                Write-LogOk "Chocolatey v$ver detected at $($cmd.Source)"
                return
            }
        }

        # --- Attempt install -------------------------------------------------
        Write-LogWarn "Chocolatey not found - installing..."
        $chocoRoot = Join-Path $env:ProgramData "chocolatey"
        $chocoBin = Join-Path $chocoRoot "bin"
        try {
            if (Test-Path $chocoRoot) {
                Write-LogInfo "Removing incomplete Chocolatey folder..."
                Remove-Item -Recurse -Force $chocoRoot -ErrorAction SilentlyContinue | Out-Null
                Start-Sleep -Seconds 1
            }

            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $env:ChocolateyUseWindowsCompression = 'false'
            $env:ChocolateyInstall = $chocoRoot
            $tmp = Join-Path $env:TEMP 'chocolatey\chocoInstall'
            Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue | Out-Null
            Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        } catch {
            Write-LogFail "Chocolatey installation script failed: $($_.Exception.Message)"
        }

        # --- Verify after install -------------------------------------------
        $cmd2 = Get-Command choco.exe -ErrorAction SilentlyContinue
        if ($cmd2) {
            $ver2 = (& choco --version 2>$null).Trim()
            if ($ver2) {
                $script:ChocoAvailable = $true
                Write-LogOk "Chocolatey installed successfully (v$ver2)."
                return
            }
        }

        $script:ChocoAvailable = $false
        Write-LogFail "Chocolatey installation failed or not detected on PATH."
    } catch {
        $script:ChocoAvailable = $false
        Write-LogFail "Ensure-Choco error: $($_.Exception.Message)"
    }
}
