using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text;

namespace UAMotorsCADAlert.Services;

public class UserProfile
{
    [JsonPropertyName("email")]
    public string Email { get; set; } = string.Empty;
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
}

public class WhitelistEntry
{
    [JsonPropertyName("nombre")]
    public string Nombre { get; set; } = string.Empty;
}

public static class UserService
{
    public static string GetProfileFilePath() => Path.Combine(Config.GetAppDataDir(), "user_profile.uamotors");

    public static UserProfile? LoadLocalProfile()
    {
        string path = GetProfileFilePath();
        if (!File.Exists(path)) return null;

        try
        {
            byte[] encodedBytes = File.ReadAllBytes(path);
            string b64Str = Encoding.UTF8.GetString(encodedBytes);
            string decodedJson = Encoding.UTF8.GetString(Convert.FromBase64String(b64Str));
            return JsonSerializer.Deserialize<UserProfile>(decodedJson);
        }
        catch
        {
            return null;
        }
    }

    public static UserProfile SaveLocalProfile(string email, string name)
    {
        var profile = new UserProfile { Email = email.Trim().ToLower(), Name = name.Trim() };
        string jsonStr = JsonSerializer.Serialize(profile);
        string b64Str = Convert.ToBase64String(Encoding.UTF8.GetBytes(jsonStr));
        File.WriteAllText(GetProfileFilePath(), b64Str);
        return profile;
    }

    private static Dictionary<string, WhitelistEntry>? LoadDriveWhitelist(string rutaUamotors)
    {
        string dbPath = Path.Combine(rutaUamotors, Config.RelDriveDbPath);
        if (!File.Exists(dbPath)) return null;

        try
        {
            byte[] encodedBytes = File.ReadAllBytes(dbPath);
            string b64Str = Encoding.UTF8.GetString(encodedBytes);
            string decodedJson = Encoding.UTF8.GetString(Convert.FromBase64String(b64Str));
            return JsonSerializer.Deserialize<Dictionary<string, WhitelistEntry>>(decodedJson);
        }
        catch
        {
            return null;
        }
    }

    public static (bool Success, string? Name, string ErrorMsg) VerifyUserEmail(string email, string rutaUamotors)
    {
        string emailClean = email.Trim().ToLower();
        if (string.IsNullOrEmpty(emailClean) || !emailClean.Contains("@"))
            return (false, null, "Por favor ingresa un correo electrónico válido.");

        var whitelist = LoadDriveWhitelist(rutaUamotors);
        if (whitelist == null)
            return (false, null, $"No se encontró la BD de usuarios en Drive.");

        if (whitelist.TryGetValue(emailClean, out var userEntry))
        {
            string name = !string.IsNullOrEmpty(userEntry.Nombre) ? userEntry.Nombre : "Usuario Autorizado";
            return (true, name, string.Empty);
        }

        return (false, null, "El correo no está registrado en la lista de usuarios autorizados de UAMOTORS.");
    }
}
