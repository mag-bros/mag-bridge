. "./progress.ps1"  # Your New-ProgressForm function

# ────────────────────────────────────────────────
# 🧾 Logging setup
# ────────────────────────────────────────────────
$LogPath = Join-Path $PSScriptRoot "installer.log"
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$timestamp][$Level] $Message"
    Write-Host $line
    Add-Content -Path $LogPath -Value $line
}

Write-Log "=== Installer session started ==="

try {
    Add-Type -AssemblyName System.Windows.Forms
    $progressForm = New-ProgressForm -Title "Installer" -Max 100

    $messages = @(
        "Preparing installer...",
        "Installing component 1...",
        "Installing component 2...",
        "Finalizing..."
    )

    $script:step = 0
    Write-Log "Progress form created. Steps: $($messages.Count)"

    $timer = New-Object System.Windows.Forms.Timer
    $timer.Interval = 700

    $null = $timer.Add_Tick({
            try {
                if ($script:step -lt $messages.Count) {
                    $msg = $messages[$script:step]
                    $pct = [Math]::Min(($script:step + 1) / $messages.Count * 100, 100)

                    if ($progressForm -and $progressForm.Form -and -not $progressForm.Form.IsDisposed) {
                        $progressForm.Update($msg)
                        $progressForm.Bar.Value = $pct
                    }

                    Write-Log ("Progress: {0}% — {1}" -f $pct, $msg)
                    $script:step++
                } else {
                    # Stop timer safely and close form on UI thread
                    $timer.Stop()
                    Write-Log "All steps completed. Closing soon..."
                    if ($progressForm -and $progressForm.Form -and -not $progressForm.Form.IsDisposed) {
                        $progressForm.Update("Installation complete.")
                        [System.Windows.Forms.Application]::DoEvents()
                        Start-Sleep -Milliseconds 800
                        $null = $progressForm.Form.BeginInvoke([Action] {
                                if ($progressForm.Form -and -not $progressForm.Form.IsDisposed) {
                                    $progressForm.Form.Close()
                                }
                            })
                    }
                }
            } catch {
                Write-Log "Timer tick failed: $($_.Exception.Message)" "ERROR"
                $timer.Stop()
                if ($progressForm -and $progressForm.Form -and -not $progressForm.Form.IsDisposed) {
                    $progressForm.Update("Error: $($_.Exception.Message)")
                }
            }
        })

    # Optional: clean up when form is closing
    $progressForm.Form.Add_FormClosing({
            Write-Log "Form closing — disposing timers."
            if ($timer.Enabled) { $timer.Stop() }
            $timer.Dispose()
        })

    $progressForm.Form.Add_Shown({
            Write-Log "Starting timer..."
            $timer.Start()
        })

    [void][System.Windows.Forms.Application]::Run($progressForm.Form)
    Write-Log "Form closed normally."
} catch {
    Write-Log "FATAL: $($_.Exception.Message)" "ERROR"
} finally {
    Write-Log "=== Installer session ended ==="
}
