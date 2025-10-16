public static class Log
{
    private static readonly string LogDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "DevKit\\Logs");

    static Log() => Directory.CreateDirectory(LogDir);

    public static string FilePath => Path.Combine(LogDir, $"devkit_{DateTime.Now:yyyyMMdd_HHmmss}.log");

    public static void Write(string message)
    {
        var line = $"{DateTime.Now:HH:mm:ss} {message}";
        Console.WriteLine(line);
        File.AppendAllText(FilePath, line + Environment.NewLine);
    }
}
