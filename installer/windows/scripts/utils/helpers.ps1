# 🖥️ --- UI availability check -------------------------------------------------
# Detects if Windows Forms and Drawing assemblies are available.
# Sets $script:UIAvailable to $true or $false for GUI / headless mode detection.

function Check-UIAvailable {
    $script:UIAvailable = $true
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
        Add-Type -AssemblyName System.Drawing -ErrorAction Stop
        [System.Windows.Forms.Application]::EnableVisualStyles()
    } catch {
        $script:UIAvailable = $false
        Write-Host "Headless environment detected — skipping GUI screens."
    }
}

# 🔁 --- Ensure-Path ----------------------------------------------------------
# Ensures Chocolatey and GNU Make directories are in PATH and refreshes current session.
function Ensure-Path {
    try {
        $makeDir = "C:\ProgramData\chocolatey\lib\make\tools\install\bin"
        $chocoBin = "C:\ProgramData\chocolatey\bin"

        foreach ($dir in @($chocoBin, $makeDir)) {
            if (Test-Path $dir) {
                $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
                if (-not ($machine -split ';' | Where-Object { $_ -ieq $dir })) {
                    [Environment]::SetEnvironmentVariable('Path', "$machine;$dir", 'Machine')
                    Write-LogInfo "Added to PATH: $dir"
                }
            }
        }

        # Refresh current PowerShell session PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
        [System.Environment]::GetEnvironmentVariable('Path', 'User')

        Write-LogOk "PATH refreshed successfully."
    } catch {
        Write-LogFail "Ensure-Path failed: $($_.Exception.Message)"
    }
}
