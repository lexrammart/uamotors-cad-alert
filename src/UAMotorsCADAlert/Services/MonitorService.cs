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
        _userDisplay = profile != null ? profile.Name : "Usuario Desconocido";

        _watcher = new FileSystemWatcher(rutaActiva)
        {
            IncludeSubdirectories = true,
            EnableRaisingEvents = true,
            NotifyFilter = NotifyFilters.FileName | NotifyFilters.DirectoryName | NotifyFilters.LastWrite | NotifyFilters.CreationTime | NotifyFilters.Attributes
        };

        _watcher.Created += OnCreated;
        _watcher.Changed += OnCreated;
        _watcher.Renamed += OnRenamed;
        _watcher.Deleted += OnDeleted;

        Task.Factory.StartNew(GhostLockWatcher, TaskCreationOptions.LongRunning);
    }

    private async Task GhostLockWatcher()
    {
        while (true)
        {
            await Task.Delay(5000); // Revisión periódica cada 5 segundos
            
            bool isSldworksClosed = !SldworksEstaAbierto();
            List<string> pathsToCheck;
            
            lock (_activeLockPaths)
            {
                pathsToCheck = _activeLockPaths.ToList();
            }

            foreach (var path in pathsToCheck)
            {
                // Liberar el estado SI Y SOLO SI:
                // 1. SolidWorks se cerró por completo (crasheo/cierre normal)
                // 2. El archivo ya no existe físicamente (el sistema operativo perdió el evento de borrado)
                // 3. El archivo existe pero ya no está bloqueado por el sistema
                if (isSldworksClosed || !File.Exists(path) || !EsBloqueoRealSw(path))
                {
                    bool removed;
                    lock (_activeLockPaths)
                    {
                        removed = _activeLockPaths.Remove(path);
                    }
                    
                    if (removed)
                    {
                        string filename = Path.GetFileName(path);
                        string realName = filename.Substring(2);
                        DiscordService.SendMessage($"🟢 **[LIBRE]:** Ensamble disponible (`{realName}`) - Liberado por `{_userDisplay}` (Cierre inesperado)");
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
            catch (Exception) { }
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
        catch (Exception) { }
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
        catch (Exception) { }
        return false;
    }

    private static bool EsBloqueoRealSw(string filepath)
    {
        // En modo dev aceptamos simulaciones.
        if (Config.Debug) 
            return true; 
            
        // 1. Si SolidWorks ni siquiera está abierto en esta compu, es 100% seguro que 
        // el archivo fue sincronizado por Google Drive desde la compu de alguien más.
        if (!SldworksEstaAbierto())
            return false;
            
        try
        {
            // 2. Ignorar archivos "fantasma" muy viejos que Google Drive pueda estar 
            // sincronizando o actualizando tardíamente. Si tiene más de 5 minutos de viejo, es un fantasma atascado.
            if (DateTime.Now - File.GetLastWriteTime(filepath) > TimeSpan.FromMinutes(5))
                return false;

            // 3. Leemos el contenido del archivo ~$ de SolidWorks.  
            // SolidWorks graba el nombre de usuario de Windows adentro del archivo.
            using var fs = new FileStream(filepath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
            using var reader = new BinaryReader(fs);
            byte[] bytes = reader.ReadBytes((int)fs.Length);
            
            string ascii = System.Text.Encoding.ASCII.GetString(bytes);
            string unicode = System.Text.Encoding.Unicode.GetString(bytes);
            string defaultEnc = System.Text.Encoding.Default.GetString(bytes);
            
            // Verificamos si nuestro nombre de usuario de Windows está dentro del archivo
            if (ascii.Contains(Environment.UserName, StringComparison.OrdinalIgnoreCase) || 
                unicode.Contains(Environment.UserName, StringComparison.OrdinalIgnoreCase) ||
                defaultEnc.Contains(Environment.UserName, StringComparison.OrdinalIgnoreCase))
            {
                return true; // ¡Nosotros somos los dueños del candado!
            }
            
            // Si el archivo se pudo leer y NO tiene nuestro nombre de usuario,
            // significa que alguien más lo bloqueó y Google Drive nos lo sincronizó.
            return false;
        }
        catch (IOException)
        {
            // Si lanza IOException, significa que un proceso local (SLDWORKS)
            // lo tiene bloqueado de forma estricta. Asumimos que es un bloqueo local válido.
            return true;
        }
        catch (Exception)
        {
            return false;
        }
    }

    private void OnRenamed(object sender, RenamedEventArgs e)
    {
        OnCreated(sender, e);
    }

    private void OnCreated(object sender, FileSystemEventArgs e)
    {
        string filename = Path.GetFileName(e.FullPath);
        if (Regex.IsMatch(filename, Config.LockPattern, RegexOptions.IgnoreCase))
        {
            // 1. Validar que sea un candado real y nuestro (usuario coincida y sea reciente)
            if (!EsBloqueoRealSw(e.FullPath))
                return;

            lock (_activeLockPaths)
            {
                if (!_activeLockPaths.Add(e.FullPath))
                    return; // Si ya estaba registrado, ignorar para no mandar 2 mensajes
            }
            string realName = filename.Substring(2);
            DiscordService.SendMessage($"🔴 **[OCUPADO]:** Ensamble en uso (`{realName}`) por `{_userDisplay}`");
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
                DiscordService.SendMessage($"🟢 **[LIBRE]:** Ensamble disponible (`{realName}`) - Liberado por `{_userDisplay}`");
            }
        }
    }
}
