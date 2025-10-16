# --- Helper: pump UI messages (no-op in console) -----------------------------
function Invoke-UiPump { if ($script:UIAvailable) { [System.Windows.Forms.Application]::DoEvents() } }

# --- New-ProgressForm (unchanged API; safer internals) ----------------------
# 🪟 --- New-ProgressForm -----------------------------------------------------
# Creates GUI or console fallback progress form with working refresh & updates.
function New-ProgressForm {
    param([string]$Title = "Generic Installer", [int]$Max = 4)

    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $form = New-Object System.Windows.Forms.Form
    $form.Text = $Title
    $form.Width = 540; $form.Height = 180
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false; $form.MinimizeBox = $false
    $form.TopMost = $true
    $form.BackColor = [System.Drawing.Color]::FromArgb(245, 245, 245)
    $form.ShowInTaskbar = $true

    $label = New-Object System.Windows.Forms.Label
    $label.Left = 20; $label.Top = 20
    $label.Width = 480; $label.Height = 25
    $label.AutoSize = $false
    $label.UseMnemonic = $false
    $label.TextAlign = 'MiddleLeft'
    $label.Font = New-Object System.Drawing.Font("Segoe UI", 10)
    $label.ForeColor = [System.Drawing.Color]::FromArgb(30, 30, 30)
    $label.BackColor = [System.Drawing.Color]::FromArgb(245, 245, 245)
    $label.Text = "Preparing installer..."
    $form.Controls.Add($label)

    $bar = New-Object System.Windows.Forms.ProgressBar
    $bar.Left = 20; $bar.Top = 60
    $bar.Width = 480; $bar.Height = 25
    $bar.Style = 'Continuous'
    $bar.Minimum = 0; $bar.Maximum = $Max; $bar.Value = 0
    $form.Controls.Add($bar)

    $btnCancel = New-Object System.Windows.Forms.Button
    $btnCancel.Text = "Cancel"
    $btnCancel.Left = 400; $btnCancel.Top = 100
    $btnCancel.Width = 100; $btnCancel.Height = 30
    $btnCancel.Add_Click({ $form.Tag = "Cancelled"; $form.Close() })
    $form.Controls.Add($btnCancel)

    return [PSCustomObject]@{
        Form   = $form
        Label  = $label
        Bar    = $bar
        Cancel = $btnCancel
        Update = {
            param($text)
            if ($this.Form -and -not $this.Form.IsDisposed) {
                $this.Label.Text = $text
                $this.Label.Refresh()
                $this.Bar.Refresh()
                [System.Windows.Forms.Application]::DoEvents()
            }
        }
        Close  = {
            if ($this.Form -and -not $this.Form.IsDisposed) {
                if ($this.Form.Tag -ne "Cancelled") {
                    $this.Label.Text = "Installation complete."
                    $this.Label.Refresh()
                    Start-Sleep -Milliseconds 200
                }
                $this.Form.Close()
                $this.Form.Dispose()
                [System.Windows.Forms.Application]::DoEvents()
            }
        }
    }
}


# --- Update-ProgressForm (checks GUI/console; pumps UI) ----------------------
function Update-ProgressForm($Ui, [int]$Step, [int]$Total, [string]$Msg) {
    if (-not $Ui) { return }

    if ($Ui.Form) {
        try {
            $Ui.Label.Text = $Msg
            $Ui.Label.Refresh()            # 🟢 force GDI redraw of label region
            $Ui.Bar.Maximum = [Math]::Max(1, $Total)
            $Ui.Bar.Value = [Math]::Min([Math]::Max(0, $Step), $Ui.Bar.Maximum)
            $Ui.Bar.Refresh()
            $Ui.Form.Refresh()
            [System.Windows.Forms.Application]::DoEvents()
        } catch {
            Write-Warning "Failed to update progress form: $_"
        }
    } else {
        $percent = [math]::Round(($Step / [Math]::Max(1, $Total)) * 100)
        Write-Host ("[{0,2}/{1}] {2,-30} ({3,3}%)" -f $Step, $Total, $Msg, $percent)
    }
}

function Close-ProgressForm($Ui) {
    if (-not $Ui) { return }

    if ($Ui.Form) {
        try {
            $f = $Ui.Form

            # If we're not on the UI thread, marshal the close to it.
            if ($f.InvokeRequired) {
                $null = $f.BeginInvoke([System.Windows.Forms.MethodInvoker] { 
                        try { $f.Close() } catch {}
                    })
            } else {
                try { $f.Close() } catch {}
            }

            # Give the message loop a tick to process the close.
            [System.Windows.Forms.Application]::DoEvents()
            Start-Sleep -Milliseconds 150

            # Final safeguard: dispose if still hanging around.
            if ($f -and -not $f.IsDisposed) {
                try { $f.Hide() } catch {}
                try { $f.Dispose() } catch {}
            }
        } catch {
            Write-Warning "Failed to close progress form: $_"
        }
    } else {
        Write-Host "Installation completed."
    }
}

# Helper to advance progress uniformly
function Advance-Step {
    param(
        [Parameter(Mandatory)][string]$Message,
        [scriptblock]$Action = $null,   # optional operation to run
        [switch]$Background,            # run in background runspace
        [int]$DelayMs = 250             # optional pause to let UI catch up
    )

    if (-not $script:InstallerState) { return }

    # Increment and log step
    $script:InstallerState.StepCurrent++
    Write-LogInfo $Message

    # Update progress UI immediately
    Update-ProgressForm -Ui $script:InstallerState.Ui `
        -Step $script:InstallerState.StepCurrent `
        -Total $script:InstallerState.StepsTotal `
        -Message $Message

    # 💤 micro-yield — ensure UI repaints before running action
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds $DelayMs

    # --- Run provided action -------------------------------------------------
    if ($Action) {
        if ($Background) {
            # 🧵 Run asynchronously in runspace
            $rs = [runspacefactory]::CreateRunspace()
            $rs.ApartmentState = 'STA'
            $rs.ThreadOptions = 'ReuseThread'
            $rs.Open()

            $ps = [powershell]::Create()
            $ps.Runspace = $rs
            $ps.AddScript($Action) | Out-Null
            $handle = $ps.BeginInvoke()

            while (-not $handle.IsCompleted) {
                [System.Windows.Forms.Application]::DoEvents()
                Start-Sleep -Milliseconds 100
            }

            $ps.EndInvoke($handle)
            $ps.Dispose()
            $rs.Close()
            $rs.Dispose()
        } else {
            # ⚙️ Run synchronously (blocking)
            & $Action
        }
    }
}
