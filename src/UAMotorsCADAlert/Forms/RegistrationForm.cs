namespace UAMotorsCADAlert.Forms;

using System.Reflection;
using UAMotorsCADAlert.Services;

public class RegistrationForm : Form
{
    private TextBox _emailInput = null!;
    private Button _verifyButton = null!;
    private Label _statusLabel = null!;
    private string _rutaUamotors;
    public bool IsRegistered { get; private set; }

    public RegistrationForm(string rutaUamotors)
    {
        _rutaUamotors = rutaUamotors;
        InitializeComponent();
    }

    private void InitializeComponent()
    {
        this.Text = "UAMOTORS CAD Alert - Registro";
        this.Size = new Size(750, 500);
        this.FormBorderStyle = FormBorderStyle.FixedDialog;
        this.MaximizeBox = false;
        this.MinimizeBox = false;
        this.StartPosition = FormStartPosition.CenterScreen;
        this.BackColor = Color.FromArgb(248, 250, 252);
        this.AutoScaleMode = AutoScaleMode.Dpi;

        var titleLabel = new Label
        {
            Text = "UAMOTORS CAD Alert",
            Font = new Font("Segoe UI", 18, FontStyle.Bold),
            ForeColor = Color.FromArgb(15, 23, 42),
            AutoSize = true,
            Location = new Point(40, 30)
        };
        this.Controls.Add(titleLabel);

        var versionLabel = new Label
        {
            Text = "v2.0",
            Font = new Font("Segoe UI", 9, FontStyle.Bold),
            ForeColor = Color.FromArgb(100, 116, 139),
            AutoSize = true,
            Location = new Point(40, 65)
        };
        this.Controls.Add(versionLabel);

        var subtitleLabel = new Label
        {
            Text = "Ingresa tu correo institucional para vincular este equipo:",
            Font = new Font("Segoe UI", 11),
            ForeColor = Color.FromArgb(100, 116, 139),
            AutoSize = true,
            Location = new Point(40, 95)
        };
        this.Controls.Add(subtitleLabel);

        var emailLabel = new Label
        {
            Text = "Correo: ",
            Font = new Font("Segoe UI", 11, FontStyle.Bold),
            ForeColor = Color.FromArgb(15, 23, 42),
            AutoSize = true,
            Location = new Point(40, 140)
        };
        this.Controls.Add(emailLabel);

        try
        {
            var assembly = Assembly.GetExecutingAssembly();
            using var stream = assembly.GetManifestResourceStream("UAMotorsCADAlert.Resources.uamotors.png");
            if (stream != null && stream.Length > 0)
            {
                var logoBox = new PictureBox
                {
                    Image = Image.FromStream(stream),
                    SizeMode = PictureBoxSizeMode.Zoom,
                    Size = new Size(90, 90),
                    Location = new Point(600, 25),
                    BackColor = Color.Transparent
                };
                this.Controls.Add(logoBox);
            }
        }
        catch (Exception) { }

        _emailInput = new TextBox
        {
            Font = new Font("Segoe UI", 12),
            Size = new Size(650, 35),
            Location = new Point(40, 170)
        };
        this.Controls.Add(_emailInput);

        _statusLabel = new Label
        {
            Text = "",
            Font = new Font("Segoe UI", 10),
            AutoSize = false,
            Size = new Size(650, 60),
            Location = new Point(40, 215)
        };
        this.Controls.Add(_statusLabel);

        _verifyButton = new Button
        {
            Text = "Verificar y activar monitoreo",
            Font = new Font("Segoe UI", 11, FontStyle.Bold),
            BackColor = Color.FromArgb(220, 38, 38), // Rojo
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat,
            Size = new Size(650, 45),
            Location = new Point(40, 290),
            Cursor = Cursors.Hand
        };
        _verifyButton.FlatAppearance.BorderSize = 0;
        _verifyButton.Click += VerifyButton_Click;
        this.Controls.Add(_verifyButton);

        var footerLabel = new LinkLabel
        {
            Text = "Desarrollado por Alejandro Ramírez | UAMOTORS, Departamento de Electronics",
            Font = new Font("Segoe UI", 9),
            LinkColor = Color.FromArgb(37, 99, 235),
            ActiveLinkColor = Color.FromArgb(37, 99, 235),
            AutoSize = true,
            Location = new Point(40, 410)
        };
        footerLabel.LinkArea = new LinkArea(17, 17);
        footerLabel.LinkClicked += (s, ev) => System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo("https://github.com/lexrammart") { UseShellExecute = true });
        this.Controls.Add(footerLabel);

        // Permitir que la tecla Enter active el botón
        this.AcceptButton = _verifyButton;
    }

    private async void VerifyButton_Click(object? sender, EventArgs e)
    {
        string email = _emailInput.Text;
        _statusLabel.Text = "Verificando en la base de datos de Drive...";
        _statusLabel.ForeColor = Color.FromArgb(37, 99, 235);
        _verifyButton.Enabled = false;

        var result = await Task.Run(() => UserService.VerifyUserEmail(email, _rutaUamotors));

        if (result.Success)
        {
            UserService.SaveLocalProfile(email, result.Name!);
            _statusLabel.Text = $"✅ ¡Bienvenidx {result.Name}! Registro completado.";
            _statusLabel.ForeColor = Color.FromArgb(22, 163, 74);
            IsRegistered = true;
            await Task.Delay(3000);
            this.Close();
        }
        else
        {
            _statusLabel.Text = $"❌ {result.ErrorMsg}";
            _statusLabel.ForeColor = Color.FromArgb(220, 38, 38);
            _verifyButton.Enabled = true;
            _emailInput.Enabled = true;
        }
    }
}
