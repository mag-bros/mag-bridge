using System;
using System.Drawing;
using System.IO;
using System.Windows.Forms;
using MagBridge.Core;

namespace MagBridge.UI
{
  public class LicenseDialog : Form
  {
    private readonly TextBox licenseText;
    private readonly Button acceptButton;
    private readonly Button declineButton;
    private readonly Settings settings;

    public bool Accepted { get; private set; }

    public LicenseDialog(Settings settings)
    {
      this.settings = settings ?? throw new ArgumentNullException(nameof(settings));

      // === Window setup ==============================================
      Text = $"{settings.Name} — License Agreement";
      StartPosition = FormStartPosition.CenterScreen;
      Size = new Size(800, 600);
      MinimumSize = new Size(700, 500);
      Font = new Font("Consolas", 10);

      // Safe default icon — no file dependency
      try
      {
        Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath) ?? SystemIcons.Application;
      }
      catch
      {
        Icon = SystemIcons.Application;
      }

      // === License text area =========================================
      licenseText = new TextBox
      {
        Multiline = true,
        ReadOnly = true,
        ScrollBars = ScrollBars.Vertical,
        Dock = DockStyle.Fill,
        Font = Theme.MonoFont,
        BackColor = Theme.Surface,
        ForeColor = Theme.Text,
        BorderStyle = BorderStyle.FixedSingle,
        Text = settings.LoadLicenseText(),
        TabStop = false
      };


      // === Buttons ===================================================
      acceptButton = new ThemedButton
      {
        Text = "Accept",
        DialogResult = DialogResult.OK,
        Anchor = AnchorStyles.Bottom | AnchorStyles.Right,
        Margin = new Padding(8)
      };
      acceptButton.Click += (_, __) =>
      {
        Accepted = true;
        Close();
      };

      declineButton = new ThemedButton
      {
        Text = "Decline",
        DialogResult = DialogResult.Cancel,
        Anchor = AnchorStyles.Bottom | AnchorStyles.Right,
        Margin = new Padding(8)
      };
      declineButton.Click += (_, __) =>
      {
        Accepted = false;
        Close();
      };

      // === Layout panel ==============================================
      var buttonPanel = new Panel
      {
        Dock = DockStyle.Bottom,
        Height = Theme.ButtonBarHeight,
        Padding = new Padding(0, 8, 16, 8),
        BackColor = Theme.Surface
      };
      buttonPanel.Controls.Add(acceptButton);
      buttonPanel.Controls.Add(declineButton);

      // Position buttons relative to panel size
      buttonPanel.Resize += (_, __) =>
      {
        declineButton.Left = buttonPanel.Width - declineButton.Width - 20;
        acceptButton.Left = declineButton.Left - acceptButton.Width - 10;
        declineButton.Top = acceptButton.Top = (buttonPanel.Height - acceptButton.Height) / 2;
      };

      // === Control order =============================================
      buttonPanel.Controls.Add(declineButton);
      buttonPanel.Controls.Add(acceptButton);
      acceptButton.Left = buttonPanel.Width - acceptButton.Width * 2 - 24;
      declineButton.Left = buttonPanel.Width - declineButton.Width - 12;
      acceptButton.Top = declineButton.Top = (buttonPanel.Height - acceptButton.Height) / 2;

      // --- Add to form ---------------------------------------------------------
      Controls.Add(licenseText);
      Controls.Add(buttonPanel);

      // === UX polish =================================================
      Shown += (_, __) =>
      {
        licenseText.SelectionStart = 0;
        licenseText.SelectionLength = 0;
        acceptButton.Focus();
      };
    }
  }
}
