using System.Reflection;

namespace UAMotorsCADAlert;

public class TrayApplicationContext : ApplicationContext
{
    private readonly NotifyIcon _trayIcon;

    public TrayApplicationContext(string userDisplay)
    {
        _trayIcon = new NotifyIcon()
        {
            Icon = LoadIcon(),
            ContextMenuStrip = new ContextMenuStrip(),
            Visible = true,
            Text = $"UAMOTORS CAD Alert\nUsuario: {userDisplay}"
        };

        var exitItem = new ToolStripMenuItem("Cerrar UAMOTORS CAD Alert", null, Exit);
        _trayIcon.ContextMenuStrip.Items.Add(exitItem);
    }

    private Icon LoadIcon()
    {
        try
        {
            var assembly = Assembly.GetExecutingAssembly();
            using var stream = assembly.GetManifestResourceStream("UAMotorsCADAlert.Resources.cad_alert_icon.ico");
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
