namespace UAMotorsCADAlert;

public static class Config
{
    public const string WebhookUrl = "https://discord.com/api/webhooks/1533988281195171962/nv3cJEvWrUhcEPDo1zH5zjcABusHsdbl65PCaYNPJwpXtLg6gPWTp1DcxH7OOVyEI5nM";
    public const string DevWebhookUrl = "https://discord.com/api/webhooks/1537230363766689914/Jij7QPz07-IfrmHdgDhEB762T2BsguRg0_73hr1QakDtPCcObrof--Gbk3rDt5_WVjBy";
    
    public const bool Debug = true;
    
    public const string TargetFolder = "UAMOTORS";
    public const string BaseName = "OP-01assembly";
    
    public const string AssemblyPattern = @"^OP-01assembly\d*\.SLDASM$";
    public const string LockPattern = @"^~\$OP-01assembly\d*\.SLDASM$";
    
    public const string InstallFolderName = "UAMotorsCAD";
    
    public static readonly string RelDriveDbPath = Path.Combine("2026", "Design", "Electronics", "Data-Code telemetry", "auamotors_cad_alert", "authorized_users.uamotors");
    
    public static string GetWebhookUrl() => Debug ? DevWebhookUrl : WebhookUrl;
    
    public static string GetAppDataDir()
    {
        string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        string path = Path.Combine(localAppData, InstallFolderName);
        Directory.CreateDirectory(path);
        return path;
    }
}
