"""
User registration GUI interface using Tkinter.
"""

import tkinter as tk
from src.services.user_service import verify_user_email, save_local_profile


def mostrar_ventana_registro(ruta_uamotors):
    root = tk.Tk()
    root.title("UAMOTORS CAD Alert - Registro de Usuario")
    root.geometry("460x310")
    root.resizable(False, False)

    bg_color = "#f8fafc"
    primary_color = "#0f172a"
    accent_color = "#2563eb"

    root.configure(bg=bg_color)

    tk.Label(
        root,
        text="⚙️ UAMOTORS CAD Alert",
        font=("Segoe UI", 16, "bold"),
        bg=bg_color,
        fg=primary_color,
    ).pack(pady=(22, 4))

    tk.Label(
        root,
        text="Ingresa tu correo institucional para vincular este equipo:",
        font=("Segoe UI", 10),
        bg=bg_color,
        fg="#64748b",
    ).pack(pady=(0, 16))

    tk.Label(
        root,
        text="Correo Electrónico:",
        font=("Segoe UI", 10, "bold"),
        bg=bg_color,
        fg=primary_color,
    ).pack(anchor="w", padx=42)

    entry_email = tk.Entry(
        root, font=("Segoe UI", 11), width=36, bd=1, relief="solid"
    )
    entry_email.pack(padx=42, pady=(5, 12), ipady=5)
    entry_email.focus()

    lbl_status = tk.Label(
        root, text="", font=("Segoe UI", 9), bg=bg_color, wraplength=380
    )
    lbl_status.pack(pady=(0, 12))

    registrado = [False]

    def on_verificar():
        email = entry_email.get()
        lbl_status.config(
            text="Verificando en la base de datos de Drive...", fg="#2563eb"
        )
        root.update_idletasks()

        exito, nombre, err_msg = verify_user_email(email, ruta_uamotors)
        if exito:
            save_local_profile(email, nombre)
            lbl_status.config(
                text=f"✅ ¡Bienvenido(a) {nombre}! Registro completado.",
                fg="#16a34a",
            )
            registrado[0] = True
            root.after(1500, root.destroy)
        else:
            lbl_status.config(text=f"❌ {err_msg}", fg="#dc2626")

    btn_verificar = tk.Button(
        root,
        text="Verificar y Activar Monitoreo",
        font=("Segoe UI", 10, "bold"),
        bg=accent_color,
        fg="white",
        activebackground="#1d4ed8",
        activeforeground="white",
        bd=0,
        relief="flat",
        cursor="hand2",
        command=on_verificar,
    )
    btn_verificar.pack(padx=42, ipady=6, fill="x")

    # Si cierran la ventana con la 'X', root.destroy terminará el mainloop y retornará False
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    root.mainloop()
    return registrado[0]
