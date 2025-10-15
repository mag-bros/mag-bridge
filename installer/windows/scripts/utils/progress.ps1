# --- Helper: pump UI messages (no-op in console) -----------------------------
function Invoke-UiPump { if ($script:UIAvailable) { [System.Windows.Forms.Application]::DoEvents() } }

# --- New-ProgressForm (unchanged API; safer internals) ----------------------
function New-ProgressForm {
    param([string]$Title = "Generic Installer", [int]$Max = 4)

    if (-not $script:UIAvailable) {
        $progress = [PSCustomObject]@{
            Step   = 0
            Max    = $Max
            Label  = "Preparing..."
            Update = {
                param($text)
                $this.Step = [Math]::Min($this.Step + 1, $this.Max)
                $percent = [math]::Round(($this.Step / [Math]::Max(1, $this.Max)) * 100)
                Write-Host ("[{0,2}/{1}] {2,-30} ({3,3}%)" -f $this.Step, $this.Max, $text, $percent)
            }
            Close  = { Write-Host "Installation completed." }
            Form   = $null
        }
        $progress.Update.Invoke("Starting in console mode...")
        return $progress
    }

    $form = New-Object System.Windows.Forms.Form
    $form.Text = $Title
    $form.Width = 540; $form.Height = 180
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false; $form.MinimizeBox = $false; $form.TopMost = $true
    $form.BackColor = [System.Drawing.Color]::FromArgb(245, 245, 245)

    $label = New-Object System.Windows.Forms.Label
    $label.Width = 500; $label.Height = 30; $label.Left = 20; $label.Top = 20
    $label.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Regular)
    $label.Text = "Preparing installer..."

    $bar = New-Object System.Windows.Forms.ProgressBar
    $bar.Left = 20; $bar.Top = 60; $bar.Width = 480; $bar.Height = 25
    $bar.Style = "Continuous"; $bar.Minimum = 0; $bar.Maximum = $Max; $bar.Value = 0

    $btnCancel = New-Object System.Windows.Forms.Button
    $btnCancel.Text = "Cancel"; $btnCancel.Left = 400; $btnCancel.Top = 100
    $btnCancel.Width = 100; $btnCancel.Height = 30
    $btnCancel.Add_Click({ $form.Tag = "Cancelled"; $form.Close() })

    $form.Controls.AddRange(@($label, $bar, $btnCancel))

    return [PSCustomObject]@{
        Form   = $form
        Label  = $label
        Bar    = $bar
        Cancel = $btnCancel
        Update = {
            param($text)
            $this.Label.Text = $text
            $this.Bar.Value = [Math]::Min($this.Bar.Value + 1, $this.Bar.Maximum)
            $this.Form.Refresh(); Invoke-UiPump
        }
        Close  = {
            if ($this.Form -and -not $this.Form.IsDisposed) {
                if ($this.Form.Tag -ne "Cancelled") { $this.Label.Text = "Installation complete."; Start-Sleep -Milliseconds 200 }
                $this.Form.Close(); $this.Form.Dispose()
                Invoke-UiPump
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
            $Ui.Bar.Maximum = [Math]::Max(1, $Total)
            $Ui.Bar.Value = [Math]::Min([Math]::Max(0, $Step), $Ui.Bar.Maximum)
            $Ui.Form.Refresh(); Invoke-UiPump
        } catch { Write-Warning "Failed to update progress form: $_" }
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
function Advance-Step([string]$msg) {
    $script:InstallerState.StepCurrent++
    Update-ProgressForm -Ui $script:InstallerState.Ui `
        -Step $script:InstallerState.StepCurrent `
        -Total $script:InstallerState.StepsTotal `
        -Message $msg
}
