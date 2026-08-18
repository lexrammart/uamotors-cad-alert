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

            while (true)
            {
                string url = "";
                
                // 1. Obtener la URL más reciente de la DB cada vez que intentamos (o reintentamos)
                if (!string.IsNullOrEmpty(Config.ResolvedDrivePath))
                {
                    var db = UserService.LoadDriveDatabase(Config.ResolvedDrivePath);
                    if (db != null && db.Config.TryGetValue("webhook_url", out var wh) && !string.IsNullOrEmpty(wh))
                    {
                        if (Uri.TryCreate(wh, UriKind.Absolute, out Uri? uriResult) && 
                            (uriResult.Scheme == Uri.UriSchemeHttp || uriResult.Scheme == Uri.UriSchemeHttps))
                        {
                            url = wh;
                        }
                    }
                }

                // 2. Si no hay URL configurada, pausamos y volvemos a leer la DB después
                if (string.IsNullOrEmpty(url))
                {
                    await Task.Delay(10000);
                    continue; 
                }

                // 3. Intentar enviar
                try
                {
                    using var content = new StringContent(json, Encoding.UTF8, "application/json");
                    var response = await _httpClient.PostAsync(url, content);
                    
                    if (response.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
                    {
                        await Task.Delay(5000);
                        continue;
                    }
                    break; // Exito, salimos del ciclo de reintentos y pasamos al siguiente mensaje
                }
                catch (HttpRequestException)
                {
                    // Fallo de red, esperamos 15s y volvemos a empezar el ciclo (lo cual volverá a leer la DB)
                    await Task.Delay(15000); 
                }
                catch
                {
                    // Otros errores graves (ej. URL rota no detectada), descartamos el mensaje para no trabar la cola
                    break; 
                }
            }
        }
    }
}
