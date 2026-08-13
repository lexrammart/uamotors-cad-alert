using System.Text.RegularExpressions;

namespace UAMotorsCADAlert.Services;

public class MonitorService
{
    private readonly FileSystemWatcher _watcher;
    private readonly HashSet<string> _activeLockPaths = new();
    private readonly string _userDisplay;

    public MonitorService(string rutaActiva)
    {
        var profile = UserService.LoadLocalProfile();
        _userDisplay = profile != null ? $"{profile.Name} ({profile.Email})" : "Usuario Desconocido";

        _watcher = new FileSystemWatcher(rutaActiva)
        {
            IncludeSubdirectories = true,
            EnableRaisingEvents = true
        };

        _watcher.Created += OnCreated;
        _watcher.Deleted += OnDeleted;
    }

    public static string? BuscarCarpetaUamotors()
    {
        string userHome = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        string[] driveNames = { "Google Drive", "Drive", "GoogleDrive" };

        foreach (var name in driveNames)
        {
            string path = Path.Combine(userHome, name, Config.TargetFolder);
            if (Directory.Exists(path) && VerificarEnsamble(path))
                return path;
        }

        foreach (var drive in DriveInfo.GetDrives().Where(d => d.IsReady && d.DriveType == DriveType.Fixed))
        {
            try
            {
                var dirs = Directory.GetDirectories(drive.RootDirectory.FullName);
                foreach (var d in dirs)
                {
                    if (Path.GetFileName(d).Equals(Config.TargetFolder, StringComparison.OrdinalIgnoreCase))
                    {
                        if (VerificarEnsamble(d)) return d;
                    }
                }
            }
            catch { }
        }

        return null;
    }

    private static bool VerificarEnsamble(string ruta)
    {
        try
        {
            foreach (var file in Directory.EnumerateFiles(ruta, "*", SearchOption.AllDirectories))
            {
                if (Regex.IsMatch(Path.GetFileName(file), Config.AssemblyPattern, RegexOptions.IgnoreCase))
                    return true;
            }
        }
        catch { }
        return false;
    }

    private static bool EsBloqueoRealSW(string filepath)
    {
        try
        {
            using var fs = new FileStream(filepath, FileMode.Append, FileAccess.Write, FileShare.None);
            return false;
        }
        catch (IOException)
        {
            return true;
        }
        catch (UnauthorizedAccessException)
        {
            return true;
        }
        catch
        {
            return false;
        }
    }

    private void OnCreated(object sender, FileSystemEventArgs e)
    {
        string filename = Path.GetFileName(e.FullPath);
        if (Regex.IsMatch(filename, Config.LockPattern, RegexOptions.IgnoreCase))
        {
            if (!EsBloqueoRealSW(e.FullPath))
                return;

            lock (_activeLockPaths)
            {
                _activeLockPaths.Add(e.FullPath);
            }
            string realName = filename.Substring(2);
            DiscordService.SendMessage($"🔴 **[OCUPADO]:** Ensamble en uso (`{realName}`) por **{_userDisplay}**");
        }
    }

    private void OnDeleted(object sender, FileSystemEventArgs e)
    {
        string filename = Path.GetFileName(e.FullPath);
        if (Regex.IsMatch(filename, Config.LockPattern, RegexOptions.IgnoreCase))
        {
            bool removed;
            lock (_activeLockPaths)
            {
                removed = _activeLockPaths.Remove(e.FullPath);
            }

            if (removed)
            {
                string realName = filename.Substring(2);
                DiscordService.SendMessage($"🟢 **[LIBRE]:** Ensamble disponible (`{realName}`) - Liberado por **{_userDisplay}**");
            }
        }
    }
}
