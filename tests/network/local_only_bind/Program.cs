using System.Net;
using System.Net.Sockets;
using MUnique.OpenMU.Network;

// Focused real helper/socket checks, not an OpenMU integration or persistence test.
var variable = LocalOnlyBinding.EnvironmentVariableName;
var previous = Environment.GetEnvironmentVariable(variable);
try
{
    foreach (var legacy in new string?[] { null, "0" })
    {
        Environment.SetEnvironmentVariable(variable, legacy);
        Require(LocalOnlyBinding.GetAddress().Equals(IPAddress.Any), "Legacy address changed.");
        // Do not start a wildcard socket even in the test.
    }

    foreach (var invalid in new[] { "true", "false", "yes", "2", " 1", "1 ", "127.0.0.1" })
    {
        Environment.SetEnvironmentVariable(variable, invalid);
        try
        {
            LocalOnlyBinding.GetAddress();
            throw new Exception("Invalid option silently accepted.");
        }
        catch (InvalidOperationException)
        {
            // Expected before any socket construction.
        }
    }

    Environment.SetEnvironmentVariable(variable, "1");
    var address = LocalOnlyBinding.GetAddress();
    Require(address.Equals(IPAddress.Loopback), "Opt-in is not IPv4 loopback.");
    var listener = new TcpListener(address, 0);
    try
    {
        var connectionTimeout = TimeSpan.FromSeconds(5);
        listener.Start();
        var endpoint = (IPEndPoint)listener.LocalEndpoint;
        Require(endpoint.Address.Equals(IPAddress.Loopback), "Actual socket is not loopback.");
        using var client = new TcpClient(AddressFamily.InterNetwork);
        await client.ConnectAsync(endpoint.Address, endpoint.Port).WaitAsync(connectionTimeout);
        using var accepted = await listener.AcceptTcpClientAsync().WaitAsync(connectionTimeout);
        Require(accepted.Connected, "Loopback connection failed.");
    }
    finally
    {
        listener.Stop();
    }

    Console.WriteLine("PASS: legacy selection, invalid options, loopback selection/socket/connect.");
}
finally
{
    Environment.SetEnvironmentVariable(variable, previous);
}

static void Require(bool condition, string message)
{
    if (!condition)
    {
        throw new Exception(message);
    }
}
