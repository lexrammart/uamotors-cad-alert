using System.Diagnostics;
using System.Reflection;

namespace UAMotorsCADAlert.Services;

public static class InstallerService
{
    private static Mutex? _instanceMutex;

    public static void CheckSingleInstance()
    {
        _instanceMutex = new Mutex(true, "UAMotorsCADAlert_SingleInstance_Mutex", out bool createdNew);
        if (!createdNew)
        {
            Environment.Exit(0);
        }
    }

    public static void AutoInstalar()
    {
        if (Config.Debug) return;

        string actualPath = Environment.ProcessPath ?? Assembly.GetExecutingAssembly().Location;
        string exeName = Path.GetFileName(actualPath);
        string installFolder = Config.GetAppDataDir();
        string targetPath = Path.Combine(installFolder, exeName);

        if (!actualPath.Equals(targetPath, StringComparison.OrdinalIgnoreCase))
        {
            CleanupOldPythonVersion();
            KillPreviousInstance(exeName);

            try
            {
                File.Copy(actualPath, targetPath, true);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error al instalar: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                Environment.Exit(1);
            }

            CreateScheduledTask(targetPath);
            CreateStartMenuShortcut(targetPath, exeName);

            MessageBox.Show("¡Instalación completada!\nLas alertas de SolidWorks quedaron activadas y se iniciarán con el sistema.", "UAMOTORS CAD", MessageBoxButtons.OK, MessageBoxIcon.Information);
            
            Process.Start(new ProcessStartInfo
            {
                FileName = targetPath,
                WorkingDirectory = installFolder
            });
            Environment.Exit(0);
        }
    }

    private static void KillPreviousInstance(string exeName)
    {
        try
        {
            int currentId = Process.GetCurrentProcess().Id;
            var processes = Process.GetProcessesByName(Path.GetFileNameWithoutExtension(exeName));
            foreach (var p in processes)
            {
                if (p.Id != currentId)
                {
                    p.Kill();
                    p.WaitForExit();
                }
            }
        }
        catch { }
    }

    private static void CleanupOldPythonVersion()
    {
        try
        {
            // 1. Matar el proceso compilado de la versión anterior en Python
            foreach (var p in Process.GetProcessesByName("uamotors_cad_alert"))
            {
                p.Kill();
                p.WaitForExit(2000);
            }

            // 2. Limpiar la carpeta de inicio (Startup) de accesos directos o scripts .bat viejos
            string startupFolder = Environment.GetFolderPath(Environment.SpecialFolder.Startup);
            foreach (var file in Directory.GetFiles(startupFolder))
            {
                string name = Path.GetFileName(file).ToLower();
                if (name.Contains("uamotors") || name.Contains("cad_alert"))
                {
                    File.Delete(file);
                }
            }

            // 3. Limpiar el registro de Windows (por si la versión vieja se ancló ahí)
            using var key = Microsoft.Win32.Registry.CurrentUser.OpenSubKey(@"Software\Microsoft\Windows\CurrentVersion\Run", true);
            if (key != null)
            {
                if (key.GetValue("UAMotorsCADAlert") != null) key.DeleteValue("UAMotorsCADAlert", false);
                if (key.GetValue("uamotors_cad_alert") != null) key.DeleteValue("uamotors_cad_alert", false);
            }
        }
        catch { }
    }

    private static void CreateScheduledTask(string targetPath)
    {
        try
        {
            string taskName = "UAMotorsCADAlertTask";
            string args = $"/Create /TN \"{taskName}\" /TR \"\\\"{targetPath}\\\"\" /SC ONLOGON /F";
            Process.Start(new ProcessStartInfo
            {
                FileName = "schtasks.exe",
                Arguments = args,
                CreateNoWindow = true,
                WindowStyle = ProcessWindowStyle.Hidden
            })?.WaitForExit();
        }
        catch { }
    }

    private static void CreateStartMenuShortcut(string targetPath, string exeName)
    {
        try
        {
            string startMenu = Environment.GetFolderPath(Environment.SpecialFolder.StartMenu);
            string programsFolder = Path.Combine(startMenu, "Programs");
            string shortcutPath = Path.Combine(programsFolder, Path.GetFileNameWithoutExtension(exeName) + ".lnk");

            string psCmd = $"$s=(New-Object -COM WScript.Shell).CreateShortcut('{shortcutPath}');$s.TargetPath='{targetPath}';$s.Save()";
            Process.Start(new ProcessStartInfo
            {
                FileName = "powershell",
                Arguments = $"-Command \"{psCmd}\"",
                CreateNoWindow = true,
                WindowStyle = ProcessWindowStyle.Hidden
            })?.WaitForExit();
        }
        catch { }
    }
}
