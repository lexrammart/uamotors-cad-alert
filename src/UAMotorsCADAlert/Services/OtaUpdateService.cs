using System.Diagnostics;
using System.Reflection;
using System.Text.Json;

namespace UAMotorsCADAlert.Services;

public static class OtaUpdateService
{
    private const string RepoUrl = "https://api.github.com/repos/lexrammart/uamotors-cad-alert/releases/latest";
    private static readonly HttpClient _httpClient;

    static OtaUpdateService()
    {
        _httpClient = new HttpClient();
        _httpClient.DefaultRequestHeaders.Add("User-Agent", "UAMotorsCADAlert-Updater");
    }

    public static string GetCurrentVersion()
    {
        try
        {
            var assembly = Assembly.GetExecutingAssembly();
            using var stream = assembly.GetManifestResourceStream("UAMotorsCADAlert.version.txt");
            if (stream != null)
            {
                using var reader = new StreamReader(stream);
                return reader.ReadToEnd().Trim();
            }
        }
        catch { }
        return "v2.0"; // fallback
    }

    public static async Task CheckForUpdatesAsync(Action<string>? onUpdateFound = null)
    {
        // En entorno de desarrollo (Rider) no intentamos actualizar para evitar crasheos
        if (Config.Debug || Debugger.IsAttached || AppDomain.CurrentDomain.BaseDirectory.Contains("bin\\Debug", StringComparison.OrdinalIgnoreCase))
        {
            return;
        }

        try
        {
            var response = await _httpClient.GetAsync(RepoUrl);
            if (!response.IsSuccessStatusCode) return;

            string json = await response.Content.ReadAsStringAsync();
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            if (root.TryGetProperty("tag_name", out var tagElement))
            {
                string latestVersion = tagElement.GetString() ?? "";
                string currentVersion = GetCurrentVersion();

                if (IsNewerVersion(currentVersion, latestVersion))
                {
                    // Buscar el asset .exe
                    if (root.TryGetProperty("assets", out var assets) && assets.GetArrayLength() > 0)
                    {
                        foreach (var asset in assets.EnumerateArray())
                        {
                            if (asset.TryGetProperty("name", out var nameElement) && 
                                nameElement.GetString()?.EndsWith(".exe", StringComparison.OrdinalIgnoreCase) == true)
                            {
                                if (asset.TryGetProperty("browser_download_url", out var downloadUrlElement))
                                {
                                    string downloadUrl = downloadUrlElement.GetString() ?? "";
                                    onUpdateFound?.Invoke($"Descargando actualización a {latestVersion}...");
                                    await DownloadAndApplyUpdate(downloadUrl);
                                    break;
                                }
                            }
                        }
                    }
                }
            }
        }
        catch { }
    }

    private static bool IsNewerVersion(string current, string latest)
    {
        // current: "v2.0", latest: "v2.1.0"
        current = current.ToLower().Replace("v", "").Trim();
        latest = latest.ToLower().Replace("v", "").Trim();

        if (Version.TryParse(current, out var currentVer) && Version.TryParse(latest, out var latestVer))
        {
            return latestVer > currentVer;
        }
        
        // Si no es parseable (ej. faltan minor/build), comparamos los strings asumiendo que el usuario incrementa correctamente
        return string.Compare(latest, current, StringComparison.Ordinal) > 0;
    }

    private static async Task DownloadAndApplyUpdate(string downloadUrl)
    {
        try
        {
            var updateData = await _httpClient.GetByteArrayAsync(downloadUrl);
            
            // Guardar en una carpeta temporal con el mismo nombre exacto para que el instalador lo reconozca
            string tempDir = Path.Combine(Path.GetTempPath(), "UAMotorsUpdate");
            Directory.CreateDirectory(tempDir);
            
            string actualExeName = Path.GetFileName(Environment.ProcessPath ?? Assembly.GetExecutingAssembly().Location);
            string tempExePath = Path.Combine(tempDir, actualExeName);

            File.WriteAllBytes(tempExePath, updateData);

            // Iniciar el instalador desde la carpeta temporal
            Process.Start(new ProcessStartInfo
            {
                FileName = tempExePath,
                WorkingDirectory = tempDir,
                UseShellExecute = true
            });

            // Cerrar la instancia actual para que el nuevo .exe la sobrescriba
            Environment.Exit(0);
        }
        catch { }
    }

    public static void StartBackgroundUpdateChecker(Action<string>? onUpdateFound)
    {
        Task.Run(async () =>
        {
            while (true)
            {
                await CheckForUpdatesAsync(onUpdateFound);
                await Task.Delay(TimeSpan.FromHours(4)); // Revisa cada 4 horas
            }
        });
    }
}
