using System;
using System.Drawing;
using System.Windows.Forms;

namespace DevKit.UI
{
    public class LicenseDialog : Form
    {
        private readonly TextBox licenseText;
        private readonly Button acceptButton;
        private readonly Button declineButton;

        public bool Accepted { get; private set; } = false;

        public LicenseDialog()
        {
            Text = "Open-Source License Notice";
            StartPosition = FormStartPosition.CenterScreen;
            Size = new Size(800, 600);
            Font = new Font("Consolas", 10);
            MinimumSize = new Size(700, 500);

            licenseText = new TextBox
            {
                Multiline = true,
                ReadOnly = true,
                ScrollBars = ScrollBars.Vertical,
                Dock = DockStyle.Top,
                Height = ClientSize.Height - 70,
                Font = new Font("Consolas", 10),
                BackColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Text = GetLicenseNotice(),
                TabStop = false // 👈 prevents focus highlight
            };

            acceptButton = new Button
            {
                Text = "Accept",
                DialogResult = DialogResult.OK,
                Anchor = AnchorStyles.Bottom | AnchorStyles.Right,
                Width = 120,
                Height = 35,
                Top = ClientSize.Height - 50,
                Left = ClientSize.Width - 270
            };
            acceptButton.Click += (_, __) =>
            {
                Accepted = true;
                Close();
            };

            declineButton = new Button
            {
                Text = "Decline",
                DialogResult = DialogResult.Cancel,
                Anchor = AnchorStyles.Bottom | AnchorStyles.Right,
                Width = 120,
                Height = 35,
                Top = ClientSize.Height - 50,
                Left = ClientSize.Width - 140
            };
            declineButton.Click += (_, __) =>
            {
                Accepted = false;
                Close();
            };

            Controls.Add(licenseText);
            Controls.Add(acceptButton);
            Controls.Add(declineButton);

            AcceptButton = acceptButton;
            CancelButton = declineButton;

            // 👇 ensures text is shown from the start and focus is on the button
            Shown += (_, __) =>
            {
                licenseText.SelectionStart = 0;
                licenseText.SelectionLength = 0;
                acceptButton.Focus();
            };
        }

        private static string GetLicenseNotice() => @"
DEVKIT INSTALLER — OPEN-SOURCE LICENSE NOTICE
──────────────────────────────────────────────────────────────

PURPOSE
This installer automates the setup of required developer tools using
official, publicly available installers and package feeds.

COMPONENTS INSTALLED (AND LICENSES)
• GNU Make — GNU General Public License v3 (GPL-3.0)
  https://www.gnu.org/software/make/

• Chocolatey (Community Edition) — Apache License 2.0
  https://community.chocolatey.org/
  Note: Only the free community client is installed. Commercial editions
  (e.g., Chocolatey for Business) are NOT included.

• Node.js — MIT License
  https://nodejs.org/

• npm (CLI) — Artistic License 2.0
  https://github.com/npm/cli

• Electron — MIT License
  https://www.electronjs.org/

ADDITIONAL DEPENDENCIES
Tools installed via these package managers (e.g., npm packages) are subject
to THEIR OWN licenses. Some packages may impose additional obligations
(e.g., attribution, source disclosure, copyleft). Review license terms for
any additional software you install.

WHAT THIS INSTALLER DOES (AND DOES NOT DO)
• Installs the tools listed above from their official sources.
• Does NOT modify, sublicense, or bundle altered versions of those tools.
• Does NOT grant you any additional rights beyond the upstream licenses.

YOUR RESPONSIBILITIES
• Ensure your use complies with the applicable licenses and your
  organization's policies.
• For business/enterprise use of Chocolatey, evaluate whether a commercial
  license or support subscription is appropriate for your environment.
• Verify and comply with the licenses of any downstream packages you install
  using these tools (e.g., npm dependencies).

WARRANTY & LIABILITY
This installer and its authors provide the software “AS IS,” without
warranty of any kind. To the maximum extent permitted by law, no liability
is assumed for any direct or indirect damages arising from installation,
use, or reliance on these tools.

CONSENT
By clicking “Accept,” you acknowledge that you have read and understood this
notice, and agree to comply with the licenses of the installed components
and any additional dependencies you choose to install. Click “Decline” to
exit without making changes.

Press 'Accept' to continue or 'Decline' to exit.";

    }
}
