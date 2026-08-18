using System.Reflection;
using UAMotorsCADAlert.Services;

namespace UAMotorsCADAlert;

public class TrayApplicationContext : ApplicationContext
{
    private readonly NotifyIcon _trayIcon;

    private MonitorService? _monitorInstance;
    private UserProfile? _profile;
    private string _currentVersion;

    public TrayApplicationContext(UserProfile? profile)
    {
        _profile = profile;
        _currentVersion = Services.OtaUpdateService.GetCurrentVersion();
        
        _trayIcon = new NotifyIcon()
        {
            Icon = LoadIcon(),
            ContextMenuStrip = new ContextMenuStrip(),
            Visible = true,
            Text = GetTrayText(false)
        };

        var exitItem = new ToolStripMenuItem("Cerrar UAMOTORS CAD ALERT", null, Exit);
        _trayIcon.ContextMenuStrip.Items.Add(exitItem);

        Services.OtaUpdateService.StartBackgroundUpdateChecker(msg => 
        {
            _trayIcon.ShowBalloonTip(3000, "Actualización Automática", msg, ToolTipIcon.Info);
        });

        // Iniciar el watcher asíncrono sin bloquear el hilo principal
        Task.Run(() => StartDriveConnectionWatcher());
    }

    private string GetTrayText(bool isConnected)
    {
        string username = _profile?.Name ?? "USUARIO";
        string text;
        
        if (isConnected)
        {
            text = $"UAMOTORS CAD ALERT ({_currentVersion})\nUSUARIO: {username}";
        }
        else
        {
            // Cortar por la primera palabra
            string[] parts = username.Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
            string firstName = parts.Length > 0 ? parts[0] : "USUARIO";
            
            // Limitar a máximo 12 caracteres
            if (firstName.Length > 12)
            {
                firstName = firstName.Substring(0, 12);
            }
            
            // Agregar "..." si el nombre original era más largo (tenía más palabras o excedía 12 caracteres)
            // o simplemente agregarlo como solicitaste para indicar acortamiento visual.
            bool needsDots = parts.Length > 1 || username.Length > 12;
            string displayName = needsDots ? $"{firstName}..." : firstName;

            text = $"UAMOTORS CAD ALERT {_currentVersion}\nUSR: {displayName}\nSin conexión Drive";
        }
        
        // Ensure text is not longer than 63 chars (Windows limit)
        if (text.Length >= 64) text = text.Substring(0, 63);
        return text;
    }

    private async Task StartDriveConnectionWatcher()
    {
        int elapsedSeconds = 0;
        bool errorShown = false;
        bool isConnected = false;

        while (true)
        {
            if (!isConnected)
            {
                string? rutaActiva = Services.MonitorService.BuscarCarpetaUAMOTORS();

                if (!string.IsNullOrEmpty(rutaActiva))
                {
                    // -- DRIVE ENCONTRADO --
                    Config.ResolvedDrivePath = rutaActiva;

                    if (_profile == null)
                    {
                        var form = new Forms.RegistrationForm(rutaActiva);
                        form.ShowDialog();

                        if (!form.IsRegistered)
                        {
                            Environment.Exit(0);
                        }

                        _profile = Services.UserService.LoadLocalProfile();
                        Services.DiscordService.SendMessage($"⚙️ Monitoreo de CAD activo para: `{_profile?.Name ?? "Usuario"}`");
                    }

                    // Iniciar el Monitor
                    _monitorInstance = new MonitorService(rutaActiva);
                    
                    // Actualizar UI
                    isConnected = true;
                    _trayIcon.Text = GetTrayText(true);

                    // Aviso de reconexión si hubo error previo
                    if (errorShown)
                    {
                        MessageBox.Show(
                            "Se encontró la conexión con Drive, monitoreo de CAD activo.",
                            "Reconexión Exitosa - UAMOTORS CAD ALERT",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Information,
                            MessageBoxDefaultButton.Button1,
                            MessageBoxOptions.ServiceNotification // Ensures it pops up from background
                        );
                    }
                }
                else
                {
                    // -- DRIVE NO ENCONTRADO --
                    elapsedSeconds += 5;
                    
                    if (elapsedSeconds >= 45 && !errorShown)
                    {
                        // Mostrar error una sola vez después de 45 segundos
                        errorShown = true;
                        MessageBox.Show(
                            "No se encontró la carpeta 'UAMOTORS' en tu Google Drive.\n\nPor favor revisa tu conexión a internet o asegúrate de tener Google Drive para escritorio iniciado y sincronizado.",
                            "Sin Conexión - UAMOTORS CAD ALERT",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Warning,
                            MessageBoxDefaultButton.Button1,
                            MessageBoxOptions.ServiceNotification
                        );
                    }

                    int delaySeconds = (elapsedSeconds >= 300) ? 15 : 5;
                    await Task.Delay(delaySeconds * 1000);
                }
            }
            else
            {
                // -- ESTAMOS CONECTADOS --
                // Monitorear pasivamente si la carpeta desaparece (Drive se cerró / perdió internet)
                await Task.Delay(15000); // Revisamos cada 15 seg
                
                if (!Directory.Exists(Config.ResolvedDrivePath))
                {
                    // ¡SE PERDIÓ LA CONEXIÓN!
                    isConnected = false;
                    elapsedSeconds = 0; // Reiniciar contador para volver a avisar si no vuelve pronto
                    errorShown = false; 
                    
                    _monitorInstance?.Stop();
                    _monitorInstance = null;
                    
                    _trayIcon.Text = GetTrayText(false);
                }
            }
        }
    }

    private Icon LoadIcon()
    {
        try
        {
            var assembly = Assembly.GetExecutingAssembly();
            using var stream = assembly.GetManifestResourceStream("UAMotorsCADAlert.Resources.cad_alert.ico");
            if (stream != null)
            {
                return new Icon(stream);
            }
        }
        catch { }
        return SystemIcons.Application;
    }

    private void Exit(object? sender, EventArgs e)
    {
        _trayIcon.Visible = false;
        _trayIcon.Dispose();
        Environment.Exit(0);
    }
}
