using System;
using System.IO;
using System.Threading.Tasks;

namespace DevKit
{
    internal static class Program
    {
        [STAThread]
        private static async Task Main(string[] args)
        {
            Console.Title = "DevKit Admin Executor";

            if (!Utilities.IsRunningAsAdministrator())
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine("⚠️  DevKit is not running as Administrator. Attempting to relaunch...");
                Console.ResetColor();

                if (Utilities.RelaunchAsAdministrator())
                    return; // Relaunched as admin, current instance exits.

                Console.WriteLine("❌ User denied elevation. Press Enter to exit.");
                Console.ReadLine();
                return;
            }

            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("✅ Running as Administrator.");
            Console.ResetColor();

            string scriptPath = Path.Combine(AppContext.BaseDirectory, "Scripts", "Ensure-Hello.ps1");
            Console.WriteLine($"[DEBUG] Script path: {scriptPath}");

            if (!File.Exists(scriptPath))
            {
                Console.WriteLine($"Script not found: {scriptPath}");
                return;
            }

            // Run PowerShell script via hosted runspace
            try
            {
                var host = new PowerShellHost();
                await host.ExecuteScriptAsync(scriptPath);
                Console.WriteLine("\n✅ Script execution completed successfully.");
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"❌ Error during script execution: {ex.Message}");
                Console.ResetColor();
            }

            Console.WriteLine("\nPress Enter to close...");
            Console.ReadLine();
        }
    }
}
