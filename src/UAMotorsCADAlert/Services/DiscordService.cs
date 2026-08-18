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
                    // Validacion basica para no ciclarse infinitamente si el usuario pegó mal la URL
                    if (Uri.TryCreate(wh, UriKind.Absolute, out Uri? uriResult) && 
                        (uriResult.Scheme == Uri.UriSchemeHttp || uriResult.Scheme == Uri.UriSchemeHttps))
                    {
                        url = wh;
                        break;
                    }
                    else
                    {
                        // Si la URL esta mal escrita, descartamos el mensaje para no trabar la cola
                        url = "";
                        break;
                    }
                }
                else
                {
                    await Task.Delay(10000); // Reintento de lectura de configuracion
                }
            }

            if (string.IsNullOrEmpty(url)) continue; // Se descarta el mensaje por URL invalida

            while (true)
            {
                try
                {
                    // StringContent debe instanciarse por cada intento, de lo contrario lanza InvalidOperationException al reintentar
                    using var content = new StringContent(json, Encoding.UTF8, "application/json");
                    var response = await _httpClient.PostAsync(url, content);
                    
                    if (response.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
                    {
                        await Task.Delay(5000);
                        continue;
                    }
                    break; // Exito
                }
                catch (HttpRequestException)
                {
                    await Task.Delay(15000); // Reintento solo en fallos de red
                }
                catch
                {
                    break; // Otros errores (ej. URL malformada no detectada), se descarta para no trabar
                }
            }
        }
    }
}
