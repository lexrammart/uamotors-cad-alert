namespace UAMotorsCADAlert.Forms;

using System.Reflection;
using UAMotorsCADAlert.Services;

public class RegistrationForm : Form
{
    private TextBox _emailInput = null!;
    private Button _verifyButton = null!;
    private Label _statusLabel = null!;
    private string _rutaUAMOTORS;
    public bool IsRegistered { get; private set; }

    public RegistrationForm(string rutaUAMOTORS)
    {
        _rutaUAMOTORS = rutaUAMOTORS;
        InitializeComponent();
    }

    private void InitializeComponent()
    {
        this.Text = "UAMOTORS CAD ALERT - Registro";
        this.FormBorderStyle = FormBorderStyle.FixedDialog;
        this.MaximizeBox = false;
        this.MinimizeBox = false;
        this.StartPosition = FormStartPosition.CenterScreen;
        this.BackColor = Color.FromArgb(248, 250, 252);
        this.AutoScaleMode = AutoScaleMode.Dpi;

        // Auto-dimensionamiento
        this.AutoSize = true;
        this.AutoSizeMode = AutoSizeMode.GrowAndShrink;
        this.MinimumSize = new Size(720, 0);

        // Panel principal
        var mainLayout = new TableLayoutPanel
        {
            Dock = DockStyle.Top,
            AutoSize = true,
            AutoSizeMode = AutoSizeMode.GrowAndShrink,
            ColumnCount = 1,
            Padding = new Padding(35, 25, 35, 30)
        };
        mainLayout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100f));
        this.Controls.Add(mainLayout);

        var headerPanel = new TableLayoutPanel
        {
            Dock = DockStyle.Top,
            AutoSize = true,
            ColumnCount = 2,
            RowCount = 1,
            Margin = new Padding(0, 0, 0, 15)
        };
        headerPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 80f));
        headerPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 20f));

        var titleBox = new FlowLayoutPanel
        {
            Dock = DockStyle.Fill,
            FlowDirection = FlowDirection.TopDown,
            AutoSize = true,
            WrapContents = false,
            Margin = new Padding(0)
        };

        var titleLabel = new Label
        {
            Text = "UAMOTORS CAD ALERT v2.0",
            Font = new Font("Segoe UI", 18, FontStyle.Bold),
            ForeColor = Color.FromArgb(15, 23, 42),
            AutoSize = true,
            Margin = new Padding(0, 0, 0, 8)
        };
        titleBox.Controls.Add(titleLabel);

        var subtitleLabel = new Label
        {
            Text = "Ingresa tu correo institucional para vincular este equipo:",
            Font = new Font("Segoe UI", 11),
            ForeColor = Color.FromArgb(100, 116, 139),
            AutoSize = true,
            Margin = new Padding(0)
        };
        titleBox.Controls.Add(subtitleLabel);
        headerPanel.Controls.Add(titleBox, 0, 0);

        try
        {
            var assembly = Assembly.GetExecutingAssembly();
            using var stream = assembly.GetManifestResourceStream("UAMotorsCADAlert.Resources.cad_alert.png");
            if (stream != null && stream.Length > 0)
            {
                var logoBox = new PictureBox
                {
                    Image = Image.FromStream(stream),
                    SizeMode = PictureBoxSizeMode.Zoom,
                    Size = new Size(80, 80),
                    Anchor = AnchorStyles.Top | AnchorStyles.Right,
                    BackColor = Color.Transparent,
                    Margin = new Padding(0)
                };
                headerPanel.Controls.Add(logoBox, 1, 0);
            }
        }
        catch (Exception) { }

        mainLayout.Controls.Add(headerPanel);

        var emailLabel = new Label
        {
            Text = "Correo:",
            Font = new Font("Segoe UI", 11, FontStyle.Bold),
            ForeColor = Color.FromArgb(15, 23, 42),
            AutoSize = true,
            Margin = new Padding(0, 5, 0, 6)
        };
        mainLayout.Controls.Add(emailLabel);

        _emailInput = new TextBox
        {
            Font = new Font("Segoe UI", 12),
            Dock = DockStyle.Top,
            Margin = new Padding(0, 0, 0, 10)
        };
        mainLayout.Controls.Add(_emailInput);

        _statusLabel = new Label
        {
            Text = "",
            Font = new Font("Segoe UI", 10),
            AutoSize = true,
            Dock = DockStyle.Top,
            MinimumSize = new Size(0, 24),
            Margin = new Padding(0, 0, 0, 15)
        };
        mainLayout.Controls.Add(_statusLabel);

        _verifyButton = new Button
        {
            Text = "Verificar y activar monitoreo",
            Font = new Font("Segoe UI", 11, FontStyle.Bold),
            BackColor = Color.FromArgb(220, 38, 38),
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat,
            Height = 46,
            Dock = DockStyle.Top,
            Cursor = Cursors.Hand,
            Margin = new Padding(0, 0, 0, 25)
        };
        _verifyButton.FlatAppearance.BorderSize = 0;
        _verifyButton.Click += VerifyButton_Click;
        mainLayout.Controls.Add(_verifyButton);

        var footerLabel = new LinkLabel
        {
            Text = "Desarrollado por Alejandro Ramírez | UAMOTORS, Departamento de Electrónica",
            Font = new Font("Segoe UI", 9),
            LinkColor = Color.FromArgb(37, 99, 235),
            ActiveLinkColor = Color.FromArgb(37, 99, 235),
            AutoSize = true,
            Margin = new Padding(0, 0, 0, 4)
        };
        footerLabel.LinkArea = new LinkArea(17, 17);
        footerLabel.LinkClicked += (s, ev) => 
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo("https://github.com/lexrammart") { UseShellExecute = true });
        mainLayout.Controls.Add(footerLabel);

        var uamLabel = new Label
        {
            Text = "Universidad Autónoma Metropolitana",
            Font = new Font("Segoe UI", 9, FontStyle.Italic),
            ForeColor = Color.FromArgb(100, 116, 139),
            AutoSize = true,
            Margin = new Padding(0)
        };
        mainLayout.Controls.Add(uamLabel);

        this.AcceptButton = _verifyButton;
    }

    private async void VerifyButton_Click(object? sender, EventArgs e)
    {
        string email = _emailInput.Text;
        _statusLabel.Text = "Verificando en la base de datos de Drive...";
        _statusLabel.ForeColor = Color.FromArgb(37, 99, 235);
        _verifyButton.Enabled = false;

        var result = await Task.Run(() => UserService.VerifyUserEmail(email, _rutaUAMOTORS));

        if (result.Success)
        {
            UserService.SaveLocalProfile(email, result.Name!);
            _statusLabel.Text = $"Registro completado para el usuario: {result.Name}.";
            _statusLabel.ForeColor = Color.FromArgb(22, 163, 74);
            IsRegistered = true;
            await Task.Delay(3000);
            this.Close();
        }
        else
        {
            _statusLabel.Text = result.ErrorMsg;
            _statusLabel.ForeColor = Color.FromArgb(220, 38, 38);
            _verifyButton.Enabled = true;
            _emailInput.Enabled = true;
        }
    }
}
