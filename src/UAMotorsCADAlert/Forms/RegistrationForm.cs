namespace UAMotorsCADAlert.Forms;

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
        this.Size = new Size(460, 310);
        this.FormBorderStyle = FormBorderStyle.FixedDialog;
        this.MaximizeBox = false;
        this.MinimizeBox = false;
        this.StartPosition = FormStartPosition.CenterScreen;
        this.BackColor = Color.FromArgb(248, 250, 252);

        var titleLabel = new Label
        {
            Text = "⚙️ UAMOTORS CAD Alert",
            Font = new Font("Segoe UI", 16, FontStyle.Bold),
            ForeColor = Color.FromArgb(15, 23, 42),
            AutoSize = true,
            Location = new Point(42, 22)
        };
        this.Controls.Add(titleLabel);

        var subtitleLabel = new Label
        {
            Text = "Ingresa tu correo institucional para vincular este equipo:",
            Font = new Font("Segoe UI", 10),
            ForeColor = Color.FromArgb(100, 116, 139),
            AutoSize = true,
            Location = new Point(42, 60)
        };
        this.Controls.Add(subtitleLabel);

        var emailLabel = new Label
        {
            Text = "Correo Electrónico:",
            Font = new Font("Segoe UI", 10, FontStyle.Bold),
            ForeColor = Color.FromArgb(15, 23, 42),
            AutoSize = true,
            Location = new Point(42, 100)
        };
        this.Controls.Add(emailLabel);

        _emailInput = new TextBox
        {
            Font = new Font("Segoe UI", 11),
            Size = new Size(360, 30),
            Location = new Point(42, 125)
        };
        this.Controls.Add(_emailInput);

        _statusLabel = new Label
        {
            Text = "",
            Font = new Font("Segoe UI", 9),
            AutoSize = false,
            Size = new Size(360, 40),
            Location = new Point(42, 165)
        };
        this.Controls.Add(_statusLabel);

        _verifyButton = new Button
        {
            Text = "Verificar y Activar Monitoreo",
            Font = new Font("Segoe UI", 10, FontStyle.Bold),
            BackColor = Color.FromArgb(37, 99, 235),
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat,
            Size = new Size(360, 40),
            Location = new Point(42, 210),
            Cursor = Cursors.Hand
        };
        _verifyButton.FlatAppearance.BorderSize = 0;
        _verifyButton.Click += VerifyButton_Click;
        this.Controls.Add(_verifyButton);
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
            _statusLabel.Text = $"✅ ¡Bienvenido(a) {result.Name}! Registro completado.";
            _statusLabel.ForeColor = Color.FromArgb(22, 163, 74);
            IsRegistered = true;
            await Task.Delay(1500);
            this.Close();
        }
        else
        {
            _statusLabel.Text = $"❌ {result.ErrorMsg}";
            _statusLabel.ForeColor = Color.FromArgb(220, 38, 38);
            _verifyButton.Enabled = true;
        }
    }
}
