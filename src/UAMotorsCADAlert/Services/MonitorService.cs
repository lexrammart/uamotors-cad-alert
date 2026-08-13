using System.Text.RegularExpressions;
using System.Diagnostics;

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

        Task.Factory.StartNew(GhostLockWatcher, TaskCreationOptions.LongRunning);
    }

    private async Task GhostLockWatcher()
    {
        while (true)
        {
            await Task.Delay(5000);
            if (!SldworksEstaAbierto())
            {
                List<string> paths;
                lock (_activeLockPaths)
                {
                    paths = _activeLockPaths.ToList();
                }
                foreach (var path in paths)
                {
                    if (File.Exists(path))
                    {
                        try { File.Delete(path); } catch { }
                    }
                }
            }
        }
    }

    public static bool SldworksEstaAbierto()
    {
        try
        {
            return Process.GetProcessesByName("SLDWORKS").Length > 0;
        }
        catch
        {
            return true;
        }
    }

    public static string? BuscarCarpetaUamotors()
    {
        string target = Config.TargetFolder;
        
        string userHome = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        string[] driveNames = { "Google Drive", "Drive", "GoogleDrive" };

        foreach (var name in driveNames)
        {
            string path = Path.Combine(userHome, name, target);
            if (Directory.Exists(path) && VerificarEnsamble(path))
                return path;
        }

        foreach (var drive in DriveInfo.GetDrives().Where(d => d.IsReady))
        {
            // Ignoramos C: por rendimiento, asumiendo que Drive crea un disco virtual (G:, H:, etc)
            if (drive.Name.StartsWith("C", StringComparison.OrdinalIgnoreCase)) continue;

            try
            {
                string? candidate = FindFolderDeep(drive.RootDirectory, target, 0, 2);
                if (candidate != null) return candidate;
            }
            catch { }
        }

        return null;
    }

    private static string? FindFolderDeep(DirectoryInfo dir, string target, int currentDepth, int maxDepth)
    {
        if (currentDepth > maxDepth) return null;

        try
        {
            foreach (var d in dir.GetDirectories())
            {
                if (d.Name.Equals(target, StringComparison.OrdinalIgnoreCase))
                {
                    if (VerificarEnsamble(d.FullName)) return d.FullName;
                }
            }

            foreach (var d in dir.GetDirectories())
            {
                string? found = FindFolderDeep(d, target, currentDepth + 1, maxDepth);
                if (found != null) return found;
            }
        }
        catch { }
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
