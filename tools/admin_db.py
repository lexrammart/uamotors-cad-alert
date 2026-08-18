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

def find_uamotors_folder():
    if os.name == 'nt': # Windows
        possible_paths = [
            os.path.join(os.path.expanduser("~"), "Google Drive", TARGET_FOLDER),
            "G:\\Unidades compartidas\\UAMOTORS",
            "G:\\Shared drives\\UAMOTORS",
            "H:\\Unidades compartidas\\UAMOTORS",
            "H:\\Shared drives\\UAMOTORS"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                return p
    else: # macOS
        cloud_storage = os.path.expanduser("~/Library/CloudStorage")
        if os.path.exists(cloud_storage):
            for item in os.listdir(cloud_storage):
                if item.startswith("GoogleDrive-"):
                    path_en = os.path.join(cloud_storage, item, "Shared drives", "UAMOTORS")
                    if os.path.exists(path_en):
                        return path_en
                    path_es = os.path.join(cloud_storage, item, "Unidades compartidas", "UAMOTORS")
                    if os.path.exists(path_es):
                        return path_es
    return None

def get_encryption_key():
    secret = "UAMOTORS_2026_CAD_ELECTRONICS"
    salt = "UAMOTORS_CAD_ALERT_SALT"
    key = hashlib.pbkdf2_hmac('sha256', secret.encode(), salt.encode(), 100000)
    return base64.urlsafe_b64encode(key)

def get_db_path():
    base = find_uamotors_folder()
    if not base:
        messagebox.showerror("Error Crítico", "No se encontró la carpeta 'UAMOTORS' en tu Google Drive.\nAsegúrate de tener Google Drive sincronizado.")
        return ""
    return os.path.join(base, REL_DRIVE_DB_PATH)

class AdminPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UAMOTORS CAD ALERT - Panel de Administrador")
        self.geometry("700x600")
        self.minsize(500, 400)
        self.db_path = get_db_path()
        self.fernet = Fernet(get_encryption_key())
        
        self.db_data = {
            "config": {
                "webhook_url": "",
                "saved_webhooks": "[]" # Serializado como string para no romper Dictionary<string, string> en C#
            },
            "users": {}
        }
        
        self.setup_ui()
        self.load_db()

    def setup_ui(self):
        # Configurar para que la ventana sea responsiva
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Crear Notebook (Pestañas)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # ================= PESTAÑA USUARIOS =================
        self.tab_users = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_users, text="👥 Usuarios")
        self.setup_users_tab()

        # ================= PESTAÑA DISCORD =================
        self.tab_discord = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_discord, text="👾 Discord Server")
        self.setup_discord_tab()

    def setup_users_tab(self):
        self.tab_users.grid_rowconfigure(1, weight=1)
        self.tab_users.grid_columnconfigure(0, weight=1)

        # Formulario Agregar
        add_frame = tk.LabelFrame(self.tab_users, text="Agregar Nuevo Usuario")
        add_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Inner frame to keep things centered-ish but aligned
        inner_frame = tk.Frame(add_frame)
        inner_frame.pack(pady=5)
        
        tk.Label(inner_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_name = tk.Entry(inner_frame, width=35)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(inner_frame, text="Correo:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_email = tk.Entry(inner_frame, width=35)
        self.entry_email.grid(row=1, column=1, padx=5, pady=5)
        
        btn_add = tk.Button(inner_frame, text="Agregar Usuario", command=self.add_user, width=15)
        btn_add.grid(row=2, column=0, columnspan=2, pady=(5, 5))

        # Lista de Usuarios
        list_frame = tk.LabelFrame(self.tab_users, text="Usuarios Registrados")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        search_frame = tk.Frame(list_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(search_frame, text="Buscar por correo:").pack(side="left")
        self.entry_search = tk.Entry(search_frame, width=30)
        self.entry_search.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_search.bind("<KeyRelease>", lambda e: self.refresh_users_list())
        
        style = ttk.Style()
        style.configure("Treeview", font=("Menlo", 10))
        
        columns = ("email", "name")
        self.tree_users = ttk.Treeview(list_frame, columns=columns, show="headings", style="Treeview")
        self.tree_users.heading("email", text="Correo Electrónico")
        self.tree_users.heading("name", text="Nombre")
        self.tree_users.column("email", width=200, anchor="w")
        self.tree_users.column("name", width=250, anchor="w")
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_users.yview)
        self.tree_users.configure(yscroll=scrollbar.set)
        
        self.tree_users.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # Acciones
        action_frame = tk.Frame(self.tab_users)
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        btn_remove = tk.Button(action_frame, text="Eliminar Seleccionado", command=self.remove_user)
        btn_remove.pack(side="left", padx=5)
        
        btn_import = tk.Button(action_frame, text="Importar CSV", command=self.import_csv)
        btn_import.pack(side="right", padx=5)

    def setup_discord_tab(self):
        self.tab_discord.grid_rowconfigure(1, weight=1)
        self.tab_discord.grid_columnconfigure(0, weight=1)

        # Formulario Agregar
        add_frame = tk.LabelFrame(self.tab_discord, text="Agregar Nuevo Webhook")
        add_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        inner_frame = tk.Frame(add_frame)
        inner_frame.pack(pady=5, fill="x", expand=True, padx=10)
        
        tk.Label(inner_frame, text="Nombre (Ej. Pruebas):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_wh_name = tk.Entry(inner_frame)
        self.entry_wh_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        tk.Label(inner_frame, text="URL del Webhook:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_wh_url = tk.Entry(inner_frame)
        self.entry_wh_url.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        inner_frame.grid_columnconfigure(1, weight=1)

        btn_add_wh = tk.Button(inner_frame, text="Agregar a la Lista", command=self.add_webhook)
        btn_add_wh.grid(row=2, column=0, columnspan=2, pady=(5, 5))

        # Lista de Webhooks
        list_frame = tk.LabelFrame(self.tab_discord, text="Webhooks Guardados")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        columns = ("status", "name", "url")
        self.tree_webhooks = ttk.Treeview(list_frame, columns=columns, show="headings", style="Treeview")
        self.tree_webhooks.heading("status", text="Estado")
        self.tree_webhooks.heading("name", text="Nombre")
        self.tree_webhooks.heading("url", text="URL")
        
        self.tree_webhooks.column("status", width=80, anchor="center")
        self.tree_webhooks.column("name", width=150, anchor="w")
        self.tree_webhooks.column("url", width=300, anchor="w")
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_webhooks.yview)
        self.tree_webhooks.configure(yscroll=scrollbar.set)
        
        self.tree_webhooks.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # Acciones
        action_frame = tk.Frame(self.tab_discord)
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        btn_activate = tk.Button(action_frame, text="Marcar como ACTIVO", command=self.activate_webhook, fg="green", font=("", 10, "bold"))
        btn_activate.pack(side="left", padx=5)
        
        btn_remove = tk.Button(action_frame, text="Eliminar Seleccionado", command=self.remove_webhook)
        btn_remove.pack(side="right", padx=5)

    # ================= LOGICA DE BASE DE DATOS =================
    
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
                
            if "config" not in self.db_data:
                self.db_data["config"] = {"webhook_url": "", "saved_webhooks": "[]"}
            else:
                if "saved_webhooks" not in self.db_data["config"]:
                    self.db_data["config"]["saved_webhooks"] = "[]"
                
            self.refresh_users_list()
            self.refresh_webhooks_list()
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

    # ================= LOGICA DE USUARIOS =================
    
    def refresh_users_list(self):
        for item in self.tree_users.get_children():
            self.tree_users.delete(item)
            
        search_term = ""
        if hasattr(self, "entry_search"):
            search_term = self.entry_search.get().strip().lower()
            
        users = self.db_data.get("users", {})
        for email, info in users.items():
            if search_term in email:
                self.tree_users.insert("", "end", values=(email, info.get("nombre", "")))

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
        self.refresh_users_list()
        
        self.entry_name.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)

    def remove_user(self):
        selected = self.tree_users.selection()
        if not selected:
            return
            
        item = selected[0]
        email = self.tree_users.item(item, "values")[0]
        
        if messagebox.askyesno("Confirmar", f"Eliminar a {email}?"):
            if email in self.db_data.get("users", {}):
                del self.db_data["users"][email]
                self.save_db()
                self.refresh_users_list()

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
                self.refresh_users_list()
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")

    # ================= LOGICA DE WEBHOOKS =================
    
    def get_saved_webhooks(self):
        try:
            val = self.db_data["config"].get("saved_webhooks", "[]")
            return json.loads(val)
        except:
            return []
            
    def set_saved_webhooks(self, wh_list):
        self.db_data["config"]["saved_webhooks"] = json.dumps(wh_list)

    def refresh_webhooks_list(self):
        for item in self.tree_webhooks.get_children():
            self.tree_webhooks.delete(item)
            
        active_url = self.db_data["config"].get("webhook_url", "")
        wh_list = self.get_saved_webhooks()
        
        for idx, wh in enumerate(wh_list):
            name = wh.get("name", "Sin Nombre")
            url = wh.get("url", "")
            status = "★ ACTIVO" if url == active_url and url != "" else ""
            self.tree_webhooks.insert("", "end", iid=str(idx), values=(status, name, url))

    def add_webhook(self):
        name = self.entry_wh_name.get().strip()
        url = self.entry_wh_url.get().strip()
        
        if not name or not url.startswith("http"):
            messagebox.showwarning("Advertencia", "Ingresa un nombre y una URL válida que empiece con http.")
            return
            
        wh_list = self.get_saved_webhooks()
        wh_list.append({"name": name, "url": url})
        self.set_saved_webhooks(wh_list)
        
        # Si es el unico, activarlo por defecto
        if len(wh_list) == 1:
            self.db_data["config"]["webhook_url"] = url
            
        self.save_db()
        self.refresh_webhooks_list()
        
        self.entry_wh_name.delete(0, tk.END)
        self.entry_wh_url.delete(0, tk.END)

    def remove_webhook(self):
        selected = self.tree_webhooks.selection()
        if not selected:
            return
            
        idx = int(selected[0])
        wh_list = self.get_saved_webhooks()
        
        if idx < len(wh_list):
            wh = wh_list[idx]
            if messagebox.askyesno("Confirmar", f"Eliminar Webhook '{wh['name']}'?"):
                # Si estaba activo, limpiarlo
                if self.db_data["config"].get("webhook_url", "") == wh['url']:
                    self.db_data["config"]["webhook_url"] = ""
                
                wh_list.pop(idx)
                self.set_saved_webhooks(wh_list)
                self.save_db()
                self.refresh_webhooks_list()

    def activate_webhook(self):
        selected = self.tree_webhooks.selection()
        if not selected:
            messagebox.showinfo("Info", "Selecciona un Webhook de la lista para activarlo.")
            return
            
        idx = int(selected[0])
        wh_list = self.get_saved_webhooks()
        
        if idx < len(wh_list):
            wh = wh_list[idx]
            self.db_data["config"]["webhook_url"] = wh['url']
            self.save_db()
            self.refresh_webhooks_list()
            messagebox.showinfo("Éxito", f"Webhook '{wh['name']}' marcado como ACTIVO.")

if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()
