using System;
using System.Diagnostics;
using System.Security.Principal;

namespace MagBridge
{
    public static class Utilities
    {
        public static bool IsRunningAsAdministrator()
        {
            using var identity = WindowsIdentity.GetCurrent();
            var principal = new WindowsPrincipal(identity);
            return principal.IsInRole(WindowsBuiltInRole.Administrator);
        }

        public static bool RelaunchAsAdministrator()
        {
            try
            {
                var exeName = Process.GetCurrentProcess().MainModule?.FileName;
                if (string.IsNullOrEmpty(exeName))
                    return false;

                var psi = new ProcessStartInfo
                {
                    FileName = exeName,
                    UseShellExecute = true,
                    Verb = "runas"
                };

                Process.Start(psi);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to relaunch as admin: {ex.Message}");
                return false;
            }
        }
    }
}
