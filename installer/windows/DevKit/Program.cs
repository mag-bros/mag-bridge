using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using DevKit.UI;

internal static class Program
{
    [STAThread]
    static void Main()
    {
        // Initialize application and enable modern WinForms settings
        ApplicationConfiguration.Initialize();
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);

        // Optional: open console if launched from Explorer
        AllocConsole();
        Console.WriteLine("=== DevKit Installer ===");
        Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Starting...");

        // Show license dialog first
        using (var licenseDialog = new LicenseDialog())
        {
            if (licenseDialog.ShowDialog() != DialogResult.OK || !licenseDialog.Accepted)
            {
                MessageBox.Show(
                    "You must accept the license terms to proceed.",
                    "License Agreement",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
                return;
            }
        }

        // Run main installer GUI
        Application.Run(new ProgressForm());

        // Log after installer closes
        Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Completed.");
        Console.WriteLine("Press any key to exit...");
        Console.ReadKey(true);
    }

    [DllImport("kernel32.dll")]
    private static extern bool AllocConsole();
}
