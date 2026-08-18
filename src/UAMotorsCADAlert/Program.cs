using UAMotorsCADAlert.Forms;
using UAMotorsCADAlert.Services;

namespace UAMotorsCADAlert;

static class Program
{
    private static MonitorService? _monitorInstance;

    [STAThread]
    static void Main()
    {
        ApplicationConfiguration.Initialize();
        
        InstallerService.CheckSingleInstance();

        // Instalacion de la aplicacion en entorno de produccion
        InstallerService.AutoInstalar();

        var profile = UserService.LoadLocalProfile();
        
        // Iniciar el contexto de aplicación del System Tray (icono junto al reloj)
        var trayContext = new TrayApplicationContext(profile);
        Application.Run(trayContext);
    }
}
