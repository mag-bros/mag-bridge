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

# 🚪 --- Exit-Console ---------------------------------------------------------
# Displays a final message, waits briefly, and closes the PowerShell session.
# Example:
#   Exit-Console -Delay 2 -Message "Exiting console..."
# ------------------------------------------------------------------------------

function Exit-Console {
    param(
        [int]$Delay = 2,
        [string]$Message = "Exiting console..."
    )

    try {
        Write-Host ""
        Write-Host "========================================================"
        Write-Host "  $Message"
        Write-Host "========================================================"
        Start-Sleep -Seconds $Delay
        exit
    } catch {
        Write-Warning "Exit-Console failed: $($_.Exception.Message)"
        exit 1
    }
}

# 🕒 --- Start-UiHeartbeat -----------------------------------------------------
# Starts a background timer that keeps Windows Forms responsive
# without blocking the main installer thread.
function Start-UiHeartbeat {
    param([int]$Interval = 120)

    if (-not $script:UIAvailable) { return }

    if ($script:UiTimer -and $script:UiTimer.Enabled) { return } # already running

    $script:UiTimer = New-Object System.Windows.Forms.Timer
    $script:UiTimer.Interval = $Interval
    $script:UiTimer.Add_Tick({ [System.Windows.Forms.Application]::DoEvents() })
    $script:UiTimer.Start()
}

# 🛑 --- Stop-UiHeartbeat ------------------------------------------------------
# Stops and disposes the background timer cleanly.
function Stop-UiHeartbeat {
    if ($script:UiTimer) {
        try { $script:UiTimer.Stop(); $script:UiTimer.Dispose() } catch {}
        Remove-Variable -Name UiTimer -Scope Script -ErrorAction SilentlyContinue
    }
}
