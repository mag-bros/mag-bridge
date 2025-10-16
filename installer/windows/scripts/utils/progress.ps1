# --- Helper: pump UI messages (no-op in console) -----------------------------
function Invoke-UiPump { if ($script:UIAvailable) { [System.Windows.Forms.Application]::DoEvents() } }

# 🪟 --- New-ProgressForm -----------------------------------------------------
# Creates GUI or console fallback progress form with working refresh & updates.
function New-ProgressForm {
    param(
        [string]$Title = "My Installer",
        [int]   $Max = 100  # maximum value for progress bar
    )
    Add-Type -AssemblyName System.Windows.Forms, System.Drawing  # ensure WinForms is loaded
    # Create form and controls
    $form = New-Object System.Windows.Forms.Form
    $form.Text = $Title
    $form.Width = 500
    $form.Height = 250
    $form.StartPosition = 'CenterScreen'
    $form.FormBorderStyle = 'FixedDialog'
    $form.MaximizeBox = $false
    $form.MinimizeBox = $false
    $form.Topmost = $true  # keep on top of other windows (optional)
    $form.BackColor = [System.Drawing.Color]::White

    $label = New-Object System.Windows.Forms.Label
    $label.AutoSize = $true
    $label.Location = New-Object System.Drawing.Point(20, 20)
    $label.Text = "Initializing..."
    $form.Controls.Add($label)

    $progressBar = New-Object System.Windows.Forms.ProgressBar
    $progressBar.Location = New-Object System.Drawing.Point(20, 50)
    $progressBar.Width = 340
    $progressBar.Minimum = 0
    $progressBar.Maximum = $Max
    $progressBar.Value = 0
    $form.Controls.Add($progressBar)

    # Create a PSObject to hold the form and provide methods
    $progressObj = [PSCustomObject]@{
        Form  = $form
        Label = $label
        Bar   = $progressBar
    }
    # Add an Update() method to change the label text (on UI thread)
    $progressObj | Add-Member -MemberType ScriptMethod -Name Update -Value {
        param([string]$Text)
        if ($this.Form -and -not $this.Form.IsDisposed) {
            $this.Label.Text = $Text
            $null = [System.Windows.Forms.Application]::DoEvents()  # allow immediate UI update
        }
    }
    # Add a Close() method to close the form
    $progressObj | Add-Member -MemberType ScriptMethod -Name Close -Value {
        if ($this.Form -and -not $this.Form.IsDisposed) {
            # You can add any cleanup logic here if needed
            # $this.Form.Close()
        }
    }
    return $progressObj
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
