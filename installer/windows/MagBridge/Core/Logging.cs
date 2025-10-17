using System;
using System.Drawing;
using System.IO;
using System.Windows.Forms;

namespace MagBridge.Core
{
    public static class Log
    {
        private static readonly string LogDir =
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "MagBridge", "Logs");

        static Log() => Directory.CreateDirectory(LogDir);

        private static readonly string FilePath =
            Path.Combine(LogDir, $"devkit_{DateTime.Now:yyyyMMdd_HHmmss}.log");

        public static void Write(string message, TextBoxBase? targetBox = null)
        {
            string timestamp = $"[{DateTime.Now:HH:mm:ss}]";
            string line = $"{timestamp} {message}";
            string upper = message.ToUpperInvariant();

            // Determine color by severity
            Color uiColor;
            ConsoleColor consoleColor;

            if (upper.Contains("[ERR]") || upper.Contains("[ERROR]"))
            {
                uiColor = Color.FromArgb(220, 76, 70);
                consoleColor = ConsoleColor.Red;
            }
            else if (upper.Contains("[WARN]"))
            {
                uiColor = Color.Goldenrod;
                consoleColor = ConsoleColor.Yellow;
            }
            else if (upper.Contains("[OK]") || upper.Contains("[SUCCESS]"))
            {
                uiColor = Color.LimeGreen;
                consoleColor = ConsoleColor.Green;
            }
            else
            {
                uiColor = Color.LightGray;
                consoleColor = ConsoleColor.Gray;
            }

            // --- Console output ---
            var old = Console.ForegroundColor;
            Console.ForegroundColor = consoleColor;
            Console.WriteLine(line);
            Console.ForegroundColor = old;

            // --- UI output ---
            if (targetBox is { IsHandleCreated: true })
            {
                targetBox.BeginInvoke((Action)(() =>
                {
                    if (targetBox is RichTextBox rich)
                    {
                        int start = rich.TextLength;
                        rich.SelectionStart = start;
                        rich.SelectionColor = uiColor;
                        rich.AppendText(line + Environment.NewLine);
                        rich.SelectionColor = rich.ForeColor;
                        rich.ScrollToCaret();
                    }
                    else
                    {
                        // fallback for ThemedTextBox / TextBox
                        targetBox.AppendText(line + Environment.NewLine);
                    }
                }));
            }

            // --- File output ---
            File.AppendAllText(FilePath, line + Environment.NewLine);
        }
    }
}
