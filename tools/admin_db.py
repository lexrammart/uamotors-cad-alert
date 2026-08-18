import os
import json
import base64
import csv
import hashlib
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from cryptography.fernet import Fernet

TARGET_FOLDER = "UAMOTORS"
REL_DRIVE_DB_PATH = os.path.join("2026", "Design", "Electronics", "CAD-Alert", "authorized_users.uamotors")
MAC_DRIVE_UAMOTORS_PATH = "/Users/alejandro/Library/CloudStorage/GoogleDrive-[CORREO_INSTITUCIONAL_REDACTADO]/Shared drives/UAMOTORS"

def get_encryption_key():
    secret = "UAMOTORS_2026_CAD_ELECTRONICS"
    salt = "UAMOTORS_CAD_ALERT_SALT"
    key = hashlib.pbkdf2_hmac('sha256', secret.encode(), salt.encode(), 100000)
    return base64.urlsafe_b64encode(key)

def get_db_path():
    if os.name != 'nt':
        base = MAC_DRIVE_UAMOTORS_PATH
    else:
        base = os.path.join(os.path.expanduser("~"), "Google Drive", TARGET_FOLDER)
    return os.path.join(base, REL_DRIVE_DB_PATH)

class AdminPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UAMOTORS CAD ALERT - Panel de Administrador")
        self.geometry("650x550")
        self.db_path = get_db_path()
        self.fernet = Fernet(get_encryption_key())
        
        self.db_data = {
            "config": {"webhook_url": ""},
            "users": {}
        }
        
        self.setup_ui()
        self.load_db()

    def setup_ui(self):
        config_frame = tk.LabelFrame(self, text="Configuracion del Sistema")
        config_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(config_frame, text="URL del Webhook:").pack(side="left", padx=5, pady=5)
        self.entry_webhook = tk.Entry(config_frame, width=50)
        self.entry_webhook.pack(side="left", padx=5, pady=5)
        btn_save_config = tk.Button(config_frame, text="Guardar Webhook", command=self.save_config)
        btn_save_config.pack(side="left", padx=5, pady=5)

        add_frame = tk.LabelFrame(self, text="Agregar Nuevo Usuario")
        add_frame.pack(fill="x", padx=10, pady=5)
        
        inner_frame = tk.Frame(add_frame)
        inner_frame.pack(pady=10)
        
        tk.Label(inner_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_name = tk.Entry(inner_frame, width=35)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(inner_frame, text="Correo:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_email = tk.Entry(inner_frame, width=35)
        self.entry_email.grid(row=1, column=1, padx=5, pady=5)
        
        btn_add = tk.Button(inner_frame, text="Agregar Usuario", command=self.add_user, width=15)
        btn_add.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        list_frame = tk.LabelFrame(self, text="Usuarios Registrados")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        search_frame = tk.Frame(list_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(search_frame, text="Buscar por correo:").pack(side="left")
        self.entry_search = tk.Entry(search_frame, width=30)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", lambda e: self.refresh_list())
        
        style = ttk.Style()
        style.configure("Treeview", font=("Menlo", 10))
        
        columns = ("email", "name")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", style="Treeview")
        self.tree.heading("email", text="Correo Electronico")
        self.tree.heading("name", text="Nombre")
        self.tree.column("email", width=250, anchor="w")
        self.tree.column("name", width=300, anchor="w")
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        action_frame = tk.Frame(self)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        btn_remove = tk.Button(action_frame, text="Eliminar Seleccionado", command=self.remove_user)
        btn_remove.pack(side="left", padx=5)
        
        btn_import = tk.Button(action_frame, text="Importar CSV", command=self.import_csv)
        btn_import.pack(side="right", padx=5)

    def load_db(self):
        if not os.path.exists(self.db_path):
            return

        try:
            with open(self.db_path, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = self.fernet.decrypt(encrypted_data).decode("utf-8")
            loaded_json = json.loads(decrypted_data)
            
            if "users" in loaded_json:
                self.db_data = loaded_json
            else:
                self.db_data["users"] = loaded_json
                
            self.entry_webhook.delete(0, tk.END)
            self.entry_webhook.insert(0, self.db_data.get("config", {}).get("webhook_url", ""))
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar o desencriptar la base de datos:\n{e}")

    def save_db(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            json_str = json.dumps(self.db_data, ensure_ascii=False)
            encrypted_data = self.fernet.encrypt(json_str.encode("utf-8"))
            
            with open(self.db_path, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la base de datos:\n{e}")

    def save_config(self):
        webhook = self.entry_webhook.get().strip()
        if "config" not in self.db_data:
            self.db_data["config"] = {}
        self.db_data["config"]["webhook_url"] = webhook
        self.save_db()
        messagebox.showinfo("Exito", "Configuracion de Webhook guardada y encriptada.")

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        search_term = ""
        if hasattr(self, "entry_search"):
            search_term = self.entry_search.get().strip().lower()
            
        users = self.db_data.get("users", {})
        for email, info in users.items():
            if search_term in email:
                self.tree.insert("", "end", values=(email, info.get("nombre", "")))

    def add_user(self):
        name = self.entry_name.get().strip().upper()
        email = self.entry_email.get().strip().lower()
        
        if not name or not email or "@" not in email:
            messagebox.showwarning("Advertencia", "Ingresa un nombre y un correo valido.")
            return
            
        if "users" not in self.db_data:
            self.db_data["users"] = {}
            
        self.db_data["users"][email] = {"nombre": name}
        self.save_db()
        self.refresh_list()
        
        self.entry_name.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)

    def remove_user(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        item = selected[0]
        email = self.tree.item(item, "values")[0]
        
        if messagebox.askyesno("Confirmar", f"Eliminar a {email}?"):
            if email in self.db_data.get("users", {}):
                del self.db_data["users"][email]
                self.save_db()
                self.refresh_list()

    def import_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*"))
        )
        
        if not file_path:
            return
            
        count = 0
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        email = row[0].strip().lower()
                        name = row[1].strip().upper()
                        
                        if email == "correo" or "email" in email or "@" not in email:
                            continue
                            
                        if "users" not in self.db_data:
                            self.db_data["users"] = {}
                        self.db_data["users"][email] = {"nombre": name}
                        count += 1
            
            if count > 0:
                self.save_db()
                self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")

if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()
