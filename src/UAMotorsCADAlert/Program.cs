using UAMotorsCADAlert.Forms;
using UAMotorsCADAlert.Services;

namespace UAMotorsCADAlert;

static class Program
{
    [STAThread]
    static void Main()
    {
        ApplicationConfiguration.Initialize();

        InstallerService.CheckSingleInstance();
        InstallerService.AutoInstalar();

        string? rutaActiva = MonitorService.BuscarCarpetaUamotors();
        
        if (!string.IsNullOrEmpty(rutaActiva))
        {
            var profile = UserService.LoadLocalProfile();
            if (profile == null)
            {
                var form = new RegistrationForm(rutaActiva);
                Application.Run(form);

                if (!form.IsRegistered)
                {
                    Environment.Exit(0);
                }
                
                // Reload profile after registration
                profile = UserService.LoadLocalProfile();
            }

            DiscordService.SendMessage($"⚙️ Monitoreo de CAD activo para: **{profile?.Name ?? "Usuario"}**");
            
            // This instance keeps a reference to the FileSystemWatcher so it doesn't get garbage collected
            var monitor = new MonitorService(rutaActiva);

            // Keep the application running in the background without a main window
            Application.Run();
        }
        else
        {
            MessageBox.Show("No se encontró la carpeta 'UAMOTORS' o no contiene archivos de ensamble. Asegúrate de tener Google Drive instalado y sincronizado.", 
                "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}
