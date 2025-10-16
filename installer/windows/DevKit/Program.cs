internal static class Program
{
    [STAThread]
    static void Main()
    {
        AllocConsole();  // opens console if started from Explorer
        ApplicationConfiguration.Initialize();

        Console.WriteLine("=== DevKit Installer ===");
        Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Starting...");

        Application.Run(new ProgressForm());

        Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Completed.");
        Console.ReadKey(true);
    }

    [System.Runtime.InteropServices.DllImport("kernel32.dll")]
    private static extern bool AllocConsole();

}
