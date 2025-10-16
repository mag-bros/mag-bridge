# 🧾 --- Show-LicenseDialog ---------------------------------------------------------
# Displays license info for GNU Make (GPLv3) and Chocolatey (Apache 2.0).
# Keeps installer form active after closing.
# Returns $true if accepted, $false if declined.
# ------------------------------------------------------------------------------

function Show-LicenseDialog {
    param(
        [System.Windows.Forms.Form] $OwnerForm
    )

    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $form = New-Object System.Windows.Forms.Form
    $form.Text = "License Information and Consent"
    $form.Width = 720
    $form.Height = 520
    $form.StartPosition = "CenterParent"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false
    $form.MinimizeBox = $false
    $form.TopMost = $true
    $form.BackColor = [System.Drawing.Color]::FromArgb(245, 245, 245)

    $labelTitle = New-Object System.Windows.Forms.Label
    $labelTitle.Text = "Please review the third-party license information below:"
    $labelTitle.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $labelTitle.AutoSize = $true
    $labelTitle.Top = 15
    $labelTitle.Left = 15

    $textBox = New-Object System.Windows.Forms.TextBox
    $textBox.Multiline = $true
    $textBox.ScrollBars = "Vertical"
    $textBox.ReadOnly = $true
    $textBox.WordWrap = $true
    $textBox.Font = New-Object System.Drawing.Font("Consolas", 9)
    $textBox.Width = 670
    $textBox.Height = 360
    $textBox.Left = 15
    $textBox.Top = 50
    $textBox.Text = @"
This installer automates the setup of required open-source tools:
───────────────────────────────────────────────────────────────
• GNU Make (licensed under GNU General Public License v3)
  → https://www.gnu.org/software/make/
  Freely redistributable and open-source. Installed via official sources.

• Chocolatey Community Edition (Apache 2.0 license)
  → https://community.chocolatey.org/
  Only the free community client is installed.
  No commercial or business versions are included.
  Use in enterprise settings may require a commercial license.

───────────────────────────────────────────────────────────────
By proceeding, you acknowledge that:
- Only open-source components are installed.
- You are responsible for license compliance in your environment.
- The authors provide this installer without warranty.

“• Electron (MIT license) + npm / Node.js (Artistic License 2.0)
→ These open-source tools will be installed as part of the setup.

By proceeding, you acknowledge that:
- The installer includes open-source components under their respective licenses.
- You are responsible for license compliance of all dependencies (including those installed via npm).
- Some npm packages may impose additional obligations (e.g. source disclosure).
- The authors provide this installer without warranty, and you accept full responsibility for legal compliance in your environment.”
Press “Accept” to continue or “Decline” to exit the setup.
"@

    $btnAccept = New-Object System.Windows.Forms.Button
    $btnAccept.Text = "Accept"
    $btnAccept.Width = 100
    $btnAccept.Height = 35
    $btnAccept.Top = 430
    $btnAccept.Left = 400

    $btnDecline = New-Object System.Windows.Forms.Button
    $btnDecline.Text = "Decline"
    $btnDecline.Width = 100
    $btnDecline.Height = 35
    $btnDecline.Top = 430
    $btnDecline.Left = 520

    $form.Controls.AddRange(@($labelTitle, $textBox, $btnAccept, $btnDecline))

    $btnAccept.Add_Click({ $form.Tag = "Accepted"; $form.Close() })
    $btnDecline.Add_Click({ $form.Tag = "Declined"; $form.Close() })

    $form.Add_Shown({
            $btnAccept.Focus()
            $textBox.SelectionLength = 0
            $textBox.DeselectAll()
        })

    # 👇 Show dialog as child of progress form
    if ($OwnerForm -and -not $OwnerForm.IsDisposed) {
        $form.ShowDialog($OwnerForm) | Out-Null
    } else {
        $form.ShowDialog() | Out-Null
    }

    # --- Result handling ----------------------------------------------------
    if ($form.Tag -ne "Accepted") {
        Write-Host "License not accepted. Exiting setup..."
        Start-Sleep -Seconds 2
        exit 1
    }

    Write-Host "License accepted. Proceeding with installation..."
    return $true
}
