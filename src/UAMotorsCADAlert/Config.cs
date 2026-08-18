namespace UAMotorsCADAlert;

public static class Config
{
    public static bool Debug = false;

    public const string TargetFolder = "UAMOTORS";
    public const string BaseName = "OP-01assembly / GENERAL ASSEMBLY E";

    public const string AssemblyPattern = @"^(OP-01assembly\d*|GENERAL ASSEMBLY E)\.SLDASM$";
    public const string LockPattern = @"^~\$(OP-01assembly\d*|GENERAL ASSEMBLY E)\.SLDASM$";

    public const string InstallFolderName = "UAMOTORSCADALERT";

    public static readonly string RelDriveDbPath = Path.Combine("2026", "Design", "Electronics", "CAD-Alert", "authorized_users.uamotors");

    public static string ResolvedDrivePath { get; set; } = string.Empty;

    public static string GetAppDataDir()
    {
        string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        string path = Path.Combine(localAppData, InstallFolderName);
        Directory.CreateDirectory(path);
        return path;
    }
}
