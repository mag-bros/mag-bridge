using System.Runtime.InteropServices;
using MagBridge.Core;
using MagBridge.UI;

internal static class Program
{
    [STAThread]
    static void Main()
    {
        // === Initialization ===============================================
        ApplicationConfiguration.Initialize();
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);

        AllocConsole();
        Console.WriteLine("=== MagBridge Installer ===");
        Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Starting...");

        // === Load static settings =========================================
        Settings settings;
        try
        {
            settings = Settings.Load();
            Console.WriteLine($"Loaded configuration, RunType: {settings.RunType} - v{settings.Version}");
            Console.WriteLine($"Description: {settings.Description}");
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                $"Failed to load configuration:\n{ex.Message}",
                "Installer Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
            return;
        }

        // === Welcome screen ===============================================
        try
        {
            using (var welcome = new WelcomeDialog(settings))
            {
                if (welcome.ShowDialog() != DialogResult.OK)
                    return;

                settings.SelectedPackages = welcome.SelectedPackageKeys
                    .ToHashSet(StringComparer.OrdinalIgnoreCase);
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                $"Error displaying Welcome screen:\n{ex.Message}",
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
            return;
        }

        // === License agreement ============================================
        // try
        // {
        //     using (var licenseDialog = new LicenseDialog(settings))
        //     {
        //         if (licenseDialog.ShowDialog() != DialogResult.OK || !licenseDialog.Accepted)
        //         {
        //             MessageBox.Show(
        //                 "You must accept the license terms to proceed.",
        //                 "License Agreement",
        //                 MessageBoxButtons.OK,
        //                 MessageBoxIcon.Information
        //             );
        //             return;
        //         }
        //     }
        // }
        // catch (Exception ex)
        // {
        //     MessageBox.Show(
        //         $"License display error:\n{ex.Message}",
        //         "License Error",
        //         MessageBoxButtons.OK,
        //         MessageBoxIcon.Error
        //     );
        //     return;
        // }

        // === Run Tasks ================================================
        try
        {
            var progressForm = new ProgressForm(settings) { };
            Application.Run(progressForm);
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                $"Program error:\n{ex.Message}",
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }

        // === Cleanup ======================================================
        Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Completed.");
    }

    [DllImport("kernel32.dll")]
    private static extern bool AllocConsole();
}
