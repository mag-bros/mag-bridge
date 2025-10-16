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
This installer automates the setup of required open-source tools:
───────────────────────────────────────────────────────────────
• GNU Make (GNU General Public License v3)
  → https://www.gnu.org/software/make/
  Freely redistributable and open-source. Installed via official sources.

• Chocolatey Community Edition (Apache 2.0 License)
  → https://community.chocolatey.org/
  Only the free community client is installed.
  No commercial or business versions are included.
  Use in enterprise settings may require a commercial license.

• Electron (MIT License)
  • npm / Node.js (Artistic License 2.0)
  → https://nodejs.org/
  → https://www.electronjs.org/
  Open-source software distributed under their respective licenses.
  Some npm packages may impose additional obligations (e.g., source disclosure).

───────────────────────────────────────────────────────────────
By proceeding, you acknowledge that:
- Only open-source components are installed.
- You are responsible for license compliance in your environment.
- The authors provide this installer without warranty or liability.

Press 'Accept' to continue or 'Decline' to exit setup.";

    }
}
