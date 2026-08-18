using System.Text.Json;
using System.Text;
using System.Collections.Concurrent;

namespace UAMotorsCADAlert.Services;

public static class DiscordService
{
    private static readonly BlockingCollection<string> _messageQueue = new();
    private static readonly HttpClient _httpClient = new();

    static DiscordService()
    {
        Task.Factory.StartNew(WorkerLoop, TaskCreationOptions.LongRunning);
    }

    public static void SendMessage(string message)
    {
        _messageQueue.Add(message);
    }

    private static async Task WorkerLoop()
    {
        foreach (var message in _messageQueue.GetConsumingEnumerable())
        {
            var payload = new { content = message };
            string json = JsonSerializer.Serialize(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            string url = "";
            while (true)
            {
                if (string.IsNullOrEmpty(Config.ResolvedDrivePath))
                {
                    await Task.Delay(5000);
                    continue;
                }

                var db = UserService.LoadDriveDatabase(Config.ResolvedDrivePath);
                if (db != null && db.Config.TryGetValue("webhook_url", out var wh) && !string.IsNullOrEmpty(wh))
                {
                    url = wh;
                    break;
                }
                else
                {
                    await Task.Delay(10000); // Reintento de lectura de configuracion
                }
            }

            while (true)
            {
                try
                {
                    var response = await _httpClient.PostAsync(url, content);
                    if (response.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
                    {
                        await Task.Delay(5000);
                        continue;
                    }
                    break;
                }
                catch
                {
                    await Task.Delay(15000); // Reintento de conexion
                }
            }
        }
    }
}
