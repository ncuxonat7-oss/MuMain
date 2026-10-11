// Bounded, in-memory observations only. Raw output is drained and never retained.
using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;

public sealed class MuConsoleObserver
{
    private const int MaximumLine = 8192;
    private readonly string expectedPid;
    public volatile bool PidSeen;
    public volatile bool ErrorSeen;
    public Task OutputTask { get; }
    public Task ErrorTask { get; }

    public MuConsoleObserver(Process process)
    {
        expectedPid = "PID: " + process.Id;
        OutputTask = Drain(process.StandardOutput);
        ErrorTask = Drain(process.StandardError);
    }

    private async Task Drain(StreamReader reader)
    {
        char[] buffer = new char[2048];
        StringBuilder line = new StringBuilder();
        bool truncated = false;
        int count;
        while ((count = await reader.ReadAsync(buffer, 0, buffer.Length).ConfigureAwait(false)) != 0)
        {
            for (int i = 0; i < count; i++)
            {
                if (buffer[i] == '\n')
                {
                    Inspect(line.ToString(), truncated);
                    line.Clear();
                    truncated = false;
                }
                else if (line.Length < MaximumLine) { line.Append(buffer[i]); }
                else { truncated = true; }
            }
        }
        if (line.Length != 0) { Inspect(line.ToString(), truncated); }
    }

    private void Inspect(string line, bool truncated)
    {
        if (!truncated && line.Trim() == expectedPid) { PidSeen = true; }
        if (truncated || line.IndexOf("[ERR", StringComparison.OrdinalIgnoreCase) >= 0 ||
            line.IndexOf("[FTL", StringComparison.OrdinalIgnoreCase) >= 0 ||
            line.IndexOf("exception", StringComparison.OrdinalIgnoreCase) >= 0 ||
            line.IndexOf("error", StringComparison.OrdinalIgnoreCase) >= 0 ||
            line.IndexOf("fatal", StringComparison.OrdinalIgnoreCase) >= 0)
        { ErrorSeen = true; }
    }
}
