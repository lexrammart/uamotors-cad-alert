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

            string url = Config.GetWebhookUrl();

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
                    await Task.Delay(15000); // Retry after 15s on network error
                }
            }
        }
    }
}
