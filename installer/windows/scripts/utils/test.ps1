# Save as test-progress.ps1 and run:
# powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -File .\test-progress.ps1

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text = "Test"
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
$label.Text = "Preparing..."
$form.Controls.Add($label)

$bar = New-Object System.Windows.Forms.ProgressBar
$bar.Left = 20; $bar.Top = 60
$bar.Width = 480; $bar.Height = 25
$bar.Style = 'Continuous'
$bar.Minimum = 0; $bar.Maximum = 4; $bar.Value = 0
$form.Controls.Add($bar)

$form.Shown.Add({
        # step 1
        $label.Text = "Step 1 - Ensuring Chocolatey..."
        $label.Refresh(); $bar.Value = 1; $bar.Refresh()
        [Windows.Forms.Application]::DoEvents(); Start-Sleep -Milliseconds 600

        # step 2
        $label.Text = "Step 2 - Ensuring GNU Make..."
        $label.Refresh(); $bar.Value = 2; $bar.Refresh()
        [Windows.Forms.Application]::DoEvents(); Start-Sleep -Milliseconds 600

        # step 3
        $label.Text = "Step 3 - Updating PATH..."
        $label.Refresh(); $bar.Value = 3; $bar.Refresh()
        [Windows.Forms.Application]::DoEvents(); Start-Sleep -Milliseconds 600

        # step 4
        $label.Text = "Step 4 - Finalizing..."
        $label.Refresh(); $bar.Value = 4; $bar.Refresh()
        [Windows.Forms.Application]::DoEvents(); Start-Sleep -Milliseconds 600

        $label.Text = "Done."
        $label.Refresh()
    })

[void]$form.ShowDialog()
