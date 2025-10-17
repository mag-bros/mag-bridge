# 💬 --- Welcome Form ---------------------------------------------------------------
# Displays the MagBridge Project welcome screen with project info, logo, and component selection.
# Automatically falls back to console mode if no GUI is available.

function Show-WelcomeDialog {
    if ($script:UIAvailable) {
        # --- Form setup -----------------------------------------------------
        $form = New-Object System.Windows.Forms.Form
        $form.Text = "MagBridge Project — GNU Make Installer"
        $form.Width = 600; $form.Height = 420
        $form.StartPosition = "CenterScreen"
        $form.FormBorderStyle = "FixedDialog"
        $form.MaximizeBox = $false; $form.MinimizeBox = $false
        $form.TopMost = $true
        $form.BackColor = [System.Drawing.Color]::FromArgb(250,250,250)

        # --- Logo placeholder ----------------------------------------------
        $logoBox = New-Object System.Windows.Forms.PictureBox
        $logoBox.Width = 80; $logoBox.Height = 80
        $logoBox.Left = 25; $logoBox.Top = 25
        $logoBox.BorderStyle = "FixedSingle"

        # --- Title label ----------------------------------------------------
        $title = New-Object System.Windows.Forms.Label
        $title.Text = "Welcome to the MagBridge Project Installer"
        $title.Font = New-Object System.Drawing.Font("Segoe UI",14,[System.Drawing.FontStyle]::Bold)
        $title.Left = 120; $title.Top = 35; $title.Width = 440; $title.Height = 30

        # --- Description ----------------------------------------------------
        $desc = New-Object System.Windows.Forms.Label
        $desc.Text =
"This open-source project streamlines chemists’ workflows through simplicity and thoughtful design focused on user experience.

This installer will:
 • Install Chocolatey (if missing or broken)
 • Install GNU Make via Chocolatey
 • Update PATH
 • Verify installation"
        $desc.Font = New-Object System.Drawing.Font("Segoe UI",10)
        $desc.Left = 40; $desc.Top = 110; $desc.Width = 520; $desc.Height = 140
        $desc.AutoSize = $false

        # --- Checkboxes -----------------------------------------------------
        $chkChoco.Checked = $true


        $chkMake = New-Object System.Windows.Forms.CheckBox
        $chkMake.Text = "GNU Make for Windows"
        $chkMake.Left = 60; $chkMake.Top = 290; $chkMake.Width = 400
        $chkMake.Checked = $true

        # --- Buttons --------------------------------------------------------
        $btnInstall = New-Object System.Windows.Forms.Button
        $btnInstall.Text = "Install"
        $btnInstall.Width = 100; $btnInstall.Height = 35
        $btnInstall.Left = 460; $btnInstall.Top = 340
        $btnInstall.DialogResult = [System.Windows.Forms.DialogResult]::OK
        $btnInstall.Font = New-Object System.Drawing.Font("Segoe UI",10,[System.Drawing.FontStyle]::Bold)

        $btnCancel = New-Object System.Windows.Forms.Button
        $btnCancel.Text = "Cancel"
        $btnCancel.Width = 100; $btnCancel.Height = 35
        $btnCancel.Left = 340; $btnCancel.Top = 340
        $btnCancel.DialogResult = [System.Windows.Forms.DialogResult]::Cancel

        $form.Controls.AddRange(@($logoBox,$title,$desc,$chkChoco,$chkMake,$btnInstall,$btnCancel))

        # --- Show dialog ----------------------------------------------------
        $dialogResult = $form.ShowDialog()

        # --- Store user decisions ------------------------------------------
        # Example: 
        # if (-not $Global:InstallOptions.Chocolatey) {
        #     Write-LogWarn "Not installing Chocolatey."
        # }

        $Global:InstallOptions = [PSCustomObject]@{
            Continue    = ($dialogResult -eq [System.Windows.Forms.DialogResult]::OK)
            Chocolatey  = $chkChoco.Checked
            Make        = $chkMake.Checked
        }

        if (-not $InstallOptions.Continue) {
            Write-Host "❌  Installation cancelled by user."
            exit 0
        }

        Write-Host "✅  Proceeding with installation..."
        Write-Host ("Selected components: " +
                    ("Chocolatey " * [int]$InstallOptions.Chocolatey) +
                    ("GNU Make " * [int]$InstallOptions.Make))
    }
    else {
        # --- Fallback for CI/CD or no GUI ----------------------------------
        Write-Host @"
MagBridge Project — Open Source Initiative
This tool streamlines chemists’ workflows through simplicity and usability.

Tasks to perform:
 • Install Chocolatey (if missing)
 • Install GNU Make via Chocolatey
 • Update PATH
 • Verify installation
"@
        $response = Read-Host "Continue installation? (Y/N)"
        if ($response -notmatch '^[Yy]') { exit 0 }

        $Global:InstallOptions = [PSCustomObject]@{
            Continue   = $true
            Chocolatey = $true
            Make       = $true
        }
    }
}
